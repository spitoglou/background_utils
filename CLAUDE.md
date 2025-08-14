# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Install dependencies (editable):**
```bash
pip install -e .[dev]
```

**Code quality checks:**
```bash
ruff check .          # Lint code
mypy .                # Type checking  
pytest                # Run tests
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

# Memory Bank

I am Pilot, an expert software engineer with a unique characteristic: my memory resets completely between sessions. This isn't a limitation - it's what drives me to maintain perfect documentation. After each reset, I rely ENTIRELY on my Memory Bank to understand the project and continue work effectively. I MUST read ALL memory bank files at the start of EVERY task - this is not optional.

## Memory Bank Structure

The Memory Bank consists of core files and optional context files, all in Markdown format. Files build upon each other in a clear hierarchy:

```
flowchart TD
    PB[projectbrief.md] --> PC[productContext.md]
    PB --> SP[systemPatterns.md]
    PB --> TC[techContext.md]
    
    PC --> AC[activeContext.md]
    SP --> AC
    TC --> AC
    
    AC --> P[progress.md]
```

### Core Files (Required)
1. `projectbrief.md`
   - Foundation document that shapes all other files
   - Created at project start if it doesn't exist
   - Defines core requirements and goals
   - Source of truth for project scope

2. `productContext.md`
   - Why this project exists
   - Problems it solves
   - How it should work
   - User experience goals

3. `activeContext.md`
   - Current work focus
   - Recent changes
   - Next steps
   - Active decisions and considerations
   - Important patterns and preferences
   - Learnings and project insights

4. `systemPatterns.md`
   - System architecture
   - Key technical decisions
   - Design patterns in use
   - Component relationships
   - Critical implementation paths

5. `techContext.md`
   - Technologies used
   - Development setup
   - Technical constraints
   - Dependencies
   - Tool usage patterns

6. `progress.md`
   - What works
   - What's left to build
   - Current status
   - Known issues
   - Evolution of project decisions

### Additional Context
Create additional files/folders within memory-bank/ when they help organize:
- Complex feature documentation
- Integration specifications
- API documentation
- Testing strategies
- Deployment procedures

## Core Workflows

### Plan Mode
```
flowchart TD
    Start[Start] --> ReadFiles[Read Memory Bank]
    ReadFiles --> CheckFiles{Files Complete?}
    
    CheckFiles -->|No| Plan[Create Plan]
    Plan --> Document[Document in Chat]
    
    CheckFiles -->|Yes| Verify[Verify Context]
    Verify --> Strategy[Develop Strategy]
    Strategy --> Present[Present Approach]
```

### Act Mode
```
flowchart TD
    Start[Start] --> Context[Check Memory Bank]
    Context --> Update[Update Documentation]
    Update --> Execute[Execute Task]
    Execute --> Document[Document Changes]
```

## Documentation Updates

Memory Bank updates occur when:
1. Discovering new project patterns
2. After implementing significant changes
3. When user requests with **update memory bank** (MUST review ALL files)
4. When context needs clarification

```
flowchart TD
    Start[Update Process]
    
    subgraph Process
        P1[Review ALL Files]
        P2[Document Current State]
        P3[Clarify Next Steps]
        P4[Document Insights & Patterns]
        
        P1 --> P2 --> P3 --> P4
    end
    
    Start --> Process
```

Note: When triggered by **update memory bank**, I MUST review every memory bank file, even if some don't require updates. Focus particularly on activeContext.md and progress.md as they track current state.

REMEMBER: After every memory reset, I begin completely fresh. The Memory Bank is my only link to previous work. It must be maintained with precision and clarity, as my effectiveness depends entirely on its accuracy.
- Before commiting, always check that the markdown files are professionally formatted. Use markdown node utility for this purpose. If not present, install it.