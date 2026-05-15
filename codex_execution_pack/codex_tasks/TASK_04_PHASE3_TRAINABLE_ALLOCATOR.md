# TASK 04 — Phase 3: Oracle Allocation and Trainable Allocator Scaffold

You are Codex working in the repository root.

## Goal

Add the scaffold for a trainable budgeted modality allocator, without requiring expensive model training.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`
- Current anchor, allocator, benchmark, evaluation code

The research plan says novelty should move beyond regex anchors by framing the method as Budgeted Fidelity Allocation. The trainable allocator should be supervised by oracle allocation data and later improved with downstream/verifier-aware learning.

## Tasks

1. Extend action space:

```text
VIS_LOW
VIS_HIGH
TEXT_ANCHOR
TEXT_LATENT
DROP
REREAD_CANDIDATE
```

Add:

```text
revision_context/allocator/actions.py
revision_context/allocator/features.py
```

2. Implement span featurization:

Features should include:

- anchor type one-hot
- query overlap score
- estimated token cost
- digit/symbol density
- line/page position
- table/code/formula/path flags
- risk heuristic
- answer-type prior from query

3. Implement oracle allocation generator:

```text
revision_context/training/oracle_allocation.py
```

For synthetic data, use answer-span metadata to label minimal needed spans as `TEXT_ANCHOR` or `REREAD_CANDIDATE`, and background spans as `VIS_LOW` or `DROP`.

CLI:

```bash
python -m revision_context.cli make-oracle-allocation \
  --input data/synthetic/fidbench_tiny.jsonl \
  --out data/synthetic/oracle_alloc_tiny.jsonl
```

4. Implement lightweight trainable router:

```text
revision_context/allocator/trainable_router.py
revision_context/training/train_router.py
```

Requirements:

- CPU-friendly baseline such as logistic regression, sklearn if available, or a small pure PyTorch MLP.
- If dependency is unavailable, implement a simple fallback linear classifier.
- Save model to `outputs/router_smoke/router.json` or `.pt`.
- Inference should return action probabilities or scores.

CLI:

```bash
python -m revision_context.cli train-router \
  --train data/synthetic/oracle_alloc_tiny.jsonl \
  --out outputs/router_smoke

python -m revision_context.cli run-hybrid \
  --input data/synthetic/fidbench_tiny.jsonl \
  --out outputs/router_hybrid_smoke \
  --allocator trainable \
  --router outputs/router_smoke/router.json \
  --anchor-budget 128 \
  --limit 30
```

5. Add allocator ablation fields to result JSON:

```json
"allocator": {
  "name": "heuristic|trainable",
  "features": {...},
  "action_scores": {...}
}
```

6. Add tests:

- feature extraction consistency
- oracle label creation
- router train/load/predict smoke test

## Constraints

- Do not implement Gumbel-Softmax or RL yet.
- Do not require GPU.
- Do not claim the trainable allocator is final; label it as scaffold.
- Keep heuristic fallback available.

## Done when

The following commands run:

```bash
python -m revision_context.cli make-fidbench --out data/synthetic/fidbench_tiny.jsonl --n 100 --context-lengths 8000 --seed 3
python -m revision_context.cli make-oracle-allocation --input data/synthetic/fidbench_tiny.jsonl --out data/synthetic/oracle_alloc_tiny.jsonl
python -m revision_context.cli train-router --train data/synthetic/oracle_alloc_tiny.jsonl --out outputs/router_smoke
python -m revision_context.cli run-hybrid --input data/synthetic/fidbench_tiny.jsonl --out outputs/router_hybrid_smoke --allocator trainable --router outputs/router_smoke/router.json --anchor-budget 128 --limit 30
pytest -q
```

## Final report

Report:

1. Files changed
2. Commands run
3. Router type and saved path
4. Example allocator output
5. Next task: `codex_tasks/TASK_05_PHASE4_ALIGNMENT_RISK.md`
