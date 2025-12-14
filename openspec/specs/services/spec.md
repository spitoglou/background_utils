# Service Management Specification

## Purpose

Provide long-running background services with Windows system tray integration for monitoring and control.

## Requirements

### Requirement: Service Manager

The system SHALL provide a ServiceManager that can start, stop, and monitor multiple services concurrently.

#### Scenario: Start Multiple Services
- **WHEN** ServiceManager starts with multiple service specifications
- **THEN** each service runs on its own dedicated thread

#### Scenario: Graceful Shutdown
- **WHEN** ServiceManager receives shutdown signal
- **THEN** all services stop gracefully within 10-second timeout

### Requirement: Cooperative Service Pattern

The system SHALL implement cooperative services that respond to stop events.

#### Scenario: Service Stops on Event
- **WHEN** service receives stop_event signal
- **THEN** service terminates its main loop and exits

#### Scenario: Service Continues on Failure
- **WHEN** one service crashes
- **THEN** other services continue running

### Requirement: Windows Tray Integration

The system SHALL provide a Windows system tray icon for service management on Windows platforms.

#### Scenario: Tray Menu Options
- **WHEN** user right-clicks tray icon
- **THEN** display menu with View Log, Stop Services, Restart Services, Exit

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
- See [System Patterns - Service Pattern](memory-bank/systemPatterns.md#service-pattern)
- Critical lessons learned in [Active Context](memory-bank/activeContext.md#critical-tray-lessons-learned)

**Technical Achievements:**
- Windows 11 tray compatibility solved (pystray solution)
- Threading conflicts resolved (manager reference issues)
- Reliable service lifecycle management implemented