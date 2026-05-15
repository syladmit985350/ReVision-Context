from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Anchor:
    anchor_id: str
    anchor_type: str
    text: str
    start_char: int
    end_char: int
    page: int
    line: int
    score: float = 0.0
    token_estimate: int = 0
    features: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "anchor_id": self.anchor_id,
            "type": self.anchor_type,
            "text": self.text,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "page": self.page,
            "line": self.line,
            "score": self.score,
            "token_estimate": self.token_estimate,
            "features": self.features,
        }
