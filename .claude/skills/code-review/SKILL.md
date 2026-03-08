---
name: code-review
description: >
  Multi-level code review using the code-reviewer agent. Supports peer review,
  architecture review, security review, and reliability review. Use when asked to
  review code, after significant implementation work, before merging a feature
  branch, or when code quality assessment is needed. Covers both quick single-level
  reviews and full 4-level enterprise review protocols.
---

# Code Review

Multi-level code review following enterprise engineering standards.

Load the `agent-coordination` skill for coordination protocols when running
multi-level reviews.

## Review Levels

### Level 1: Peer Review (Default)

Invoke the `code-reviewer` agent (`.claude/agents/code-reviewer.md`):

```
Task(
  description="Code review of [scope]",
  prompt="""
  You are the code-reviewer agent.
  Read: .claude/agents/code-reviewer.md

  Review the following scope for security, correctness, performance, and maintainability.

  Scope: [specified files/directories]

  Project context:
  - Python 3.12+, strict type hints, line length 100
  - Ruff rules E/F/I/UP/B, strict mypy with Pydantic plugin
  - Loguru logging (no print()), cooperative service shutdown pattern
  - No AI attribution in commit messages

  Context from prior work:
  - [Reference any relevant recent reports from registry]

  Severity: BLOCKING | NON-BLOCKING | NIT
  Output: .claude/reports/review/L1-peer-YYYYMMDD.md
  """,
  subagent_type="general"
)
```

### Level 2: Architecture Review

**Trigger when ANY apply:**
- Change exceeds 200 lines
- New service or CLI command module
- Cross-cutting concerns affected (config, logging, threading)

Analyze:
- Service pattern compliance (cooperative shutdown, thread safety)
- CLI dynamic import pattern
- Pydantic Settings configuration pattern
- Dependency direction and appropriateness

Output: `.claude/reports/review/L2-arch-YYYYMMDD.md`

### Level 3: Security Review

**Trigger when change touches ANY of:**
- Credential handling (BGU_GMAIL_PASSWORD, .env)
- IMAP/network connections
- Subprocess calls (netsh)
- File system operations (%LOCALAPPDATA%)
- User input handling

Invoke `security-engineer` agent in scan mode.
Output: `.claude/reports/security/L3-security-YYYYMMDD.md`

### Level 4: Reliability Review

**Trigger when change affects ANY of:**
- Service lifecycle (start, stop, restart)
- Threading model (stop_event, daemon threads)
- Error handling or retry logic
- Windows-specific operations (pystray, tray controller)

Assess failure modes, graceful degradation, thread safety, shutdown timeout handling.
Output: `.claude/reports/sre/L4-reliability-YYYYMMDD.md`

## Execution Modes

| Mode | Levels | When |
|------|--------|------|
| Quick | L1 only | Fast review, small changes |
| Security | L1 + L3 | Security-sensitive changes |
| Full | All 4 | Major features, pre-merge |
| Auto | Triggered levels | Default -- analyze scope and apply triggers |

Levels run sequentially -- each may need prior level's output.

## Summary Report

After completing applicable levels, produce a summary:

```markdown
# Full Review Summary: [path]

## Levels Completed
- [x] L1: Peer Review
- [ ] L2: Architecture Review
- [ ] L3: Security Review
- [ ] L4: Reliability Review

## Blocking Issues
| Level | Issue | Location | Severity |

## Non-Blocking Issues
| Level | Issue | Location | Priority |

## Verdict
- [ ] APPROVED: Ready to merge
- [ ] CHANGES REQUESTED: Blocking issues remain
```

Output: `.claude/reports/review/full-review-YYYYMMDD.md`

After completion, update `_registry.md` with all reports produced.

## Pre-Review Checklist

1. Check `.claude/reports/_registry.md` for recent reviews to avoid duplication
2. Determine scope (specific files, directories, or current diff)
3. Select appropriate review level(s)
4. If critical issues found, consider creating OpenSpec proposal or tech debt entries
