# CODEX_TASK_INDEX.md — How to Run the Segmented Codex Plan

This pack converts `docs/research_plan.md` into small Codex-executable task files.

## Recommended setup

Copy these files into the root of your repository:

```text
AGENTS.md
docs/research_plan.md
codex_tasks/
scripts/
prompts/
```

Then run Codex one task at a time.

## Suggested task order

| Order | Task file | Purpose |
|---:|---|---|
| 00 | `codex_tasks/TASK_00_PROJECT_BOOTSTRAP.md` | Create repository skeleton, configs, baseline clone scripts, smoke-test structure. |
| 01 | `codex_tasks/TASK_01_PHASE0_RENDER_MAPPING_SYNTHETIC.md` | Implement rendering, page-line mapping, synthetic exactness examples, first diagnostics. |
| 02 | `codex_tasks/TASK_02_PHASE1_HEURISTIC_HYBRID.md` | Implement regex/query anchors, budget packer, prompt builder, verifier/reread stub. |
| 03 | `codex_tasks/TASK_03_PHASE2_FIDBENCH_EVALUATOR.md` | Build FidBench-Long generator, metrics, Pareto/evaluation outputs. |
| 04 | `codex_tasks/TASK_04_PHASE3_TRAINABLE_ALLOCATOR.md` | Add oracle allocation generation and trainable router scaffold. |
| 05 | `codex_tasks/TASK_05_PHASE4_ALIGNMENT_RISK.md` | Add alignment/risk diagnostics scaffolding and hard-negative generation. |
| 06 | `codex_tasks/TASK_06_PHASE5_BASELINES_EXPERIMENTS.md` | Add baseline adapters and experiment orchestration. |
| 07 | `codex_tasks/TASK_07_RELEASE_AND_PAPER_ASSETS.md` | Prepare release checklist, plots, paper asset scripts, reproducibility docs. |

## Example Codex invocation

From the repository root:

```bash
codex "Read AGENTS.md and execute codex_tasks/TASK_00_PROJECT_BOOTSTRAP.md. Stop when the Done criteria are satisfied."
```

Then continue with:

```bash
codex "Read AGENTS.md and execute codex_tasks/TASK_01_PHASE0_RENDER_MAPPING_SYNTHETIC.md. Do not implement later phases."
```

## Important rule

Do **not** ask Codex to execute all tasks at once. Each task is designed to be reviewable and rollback-friendly.
