# Service Management Specification

## Purpose

Provide long-running background services with Windows system tray integration for monitoring and control.

## Requirements

### Requirement: Service Manager

The system SHALL provide a ServiceManager that can start, stop, and monitor multiple services concurrently with comprehensive testing coverage.

#### Scenario: Start Multiple Services
- **WHEN** ServiceManager starts with multiple service specifications
- **THEN** each service runs on its own dedicated thread

#### Scenario: Graceful Shutdown
- **WHEN** ServiceManager receives shutdown signal
- **THEN** all services stop gracefully within 10-second timeout

#### Scenario: Service Manager with Testing
- **WHEN** ServiceManager is used in production
- **THEN** all service management functionality is covered by automated tests
- **AND** tests verify thread safety and resource management
- **AND** tests validate graceful shutdown behavior

### Requirement: Cooperative Service Pattern

The system SHALL implement cooperative services that respond to stop events.

#### Scenario: Service Stops on Event
- **WHEN** service receives stop_event signal
- **THEN** service terminates its main loop and exits

#### Scenario: Service Continues on Failure
- **WHEN** one service crashes
- **THEN** other services continue running

### Requirement: Comprehensive Service Testing

The system SHALL provide comprehensive automated testing for all background services to ensure reliability and prevent regressions.

#### Scenario: Gmail Service Test Coverage
- **WHEN** Gmail notification service is tested
- **THEN** verify IMAP connection handling with mocked connections
- **AND** verify email parsing and notification generation
- **AND** verify UID tracking and persistence mechanisms
- **AND** verify error handling and automatic reconnection logic

#### Scenario: Tray Controller Test Coverage
- **WHEN** tray controller is tested
- **THEN** verify menu action functionality (View Log, Stop Services, etc.)
- **AND** verify tray lifecycle management and thread safety
- **AND** verify Windows-specific tray behavior and icon management

#### Scenario: Service Manager Test Coverage
- **WHEN** service manager is tested
- **THEN** verify coordination of multiple concurrent services
- **AND** verify graceful shutdown scenarios with timeout handling
- **AND** verify service failure handling and isolation
- **AND** verify thread management and resource cleanup

### Requirement: Windows Tray Integration

The system SHALL provide a Windows system tray icon for service management on Windows platforms with comprehensive testing coverage.

#### Scenario: Tray Menu Options
- **WHEN** user right-clicks tray icon
- **THEN** display menu with View Log, Stop Services, Restart Services, Exit

#### Scenario: Tray Integration with Testing
- **WHEN** tray controller manages services
- **THEN** all tray operations are covered by automated tests
- **AND** tests verify menu actions don't block main thread
- **AND** tests validate Windows-specific tray behavior

#### Scenario: View Log Action
- **WHEN** user selects View Log
- **THEN** open log file in default text editor

#### Scenario: Stop Services Action
- **WHEN** user selects Stop Services
- **THEN** all services stop gracefully

#### Scenario: Restart Services Action
- **WHEN** user selects Restart Services
- **THEN** services stop and restart fresh instances

#### Scenario: Exit Action
- **WHEN** user selects Exit
- **THEN** services stop and application exits completely

### Requirement: Individual Service Entry Points

The system SHALL provide individual entry points for each service.

#### Scenario: Run Example Service
- **WHEN** user runs `background-utils-service-example`
- **THEN** example service starts and runs independently

#### Scenario: Run Gmail Service
- **WHEN** user runs `background-utils-service-gmail`
- **THEN** Gmail notification service starts independently

## Technical Patterns

- Thread-based service execution with shared stop_event
- Pystray for Windows tray integration
- Pillow for tray icon image generation
- Cooperative shutdown with timeout-based thread joining
- Background workers for tray menu operations to prevent blocking

## Additional Context

**Implementation Details:**
- Cooperative services expose `run(stop_event: threading.Event)` with shared stop event
- ServiceManager starts each service on its own thread with 10-second shutdown timeout
- Continues other services if one crashes (logs exception)

**Critical Tray Lessons Learned:**
- pystray is more reliable than native Win32 `Shell_NotifyIcon` on Windows 11
- Menu handlers must run in background threads to avoid blocking the pystray event loop
- Never call `_ensure_manager()` from menu handlers — use existing manager reference
- Use `icon.run()` in daemon thread rather than `run_detached()` for better callback reliability
- Explicit visibility toggling on startup helps shell recognition
- `os._exit(0)` prevents ghost icons under `pythonw`

**Technical Achievements:**
- Windows 11 tray compatibility solved (pystray solution)
- Threading conflicts resolved (manager reference issues)
- Reliable service lifecycle management implemented