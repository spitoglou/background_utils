---
description: Invoke test-engineer agent for coverage analysis
argument-hint: [module or path]
category: Agents
tags: [agents, tests, coverage]
---

# Test Coverage Analysis

Analyze test coverage and identify gaps using the test-engineer agent.

## Steps

1. Check `.claude/reports/_registry.md` for recent coverage analyses.
2. Determine scope from argument (specific modules or full codebase).
3. Invoke the test-engineer agent:
   ```
   Task(test-engineer, "
   Analyze test coverage and identify critical gaps.

   Scope: [specified modules or full codebase]

   Run: uv run pytest --cov=src/background_utils --cov-report=term-missing

   Coverage targets:
   - Core modules (config, logging): 90%+
   - Services (manager, gmail, tray): 85%+
   - CLI commands: 80%+
   - Overall project: 85%+

   Key fixtures available: cleanup_environment, isolate_logging,
   mock_gui_components, quick_intervals, mock_imap_connection,
   mock_notifications, mock_file_system

   Context from prior work:
   - [Reference any relevant recent reports from registry]

   Output: .claude/reports/tests/coverage-analysis-YYYYMMDD.md
   ")
   ```
4. Update `_registry.md` with the new report.
5. For critical gaps, create tech debt entries or OpenSpec proposals.

## Arguments

- `$ARGUMENTS` - Optional: specific modules to analyze (defaults to full codebase)

## Examples

```
/agents:coverage                                    # Full codebase
/agents:coverage src/background_utils/services/     # Services only
/agents:coverage --focus gmail                      # Focus on Gmail service
```
