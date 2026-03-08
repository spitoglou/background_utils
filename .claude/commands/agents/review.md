---
description: Invoke code-reviewer agent for code review
argument-hint: <path>
category: Agents
tags: [agents, review, code-quality]
---

# Code Review

Run a code review using the code-reviewer agent on specified files or directories.

## Steps

1. Check `.claude/reports/_registry.md` for recent reviews to avoid duplication.
2. Determine scope from argument (specific files, directories, or current directory).
3. Invoke the code-reviewer agent:
   ```
   Task(code-reviewer, "
   Review the following scope for security, correctness, performance, and maintainability.

   Scope: [specified files/directories]

   Project context:
   - Python 3.12+, strict type hints, line length 100
   - Ruff rules E/F/I/UP/B, strict mypy with Pydantic plugin
   - Loguru logging (no print()), cooperative service shutdown pattern
   - No AI attribution in commit messages

   Context from prior work:
   - [Reference any relevant recent reports from registry]

   Output: .claude/reports/review/review-[scope]-YYYYMMDD.md
   ")
   ```
4. Update `_registry.md` with the new report.
5. If critical issues found, consider creating OpenSpec proposal or tech debt entries.

## Arguments

- `$ARGUMENTS` - Files or directories to review (required)

## Examples

```
/agents:review src/                     # Review source directory
/agents:review src/background_utils/services/  # Review services
/agents:review src/background_utils/cli/       # Review CLI
```
