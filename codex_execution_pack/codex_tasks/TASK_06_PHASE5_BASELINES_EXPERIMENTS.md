# TASK 06 — Phase 5: Baseline Adapters and Experiment Orchestration

You are Codex working in the repository root.

## Goal

Create a clean baseline-adapter and experiment-runner layer for same-budget comparisons, without requiring that every external baseline is installed.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`
- Current benchmark, eval, allocator, diagnostics code

The research plan requires fair comparison against visual, text-compression, retrieval, hybrid heuristic, oracle, and ablated variants. It also emphasizes same total budget and Pareto curves.

## Tasks

1. Create baseline adapter interface:

```text
revision_context/baselines/
  base.py
  visual_stub.py
  text_compression_stub.py
  retrieval_stub.py
  hybrid.py
  registry.py
```

Each adapter should expose:

```python
def run_example(example: dict, budget: dict) -> dict:
    ...
```

Output must include prediction, budget usage, latency estimate, and method metadata.

2. Add placeholders for external baselines:

```text
revision_context/baselines/vist_adapter.py
revision_context/baselines/glyph_adapter.py
revision_context/baselines/cepe_adapter.py
revision_context/baselines/llmlingua_adapter.py
revision_context/baselines/c3_adapter.py
revision_context/baselines/longcodezip_adapter.py
```

Each should:

- check whether the corresponding `third_party/...` directory exists
- fail with an actionable message if not installed
- not import heavy dependencies at module import time
- include TODOs for real command invocation

3. Add experiment config schema:

```text
configs/
  smoke_experiment.yaml
revision_context/eval/experiment_config.py
revision_context/eval/run_experiment.py
```

Config should support:

- dataset path
- methods
- budget sweep
- max examples
- output directory
- seed

4. Add CLI:

```bash
python -m revision_context.cli run-experiment --config configs/smoke_experiment.yaml
```

Outputs:

```text
outputs/experiments/smoke/
  method=hybrid_budget=128/results.jsonl
  method=visual_stub_budget=128/results.jsonl
  method=retrieval_stub_budget=128/results.jsonl
  aggregate_summary.csv
  pareto_summary.json
```

5. Add ablation labels:

- pure visual
- random anchors
- regex anchors
- query-aware anchors
- trainable allocator
- +verifier reread
- oracle allocation

6. Add tests for adapter registry and config loading.

## Constraints

- No heavy baseline execution yet.
- Same-budget fields must be present for every method.
- All missing third-party baselines must fail gracefully.

## Done when

The following commands run:

```bash
python -m revision_context.cli make-fidbench --out data/synthetic/fidbench_tiny.jsonl --n 100 --context-lengths 8000 --seed 5
python -m revision_context.cli run-experiment --config configs/smoke_experiment.yaml
pytest -q
```

## Final report

Report:

1. Files changed
2. Commands run
3. Methods available in registry
4. Aggregate summary path
5. Next task: `codex_tasks/TASK_07_RELEASE_AND_PAPER_ASSETS.md`
