# TASK 03 — Phase 2: FidBench-Long Generator and Evaluator

You are Codex working in the repository root.

## Goal

Turn the tiny synthetic diagnostics into a reusable benchmark/evaluation scaffold named FidBench-Long.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`
- Current synthetic, renderer, anchor, allocator, verifier code

The research plan says FidBench-Long should evaluate exactness-sensitive compression failure across numbers, dates, entity binding, table cells, formulas, code symbols, URLs/paths/config, and multi-hop mixed tasks. It should report task score, exactness score, compression ratio, expected latency, memory/KV proxy, Pareto AUC, and fidelity failure rate.

## Tasks

1. Create benchmark modules:

```text
revision_context/benchmarks/
  fidbench_long.py
  templates/
```

Support configurable generation:

```bash
python -m revision_context.cli make-fidbench \
  --out data/synthetic/fidbench_long_1k.jsonl \
  --n 1000 \
  --context-lengths 8000,32000 \
  --task-types numeric,date,table_cell,formula,code_symbol,url_path_config,multihop_mixed \
  --seed 42
```

2. Add controlled distractors:

- similar numbers, e.g. `0.001` vs `0.01`
- similar dates, e.g. `2024-03-07` vs `2024-03-17`
- similar identifiers, e.g. `user_id` vs `userID`
- table row/column distractors
- formula symbol distractors
- path/config distractors

3. Add evaluator:

```text
revision_context/eval/
  metrics.py
  failure_taxonomy.py
  pareto.py
  evaluator.py
```

Metrics:

- exact match
- normalized edit distance
- relative numeric error
- date EM
- table cell EM
- code symbol EM
- fidelity failure rate by type
- compression ratio estimate
- expected budget estimate
- Pareto summary over budget settings

4. Add experiment runner:

```text
revision_context/eval/run_eval.py
```

CLI example:

```bash
python -m revision_context.cli eval-results \
  --results outputs/hybrid_smoke/results.jsonl \
  --out outputs/hybrid_smoke/eval_summary.json
```

5. Add multi-budget runner:

```bash
python -m revision_context.cli sweep-hybrid \
  --input data/synthetic/fidbench_tiny.jsonl \
  --out outputs/sweep_smoke \
  --anchor-budgets 0,64,128,256 \
  --limit 50
```

It should produce:

```text
outputs/sweep_smoke/
  budget_0/results.jsonl
  budget_64/results.jsonl
  budget_128/results.jsonl
  budget_256/results.jsonl
  sweep_summary.csv
  pareto_summary.json
```

6. Add tests for metric edge cases.

## Constraints

- Keep the default generated dataset small for smoke tests.
- Do not require external real datasets yet; create adapter stubs with TODOs.
- Do not implement plotting unless simple matplotlib is already available.

## Done when

The following commands run:

```bash
python -m revision_context.cli make-fidbench --out data/synthetic/fidbench_tiny.jsonl --n 100 --context-lengths 8000 --seed 2
python -m revision_context.cli sweep-hybrid --input data/synthetic/fidbench_tiny.jsonl --out outputs/sweep_smoke --anchor-budgets 0,64,128,256 --limit 30
python -m revision_context.cli eval-results --results outputs/sweep_smoke/budget_128/results.jsonl --out outputs/sweep_smoke/budget_128/eval_summary.json
pytest -q
```

## Final report

Report:

1. Files changed
2. Commands run
3. Metrics implemented
4. Example sweep result
5. Next task: `codex_tasks/TASK_04_PHASE3_TRAINABLE_ALLOCATOR.md`
