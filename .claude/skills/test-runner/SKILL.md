---
name: test-runner
description: >
  Run project tests with auto-detected runner and flexible scoping. Use when
  asked to run tests, verify test results, execute a specific test suite or file,
  run tests with coverage, or check if tests pass before committing.
---

# Test Runner

## Project Setup

This is a Python project using pytest with UV. Test command: `uv run pytest`

## Commands

```bash
# Full suite (quick, quiet output)
uv run pytest --tb=short -q

# With coverage
uv run pytest --cov=src/background_utils --cov-report=term-missing

# Specific directory
uv run pytest tests/test_services/ -v

# Pattern match
uv run pytest -k "test_gmail" -v

# Verbose with short traceback
uv run pytest -v --tb=short
```

## Scoping

Determine scope from user intent:

- **Full suite**: No specific target mentioned
- **By directory**: `tests/test_services/`, `tests/test_cli/`, etc.
- **By pattern**: `-k "pattern"` for keyword matching
- **By file**: Direct path to test file
- **With coverage**: Add `--cov=src/background_utils --cov-report=term-missing`

## Reporting

After running, report:

1. Total tests run, passed, failed, skipped
2. Any failure details with file:line references
3. Coverage summary if `--cov` was used
