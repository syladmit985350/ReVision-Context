from __future__ import annotations

import re


def estimate_token_count(text: str) -> int:
    tokens = re.findall(r"[A-Za-z0-9_./:%+-]+", text)
    return max(1, len(tokens))
