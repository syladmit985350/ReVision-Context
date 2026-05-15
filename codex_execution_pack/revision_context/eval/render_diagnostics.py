from __future__ import annotations

import json
from pathlib import Path

from revision_context.renderer.types import RenderedExample


def summarize_render_outputs(
    rendered_examples: list[RenderedExample],
    out_path: Path | None = None,
) -> dict:
    total_pages = sum(len(rendered.page_paths) for rendered in rendered_examples)
    total_chars = sum(sum(rendered.chars_per_page) for rendered in rendered_examples)
    mapped_lines = sum(
        1
        for rendered in rendered_examples
        for line_mapping in rendered.line_mappings
        if line_mapping.placements
    )
    total_lines = sum(rendered.total_source_lines for rendered in rendered_examples)

    summary = {
        "num_examples_rendered": len(rendered_examples),
        "num_pages": total_pages,
        "average_characters_per_page": (
            round(total_chars / total_pages, 2) if total_pages else 0.0
        ),
        "page_line_mapping_coverage": round(mapped_lines / total_lines, 4)
        if total_lines
        else 1.0,
        "image_paths_written": [
            str(page_path)
            for rendered in rendered_examples
            for page_path in rendered.page_paths
        ],
        "mapping_paths": [str(rendered.mapping_path) for rendered in rendered_examples],
    }

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return summary
