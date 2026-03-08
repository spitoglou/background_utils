---
name: tech-debt
description: >
  View and manage the technical debt registry. Use when asked about tech debt,
  to add new debt items, resolve existing ones, review the debt backlog, or when
  findings from reviews/scans need to be tracked as deferred work.
---

# Tech Debt Management

Manage technical debt tracking via `.claude/reports/_tech-debt.md`.

## View Summary

Read `.claude/reports/_tech-debt.md` and display:

```markdown
# Tech Debt Summary

## By Priority
| Priority | Count | Oldest |
|----------|-------|--------|

## Critical Items (Immediate Attention)
[List critical items]

## Recommendations
- [If critical > 0]: Address critical debt before new features
- [If oldest > 90 days]: Review and reprioritize stale items
```

## Add Debt Item

1. Get next TD number from `.claude/reports/_tech-debt.md`
2. Add to appropriate priority section
3. Report confirmation

## Resolve Debt Item

1. Find item by ID (e.g., TD-001) in registry
2. Mark as `[x]`
3. Move to Resolved section
4. Add resolution date

## Full Review

Audit the tech debt registry:

1. Are priorities still accurate?
2. Any items that should be escalated?
3. Stale items (>90 days without progress)?
4. Items that may no longer be relevant?
5. Missing debt items based on codebase review?

## Debt Sources

Tech debt is created from:
- Code review findings marked "won't fix now"
- Security scan findings not immediately addressed
- Coverage gaps deferred to later
- OpenSpec deferred requirements

## Debt Types

| Type | Example | Typical Priority |
|------|---------|-----------------|
| Code | Duplicated logic, missing abstractions | Medium |
| Test | Low coverage, flaky tests | High |
| Dependency | Outdated packages, deprecated APIs | High |
| Architecture | Scaling limits, tight coupling | Critical |
| Documentation | Missing docs, stale docs | Low |
| Security | Unscanned credential patterns | High |
