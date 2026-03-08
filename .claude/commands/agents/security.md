---
description: Invoke security-engineer agent for security scan
argument-hint: [path or focus area]
category: Agents
tags: [agents, security, vulnerability]
---

# Security Scan

Run a security vulnerability assessment using the security-engineer agent.

## Steps

1. Check `.claude/reports/_registry.md` for recent security scans.
2. Determine scope from argument (specific files, directories, or full codebase).
3. Invoke the security-engineer agent in scan mode:
   ```
   Task(security-engineer, "
   Mode: scan

   Scope: [specified files/directories or full codebase]

   Focus areas for this project:
   - Gmail credential handling (BGU_GMAIL_PASSWORD, .env files)
   - IMAP connection security (SSL, error handling, credential leakage in logs)
   - Windows subprocess calls (netsh command injection surface)
   - File system operations (%LOCALAPPDATA%, UID cache, log files)
   - Dependency CVEs (pystray, plyer, win10toast, psutil)
   - Secret detection in source code and configuration

   Context from prior work:
   - [Reference any relevant recent reports from registry]

   Output: .claude/reports/security/security-scan-YYYYMMDD.md
   ")
   ```
4. Update `_registry.md` with the new report.
5. For critical/high findings, create tech debt entries or OpenSpec proposals.

## Arguments

- `$ARGUMENTS` - Optional: specific path or focus area (defaults to full codebase)

## Examples

```
/agents:security                                    # Full codebase scan
/agents:security src/background_utils/services/     # Scan services
/agents:security --focus credentials                # Focus on credential handling
```
