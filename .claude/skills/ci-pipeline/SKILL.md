---
name: ci-pipeline
description: >
  Run local CI pipeline with lint, type-check, and test steps. Use before
  committing significant changes, before OpenSpec archiving, when asked to run
  quality checks, or when validating that the codebase is in a clean state.
---

# CI Pipeline

Run comprehensive quality checks sequentially.

## Steps

```bash
# Step 1: Linting
uv run ruff check .

# Step 2: Type Checking
uv run mypy .

# Step 3: Tests
uv run pytest --tb=short -q
```

## Quality Gate

All three must pass:

- Lint: Zero errors from ruff
- Types: Zero errors from mypy
- Tests: All pass from pytest

## Options

- **Fix mode**: Run `uv run ruff check . --fix` before the lint step to auto-fix
- **Quick mode**: Skip tests, run lint + type-check only

## Report Output

If saving results, write to `.claude/reports/ci/ci-YYYYMMDD.md` and update
`.claude/reports/_registry.md`.

## Integration

- Run before `openspec archive` to ensure quality gate passes
- Run before committing significant changes
- Run after completing OpenSpec task implementations
