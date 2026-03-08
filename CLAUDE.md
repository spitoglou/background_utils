<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Install dependencies (with UV):**

```bash
uv sync --extra dev    # Recommended: Install dev dependencies only
# OR
uv sync --all-extras   # Install ALL dependencies including dev (explicit)
```

**IMPORTANT UV WORKFLOW:**
- For dev work: `uv sync --extra dev` (recommended for typical development)
- For complete setup: `uv sync --all-extras` (when you need everything)
- Then use `uv run <command>` to execute tools
- Unlike pip, UV requires explicit sync before running commands
- `--all-extras` is more explicit than plain `uv sync`

**Code quality checks:**

```bash
uv run ruff check .   # Lint code
uv run mypy .         # Type checking  
uv run pytest         # Run tests
```

**OpenSpec operations:**

```bash
openspec list --specs              # List all specifications
openspec show [spec-name]          # Show spec details
openspec validate [item] --strict  # Validate changes or specs
openspec archive [change-id] --yes # Archive completed change
```

**Run the CLI:**

```bash
background-utils --help
background-utils example hello
background-utils wifi show-passwords
background-utils wifi list-networks
```

**Run services:**

```bash
# Combined service manager with Windows system tray
background-utils-service

# Individual services for testing
background-utils-service-example
background-utils-service-battery
background-utils-service-gmail
background-utils-service-my
```

## Architecture Overview

This is a Python package for personal automation tools with two main components:

### 1. CLI Application (`src/background_utils/cli/`)

- **Typer-based CLI** with lazy-loaded subcommands in `cli/commands/`
- Main app in `cli/app.py` with auto-discovery of command modules
- Commands are organized as separate Typer apps (example, wifi)

### 2. Service Management (`src/background_utils/services/`)

- **ServiceManager**: Thread-based service orchestration with cooperative shutdown
- **TrayController**: Windows system tray integration using pystray
- Individual services implement `run(stop_event: threading.Event) -> None`
- Services are collected in `manager.py:_collect_default_services()`

### Core Infrastructure

