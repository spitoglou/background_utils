---
description: Initialize session context from codebase, OpenSpec, and reports
category: Session
tags: [context, session, initialization]
---

# Session Context

Initialize session context by reviewing codebase structure, OpenSpec specifications,
active changes, and report history.

## Steps

1. **Read project conventions:** `openspec/project.md`
2. **Read OpenSpec workflow:** `openspec/AGENTS.md`
3. **Check active changes:** `openspec list`
4. **Check existing specs:** `openspec list --specs`
5. **Review report state:**
   - Read `.claude/reports/_registry.md` for recent work
   - Read `.claude/reports/_tech-debt.md` for known issues
6. **Parse codebase structure:**
   - `src/background_utils/` - main package
   - `src/background_utils/cli/` - Typer CLI with lazy-loaded commands
   - `src/background_utils/services/` - background services with cooperative shutdown
   - `tests/` - pytest test suite
7. **Summarize for the user:**
   - Brief project overview
   - Active changes in progress (if any)
   - Available capabilities/specs
   - Recent reports and pending tech debt
   - Any blockers noted in proposals

## Reference

- Use `openspec show <id>` for details on specific changes or specs
- Use `/debt` to view tech debt summary
- CLAUDE.md contains architecture overview and development commands
