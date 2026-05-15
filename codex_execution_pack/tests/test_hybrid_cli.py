from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_run_hybrid_cli_writes_results_and_summary(tmp_path: Path) -> None:
    input_path = tmp_path / "synthetic.jsonl"
    out_dir = tmp_path / "hybrid"
    examples = [
        {
            "id": "numeric_qa-0000",
            "task_type": "numeric_qa",
            "context": "report\nbatch total: 173 units\nstatus: ok",
            "query": "What is the batch total?",
            "answer": "173",
            "answer_span": "173",
            "metadata": {"answer_line_index": 1},
        },
        {
            "id": "code_symbol_qa-0001",
            "task_type": "code_symbol_qa",
            "context": "service.py\ndef parse_user_id(raw_id: str) -> int:\n    return 7",
            "query": "Which function parses the raw id?",
            "answer": "parse_user_id",
            "answer_span": "parse_user_id",
            "metadata": {"answer_line_index": 1},
        },
    ]
    input_path.write_text(
        "\n".join(json.dumps(example) for example in examples) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "revision_context.cli",
            "run-hybrid",
            "--input",
            str(input_path),
            "--out",
            str(out_dir),
            "--anchor-budget",
            "32",
            "--limit",
            "2",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (out_dir / "results.jsonl").exists()
    assert (out_dir / "summary.json").exists()

    rows = read_jsonl(out_dir / "results.jsonl")
    assert len(rows) == 2
    assert all("selected_anchors" in row for row in rows)
    assert all("budget" in row for row in rows)
    assert all("verifier" in row for row in rows)
    assert all("failure_type" in row for row in rows)
    assert all("anchor_tokens" in row["budget"] for row in rows)
    assert any(row["correct"] for row in rows)

    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["num_examples"] == 2
    assert "accuracy" in summary
