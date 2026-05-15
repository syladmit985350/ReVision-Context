"""Anchor extraction interfaces for exactness-sensitive spans."""

from revision_context.anchors.query_overlap import score_anchor_query_overlap
from revision_context.anchors.regex_extractor import extract_candidate_anchors
from revision_context.anchors.scorer import score_anchor, score_anchors
from revision_context.anchors.types import Anchor

__all__ = [
    "Anchor",
    "extract_candidate_anchors",
    "score_anchor",
    "score_anchors",
    "score_anchor_query_overlap",
]
