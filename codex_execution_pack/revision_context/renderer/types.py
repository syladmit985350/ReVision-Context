from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RenderOptions:
    page_width: int = 900
    page_height: int = 1200
    font_size: int = 16
    line_height: int = 22
    margin: int = 40
    monospace: bool = True


@dataclass(frozen=True)
class RenderPlacement:
    page_number: int
    line_number: int
    segment_index: int
    text: str

    def to_dict(self) -> dict:
        return {
            "page_number": self.page_number,
            "line_number": self.line_number,
            "segment_index": self.segment_index,
            "text": self.text,
        }


@dataclass(frozen=True)
class RenderedLineMapping:
    source_line_index: int
    source_text: str
    first_page_number: int | None
    first_line_number: int | None
    placements: list[RenderPlacement] = field(default_factory=list)

    def to_dict(self, *, example_id: str) -> dict:
        return {
            "example_id": example_id,
            "source_line_index": self.source_line_index,
            "source_text": self.source_text,
            "first_page_number": self.first_page_number,
            "first_line_number": self.first_line_number,
            "placements": [placement.to_dict() for placement in self.placements],
        }


@dataclass(frozen=True)
class RenderedExample:
    example_id: str
    output_dir: Path
    page_paths: list[Path]
    mapping_path: Path
    line_mappings: list[RenderedLineMapping]
    chars_per_page: list[int]
    total_source_lines: int
