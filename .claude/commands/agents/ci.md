---
description: Run local CI pipeline (lint, type-check, test)
allowed-tools: Bash
argument-hint: [--fix|--quick]
category: Agents
tags: [agents, ci, pipeline, quality]
---

# Local CI Pipeline

Run comprehensive quality checks before commits or OpenSpec archiving.

## Steps

Run quality checks sequentially:

```bash
echo "=== Step 1/3: Linting ==="
uv run ruff check .

echo "=== Step 2/3: Type Checking ==="
uv run mypy .

echo "=== Step 3/3: Running Tests ==="
uv run pytest --tb=short -q
```

## Quality Gate Criteria

- [ ] Lint: Zero errors
- [ ] Types: Zero errors
- [ ] Tests: All pass

## Arguments

- `--fix` - Auto-fix linting issues first (`uv run ruff check . --fix`)
- `--quick` - Skip tests (lint + type-check only)

## Examples

```
/agents:ci           # Full CI pipeline
/agents:ci --fix     # Fix linting issues first
/agents:ci --quick   # Skip tests
```

## Integration

- Use before `openspec archive` to ensure quality gate passes
- Use before committing significant changes
- Results can be saved to `.claude/reports/ci/ci-YYYYMMDD.md` if needed
