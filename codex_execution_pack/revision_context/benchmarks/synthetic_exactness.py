from __future__ import annotations

import json
import random
from pathlib import Path

REQUIRED_TASK_TYPES = {
    "numeric_qa",
    "date_qa",
    "table_cell_qa",
    "code_symbol_qa",
    "url_path_config_qa",
    "formula_math_symbol_qa",
}

TASK_TYPE_ORDER = [
    "numeric_qa",
    "date_qa",
    "table_cell_qa",
    "code_symbol_qa",
    "url_path_config_qa",
    "formula_math_symbol_qa",
]


def _numeric_example(index: int, rng: random.Random) -> dict:
    answer = str(100 + index * 17 + rng.randint(0, 9))
    context_lines = [
        f"ops report {index:03d}",
        f"batch total: {answer} units",
        f"audit code: N-{index:04d}",
    ]
    return _build_example(
        task_type="numeric_qa",
        index=index,
        context_lines=context_lines,
        query="What is the batch total?",
        answer=answer,
        answer_line_index=1,
        metadata={"unit": "units"},
    )


def _date_example(index: int, rng: random.Random) -> dict:
    month = (index % 9) + 1
    day = 10 + rng.randint(0, 18)
    answer = f"2026-{month:02d}-{day:02d}"
    context_lines = [
        f"release memo {index:03d}",
        f"launch date: {answer}",
        "owner: platform-team",
    ]
    return _build_example(
        task_type="date_qa",
        index=index,
        context_lines=context_lines,
        query="What is the launch date?",
        answer=answer,
        answer_line_index=1,
        metadata={"calendar": "iso8601"},
    )


def _table_cell_example(index: int, rng: random.Random) -> dict:
    answer = str(10 + index + rng.randint(0, 5))
    region = f"west-{index % 3}"
    context_lines = [
        "sales table",
        "| region | q1 | q2 |",
        "| --- | --- | --- |",
        f"| {region} | {answer} | {answer}9 |",
    ]
    return _build_example(
        task_type="table_cell_qa",
        index=index,
        context_lines=context_lines,
        query=f"What is the q1 value for {region}?",
        answer=answer,
        answer_line_index=3,
        metadata={"table_format": "markdown"},
    )


def _code_symbol_example(index: int, rng: random.Random) -> dict:
    suffix = 2 + (index % 5)
    answer = f"sync_cache_v{suffix}"
    context_lines = [
        "service.py",
        f"def {answer}(user_id: str) -> str:",
        '    return f"cache:{user_id}"',
    ]
    return _build_example(
        task_type="code_symbol_qa",
        index=index,
        context_lines=context_lines,
        query="Which function refreshes the user cache?",
        answer=answer,
        answer_line_index=1,
        metadata={"language": "python"},
    )


def _url_path_config_example(index: int, rng: random.Random) -> dict:
    release = 10 + index
    answer = f"/srv/data/releases/r{release}"
    context_lines = [
        "deployment.env",
        f"BACKUP_PATH={answer}",
        f"API_URL=https://api.example.com/v{(index % 4) + 1}/status",
    ]
    return _build_example(
        task_type="url_path_config_qa",
        index=index,
        context_lines=context_lines,
        query="What is the backup path?",
        answer=answer,
        answer_line_index=1,
        metadata={"format": "env"},
    )


def _formula_example(index: int, rng: random.Random) -> dict:
    alpha = 2 + (index % 4)
    beta = 5 + rng.randint(0, 4)
    answer = f"alpha_{alpha}"
    context_lines = [
        "symbol sheet",
        f"loss = {answer} * beta_{beta} / gamma_{index + 1}",
        "note: use exact symbol names",
    ]
    return _build_example(
        task_type="formula_math_symbol_qa",
        index=index,
        context_lines=context_lines,
        query="Which alpha symbol appears in the loss formula?",
        answer=answer,
        answer_line_index=1,
        metadata={"notation": "ascii_math"},
    )


TASK_BUILDERS = {
    "numeric_qa": _numeric_example,
    "date_qa": _date_example,
    "table_cell_qa": _table_cell_example,
    "code_symbol_qa": _code_symbol_example,
    "url_path_config_qa": _url_path_config_example,
    "formula_math_symbol_qa": _formula_example,
}


def _build_example(
    *,
    task_type: str,
    index: int,
    context_lines: list[str],
    query: str,
    answer: str,
    answer_line_index: int,
    metadata: dict,
) -> dict:
    return {
        "id": f"{task_type}-{index:04d}",
        "task_type": task_type,
        "context": "\n".join(context_lines),
        "query": query,
        "answer": answer,
        "answer_span": answer,
        "metadata": {
            "answer_line_index": answer_line_index,
            "line_count": len(context_lines),
            **metadata,
        },
    }


def generate_synthetic_exactness_examples(n: int, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    examples: list[dict] = []
    for index in range(n):
        task_type = TASK_TYPE_ORDER[index % len(TASK_TYPE_ORDER)]
        examples.append(TASK_BUILDERS[task_type](index, rng))
    return examples


def write_synthetic_exactness_jsonl(examples: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(example, ensure_ascii=True) for example in examples)
    out_path.write_text(f"{payload}\n" if payload else "", encoding="utf-8")
