from __future__ import annotations

from dataclasses import replace

from revision_context.anchors.types import Anchor


def select_anchors_under_budget(
    anchors: list[Anchor],
    *,
    query: str,
    token_budget: int,
) -> list[Anchor]:
    del query

    ranked = sorted(
        anchors,
        key=lambda anchor: (
            -(anchor.score / max(anchor.token_estimate, 1)),
            -anchor.score,
            anchor.token_estimate,
            anchor.page,
            anchor.line,
        ),
    )

    selected: list[Anchor] = []
    used_tokens = 0
    for anchor in ranked:
        if used_tokens + anchor.token_estimate > token_budget:
            continue
        selected.append(anchor)
        used_tokens += anchor.token_estimate

    selected.sort(key=lambda anchor: (-anchor.score, anchor.page, anchor.line, anchor.start_char))
    return [replace(anchor, anchor_id=f"A{index}") for index, anchor in enumerate(selected, start=1)]
