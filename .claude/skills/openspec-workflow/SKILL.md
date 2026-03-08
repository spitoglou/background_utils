---
name: openspec-workflow
description: >
  Complete OpenSpec change lifecycle: proposal, apply, and archive. Use when asked
  to create a new OpenSpec proposal, implement an approved change, archive a
  deployed change, or when working with OpenSpec specifications. Covers scaffolding
  proposals, implementing tasks, and archiving completed work.
---

# OpenSpec Workflow

Manage the full OpenSpec change lifecycle. Refer to `openspec/AGENTS.md` for
additional conventions.

## Phase 1: Proposal

Scaffold a new OpenSpec change. **No code is written during this phase.**

### Guardrails

- Favor straightforward, minimal implementations; add complexity only when required
- Keep changes tightly scoped
- Identify ambiguities and ask follow-up questions before editing files

### Steps

1. Review `openspec/project.md`, run `openspec list` and `openspec list --specs`,
   inspect related code to ground the proposal in current behavior
2. Choose a unique verb-led `change-id` and scaffold `proposal.md`, `tasks.md`,
   and `design.md` (when needed) under `openspec/changes/<id>/`
3. Map the change into concrete capabilities or requirements
4. Capture architectural reasoning in `design.md` when the solution spans multiple
   systems or introduces new patterns
5. Draft spec deltas in `changes/<id>/specs/<capability>/spec.md` using
   `## ADDED|MODIFIED|REMOVED Requirements` with `#### Scenario:` per requirement
6. Draft `tasks.md` as an ordered list of small, verifiable work items
7. Validate with `openspec validate <id> --strict` and resolve every issue

### Reference Commands

```bash
openspec show <id> --json --deltas-only
openspec show <spec> --type spec
rg -n "Requirement:|Scenario:" openspec/specs
```

## Phase 2: Apply

Implement an approved OpenSpec change.

### Guardrails

- Favor straightforward, minimal implementations
- Keep changes tightly scoped to the requested outcome

### Steps

1. Read `changes/<id>/proposal.md`, `design.md` (if present), and `tasks.md`
2. Work through tasks sequentially, keeping edits minimal and focused
3. Confirm completion before updating statuses
4. Mark each task `- [x]` in `tasks.md` after verification
5. Reference `openspec list` or `openspec show <item>` for additional context

## Phase 3: Archive

Archive a deployed OpenSpec change.

### Steps

1. Determine the change ID (from context, arguments, or `openspec list`)
2. Validate the change ID exists and is ready to archive
3. Run `openspec archive <id> --yes`
4. Review output to confirm specs were updated and change landed in `changes/archive/`
5. Validate with `openspec validate --strict`

### Reference Commands

```bash
openspec list
openspec list --specs
openspec archive <id> --yes
openspec validate --strict
```
