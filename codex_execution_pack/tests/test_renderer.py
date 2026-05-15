from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from revision_context.eval.render_diagnostics import summarize_render_outputs
from revision_context.renderer.text_renderer import RenderedExample, render_text_to_pages
from revision_context.renderer.types import RenderOptions


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_render_text_writes_pages_mapping_and_diagnostics(tmp_path: Path) -> None:
    output_dir = tmp_path / "rendered"
    text = "\n".join(f"line {index}" for index in range(7))

    rendered = render_text_to_pages(
        text=text,
        out_dir=output_dir,
        example_id="example-001",
        options=RenderOptions(
            page_width=320,
            page_height=150,
            font_size=16,
            line_height=20,
            margin=12,
            monospace=True,
        ),
    )

    assert len(rendered.page_paths) >= 2
    assert all(path.exists() for path in rendered.page_paths)
    assert rendered.mapping_path.exists()

    mapping_rows = read_jsonl(rendered.mapping_path)
    assert len(mapping_rows) == 7
    assert mapping_rows[0]["source_line_index"] == 0
    assert mapping_rows[0]["placements"][0]["page_number"] == 1
    assert mapping_rows[0]["placements"][0]["line_number"] == 1
    assert all(row["placements"] for row in mapping_rows)

    summary = summarize_render_outputs([rendered], output_dir / "diagnostics.json")
    assert summary["num_examples_rendered"] == 1
    assert summary["num_pages"] == len(rendered.page_paths)
    assert summary["page_line_mapping_coverage"] == 1.0
    assert (output_dir / "diagnostics.json").exists()


def test_render_cli_writes_output_bundle(tmp_path: Path) -> None:
    input_path = tmp_path / "synthetic.jsonl"
    render_dir = tmp_path / "render"
    examples = [
        {
            "id": "numeric_qa-0000",
            "task_type": "numeric_qa",
            "context": "report\nbatch total: 173 units\nstatus: ok",
            "query": "What is the batch total?",
            "answer": "173",
            "answer_span": "173",
            "metadata": {"answer_line_index": 1},
        },
        {
            "id": "date_qa-0001",
            "task_type": "date_qa",
            "context": "timeline\nlaunch date: 2026-05-15\nstatus: green",
            "query": "What is the launch date?",
            "answer": "2026-05-15",
            "answer_span": "2026-05-15",
            "metadata": {"answer_line_index": 1},
        },
    ]
    input_path.write_text(
        "\n".join(json.dumps(example) for example in examples) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "revision_context.cli",
            "render",
            "--input",
            str(input_path),
            "--out",
            str(render_dir),
            "--limit",
            "2",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (render_dir / "diagnostics.json").exists()
    assert list(render_dir.rglob("*.png"))
    assert list(render_dir.rglob("mapping.jsonl"))

    diagnostics = json.loads((render_dir / "diagnostics.json").read_text(encoding="utf-8"))
    assert diagnostics["num_examples_rendered"] == 2
    assert diagnostics["page_line_mapping_coverage"] == 1.0