- **Configuration**: Pydantic Settings with environment variable support (`BGU_` prefix)
- **Logging**: Loguru with Rich console output + file logging to `%LOCALAPPDATA%\background-utils\`
- **Windows Integration**: Native tray icon, Notepad log viewer, proper shutdown handling

## Key Design Patterns

**Service Pattern:**

```python
def run(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        # Do work
        time.sleep(interval)
```

**Adding New Services:**

1. Create service module in `services/` with `run()` function
2. Add entry point in `pyproject.toml`
3. Import and add to `_collect_default_services()` in `manager.py`

**Adding CLI Commands:**

1. Create command module in `cli/commands/` with Typer app
2. Import and register in `cli/app.py`

**Configuration Management:**

- Settings loaded from environment variables with `BGU_` prefix
- Pydantic validation with sensible defaults
- `.env` file support for local development

## Commit Message Rules

- Follow conventional commits: `<type>(scope): description`
- **Never mention the LLM or AI assistant** (Claude, GPT, Copilot, etc.) in commit messages. Commits describe *what changed and why*, not *who or what wrote the code*.

## Agentic Infrastructure

### Skills (`.claude/skills/`)

- **verification-before-completion**: Enforces evidence-based completion claims. Must run
  verification commands (`pytest`, `ruff`, `mypy`, `openspec validate`) and confirm output
  before claiming any task is done, fixed, or passing. Use before committing or marking
  OpenSpec tasks complete.
- **systematic-debugging**: Structured 4-phase debugging process (root cause investigation,
  pattern analysis, hypothesis testing, implementation). Use before proposing fixes for any
  bug, test failure, or unexpected behavior. Prevents random-fix thrashing.
- **agent-coordination**: Orchestration protocol for multi-agent workflows. Defines the
  report system, coordination protocols (sequential pipeline, parallel sweep), context
  injection patterns, and session initialization. Load when coordinating across agents.

### Agents (`.claude/agents/`)

- **code-reviewer**: Senior code reviewer that checks implementations against OpenSpec
  proposals, tasks.md, and project coding standards. Use after completing a significant
  implementation step or feature. Reports issues by severity (critical/important/suggestion).
- **security-engineer**: Security scanning and threat modeling. Modes: `scan` (OWASP Top 10,
  CVE, secret detection, input validation) and `threat-model` (STRIDE, attack surface,
  data flow). Focus areas: credential handling, IMAP connections, netsh commands,
  %LOCALAPPDATA% file access.
- **test-engineer**: Test execution and coverage analysis. Runs pytest suites, identifies
  flaky tests, generates coverage reports, and recommends areas needing tests. Uses
  project fixtures and coverage priority map.

### Slash Commands

**OpenSpec** (`.claude/commands/openspec/`):
- `/openspec proposal` -- Scaffold a new OpenSpec change proposal
- `/openspec apply` -- Implement an approved OpenSpec change
- `/openspec archive` -- Archive a deployed OpenSpec change

**Agent Orchestration** (`.claude/commands/agents/`):
- `/agents:ci` -- Run CI pipeline (lint + type-check + test)
- `/agents:review` -- Code review via code-reviewer agent
- `/agents:security` -- Security scan via security-engineer agent
- `/agents:coverage` -- Coverage analysis via test-engineer agent

**Workflows** (`.claude/commands/`):
- `/test` -- Run pytest with UV
- `/review-full` -- 4-level review: peer, architecture, security, reliability
- `/debt` -- View and manage tech debt registry
- `/release` -- Version bump and release with commitizen
- `/archive` -- Archive resolved reports to `.claude/reports/archive/`
- `/session:context` -- Initialize session with active reports, tech debt, and OpenSpec state

### Reports (`.claude/reports/`)

Persistent artifacts produced by agent workflows. See the agent-coordination skill
for full protocol details.

- `_registry.md` -- Index of active reports with status tracking
- `_tech-debt.md` -- Known technical debt items (TD-001 through TD-005)
- Subdirectories: `review/`, `security/`, `tests/`, `sre/`, `ci/`, `rfc/`, `archive/`

## Available Services

### Gmail Notification Service (`gmail_notifier.py`)

- **Purpose**: Monitors Gmail inbox for new emails and shows desktop notifications
- **Features**:
  - Uses IMAP over SSL to connect to Gmail
  - Cross-platform notifications (plyer + win10toast fallback)
  - UID-based tracking to avoid duplicate notifications
  - Persistent UID cache survives service restarts
  - 60-second check interval with cooperative threading
- **Configuration**:
  - `BGU_GMAIL_EMAIL`: Gmail email address
  - `BGU_GMAIL_PASSWORD`: Gmail password or App Password (recommended)
- **Security**: Use Gmail App Passwords, enable 2FA
- **Cache**: Stores last seen UID in `%LOCALAPPDATA%\background-utils\gmail_last_uid.txt`

### Battery Monitor Service (`battery_monitor.py`)

- **Purpose**: Monitors battery status and warns when battery is low
- **Features**: Logs battery percentage and power status every 60 seconds

### Example Service (`example_service.py`)

- **Purpose**: Demonstration service showing the basic service pattern
- **Features**: Simple periodic logging with configurable interval

## Windows-Specific Features

- **System Tray**: pystray-based with context menu (View Log, Stop/Restart Services, Exit)
- **Log Access**: Tray menu opens logs in Notepad from `%LOCALAPPDATA%\background-utils\`
- **Process Management**: Handles Windows threading limitations for signal handlers
- **Graceful Shutdown**: 10-second timeout per service with proper cleanup

## Session Context

This project uses **reports + OpenSpec specs + CLAUDE.md** as its persistent context
system. There is no separate memory-bank.

### Session Initialization

At the start of a session, run `/session:context` or manually:

1. Read `.claude/reports/_registry.md` for active reports
2. Read `.claude/reports/_tech-debt.md` for known issues
3. Run `openspec list` to see active changes
4. Review CLAUDE.md for architecture and patterns

### Persistent Context Sources

| Source | Purpose |
|--------|---------|
| `CLAUDE.md` | Architecture, patterns, commands, conventions |
| `openspec/specs/` | Current truth — what IS built |
| `openspec/changes/` | Proposals — what SHOULD change |
| `.claude/reports/` | Agent-produced artifacts (reviews, scans, tests) |
| `.claude/reports/_tech-debt.md` | Known technical debt items |

### Commit Hygiene

- Before committing, verify markdown files are well-formatted
- Follow conventional commits: `<type>(scope): description`
- Never mention AI/LLM assistants in commit messages
