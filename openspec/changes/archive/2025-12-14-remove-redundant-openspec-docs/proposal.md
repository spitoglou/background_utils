# Change: Remove redundant OpenSpec documentation files

## Why

The `openspec/` directory contains 4 auxiliary markdown files that duplicate content already present in `AGENTS.md` and `MEMORY_BANK_INTEGRATION.md`. These files were created during initial OpenSpec integration but are now redundant:

- They duplicate workflow instructions from AGENTS.md
- They contain generic shell commands any developer knows
- They create confusion about which file is authoritative
- They increase maintenance burden without adding value

The unique useful content from these files has been extracted and consolidated into:
- `memory-bank/activeContext.md` - Session practices, troubleshooting, checklists
- `CLAUDE.md` - OpenSpec command reference

## What Changes

### Files to Delete

| File | Reason |
|------|--------|
| `openspec/QUICK_REFERENCE.md` | Generic git/bash commands; OpenSpec commands already in AGENTS.md |
| `openspec/SESSION_ASSESSMENT.md` | Session retrospective; useful content moved to activeContext.md |
| `openspec/SIMPLE_INTEGRATION.md` | Duplicates MEMORY_BANK_INTEGRATION.md with verbose style |
| `openspec/USAGE_GUIDE.md` | Duplicates AGENTS.md workflow; shell helpers not needed |

### Content Already Migrated

- Pre-session checklist → `memory-bank/activeContext.md`
- Troubleshooting guide → `memory-bank/activeContext.md`
- Session workflow → `memory-bank/activeContext.md`
- OpenSpec commands → `CLAUDE.md`

### Files to Keep

- `openspec/AGENTS.md` - Core AI workflow instructions (authoritative)
- `openspec/project.md` - Project conventions
- `openspec/MEMORY_BANK_INTEGRATION.md` - Integration approach
- `openspec/specs/*` - All specification files

## Impact

- **Affected specs**: None
- **Affected code**: None
- **Risk**: Low - only removing documentation files
- **Benefit**: Cleaner openspec/ directory, single source of truth
