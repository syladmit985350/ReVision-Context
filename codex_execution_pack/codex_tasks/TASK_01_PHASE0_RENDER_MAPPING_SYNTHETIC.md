# TASK 01 — Phase 0: Rendering, Page-Line Mapping, and Synthetic Diagnostics

You are Codex working in the repository root.

## Goal

Implement the first minimal research loop:

long context text → rendered page images → page/line mapping → synthetic exactness examples → diagnostic JSON output.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`
- Current code from Task 00

The research plan's Phase 0 asks for:

- running at least one visual/text-as-image baseline later
- creating render + page-line mapping
- building around 1K synthetic exactness samples eventually
- getting initial pure visual failure taxonomy

This task implements the infrastructure, not real VLM inference.

## Tasks

1. Implement a lightweight renderer module:

```text
revision_context/renderer/
  __init__.py
  types.py
  text_renderer.py
```

Required behavior:

- Accept raw text and render it into one or more page images.
- Preserve mapping from original text line to page number and line number.
- Support basic rendering options:
  - page width
  - page height
  - font size
  - line height
  - margin
  - monospace flag
- Output:
  - page PNG files
  - `mapping.jsonl`

Use PIL/Pillow if available; otherwise add it to `requirements.txt`.

2. Implement synthetic exactness data generation:

```text
revision_context/benchmarks/synthetic_exactness.py
```

Generate examples covering:

- numeric QA
- date QA
- table cell QA as markdown-like tables
- code symbol QA
- URL/path/config QA
- formula/math symbol QA

Each JSONL example should include:

```json
{
  "id": "...",
  "task_type": "...",
  "context": "...",
  "query": "...",
  "answer": "...",
  "answer_span": "...",
  "metadata": {...}
}
```

3. Add CLI commands:

```bash
python -m revision_context.cli make-synthetic --out data/synthetic/tiny_exactness.jsonl --n 20 --seed 0
python -m revision_context.cli render --input data/synthetic/tiny_exactness.jsonl --out outputs/render_smoke --limit 3
```

4. Add diagnostics:

```text
revision_context/eval/render_diagnostics.py
```

It should summarize:

- number of examples rendered
- number of pages
- average characters per page
- page-line mapping coverage
- image paths written

Save a JSON summary to:

```text
outputs/render_smoke/diagnostics.json
```

5. Add tests:

```text
tests/test_renderer.py
tests/test_synthetic_exactness.py
```

## Constraints

- Do not call any LLM or VLM.
- Do not implement anchors yet, except for preserving answer span metadata in synthetic data.
- Keep generated tiny data small enough for Git if the user commits it.

## Done when

The following commands run:

```bash
python -m revision_context.cli make-synthetic --out data/synthetic/tiny_exactness.jsonl --n 20 --seed 0
python -m revision_context.cli render --input data/synthetic/tiny_exactness.jsonl --out outputs/render_smoke --limit 3
python -m revision_context.cli smoke
pytest -q
```

The output directory should include PNG pages, mapping JSONL, and diagnostics JSON.

## Final report

Report:

1. Files changed
2. Commands run
3. Example output paths
4. Mapping format
5. Next task: `codex_tasks/TASK_02_PHASE1_HEURISTIC_HYBRID.md`
