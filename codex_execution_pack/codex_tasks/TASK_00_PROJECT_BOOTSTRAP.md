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
