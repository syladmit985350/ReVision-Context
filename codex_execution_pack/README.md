# ReVision-Context++

ReVision-Context++ is a reproducible research codebase for hybrid visual-text long-context compression under explicit budget accounting. This repository starts with a lightweight bootstrap scaffold and grows task-by-task from the execution pack.

## Bootstrap Status

This repository currently includes:

- a minimal `revision_context` Python package
- a small CLI with a `smoke` command
- baseline setup and environment-check scripts
- placeholders for data, outputs, and third-party baselines

No rendering, model inference, or training logic is implemented yet.

## Task Sequence

Execute tasks in `codex_tasks/` in order:

1. `TASK_00_PROJECT_BOOTSTRAP.md`
2. `TASK_01_PHASE0_RENDER_MAPPING_SYNTHETIC.md`
3. `TASK_02_PHASE1_HEURISTIC_HYBRID.md`
4. `TASK_03_PHASE2_FIDBENCH_EVALUATOR.md`
5. `TASK_04_PHASE3_TRAINABLE_ALLOCATOR.md`
6. `TASK_05_PHASE4_ALIGNMENT_RISK.md`
7. `TASK_06_PHASE5_BASELINES_EXPERIMENTS.md`
8. `TASK_07_RELEASE_AND_PAPER_ASSETS.md`

The detailed task prompts live in [`codex_tasks/`](codex_tasks/), with broader research context in [`docs/research_plan.md`](docs/research_plan.md).

## Quick Start

From the repository root:

```bash
python -m revision_context.cli --help
python -m revision_context.cli smoke
python scripts/check_environment.py
```

`scripts/clone_baselines.sh` is intentionally safe to rerun and skips repositories that already exist under `third_party/`.
