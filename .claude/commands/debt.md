---
description: View and manage tech debt registry
---

# Tech Debt Command

Manage technical debt tracking.

## Usage

```
/debt                          # View debt summary
/debt add [description]        # Add new debt item
/debt resolve [TD-NNN]         # Mark item resolved
/debt review                   # Full registry review
```

## View Summary

Read `.claude/reports/_tech-debt.md` and display:

```markdown
# Tech Debt Summary

## By Priority
| Priority | Count | Oldest |
|----------|-------|--------|
| Critical | [n] | [date] |
| High | [n] | [date] |
| Medium | [n] | [date] |
| Low | [n] | [date] |

## Critical Items (Immediate Attention)
[List critical items]

## Recommendations
- [If critical > 0]: Address critical debt before new features
- [If oldest > 90 days]: Review and reprioritize stale items
```

## Add Debt

```
/debt add "Description" --priority [critical|high|medium|low]
```

1. Get next TD number from `.claude/reports/_tech-debt.md`
2. Add to appropriate priority section
3. Report confirmation

## Resolve Debt

```
/debt resolve TD-NNN
```

1. Find item in registry
2. Mark as `[x]`
3. Move to Resolved section
4. Add resolution date

## Full Review

```
/debt review
```

Audit the tech debt registry:

1. Are priorities still accurate?
2. Any items that should be escalated?
3. Stale items (>90 days without progress)?
4. Items that may no longer be relevant?
5. Missing debt items based on codebase review?

## Integration

Tech debt is created from:
- `/review-full` findings marked "won't fix now"
- `/agents:security` findings not immediately addressed
- `/agents:coverage` gaps deferred to later
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
