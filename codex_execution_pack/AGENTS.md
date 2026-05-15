# AGENTS.md — ReVision-Context++ Codex Project Guidance

You are working on **ReVision-Context++: Verifiable Budgeted Fidelity Allocation for Hybrid Visual-Text Long-Context Compression**.

## Read first

Before making changes, read:

1. `docs/research_plan.md`
2. The current task file under `codex_tasks/`

Treat `docs/research_plan.md` as background context, not as a single task to implement all at once.

## Project objective

Build a reproducible research codebase that starts from a minimal plug-in prototype and gradually grows into the ReVision-Context++ paper system.

Core idea:

- Visual compression preserves broad context coverage.
- Text anchors preserve exact symbols such as numbers, dates, formulas, table cells, URLs, paths, and code identifiers.
- A budgeted allocator decides which spans should be visual, text-anchor, text-latent, dropped, or reread.
- A verifier triggers local reread under an explicitly counted expected budget.

## Implementation policy

- Do not start large-scale training unless a task explicitly asks for it.
- Prefer small runnable prototypes, deterministic fixtures, and smoke tests.
- Keep the main implementation under `revision_context/`.
- Keep external baselines under `third_party/`.
- Keep generated benchmark data under `data/`.
- Keep experimental outputs under `outputs/`.
- Use clear module boundaries:
  - `revision_context/renderer/`
  - `revision_context/anchors/`
  - `revision_context/allocator/`
  - `revision_context/prompting/`
  - `revision_context/verifier/`
  - `revision_context/reread/`
  - `revision_context/eval/`
  - `revision_context/benchmarks/`
  - `revision_context/baselines/`
  - `revision_context/training/`

## Engineering constraints

- All new scripts must be runnable from the repository root.
- Avoid hidden global state.
- Prefer JSONL/JSON/CSV outputs for experiments.
- Every task should include at least one smoke test or a small example command.
- If adding dependencies, document them in `requirements.txt` or `pyproject.toml`.
- If model inference is expensive or unavailable, implement a deterministic stub interface first and isolate the real model adapter behind a clean API.

## Research constraints

Always count total budget fairly:

- visual tokens
- text anchor tokens
- text latent tokens
- reread tokens
- render time
- vision encoder time
- LLM prefill/decode time
- expected reread cost

Never claim improvement without same-budget comparison.

## Done report format

At the end of each Codex run, report:

1. Files changed
2. Commands run
3. Smoke-test result
4. What is implemented
5. What remains intentionally stubbed
6. Next recommended task file
