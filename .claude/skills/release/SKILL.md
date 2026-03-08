---
name: release
description: >
  Version bump and release procedure using commitizen with UV. Use when asked to
  create a release, bump the version, tag a release, or prepare a changelog.
  Covers pre-release checks, version bumping, changelog generation, and pushing
  tags.
---

# Release Procedure

Execute the release procedure using commitizen with UV.

## Pre-Release Checks

Verify working tree is clean and quality gate passes:

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

## Version Types

- **patch** (0.0.X): Bug fixes, minor improvements
- **minor** (0.X.0): New features, backward-compatible
- **major** (X.0.0): Breaking changes
- **auto**: Determined from conventional commit messages
