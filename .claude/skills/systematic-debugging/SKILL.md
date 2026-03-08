---
name: systematic-debugging
description: >
  Structured 4-phase debugging process for any bug, test failure, or unexpected
  behavior. Use BEFORE proposing fixes when encountering errors -- especially
  under time pressure, after multiple failed attempts, or when the cause is not
  fully understood. Prevents random-fix thrashing.
---

# Systematic Debugging

## Core Principle

Find root cause before attempting fixes. Symptom fixes are failure.

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If Phase 1 is not complete, no fix may be proposed.

## When to Use

Use for ANY technical issue: test failures, bugs, unexpected behavior, performance
problems, build failures, service crashes, threading issues.

Use ESPECIALLY when:

- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You have already tried a fix that did not work
- You do not fully understand the issue

Do NOT skip when the issue seems simple. Simple bugs have root causes too.

## Phase 1: Root Cause Investigation

Before attempting ANY fix:

### 1. Read Error Messages Carefully

- Read stack traces completely, do not skip past them.
- Note line numbers, file paths, error codes.
- For Python: read the full traceback bottom-up.
- For pytest: read the FAILED summary AND the detailed output.

### 2. Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps or command?
- Does it happen every time or intermittently?
- If not reproducible, gather more data -- do not guess.

### 3. Check Recent Changes

- `git diff` and recent commits.
- New dependencies, config changes, environment differences.
- Did `uv sync` change anything? Check `uv.lock` diff.

### 4. Gather Evidence in Multi-Component Systems

This project has multiple layers (CLI -> services -> threads -> Windows APIs).
Before proposing fixes, add diagnostic instrumentation:

```
For EACH component boundary:
  - Log what data enters the component
  - Log what data exits the component
  - Verify environment/config propagation
  - Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.
```

### 5. Trace Data Flow

- Where does the bad value originate?
- What called this with the bad value?
- Keep tracing up until you find the source.
- Fix at source, not at symptom.

## Phase 2: Pattern Analysis

### 1. Find Working Examples

- Locate similar working code in the same codebase.
- Compare working services against the broken one.
- Check `tests/` for examples of correct usage.

### 2. Compare Against References

- If implementing a pattern (service, CLI command, config), read the reference
  implementation completely. Do not skim.

### 3. Identify Differences

- What is different between working and broken?
- List every difference, however small.
- Do not assume "that can't matter."

## Phase 3: Hypothesis and Testing

### 1. Form Single Hypothesis

State clearly: "I think X is the root cause because Y." Be specific.

### 2. Test Minimally

Make the SMALLEST possible change to test the hypothesis. One variable at a time.
Do not fix multiple things at once.

### 3. Verify Before Continuing

- Did it work? Proceed to Phase 4.
- Did not work? Form NEW hypothesis.
- Do NOT add more fixes on top.

## Phase 4: Implementation

### 1. Create Failing Test Case

```bash
uv run pytest tests/test_specific.py -x -v
```

Write the simplest possible reproduction as a test. Use the project's existing
fixtures where applicable:

- `cleanup_environment` (autouse) -- thread cleanup and GUI mocking
- `isolate_logging` (autouse) -- loguru handler isolation
- `mock_gui_components` -- pystray Icon/Menu/MenuItem mocking
- `quick_intervals` -- fast service intervals (`0.05s`)
- `mock_imap_connection` -- `imaplib.IMAP4_SSL` mock for Gmail tests
- `mock_notifications` -- plyer notification mock
- `mock_file_system` -- temp dir with mocked `LOCALAPPDATA`

### 2. Implement Single Fix

- Address the root cause identified in Phase 1-3.
- ONE change at a time.
- No "while I'm here" improvements.

### 3. Verify Fix

```bash
uv run pytest           # All tests pass
uv run ruff check .     # Linter clean
uv run mypy .           # Types clean
```

### 4. If 3+ Fixes Have Failed: Question Architecture

Pattern indicating an architectural problem:

- Each fix reveals new shared state, coupling, or a problem in a different place.
- Fixes require "massive refactoring" to implement.
- Each fix creates new symptoms elsewhere.

**Stop and question fundamentals.** Discuss with the user before attempting
more fixes. This is not a failed hypothesis -- this is a wrong architecture.

## Red Flags -- Return to Phase 1

If you catch yourself thinking:

- "Quick fix for now, investigate later"
- "Just try changing X and see"
- "Add multiple changes, run tests"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)

## Project-Specific Debugging Notes

### Threading Issues (Services)

Services use `threading.Event` for cooperative shutdown. Common traps:

- Race conditions between `stop_event.set()` and service loop checks.
- 10-second timeout means a hung service masks the real error.
- Always check thread state, not just return values.
- Note: `example_service.py` lacks a type hint on `stop_event` (uses
  `# type: ignore`) -- do not copy its signature as a reference. Use
  `battery_monitor.py` or `my_service.py` instead.

### Windows-Specific Issues

- `pystray` requires a Windows message loop -- headless tests must mock it.
- `netsh` commands require admin privileges -- check error messages.
- File paths use `%LOCALAPPDATA%` -- verify expansion.

### Configuration Issues

- Environment variables use `BGU_` prefix -- check for typos.
- Pydantic Settings validates at load time -- read validation errors carefully.
- `.env` file is loaded automatically -- check for stale values.

## Quick Reference

| Phase | Key Activities | Exit Criteria |
|---|---|---|
| 1. Root Cause | Read errors, reproduce, check changes, trace data | Understand WHAT and WHY |
| 2. Pattern | Find working examples, compare differences | Differences identified |
| 3. Hypothesis | Form theory, test minimally, one variable | Confirmed or new hypothesis |
| 4. Implementation | Failing test, single fix, verify with full suite | Bug resolved, all checks pass |
