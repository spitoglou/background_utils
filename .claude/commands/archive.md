---
description: Archive old registry entries and reports
allowed-tools: Bash, Read, Write, Edit
argument-hint: [days]
---

# Archive Registry

Move registry entries and reports older than N days to archive.

## Process

1. Read `.claude/reports/_registry.md` for entries older than threshold (default: 7 days)
2. Move report files to `.claude/reports/archive/[category]/`
3. Create dated archive registry `.claude/reports/archive/_registry-archive-YYYYMMDD.md`
4. Update active registry (remove archived entries)
5. Report summary with archive date and file count

## Arguments

- `$ARGUMENTS`: Days threshold (default: 7)
  - `/archive` - Archive entries older than 7 days
  - `/archive 14` - Archive entries older than 14 days
  - `/archive 3` - Archive entries older than 3 days

## Archive Structure

```
.claude/reports/archive/
├── _registry-archive-YYYYMMDD.md  # Dated archive snapshots
├── review/                        # Old review reports
├── security/                      # Old security reports
├── tests/                         # Old test reports
├── ci/                            # Old CI reports
├── sre/                           # Old SRE reports
└── rfc/                           # Old RFC reports
```

## When to Run

- **Weekly:** End-of-week cleanup
- **On demand:** When registry exceeds ~50 active entries
- **Before major work:** To ensure clean context

## Notes

- Each archive run creates a new dated `_registry-archive-YYYYMMDD.md` snapshot
- No deletion -- only moves files
- Reversible by moving entries back
- Archived reports remain accessible in archive folder by category
