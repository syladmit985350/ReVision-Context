from __future__ import annotations

from revision_context.anchors.types import Anchor

PLACEHOLDER_PREDICTION = "UNKNOWN"


def predict_with_stub_model(
    *,
    query: str,
    expected_answer: str,
    selected_anchors: list[Anchor],
    reread_text: str | None = None,
) -> dict:
    del query

    supporting_anchor_ids = [
        anchor.anchor_id for anchor in selected_anchors if expected_answer and expected_answer in anchor.text
    ]
    if supporting_anchor_ids:
        return {
            "prediction": expected_answer,
            "source": "anchors",
            "supporting_anchor_ids": supporting_anchor_ids,
        }

    if reread_text and expected_answer and expected_answer in reread_text:
        return {
            "prediction": expected_answer,
            "source": "reread",
            "supporting_anchor_ids": [],
        }

    return {
        "prediction": PLACEHOLDER_PREDICTION,
        "source": "placeholder",
        "supporting_anchor_ids": [],
    }
