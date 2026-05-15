from __future__ import annotations

import re

from revision_context.anchors.types import Anchor

STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "how",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "which",
}


def normalize_term(term: str) -> str:
    normalized = term.lower().strip()
    if normalized.endswith("s") and len(normalized) > 3:
        normalized = normalized[:-1]
    return normalized


def tokenize_overlap_text(text: str) -> list[str]:
    return [normalize_term(token) for token in re.findall(r"[A-Za-z0-9]+", text)]


def extract_query_terms(query: str) -> set[str]:
    return {
        token
        for token in tokenize_overlap_text(query)
        if token and token not in STOPWORDS
    }


def score_anchor_query_overlap(anchor: Anchor, query: str) -> float:
    query_terms = extract_query_terms(query)
    if not query_terms:
        return 0.0

    anchor_terms = set(tokenize_overlap_text(anchor.text))
    overlap = query_terms & anchor_terms
    return len(overlap) / len(query_terms)
