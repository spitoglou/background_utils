# Wi-Fi Utilities Specification

## Purpose

Provide Windows-specific commands for managing Wi-Fi networks and passwords.

## Requirements

### Requirement: Show Wi-Fi Passwords

The system SHALL provide a command to display saved Wi-Fi passwords.

#### Scenario: Show Passwords Command
- **WHEN** user runs `background-utils wifi show-passwords`
- **THEN** display table of Wi-Fi profiles with passwords

#### Scenario: JSON Output
- **WHEN** user runs `background-utils wifi show-passwords --output json`
- **THEN** display JSON array of Wi-Fi profiles

### Requirement: List Available Networks

The system SHALL provide a command to list available Wi-Fi networks.

#### Scenario: List Networks Command
- **WHEN** user runs `background-utils wifi list-networks`
- **THEN** display table of available Wi-Fi networks

#### Scenario: JSON Output for Networks
- **WHEN** user runs `background-utils wifi list-networks --output json`
- **THEN** display JSON array of network information

### Requirement: Windows Service Dependency

The system SHALL require Windows Wireless AutoConfig Service for Wi-Fi operations.

#### Scenario: Service Not Running Error
- **WHEN** Wireless AutoConfig Service is not running
- **THEN** display user-friendly error with resolution steps

#### Scenario: Admin Privileges Required
- **WHEN** command requires admin privileges
- **THEN** display appropriate error message

### Requirement: Platform Compatibility

The system SHALL handle non-Windows platforms gracefully.

#### Scenario: Non-Windows Platform
- **WHEN** command runs on non-Windows platform
- **THEN** display informative error message

## Technical Patterns

- Windows netsh command for Wi-Fi management
- Platform detection and graceful error handling
- Rich table output with JSON alternative
- User-friendly error messages with resolution steps

## Additional Context

**Implementation Details:**
- Windows Wireless AutoConfig Service (wlansvc) must be running for Wi-Fi commands
- Admin privileges required for password operations
- Uses `netsh` commands; platform guards prevent execution on non-Windows

**Error Handling Lessons Learned:**
- Detect wlansvc service errors and provide user-friendly messages with resolution steps
- Distinguish between service errors and other errors for targeted guidance
- Format error messages with clear instructions (e.g., "Run `net start wlansvc` as admin")