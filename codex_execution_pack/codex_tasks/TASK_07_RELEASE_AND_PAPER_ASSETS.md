# TASK 07 — Release, Reproducibility, and Paper Asset Scripts

You are Codex working in the repository root.

## Goal

Prepare the repository for a research iteration: reproducibility docs, result tables, plotting scripts, and paper asset placeholders.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`
- Current benchmark/eval/experiment code

The research plan says the paper needs:

- Figure 1: coverage–fidelity failure example
- Figure 2: framework
- Figure 3: Pareto frontier
- Figure 4: oracle gap
- Figure 5: type-wise error breakdown
- same-budget comparison tables
- ablation tables
- failure taxonomy

## Tasks

1. Add reproducibility docs:

```text
docs/reproducibility.md
docs/benchmark_card.md
docs/baseline_status.md
```

2. Add plotting scripts:

```text
scripts/plot_pareto.py
scripts/plot_type_breakdown.py
scripts/plot_oracle_gap.py
```

They should read CSV/JSON from experiment outputs and write PNG/PDF if matplotlib is available. If matplotlib is unavailable, print an actionable install message.

3. Add paper asset directory:

```text
paper_assets/
  README.md
  figures/
  tables/
```

4. Add result table exporter:

```text
revision_context/eval/export_tables.py
```

CLI:

```bash
python -m revision_context.cli export-tables \
  --experiment outputs/experiments/smoke \
  --out paper_assets/tables
```

5. Add final smoke script:

```text
scripts/run_full_smoke.sh
```

It should run a tiny end-to-end flow:

- make tiny benchmark
- run smoke experiment
- export tables
- optionally plot

6. Update README with:

- quickstart
- task sequence
- artifact locations
- current limitations
- baseline installation instructions
- how to run smoke tests

## Constraints

- Do not overclaim paper results.
- Label all synthetic/stub results clearly as smoke-test outputs.
- Keep plotting optional if dependencies are missing.

## Done when

The following commands run:

```bash
bash scripts/run_full_smoke.sh
pytest -q
```

The repository contains:

```text
outputs/experiments/smoke/
paper_assets/tables/
docs/reproducibility.md
docs/benchmark_card.md
docs/baseline_status.md
```

## Final report

Report:

1. Files changed
2. Commands run
3. Generated artifact paths
4. Remaining work before real paper submission
