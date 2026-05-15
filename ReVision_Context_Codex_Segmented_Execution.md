# ReVision-Context++ Codex Segmented Execution File
This single file contains AGENTS.md guidance plus all segmented Codex tasks.

Official use recommendation: copy the multi-file pack into your repo and run one task at a time.

----

## AGENTS.md

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


----

## CODEX_TASK_INDEX.md

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


----

## codex_tasks/TASK_00_PROJECT_BOOTSTRAP.md

# TASK 00 — Project Bootstrap

You are Codex working in the repository root.

## Goal

Create the initial repository skeleton for ReVision-Context++ without implementing the full paper system.

## Context

Read:

- `AGENTS.md`
- `docs/research_plan.md`

The research plan says the first implementation should be a minimal plug-in inference framework, built around VIST-style visual compression, with later support for anchors, budgeted allocation, verification-triggered reread, FidBench-Long, and baselines.

## Tasks

1. Create the core directory structure:

```text
revision_context/
  __init__.py
  renderer/
  anchors/
  allocator/
  prompting/
  verifier/
  reread/
  eval/
  benchmarks/
  baselines/
  training/
data/
  synthetic/
outputs/
third_party/
scripts/
tests/
docs/
```

2. Add minimal package/config files:

```text
pyproject.toml
requirements.txt
README.md
.gitignore
```

3. Add baseline setup scripts:

```text
scripts/clone_baselines.sh
scripts/check_environment.py
```

`clone_baselines.sh` should include the repositories from the research plan, but it must be safe to run repeatedly. Use `if [ ! -d ... ]; then git clone ...; fi`.

Include at least:

- VIST
- Glyph
- CEPE
- text_or_pixels
- DeepSeek-OCR
- C3-Context-Cascade-Compression
- LongCodeZip
- LLMLingua
- Selective_Context
- LLaVolta

4. Add a minimal CLI entrypoint:

```text
revision_context/cli.py
```

It should support at least:

```bash
python -m revision_context.cli --help
python -m revision_context.cli smoke
```

5. Add a smoke test:

```text
tests/test_smoke.py
```

It should verify that the package imports and the smoke command can run.

## Constraints

- Do not clone large repositories during this task unless explicitly asked by the user.
- Do not install GPU dependencies.
- Do not implement rendering or model inference yet.
- Keep all code lightweight and CPU-only.

## Done when

- `python -m revision_context.cli smoke` runs successfully.
- `pytest -q` passes, or if pytest is unavailable, `python tests/test_smoke.py` passes.
- `README.md` explains the task sequence and points to `codex_tasks/`.

## Final report

Report:

1. Files changed
2. Commands run
3. Smoke-test result
4. Next task: `codex_tasks/TASK_01_PHASE0_RENDER_MAPPING_SYNTHETIC.md`


----

## codex_tasks/TASK_01_PHASE0_RENDER_MAPPING_SYNTHETIC.md

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


----

## codex_tasks/TASK_02_PHASE1_HEURISTIC_HYBRID.md

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


----

## codex_tasks/TASK_03_PHASE2_FIDBENCH_EVALUATOR.md

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


----

## codex_tasks/TASK_04_PHASE3_TRAINABLE_ALLOCATOR.md

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


----

## codex_tasks/TASK_05_PHASE4_ALIGNMENT_RISK.md

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


----

## codex_tasks/TASK_06_PHASE5_BASELINES_EXPERIMENTS.md

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


----

## codex_tasks/TASK_07_RELEASE_AND_PAPER_ASSETS.md

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


