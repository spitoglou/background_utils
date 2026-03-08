---
name: report-archival
description: >
  Archive old report registry entries and report files. Use when asked to clean up
  reports, archive old entries, do end-of-week cleanup, or when the report registry
  has too many active entries. Moves files to archive without deletion.
---

# Report Archival

Move registry entries and reports older than a threshold to archive.

## Process

1. Read `.claude/reports/_registry.md` for entries older than threshold (default: 7 days)
2. Move report files to `.claude/reports/archive/[category]/`
3. Create dated archive registry `.claude/reports/archive/_registry-archive-YYYYMMDD.md`
4. Update active registry (remove archived entries)
5. Report summary with archive date and file count

## Archive Structure

```
.claude/reports/archive/
  _registry-archive-YYYYMMDD.md  # Dated archive snapshots
  review/                        # Old review reports
  security/                      # Old security reports
  tests/                         # Old test reports
  ci/                            # Old CI reports
  sre/                           # Old SRE reports
  rfc/                           # Old RFC reports
```

## Threshold

Default: 7 days. Adjust based on request:
- 3 days for aggressive cleanup
- 14 days for conservative cleanup

## When to Run

- **Weekly**: End-of-week cleanup
- **On demand**: When registry exceeds ~50 active entries
- **Before major work**: To ensure clean context

## Safety

- No deletion -- only moves files
- Reversible by moving entries back
- Archived reports remain accessible in archive folder by category
- Each archive run creates a new dated registry snapshot
