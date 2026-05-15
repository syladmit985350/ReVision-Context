from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from revision_context.benchmarks.synthetic_exactness import (
    REQUIRED_TASK_TYPES,
    generate_synthetic_exactness_examples,
)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_generate_synthetic_exactness_examples_cover_required_types() -> None:
    examples = generate_synthetic_exactness_examples(n=12, seed=0)

    assert len(examples) == 12
    assert len({example["id"] for example in examples}) == 12
    assert REQUIRED_TASK_TYPES.issubset({example["task_type"] for example in examples})

    for example in examples:
        assert example["context"]
        assert example["query"]
        assert example["answer"]
        assert example["answer_span"] == example["answer"]
        assert example["answer_span"] in example["context"]
        assert isinstance(example["metadata"], dict)
        assert example["metadata"]["answer_line_index"] >= 0


def test_make_synthetic_cli_writes_jsonl(tmp_path: Path) -> None:
    out_path = tmp_path / "tiny_exactness.jsonl"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "revision_context.cli",
            "make-synthetic",
            "--out",
            str(out_path),
            "--n",
            "8",
            "--seed",
            "7",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert out_path.exists()

    rows = read_jsonl(out_path)
    assert len(rows) == 8
    assert rows[0]["id"].startswith("numeric_qa-")
