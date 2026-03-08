---
name: agent-coordination
description: >
  Orchestration protocol for multi-agent workflows. Use when coordinating work
  across agents (code-reviewer, security-engineer, test-engineer), producing or
  consuming reports, running sequential pipelines or parallel sweeps, or managing
  the report registry and lifecycle.
---

# Agent Coordination Skill

Orchestration protocol for multi-agent workflows in the **background-utils** project.

## Available Agents

| Agent | Trigger | Mode |
|-------|---------|------|
| `code-reviewer` | After significant implementation or feature branch | Single mode: full review |
| `security-engineer` | Security-sensitive changes (credentials, subprocess, network) | `scan` or `threat-model` |
| `test-engineer` | After code changes, before merge | Run tests, coverage analysis |

## Report System

Reports are the primary communication channel between agents and across sessions.

### Directory Structure

```
.claude/reports/
  _registry.md        # Active report index
  _tech-debt.md       # Tracked technical debt items
  review/             # Code review reports
  security/           # Security scan/threat-model reports
  tests/              # Test execution and coverage reports
  sre/                # Reliability and performance reports
  ci/                 # CI pipeline reports
  rfc/                # Design proposals and RFCs
  archive/            # Completed/superseded reports
```

### Report Lifecycle

1. **Create** -- Agent writes report to the appropriate category directory
2. **Register** -- Add entry to `_registry.md` with status `Active`
3. **Consume** -- Other agents or the orchestrator reads the report
4. **Archive** -- Move to `archive/` when superseded or resolved; update registry status

### Naming Convention

```
<category>/<type>-YYYYMMDD.md
```

Examples:
- `security/security-scan-20260308.md`
- `tests/coverage-analysis-20260308.md`
- `review/review-add-2fa-20260308.md`

### Registry Format

```markdown
| Report | Status | Summary |
|--------|--------|---------|
| [security-scan-20260308](security/security-scan-20260308.md) | Active | 0 critical, 2 medium findings |
| [coverage-analysis-20260308](tests/coverage-analysis-20260308.md) | Active | 56% overall, gaps in CLI |
```

Valid statuses: `Active`, `Resolved`, `Superseded`, `Archived`

## Coordination Protocols

### Sequential Pipeline (e.g., code-review skill)

Run agents in order, each receiving the previous agent's report as context:

```
1. code-reviewer  --> review report
2. security-engineer (scan mode) --> security report
3. test-engineer  --> test report
4. Orchestrator summarizes all reports
```

### Parallel Sweep (e.g., ci-pipeline skill)

Run independent checks concurrently:

```
parallel:
  - ruff check .
  - mypy .
  - pytest
then:
  - Aggregate results into CI report
```

### Context Injection

When invoking an agent via `Task()`, inject relevant context:

```
Task(
  description="Security scan for credential changes",
  prompt="""
  You are the security-engineer agent.
  Read: .claude/agents/security-engineer.md
  
  Context:
  - Changed files: [list]
  - Related reports: [links]
  - OpenSpec spec: openspec/specs/gmail/spec.md
  
  Mode: scan
  Focus: credential handling changes
  
  Output: .claude/reports/security/security-scan-YYYYMMDD.md
  Also update: .claude/reports/_registry.md
  """,
  subagent_type="general"
)
```

### Tech Debt Tracking

`_tech-debt.md` tracks known debt items in this format:

```markdown
| ID | Title | Severity | Component | Notes |
|----|-------|----------|-----------|-------|
| TD-001 | Low test coverage (~56%) | High | All | Target: 85% |
```

Agents may add new debt items when they discover issues. Use the `tech-debt`
skill to view and manage the debt registry.

## Session Initialization

At the start of a session involving agent work:

1. Read `_registry.md` to see active reports
2. Read `_tech-debt.md` for known issues
3. Check `openspec list` for active changes
4. Review recent reports in relevant categories

This replaces the previous memory-bank workflow. Reports + OpenSpec specs + CLAUDE.md
are the project's persistent context system.

## Integration with OpenSpec

- **Before implementing a change**: Check if a security scan or review report exists
- **After implementing a change**: Run test-engineer, then code-reviewer
- **Before archiving a change**: Ensure all agent reports are resolved or archived
- Reports reference OpenSpec change IDs when applicable

## Key Principles

1. **Reports are artifacts** -- They persist across sessions and provide audit trails
2. **Registry is the index** -- Always update `_registry.md` when creating or archiving reports
3. **Agents are stateless** -- Each invocation starts fresh; inject all needed context
4. **Sequential when dependent** -- If agent B needs agent A's output, run sequentially
5. **Parallel when independent** -- Lint, type-check, and test can run concurrently
