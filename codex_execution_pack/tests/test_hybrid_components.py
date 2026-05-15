from __future__ import annotations

import json
from pathlib import Path

from revision_context.allocator.heuristic_allocator import select_anchors_under_budget
from revision_context.anchors.query_overlap import score_anchor_query_overlap
from revision_context.anchors.regex_extractor import extract_candidate_anchors
from revision_context.prompting.hybrid_prompt import build_hybrid_prompt_bundle
from revision_context.renderer.text_renderer import render_text_to_pages
from revision_context.renderer.types import RenderOptions
from revision_context.reread.local_reread import reread_lines_around_coordinate
from revision_context.verifier.exactness_verifier import verify_prediction


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_regex_extraction_and_query_overlap(tmp_path: Path) -> None:
    context = "\n".join(
        [
            "report generated: 2026-05-15",
            "timeout_ms = 3000",
            "API_URL=https://api.example.com/v1/status",
            "def parse_user_id(raw_id: str) -> int:",
            "| region | q1 |",
            "| west-0 | 18 |",
            "Formula: alpha_2 + beta_7",
        ]
    )
    rendered = render_text_to_pages(
        text=context,
        out_dir=tmp_path / "rendered",
        example_id="example-001",
        options=RenderOptions(page_width=500, page_height=240, font_size=16, line_height=20),
    )

    anchors = extract_candidate_anchors(
        text=context,
        query="Which function parses the raw user id and what is timeout_ms?",
        mapping_rows=read_jsonl(rendered.mapping_path),
        answer_span="3000",
    )

    anchor_types = {anchor.anchor_type for anchor in anchors}
    assert {"date", "config", "url", "code", "table_cell", "formula"}.issubset(anchor_types)
    assert all(anchor.page >= 1 and anchor.line >= 1 for anchor in anchors)

    parse_anchor = next(anchor for anchor in anchors if "parse_user_id" in anchor.text)
    timeout_anchor = next(anchor for anchor in anchors if "timeout_ms = 3000" in anchor.text)
    assert score_anchor_query_overlap(parse_anchor, "Which function parses the raw user id?") > 0
    assert timeout_anchor.features["answer_span_match"] is True


def test_budget_packing_and_prompt_formatting() -> None:
    context = "\n".join(
        [
            "page ref 1",
            "Revenue: 12.7M USD",
            "def parse_user_id(raw_id: str) -> int:",
        ]
    )
    anchors = extract_candidate_anchors(
        text=context,
        query="Which function parses the raw id?",
        mapping_rows=[
            {
                "source_line_index": 0,
                "source_text": "page ref 1",
                "first_page_number": 1,
                "first_line_number": 1,
                "placements": [{"page_number": 1, "line_number": 1, "segment_index": 0, "text": "page ref 1"}],
            },
            {
                "source_line_index": 1,
                "source_text": "Revenue: 12.7M USD",
                "first_page_number": 1,
                "first_line_number": 2,
                "placements": [{"page_number": 1, "line_number": 2, "segment_index": 0, "text": "Revenue: 12.7M USD"}],
            },
            {
                "source_line_index": 2,
                "source_text": "def parse_user_id(raw_id: str) -> int:",
                "first_page_number": 1,
                "first_line_number": 3,
                "placements": [{"page_number": 1, "line_number": 3, "segment_index": 0, "text": "def parse_user_id(raw_id: str) -> int:"}],
            },
        ],
        answer_span=None,
    )
    selected = select_anchors_under_budget(anchors, query="Which function parses the raw id?", token_budget=10)

    assert selected
    assert sum(anchor.token_estimate for anchor in selected) <= 10

    bundle = build_hybrid_prompt_bundle(
        query="Which function parses the raw id?",
        selected_anchors=selected,
        visual_page_paths=["examples/example-001/page_0001.png"],
        metadata={"example_id": "example-001"},
    )

    assert "[Critical Text Anchors]" in bundle["prompt"]
    assert "[/Critical Text Anchors]" in bundle["prompt"]
    assert "A" in bundle["prompt"]
    assert "page=01" in bundle["prompt"]
    assert "type=code" in bundle["prompt"]


def test_verifier_and_reread_trigger_on_placeholder(tmp_path: Path) -> None:
    context = "\n".join(
        [
            "runbook",
            "timeout_ms = 3000",
            "contact = ops@example.com",
        ]
    )
    rendered = render_text_to_pages(
        text=context,
        out_dir=tmp_path / "rendered",
        example_id="example-verify",
        options=RenderOptions(page_width=500, page_height=240, font_size=16, line_height=20),
    )
    mapping_rows = read_jsonl(rendered.mapping_path)

    decision = verify_prediction(
        query="What is timeout_ms?",
        prediction="UNKNOWN",
        selected_anchors=[],
        task_type="url_path_config_qa",
    )
    assert decision["needs_reread"] is True

    reread = reread_lines_around_coordinate(
        mapping_path=rendered.mapping_path,
        page=1,
        line=2,
        window=0,
    )
    assert "timeout_ms = 3000" in reread["text"]
    assert reread["reread_tokens"] > 0
