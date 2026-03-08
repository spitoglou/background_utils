---
description: Execute version bump and release procedure
allowed-tools: Bash
argument-hint: [patch|minor|major|--dry-run]
---

# Release Procedure

Execute the release procedure using commitizen with UV.

## Pre-Release Checks

Verify working tree is clean and tests pass:

```bash
git status
uv run ruff check .
uv run mypy .
uv run pytest --tb=short -q
```

Review commits since last release:

```bash
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD
```

## Bump Version

```bash
# Auto-determine bump from conventional commits
uv run cz bump --changelog

# Or specify explicitly
uv run cz bump --changelog --increment PATCH|MINOR|MAJOR

# Sync lock file after bump
uv sync --all-extras
git add uv.lock
git commit --amend --no-edit
```

## Push Release

```bash
git push && git push --tags
```

## Verify

```bash
git tag -l "v*" | tail -5
head -50 CHANGELOG.md
```

## Dry Run

Preview changes without committing:

```bash
uv run cz bump --dry-run
```

## Arguments

- `patch` - Bump patch version (0.0.X)
- `minor` - Bump minor version (0.X.0)
- `major` - Bump major version (X.0.0)
- `--dry-run` - Preview only, no changes
- None - Auto-determine from conventional commits

## Examples

```
/release              # Auto-determine from commits
/release patch        # Force patch bump
/release --dry-run    # Preview changes
```
