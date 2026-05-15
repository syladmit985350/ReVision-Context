"""Rendering interfaces for future visual-context compression work."""

from revision_context.renderer.text_renderer import render_text_to_pages
from revision_context.renderer.types import (
    RenderOptions,
    RenderPlacement,
    RenderedExample,
    RenderedLineMapping,
)

__all__ = [
    "RenderOptions",
    "RenderPlacement",
    "RenderedExample",
    "RenderedLineMapping",
    "render_text_to_pages",
]
