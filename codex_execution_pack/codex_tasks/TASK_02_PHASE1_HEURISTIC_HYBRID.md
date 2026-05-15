# TASK 02 — Phase 1: Heuristic Hybrid Anchors, Budget Packer, Prompt Builder, Verifier/Reread Stub

You are Codex working in the repository root.

## Goal

Implement the first ReVision-Context++ hybrid prototype:

rendered pages + critical text anchors + query + verifier-triggered local reread stub.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`
- Renderer and synthetic benchmark code from previous tasks

The research plan defines exactness-sensitive spans such as numbers, dates, code identifiers, formulas, URLs, paths, table cells, and config values. The initial implementation should use regex + query overlap, then pack anchors under a token budget.

## Tasks

1. Implement anchor data structures and extraction:

```text
revision_context/anchors/
  __init__.py
  types.py
  regex_extractor.py
  query_overlap.py
  scorer.py
```

Anchor fields:

```json
{
  "anchor_id": "A1",
  "type": "number|date|code|formula|url|path|config|table_cell|entity|unknown",
  "text": "...",
  "start_char": 0,
  "end_char": 0,
  "page": 1,
  "line": 1,
  "score": 0.0,
  "features": {...}
}
```

Regex extractor should detect at least:

- integers, decimals, percentages, currency
- dates
- URLs and emails
- file paths
- config keys such as `timeout_ms = 3000`
- code identifiers and function signatures
- LaTeX-like symbols
- markdown table cells when possible

2. Implement budgeted anchor packing:

```text
revision_context/allocator/
  __init__.py
  budget.py
  heuristic_allocator.py
```

Behavior:

- Input: candidate anchors, query, total anchor token budget
- Output: selected anchors sorted by score/cost
- Token estimate can initially be whitespace/token-like count, but isolate it behind a function.

3. Implement prompt builder:

```text
revision_context/prompting/
  __init__.py
  hybrid_prompt.py
```

Required anchor block format:

```text
[Critical Text Anchors]
A1 | page=03 | line=12 | type=number | text="Revenue: 12.7M USD"
A2 | page=08 | line=04 | type=code | text="def parse_user_id(raw_id: str) -> int"
[/Critical Text Anchors]
```

4. Implement deterministic inference stub:

```text
revision_context/baselines/stub_model.py
```

The stub should:

- answer from anchors if the exact answer string is present
- otherwise return a controlled placeholder
- be deterministic for tests

5. Implement verifier and reread stub:

```text
revision_context/verifier/
  __init__.py
  exactness_verifier.py
revision_context/reread/
  __init__.py
  local_reread.py
```

Verifier should trigger reread when:

- answer contains high-risk exact symbols but no supporting anchor
- answer is placeholder/unknown
- query type appears exactness-sensitive

Reread should retrieve raw lines around a page-line coordinate using the mapping file. It should count reread tokens.

6. Add CLI command:

```bash
python -m revision_context.cli run-hybrid \
  --input data/synthetic/tiny_exactness.jsonl \
  --out outputs/hybrid_smoke \
  --anchor-budget 128 \
  --limit 10
```

Output JSONL should include:

```json
{
  "id": "...",
  "prediction": "...",
  "answer": "...",
  "correct": true,
  "selected_anchors": [...],
  "budget": {
    "anchor_tokens": 0,
    "visual_tokens_est": 0,
    "reread_tokens": 0,
    "total_tokens_est": 0
  },
  "verifier": {...},
  "failure_type": "..."
}
```

7. Add tests for:

- regex extraction
- query-overlap scoring
- budget packing
- prompt formatting
- verifier/reread behavior

## Constraints

- Do not implement trainable allocator.
- Do not call real VIST/Glyph/Qwen/GPT models yet.
- Count budgets explicitly even if visual tokens are estimated.

## Done when

The following commands run:

```bash
python -m revision_context.cli make-synthetic --out data/synthetic/tiny_exactness.jsonl --n 50 --seed 1
python -m revision_context.cli run-hybrid --input data/synthetic/tiny_exactness.jsonl --out outputs/hybrid_smoke --anchor-budget 128 --limit 10
pytest -q
```

`outputs/hybrid_smoke/results.jsonl` and `summary.json` should exist.

## Final report

Report:

1. Files changed
2. Commands run
3. Accuracy from stub run
4. Budget fields implemented
5. What remains stubbed
6. Next task: `codex_tasks/TASK_03_PHASE2_FIDBENCH_EVALUATOR.md`
