---
name: test-coverage
description: >
  Test coverage analysis using the test-engineer agent. Use when asked to analyze
  test coverage, identify testing gaps, assess coverage for specific modules, or
  when coverage metrics are needed before merging or releasing.
---

# Test Coverage Analysis

Analyze test coverage and identify gaps using the test-engineer agent.

## Process

1. Check `.claude/reports/_registry.md` for recent coverage analyses
2. Determine scope (specific modules or full codebase)
3. Invoke the test-engineer agent:

```
Task(
  description="Coverage analysis for [scope]",
  prompt="""
  You are the test-engineer agent.
  Read: .claude/agents/test-engineer.md

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
  """,
  subagent_type="general"
)
```

4. Update `_registry.md` with the new report
5. For critical gaps, create tech debt entries or OpenSpec proposals
