from __future__ import annotations

import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from revision_context.renderer.types import (
    RenderOptions,
    RenderPlacement,
    RenderedExample,
    RenderedLineMapping,
)


def _load_font(options: RenderOptions) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    font_name = "DejaVuSansMono.ttf" if options.monospace else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(font_name, options.font_size)
    except OSError:
        return ImageFont.load_default()


def _split_source_lines(text: str) -> list[str]:
    if not text:
        return [""]
    lines = text.splitlines()
    return lines or [text]


def _wrap_line(
    source_line: str,
    *,
    font: ImageFont.ImageFont | ImageFont.FreeTypeFont,
    options: RenderOptions,
) -> list[str]:
    probe_box = font.getbbox("M")
    char_width = max(1, probe_box[2] - probe_box[0])
    usable_width = max(1, options.page_width - (2 * options.margin))
    wrap_width = max(1, usable_width // char_width)
    if source_line == "":
        return [""]
    wrapped = textwrap.wrap(
        source_line,
        width=wrap_width,
        break_long_words=True,
        break_on_hyphens=False,
        drop_whitespace=False,
        replace_whitespace=False,
    )
    return wrapped or [""]


def render_text_to_pages(
    *,
    text: str,
    out_dir: Path,
    example_id: str,
    options: RenderOptions | None = None,
) -> RenderedExample:
    options = options or RenderOptions()
    out_dir.mkdir(parents=True, exist_ok=True)

    font = _load_font(options)
    lines_per_page = max(1, (options.page_height - (2 * options.margin)) // options.line_height)

    source_lines = _split_source_lines(text)
    pages: list[list[str]] = [[]]
    chars_per_page: list[int] = [0]
    line_mappings: list[RenderedLineMapping] = []

    for source_line_index, source_line in enumerate(source_lines):
        placements: list[RenderPlacement] = []
        wrapped_segments = _wrap_line(source_line, font=font, options=options)
        for segment_index, segment in enumerate(wrapped_segments):
            if len(pages[-1]) >= lines_per_page:
                pages.append([])
                chars_per_page.append(0)

            pages[-1].append(segment)
            page_number = len(pages)
            line_number = len(pages[-1])
            chars_per_page[-1] += len(segment)
            placements.append(
                RenderPlacement(
                    page_number=page_number,
                    line_number=line_number,
                    segment_index=segment_index,
                    text=segment,
                )
            )

        first_page_number = placements[0].page_number if placements else None
        first_line_number = placements[0].line_number if placements else None
        line_mappings.append(
            RenderedLineMapping(
                source_line_index=source_line_index,
                source_text=source_line,
                first_page_number=first_page_number,
                first_line_number=first_line_number,
                placements=placements,
            )
        )

    page_paths: list[Path] = []
    for page_index, page_lines in enumerate(pages, start=1):
        image = Image.new("RGB", (options.page_width, options.page_height), color="white")
        draw = ImageDraw.Draw(image)
        y = options.margin
        for page_line in page_lines:
            draw.text((options.margin, y), page_line, fill="black", font=font)
            y += options.line_height

        page_path = out_dir / f"page_{page_index:04d}.png"
        image.save(page_path)
        page_paths.append(page_path)

    mapping_path = out_dir / "mapping.jsonl"
    mapping_payload = "\n".join(
        json.dumps(mapping.to_dict(example_id=example_id), ensure_ascii=True)
        for mapping in line_mappings
    )
    mapping_path.write_text(f"{mapping_payload}\n" if mapping_payload else "", encoding="utf-8")

    return RenderedExample(
        example_id=example_id,
        output_dir=out_dir,
        page_paths=page_paths,
        mapping_path=mapping_path,
        line_mappings=line_mappings,
        chars_per_page=chars_per_page,
        total_source_lines=len(source_lines),
    )
