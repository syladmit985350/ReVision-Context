from __future__ import annotations

import json
from pathlib import Path

from revision_context.allocator.budget import estimate_token_count


def _read_mapping_rows(mapping_path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in mapping_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def reread_lines_around_coordinate(
    *,
    mapping_path: Path,
    page: int,
    line: int,
    window: int = 1,
) -> dict:
    mapping_rows = _read_mapping_rows(mapping_path)
    matched_rows = []
    for row in mapping_rows:
        row_page = int(row.get("first_page_number") or 1)
        row_line = int(row.get("first_line_number") or 1)
        if row_page != page:
            continue
        if abs(row_line - line) <= window:
            matched_rows.append(row)

    text = "\n".join(row["source_text"] for row in matched_rows)
    return {
        "page": page,
        "line": line,
        "window": window,
        "lines": matched_rows,
        "text": text,
        "reread_tokens": estimate_token_count(text) if text else 0,
    }
