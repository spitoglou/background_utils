---
description: Run tests with auto-detected runner
allowed-tools: Bash
argument-hint: [test suite or path]
---

# Run Tests

## Project Detection

This is a Python project (`pyproject.toml` present). Test command: `uv run pytest`

## Process

1. **Scope:** Use argument for specific suite/path, or run full suite
2. **Execute:** Run pytest with UV wrapper
3. **Report:** Display results summary

## Arguments

- `unit` - Unit tests only (`tests/test_unit/` or `tests/` excluding integration)
- `integration` - Integration tests
- `[path]` - Specific file/directory/pattern
- None - Full test suite

## Test Commands

```bash
# Full suite
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

## Examples

```
/test                       # All tests
/test tests/test_services/  # Service tests only
/test -k test_gmail         # Pattern match
/test --cov                 # With coverage report
```
