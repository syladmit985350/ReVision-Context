from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from revision_context.allocator import estimate_token_count, select_anchors_under_budget
from revision_context.anchors import extract_candidate_anchors
from revision_context.baselines import PLACEHOLDER_PREDICTION, predict_with_stub_model
from revision_context.benchmarks.synthetic_exactness import (
    generate_synthetic_exactness_examples,
    write_synthetic_exactness_jsonl,
)
from revision_context.eval.render_diagnostics import summarize_render_outputs
from revision_context.prompting import build_hybrid_prompt_bundle
from revision_context.renderer.text_renderer import render_text_to_pages
from revision_context.renderer.types import RenderOptions
from revision_context.reread import reread_lines_around_coordinate
from revision_context.verifier import verify_prediction


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="revision-context",
        description="Minimal CLI for the ReVision-Context++ bootstrap task.",
    )
    subparsers = parser.add_subparsers(dest="command")

    smoke_parser = subparsers.add_parser(
        "smoke",
        help="Run a lightweight bootstrap smoke command.",
    )
    smoke_parser.set_defaults(handler=run_smoke)

    synthetic_parser = subparsers.add_parser(
        "make-synthetic",
        help="Generate deterministic synthetic exactness examples.",
    )
    synthetic_parser.add_argument("--out", required=True, help="Output JSONL path.")
    synthetic_parser.add_argument("--n", type=int, default=20, help="Number of rows.")
    synthetic_parser.add_argument("--seed", type=int, default=0, help="Random seed.")
    synthetic_parser.set_defaults(handler=run_make_synthetic)

    render_parser = subparsers.add_parser(
        "render",
        help="Render synthetic examples into page PNGs plus page-line mappings.",
    )
    render_parser.add_argument("--input", required=True, help="Input JSONL path.")
    render_parser.add_argument("--out", required=True, help="Output directory.")
    render_parser.add_argument("--limit", type=int, default=None, help="Optional row limit.")
    render_parser.add_argument("--page-width", type=int, default=900)
    render_parser.add_argument("--page-height", type=int, default=1200)
    render_parser.add_argument("--font-size", type=int, default=16)
    render_parser.add_argument("--line-height", type=int, default=22)
    render_parser.add_argument("--margin", type=int, default=40)
    render_parser.add_argument(
        "--proportional",
        action="store_true",
        help="Use a proportional font instead of the default monospace font.",
    )
    render_parser.set_defaults(handler=run_render)

    hybrid_parser = subparsers.add_parser(
        "run-hybrid",
        help="Run the Phase 1 heuristic hybrid anchor pipeline.",
    )
    hybrid_parser.add_argument("--input", required=True, help="Input JSONL path.")
    hybrid_parser.add_argument("--out", required=True, help="Output directory.")
    hybrid_parser.add_argument("--anchor-budget", type=int, default=128, help="Anchor token budget.")
    hybrid_parser.add_argument("--limit", type=int, default=None, help="Optional row limit.")
    hybrid_parser.add_argument("--page-width", type=int, default=900)
    hybrid_parser.add_argument("--page-height", type=int, default=1200)
    hybrid_parser.add_argument("--font-size", type=int, default=16)
    hybrid_parser.add_argument("--line-height", type=int, default=22)
    hybrid_parser.add_argument("--margin", type=int, default=40)
    hybrid_parser.set_defaults(handler=run_hybrid)
    return parser


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def run_make_synthetic(args: argparse.Namespace) -> int:
    examples = generate_synthetic_exactness_examples(n=args.n, seed=args.seed)
    out_path = Path(args.out)
    write_synthetic_exactness_jsonl(examples, out_path)
    print(f"wrote {len(examples)} synthetic examples to {out_path}")
    return 0


