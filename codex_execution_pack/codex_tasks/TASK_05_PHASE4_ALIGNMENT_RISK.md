# TASK 05 — Phase 4: Alignment and OCR/Risk Diagnostics Scaffold

You are Codex working in the repository root.

## Goal

Add scaffold for fidelity-aware visual alignment and visual/OCR risk diagnostics. This task should prepare the codebase for later integration with VIST/DeepSeek-OCR/Glyph but remain runnable without heavy models.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`
- Current renderer, anchors, allocator, training code

The research plan proposes:

- type-aware copy loss
- page-to-anchor contrastive alignment
- hard negative loss
- OCR risk features
- rendering robustness stress tests

This task implements data structures, hard-negative generation, loss stubs, and diagnostics, not full VLM training.

## Tasks

1. Add hard-negative generator:

```text
revision_context/benchmarks/hard_negatives.py
```

Generate paired examples such as:

- `2024` vs `2025`
- `user_id` vs `userID`
- `foo_bar` vs `foo-bar`
- `0.001` vs `0.01`
- `<=` vs `<`
- `O(n log n)` vs `O(n)`

2. Add risk estimator:

```text
revision_context/anchors/risk.py
```

Risk features:

- symbol density
- visual ambiguity pairs
- small text/render density proxy
- table/code/formula/path type priors
- query exactness prior
- page crowding proxy

Integrate risk into heuristic allocator scoring.

3. Add alignment loss stubs:

```text
revision_context/training/alignment_losses.py
```

Implement pure tensor-level functions if PyTorch is available; otherwise provide clear fallback errors:

- `page_to_anchor_contrastive_loss`
- `type_weighted_copy_loss`
- `hard_negative_margin_loss`

Add docstrings that map each loss to the research plan.

4. Add OCR diagnostic adapter interface:

```text
revision_context/baselines/ocr_diagnostic.py
```

It should define a common interface for future DeepSeek-OCR/Glyph/VIST diagnostics:

```python
class OCRDiagnosticAdapter:
    def score_page(self, image_path: str, expected_text: str) -> dict:
        ...
```

Add a deterministic stub adapter that estimates risk from render density and answer type.

5. Add stress render command:

```bash
python -m revision_context.cli stress-render \
  --input data/synthetic/fidbench_tiny.jsonl \
  --out outputs/stress_render_smoke \
  --styles small_font,low_dpi,multicol,monospace \
  --limit 10
```

6. Add tests for hard negatives and risk scoring.

## Constraints

- Do not train VIST/Glyph/DeepSeek-OCR.
- Do not download large model weights.
- Keep all heavy integrations behind adapter interfaces.
- Make all diagnostics deterministic in smoke tests.

## Done when

The following commands run:

```bash
python -m revision_context.cli make-fidbench --out data/synthetic/fidbench_tiny.jsonl --n 100 --context-lengths 8000 --seed 4
python -m revision_context.cli stress-render --input data/synthetic/fidbench_tiny.jsonl --out outputs/stress_render_smoke --styles small_font,low_dpi,multicol,monospace --limit 10
pytest -q
```

## Final report

Report:

1. Files changed
2. Commands run
3. Risk features added
4. Loss stubs added
5. Next task: `codex_tasks/TASK_06_PHASE5_BASELINES_EXPERIMENTS.md`
