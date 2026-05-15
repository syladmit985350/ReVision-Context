from __future__ import annotations

from revision_context.anchors.types import Anchor


def build_hybrid_prompt_bundle(
    *,
    query: str,
    selected_anchors: list[Anchor],
    visual_page_paths: list[str],
    metadata: dict | None = None,
) -> dict:
    anchor_lines = ["[Critical Text Anchors]"]
    for anchor in selected_anchors:
        anchor_lines.append(
            f'{anchor.anchor_id} | page={anchor.page:02d} | line={anchor.line:02d} '
            f'| type={anchor.anchor_type} | text="{anchor.text}"'
        )
    anchor_lines.append("[/Critical Text Anchors]")
    anchor_block = "\n".join(anchor_lines)

    visual_block = "[Visual Pages]\n" + "\n".join(visual_page_paths) + "\n[/Visual Pages]"
    metadata = metadata or {}
    prompt = (
        f"{visual_block}\n\n"
        f"{anchor_block}\n\n"
        f"[Query]\n{query}\n[/Query]\n\n"
        f"[Metadata]\n{metadata}\n[/Metadata]"
    )
    return {
        "prompt": prompt,
        "anchor_block": anchor_block,
        "visual_page_paths": visual_page_paths,
        "metadata": metadata,
    }
