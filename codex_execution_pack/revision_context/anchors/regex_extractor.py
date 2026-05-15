from __future__ import annotations

import re
from dataclasses import replace

from revision_context.anchors.scorer import score_anchors
from revision_context.anchors.types import Anchor

DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")
URL_PATTERN = re.compile(r"https?://[^\s]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PATH_PATTERN = re.compile(r"(?:/[A-Za-z0-9._-]+)+|(?:[A-Za-z]:\\[^\s]+)")
NUMBER_PATTERN = re.compile(r"(?<![\w/])[$€£]?\d[\d,]*(?:\.\d+)?%?(?![\w/])")
LATEX_PATTERN = re.compile(r"\b(?:alpha|beta|gamma|delta|theta|lambda|sigma|pi)_[A-Za-z0-9]+\b")
IDENTIFIER_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
FUNCTION_PATTERN = re.compile(r"\bdef\s+[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)\s*(?:->\s*[^:]+)?:")
CONFIG_PATTERN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.+?)\s*$")


def _line_offsets(text: str) -> list[int]:
    offsets: list[int] = []
    offset = 0
    for line in text.splitlines() or [""]:
        offsets.append(offset)
        offset += len(line) + 1
    return offsets


def _mapping_lookup(mapping_rows: list[dict]) -> dict[int, tuple[int, int]]:
    lookup: dict[int, tuple[int, int]] = {}
    for row in mapping_rows:
        source_line_index = int(row["source_line_index"])
        page = int(row.get("first_page_number") or 1)
        line = int(row.get("first_line_number") or 1)
        lookup[source_line_index] = (page, line)
    return lookup


def _build_anchor(
    *,
    anchor_index: int,
    anchor_type: str,
    text: str,
    start_char: int,
    end_char: int,
    page: int,
    line: int,
    features: dict | None = None,
) -> Anchor:
    return Anchor(
        anchor_id=f"A{anchor_index}",
        anchor_type=anchor_type,
        text=text,
        start_char=start_char,
        end_char=end_char,
        page=page,
        line=line,
        features=features or {},
    )


def _extract_table_cell_anchors(
    *,
    line_text: str,
    line_offset: int,
    page: int,
    line_number: int,
    anchor_index_start: int,
) -> list[Anchor]:
    if not line_text.strip().startswith("|"):
        return []
    cells = [cell.strip() for cell in line_text.strip().strip("|").split("|")]
    if not cells or all(cell.replace("-", "").strip() == "" for cell in cells):
        return []

    anchors: list[Anchor] = []
    cursor = 0
    anchor_index = anchor_index_start
    for cell in cells:
        if not cell:
            continue
        match_offset = line_text.find(cell, cursor)
        if match_offset < 0:
            continue
        cursor = match_offset + len(cell)
        anchors.append(
            _build_anchor(
                anchor_index=anchor_index,
                anchor_type="table_cell",
                text=cell,
                start_char=line_offset + match_offset,
                end_char=line_offset + match_offset + len(cell),
                page=page,
                line=line_number,
                features={"source": "table_cell"},
            )
        )
        anchor_index += 1
    return anchors


def extract_candidate_anchors(
    *,
    text: str,
    query: str,
    mapping_rows: list[dict],
    answer_span: str | None = None,
) -> list[Anchor]:
    lines = text.splitlines() or [""]
    offsets = _line_offsets(text)
    mapping = _mapping_lookup(mapping_rows)

    anchors: list[Anchor] = []
    seen: set[tuple] = set()

    for source_line_index, line_text in enumerate(lines):
        line_offset = offsets[source_line_index]
        page, line_number = mapping.get(source_line_index, (1, source_line_index + 1))

        def add_anchor(anchor_type: str, anchor_text: str, start: int, end: int, features: dict | None = None) -> None:
            key = (anchor_type, anchor_text, start, end, page, line_number)
            if key in seen:
                return
            seen.add(key)
            anchors.append(
                _build_anchor(
                    anchor_index=len(anchors) + 1,
                    anchor_type=anchor_type,
                    text=anchor_text,
                    start_char=start,
                    end_char=end,
                    page=page,
                    line=line_number,
                    features=features,
                )
            )

        config_match = CONFIG_PATTERN.match(line_text)
        if config_match:
            add_anchor(
                "config",
                line_text.strip(),
                line_offset,
                line_offset + len(line_text),
                features={"key": config_match.group(1), "value": config_match.group(2)},
            )

        function_match = FUNCTION_PATTERN.search(line_text)
        if function_match:
            add_anchor(
                "code",
                function_match.group(0).strip(),
                line_offset + function_match.start(),
                line_offset + function_match.end(),
                features={"source": "function_signature"},
            )

        for match in DATE_PATTERN.finditer(line_text):
            add_anchor("date", match.group(0), line_offset + match.start(), line_offset + match.end())

        for match in URL_PATTERN.finditer(line_text):
            match_text = match.group(0)
            anchor_type = "url" if "@" not in match_text else "entity"
            add_anchor(anchor_type, match_text, line_offset + match.start(), line_offset + match.end())

        for match in PATH_PATTERN.finditer(line_text):
            add_anchor("path", match.group(0), line_offset + match.start(), line_offset + match.end())

        for match in LATEX_PATTERN.finditer(line_text):
            add_anchor("formula", match.group(0), line_offset + match.start(), line_offset + match.end())

        for match in NUMBER_PATTERN.finditer(line_text):
            add_anchor("number", match.group(0), line_offset + match.start(), line_offset + match.end())

        if any(symbol in line_text for symbol in ("=", "+", "->")) and LATEX_PATTERN.search(line_text):
            add_anchor(
                "formula",
                line_text.strip(),
                line_offset,
                line_offset + len(line_text),
                features={"source": "formula_line"},
            )

        table_cell_anchors = _extract_table_cell_anchors(
            line_text=line_text,
            line_offset=line_offset,
            page=page,
            line_number=line_number,
            anchor_index_start=len(anchors) + 1,
        )
        for anchor in table_cell_anchors:
            key = (
                anchor.anchor_type,
                anchor.text,
                anchor.start_char,
                anchor.end_char,
                anchor.page,
                anchor.line,
            )
            if key not in seen:
                seen.add(key)
                anchors.append(anchor)

        if answer_span and answer_span in line_text:
            start = line_text.index(answer_span)
            add_anchor(
                "unknown",
                line_text.strip(),
                line_offset + start,
                line_offset + start + len(answer_span),
                features={"source": "answer_span_line"},
            )

        if line_text and line_text[:1].isupper() and " " in line_text:
            entity_match = re.match(r"[A-Z][A-Za-z0-9_. -]+", line_text)
            if entity_match:
                add_anchor(
                    "entity",
                    entity_match.group(0).strip(),
                    line_offset + entity_match.start(),
                    line_offset + entity_match.end(),
                )

        if "def " in line_text:
            for match in IDENTIFIER_PATTERN.finditer(line_text):
                token = match.group(0)
                if "_" in token and len(token) > 3:
                    add_anchor(
                        "code",
                        token,
                        line_offset + match.start(),
                        line_offset + match.end(),
                        features={"source": "identifier"},
                    )

    scored_anchors = score_anchors(anchors, query=query, answer_span=answer_span)
    return [replace(anchor, anchor_id=f"A{index}") for index, anchor in enumerate(scored_anchors, start=1)]