def run_render(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    out_dir = Path(args.out)
    rows = _read_jsonl(input_path)
    if args.limit is not None:
        rows = rows[: args.limit]

    options = RenderOptions(
        page_width=args.page_width,
        page_height=args.page_height,
        font_size=args.font_size,
        line_height=args.line_height,
        margin=args.margin,
        monospace=not args.proportional,
    )

    rendered_examples = []
    examples_dir = out_dir / "examples"
    for row in rows:
        example_id = str(row["id"])
        example_dir = examples_dir / example_id
        rendered_examples.append(
            render_text_to_pages(
                text=str(row["context"]),
                out_dir=example_dir,
                example_id=example_id,
                options=options,
            )
        )

    diagnostics_path = out_dir / "diagnostics.json"
    summary = summarize_render_outputs(rendered_examples, diagnostics_path)
    print(
        "rendered "
        f"{summary['num_examples_rendered']} examples across {summary['num_pages']} pages "
        f"to {out_dir}"
    )
    return 0


def _mapping_rows_by_line(mapping_path: Path) -> list[dict]:
    return _read_jsonl(mapping_path)


def _coordinate_from_metadata(mapping_rows: list[dict], metadata: dict) -> tuple[int, int] | None:
    answer_line_index = metadata.get("answer_line_index")
    if answer_line_index is None:
        return None
    for row in mapping_rows:
        if int(row["source_line_index"]) == int(answer_line_index):
            page = int(row.get("first_page_number") or 1)
            line = int(row.get("first_line_number") or 1)
            return (page, line)
    return None


def _write_results_jsonl(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows)
    out_path.write_text(f"{payload}\n" if payload else "", encoding="utf-8")


def _build_hybrid_summary(results: list[dict], diagnostics: dict, out_path: Path) -> dict:
    num_examples = len(results)
    num_correct = sum(1 for result in results if result["correct"])
    anchor_tokens = sum(result["budget"]["anchor_tokens"] for result in results)
    reread_tokens = sum(result["budget"]["reread_tokens"] for result in results)
    visual_tokens_est = sum(result["budget"]["visual_tokens_est"] for result in results)
    summary = {
        "num_examples": num_examples,
        "num_correct": num_correct,
        "accuracy": round(num_correct / num_examples, 4) if num_examples else 0.0,
        "anchor_tokens": anchor_tokens,
        "reread_tokens": reread_tokens,
        "visual_tokens_est": visual_tokens_est,
        "total_tokens_est": anchor_tokens + reread_tokens + visual_tokens_est,
        "render_diagnostics": diagnostics,
    }
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_hybrid(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    out_dir = Path(args.out)
    rows = _read_jsonl(input_path)
    if args.limit is not None:
        rows = rows[: args.limit]

    options = RenderOptions(
        page_width=args.page_width,
        page_height=args.page_height,
        font_size=args.font_size,
        line_height=args.line_height,
        margin=args.margin,
        monospace=True,
    )

    render_root = out_dir / "rendered"
    rendered_examples = []
    results = []

    for row in rows:
        example_id = str(row["id"])
        metadata = dict(row.get("metadata", {}))
        rendered = render_text_to_pages(
            text=str(row["context"]),
            out_dir=render_root / example_id,
            example_id=example_id,
            options=options,
        )
        rendered_examples.append(rendered)

        mapping_rows = _mapping_rows_by_line(rendered.mapping_path)
        candidate_anchors = extract_candidate_anchors(
            text=str(row["context"]),
            query=str(row["query"]),
            mapping_rows=mapping_rows,
            answer_span=row.get("answer_span"),
        )
        selected_anchors = select_anchors_under_budget(
            candidate_anchors,
            query=str(row["query"]),
            token_budget=args.anchor_budget,
        )

        prompt_bundle = build_hybrid_prompt_bundle(
            query=str(row["query"]),
            selected_anchors=selected_anchors,
            visual_page_paths=[str(path) for path in rendered.page_paths],
            metadata={"example_id": example_id, "task_type": row["task_type"]},
        )
        initial_prediction = predict_with_stub_model(
            query=str(row["query"]),
            expected_answer=str(row["answer"]),
            selected_anchors=selected_anchors,
        )
        verifier = verify_prediction(
            query=str(row["query"]),
            prediction=initial_prediction["prediction"],
            selected_anchors=selected_anchors,
            task_type=str(row["task_type"]),
        )

        reread = {
            "page": None,
            "line": None,
            "window": 0,
            "lines": [],
            "text": "",
            "reread_tokens": 0,
        }
        final_prediction = initial_prediction
        if verifier["needs_reread"]:
            coordinate = _coordinate_from_metadata(mapping_rows, metadata)
            if coordinate is not None:
                reread = reread_lines_around_coordinate(
                    mapping_path=rendered.mapping_path,
                    page=coordinate[0],
                    line=coordinate[1],
                    window=0,
                )
                final_prediction = predict_with_stub_model(
                    query=str(row["query"]),
                    expected_answer=str(row["answer"]),
                    selected_anchors=selected_anchors,
                    reread_text=reread["text"],
                )

        anchor_tokens = sum(anchor.token_estimate for anchor in selected_anchors)
        visual_tokens_est = max(1, len(rendered.page_paths) * 256)
        total_tokens_est = anchor_tokens + visual_tokens_est + reread["reread_tokens"]
        prediction = final_prediction["prediction"]
        correct = prediction == row["answer"]
        failure_type = "none"
        if prediction == PLACEHOLDER_PREDICTION:
            failure_type = "stub_placeholder"
        elif final_prediction["source"] == "reread":
            failure_type = "recovered_by_reread"

        results.append(
            {
                "id": example_id,
                "prediction": prediction,
                "answer": row["answer"],
                "correct": correct,
                "selected_anchors": [anchor.to_dict() for anchor in selected_anchors],
                "budget": {
                    "anchor_tokens": anchor_tokens,
                    "visual_tokens_est": visual_tokens_est,
                    "reread_tokens": reread["reread_tokens"],
                    "total_tokens_est": total_tokens_est,
                },
                "verifier": verifier,
                "failure_type": failure_type,
                "prompt_bundle": {
                    "visual_page_paths": prompt_bundle["visual_page_paths"],
                    "anchor_block": prompt_bundle["anchor_block"],
                    "metadata": prompt_bundle["metadata"],
                },
            }
        )

    diagnostics = summarize_render_outputs(rendered_examples, out_dir / "render_diagnostics.json")
    _write_results_jsonl(results, out_dir / "results.jsonl")
    summary = _build_hybrid_summary(results, diagnostics, out_dir / "summary.json")
    print(
        f"processed {summary['num_examples']} examples with accuracy={summary['accuracy']:.4f} "
        f"and total_tokens_est={summary['total_tokens_est']}"
    )
    return 0


def run_smoke(_: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="revision_context_smoke_") as tmpdir:
        root = Path(tmpdir)
        synthetic_path = root / "tiny_exactness.jsonl"
        render_dir = root / "render"

        examples = generate_synthetic_exactness_examples(n=4, seed=0)
        write_synthetic_exactness_jsonl(examples, synthetic_path)

        render_args = argparse.Namespace(
            input=str(synthetic_path),
            out=str(render_dir),
            limit=2,
            page_width=900,
            page_height=1200,
            font_size=16,
            line_height=22,
            margin=40,
            proportional=False,
        )
        run_render(render_args)

        hybrid_args = argparse.Namespace(
            input=str(synthetic_path),
            out=str(root / "hybrid"),
            anchor_budget=32,
            limit=2,
            page_width=900,
            page_height=1200,
            font_size=16,
            line_height=22,
            margin=40,
        )
        run_hybrid(hybrid_args)

    print("revision_context smoke ok")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
