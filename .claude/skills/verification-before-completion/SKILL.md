---
name: verification-before-completion
description: >
  Enforce evidence-based completion claims for any task. Use BEFORE claiming work
  is complete, fixed, passing, or ready -- before committing, creating PRs, or
  marking OpenSpec tasks done. Requires running verification commands and
  confirming output before making any success claims.
---

# Verification Before Completion

## Core Principle

Evidence before claims, always. No completion claims without fresh verification.

## The Gate

Before claiming ANY status (pass, fix, done, complete, ready):

1. **Identify** -- What command proves this claim?
2. **Run** -- Execute the full command fresh and complete.
3. **Read** -- Full output, check exit code, count failures.
4. **Confirm** -- Does output support the claim?
   - No: State actual status with evidence.
   - Yes: State claim WITH the evidence.
5. **Only then** -- Make the claim.

Skip any step and the claim is unverified.

## Project-Specific Verification Commands

| Claim | Command | Evidence Required |
|---|---|---|
| Tests pass | `uv run pytest` | Exit 0, failure count = 0 |
| Linter clean | `uv run ruff check .` | Zero errors in output |
| Types clean | `uv run mypy .` | "Success" in output |
| Build works | `uv sync --extra dev` | No errors |
| Spec valid | `openspec validate [item] --strict` | All checks pass |
| Service runs | `background-utils-service-example` | No crash on startup |
| CLI works | `background-utils --help` | Help text rendered |

## Common Failures

| Claim | Not Sufficient |
|---|---|
| "Tests pass" | Previous run, "should pass", partial suite |
| "Linter clean" | Only ran mypy (linter != type checker) |
| "Bug fixed" | Code changed, assumed fixed |
| "OpenSpec task done" | Tasks.md checkbox ticked without running tests |
| "Service works" | Checked code logic, never started service |
| "All quality checks pass" | Ran one of three (`ruff`, `mypy`, `pytest`) |

## Red Flags -- Stop Immediately

You are about to violate this skill if you catch yourself:

- Using "should", "probably", "seems to", "looks correct"
- Expressing satisfaction before verification ("Done!", "Fixed!")
- About to commit or push without running the quality suite
- About to write a commit message that mentions an AI/LLM (Claude, GPT, Copilot, etc.)
- Relying on a previous run rather than a fresh one
- Trusting a subagent's success report without independent check
- Thinking "just this once" or "I'm confident"
- About to mark an OpenSpec task `[x]` without verification

## Rationalization Prevention

| Excuse | Reality |
|---|---|
| "Should work now" | Run the verification. |
| "I'm confident" | Confidence is not evidence. |
| "Linter passed" | Linter is not the type checker is not the test suite. |
| "Partial check is enough" | Partial proves nothing about the whole. |
| "I already ran it earlier" | State can change. Run it fresh. |
| "The change is trivial" | Trivial changes break things too. |

## Integration with OpenSpec Workflow

When completing tasks from `tasks.md` during `/openspec apply`:

1. Implement the task.
2. Run ALL relevant verification commands (not just one).
3. Confirm output in your response with evidence.
4. Only THEN mark the task `- [x]` in tasks.md.
5. After all tasks: run `openspec validate <change-id> --strict`.

## The Bottom Line

Run the command. Read the output. Then claim the result. No shortcuts.
