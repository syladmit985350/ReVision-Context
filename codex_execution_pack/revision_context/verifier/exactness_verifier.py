from __future__ import annotations

from revision_context.baselines.stub_model import PLACEHOLDER_PREDICTION
from revision_context.anchors.types import Anchor

EXACTNESS_TASK_TYPES = {
    "numeric_qa",
    "date_qa",
    "table_cell_qa",
    "code_symbol_qa",
    "url_path_config_qa",
    "formula_math_symbol_qa",
}


def verify_prediction(
    *,
    query: str,
    prediction: str,
    selected_anchors: list[Anchor],
    task_type: str,
) -> dict:
    normalized_query = query.lower()
    exactness_sensitive = task_type in EXACTNESS_TASK_TYPES or any(
        token in normalized_query
        for token in ("date", "value", "function", "url", "path", "timeout", "symbol", "total")
    )
    has_supporting_anchor = any(prediction != PLACEHOLDER_PREDICTION and prediction in anchor.text for anchor in selected_anchors)
    placeholder = prediction == PLACEHOLDER_PREDICTION
    high_risk_prediction = any(symbol in prediction for symbol in ("_", "/", ":", "-", ".", "%")) or prediction.isdigit()
    needs_reread = placeholder or (exactness_sensitive and not has_supporting_anchor and high_risk_prediction)

    reason = "anchor_supported"
    if placeholder:
        reason = "placeholder_prediction"
    elif exactness_sensitive and not has_supporting_anchor:
        reason = "missing_exact_support"

    return {
        "needs_reread": needs_reread,
        "reason": reason,
        "query_exactness_sensitive": exactness_sensitive,
        "has_supporting_anchor": has_supporting_anchor,
        "placeholder_prediction": placeholder,
    }
