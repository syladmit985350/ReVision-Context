from __future__ import annotations

from dataclasses import replace

from revision_context.allocator.budget import estimate_token_count
from revision_context.anchors.query_overlap import extract_query_terms, score_anchor_query_overlap
from revision_context.anchors.types import Anchor

TYPE_WEIGHTS = {
    "number": 2.0,
    "date": 2.4,
    "code": 2.8,
    "formula": 2.6,
    "url": 2.7,
    "path": 2.6,
    "config": 2.7,
    "table_cell": 2.5,
    "entity": 1.6,
    "unknown": 1.0,
}

TYPE_HINTS = {
    "number": {"many", "amount", "count", "total", "value"},
    "date": {"date", "day", "month", "year", "when"},
    "code": {"function", "method", "class", "identifier", "parse"},
    "formula": {"formula", "symbol", "equation", "alpha", "beta"},
    "url": {"url", "email", "endpoint", "address"},
    "path": {"path", "directory", "folder", "file"},
    "config": {"config", "setting", "timeout", "value"},
    "table_cell": {"table", "cell", "row", "column", "q1", "q2"},
}


def score_anchor(anchor: Anchor, query: str, answer_span: str | None = None) -> Anchor:
    query_terms = extract_query_terms(query)
    overlap_score = score_anchor_query_overlap(anchor, query)
    type_hint_overlap = len(TYPE_HINTS.get(anchor.anchor_type, set()) & query_terms)
    answer_span_match = bool(answer_span and answer_span in anchor.text)
    token_estimate = estimate_token_count(anchor.text)

    score = TYPE_WEIGHTS.get(anchor.anchor_type, TYPE_WEIGHTS["unknown"])
    score += overlap_score * 4.0
    score += min(type_hint_overlap, 2) * 0.75
    if answer_span_match:
        score += 5.0

    updated_features = {
        **anchor.features,
        "query_overlap": round(overlap_score, 4),
        "query_terms": sorted(query_terms),
        "type_hint_overlap": type_hint_overlap,
        "answer_span_match": answer_span_match,
    }
    return replace(
        anchor,
        score=round(score, 4),
        token_estimate=token_estimate,
        features=updated_features,
    )


def score_anchors(anchors: list[Anchor], query: str, answer_span: str | None = None) -> list[Anchor]:
    return [score_anchor(anchor, query, answer_span=answer_span) for anchor in anchors]
