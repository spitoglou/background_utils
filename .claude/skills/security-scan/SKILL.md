---
name: security-scan
description: >
  Security vulnerability assessment using the security-engineer agent. Use when
  asked to scan for security issues, after changes to credential handling, IMAP
  connections, subprocess calls, file system operations, or when assessing the
  security posture of the codebase. Covers OWASP Top 10, CVE detection, secret
  scanning, and input validation.
---

# Security Scan

Run a security vulnerability assessment using the security-engineer agent.

## Process

1. Check `.claude/reports/_registry.md` for recent security scans
2. Determine scope (specific files, directories, or full codebase)
3. Invoke the security-engineer agent in scan mode:

```
Task(
  description="Security scan for [scope]",
  prompt="""
  You are the security-engineer agent.
  Read: .claude/agents/security-engineer.md

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
  """,
  subagent_type="general"
)
```

4. Update `_registry.md` with the new report
5. For critical/high findings, create tech debt entries or OpenSpec proposals

## Threat Model Mode

For deeper analysis, invoke with `threat-model` mode instead of `scan`:

- STRIDE threat modeling
- Attack surface analysis
- Data flow assessment
- Focus on credential handling, IMAP connections, netsh commands, %LOCALAPPDATA% access
