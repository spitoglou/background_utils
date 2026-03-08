---
description: Multi-level code review (peer, architecture, security, reliability)
argument-hint: <path> [--quick|--security|--all]
allowed-tools: Read, Glob, Grep, Bash
---

# Full Review Protocol

Multi-level code review following enterprise engineering standards.

**Before proceeding:** Read the `agent-coordination` skill at
`.claude/skills/agent-coordination/SKILL.md` for coordination protocols.

## Review Target

**Path to review:** $ARGUMENTS

## Quick Reference

- `/review-full src/` - Full 4-level review
- `/review-full src/ --quick` - L1 only (peer review)
- `/review-full src/ --security` - L1 + L3 (peer + security)
- `/review-full src/ --all` - Force all 4 levels

## Review Levels

### Level 1: Peer Review (Always Required)

Invoke the `code-reviewer` agent:

```
Task(code-reviewer, "
Review [target path] for:
- Code correctness and logic errors
- Style consistency (ruff E/F/I/UP/B, line length 100)
- Type hints (strict mypy, no unwarranted Any)
- Test coverage gaps
- Error handling completeness
- Loguru logging (no print())

Severity: BLOCKING | NON-BLOCKING | NIT
Output: .claude/reports/review/L1-peer-YYYYMMDD.md
")
```

### Level 2: Architecture Review

**Trigger when ANY apply:**
- Change exceeds 200 lines
- New service or CLI command module
- Cross-cutting concerns affected (config, logging, threading)

Invoke analysis of:
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

Assess:
- Failure mode identification
- Graceful degradation capability
- Thread safety and resource cleanup
- Shutdown timeout handling (10-second window)

Output: `.claude/reports/sre/L4-reliability-YYYYMMDD.md`

## Execution Flow

1. **`--quick`**: L1 only
2. **`--security`**: L1 + L3
3. **`--all`**: All four levels regardless
4. **No flag**: Analyze target and apply triggers automatically

Levels run sequentially -- each may need prior level's output.

## Summary Report

After completing applicable levels:

```markdown
# Full Review Summary: [path]

## Levels Completed
- [x] L1: Peer Review
- [ ] L2: Architecture Review
- [ ] L3: Security Review
- [ ] L4: Reliability Review

## Blocking Issues
| Level | Issue | Location | Severity |
|-------|-------|----------|----------|

## Non-Blocking Issues
| Level | Issue | Location | Priority |
|-------|-------|----------|----------|

## Verdict
- [ ] APPROVED: Ready to merge
- [ ] CHANGES REQUESTED: Blocking issues remain
```

Output: `.claude/reports/review/full-review-YYYYMMDD.md`

After completion, update `_registry.md` with all reports produced.
