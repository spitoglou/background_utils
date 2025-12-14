# Change: Clean up documentation debt and orphaned files

## Why

The codebase has accumulated documentation debt from a recently archived OpenSpec change (`add-comprehensive-testing`). Several summary files were left orphaned in the project root, duplicating content that exists in the archive. Additionally, a stub `AGENTS.md` file duplicates instructions already present in `CLAUDE.md`, and the archive contains excessive summary files that could be consolidated.

This cleanup will:
- Remove confusion for new contributors
- Reduce duplication and maintenance burden
- Improve project organization
- Align with the project's preference for minimal documentation files

## What Changes

### Files to Delete (Root Directory)
- `FINAL_IMPLEMENTATION_COMPLETE.md` - Duplicates `openspec/changes/archive/.../FINAL_SUMMARY.md`
- `IMPLEMENTATION_SUMMARY.md` - Outdated (shows Phase 1 at 30%), superseded by archived summaries
- `AGENTS.md` - Stub file; OpenSpec instructions already exist in `CLAUDE.md`

### Files to Delete (Archive Consolidation)
- `openspec/changes/archive/2024-12-14-add-comprehensive-testing/IMPLEMENTATION_PROGRESS.md` - Progress tracking no longer needed post-archive
- `openspec/changes/archive/2024-12-14-add-comprehensive-testing/PHASE_2_SUMMARY.md` - Intermediate summary, covered by FINAL_SUMMARY.md

### Files to Keep in Archive
- `proposal.md` - Original proposal (required)
- `tasks.md` - Task checklist (required)
- `design.md` - Technical decisions (useful reference)
- `FINAL_SUMMARY.md` - Comprehensive final summary (consolidates all progress)
- `ARCHIVE_SUMMARY.md` - Archive metadata (useful for reference)
- `specs/` - Delta specs (required)

### Optional: Legacy Archive Cleanup
- `.archive/` directory contains old kilocode/memory rules that may no longer be relevant

## Impact

- **Affected specs**: None (documentation-only change)
- **Affected code**: None
- **Risk**: Low - only removing redundant documentation files
- **Rollback**: Files can be recovered from git history if needed
