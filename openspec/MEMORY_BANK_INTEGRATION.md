# Memory-Bank Integration Guide

## Simple Approach: Direct Utilization

Instead of complex synchronization, we use memory-bank as a **living reference** that OpenSpec can directly utilize.

### How It Works

1. **Memory-Bank as Source of Truth** - Contains detailed technical context and historical decisions
2. **OpenSpec as Current State** - Contains validated specifications for current capabilities
3. **Direct References** - OpenSpec specs reference memory-bank for additional context

### Benefits

- ✅ **No Complex Sync** - No need for automated synchronization scripts
- ✅ **Preserved Context** - Memory-bank retains all historical knowledge
- ✅ **Validated Specs** - OpenSpec provides structured, validated specifications
- ✅ **Easy Maintenance** - Simple reference system

## Integration Methods

### 1. Reference Links in Specs

Add links to memory-bank files directly in OpenSpec specs:

```markdown
## Additional Context

For implementation details and technical decisions, see:
- [System Patterns](memory-bank/systemPatterns.md)
- [Technical Context](memory-bank/techContext.md)
- [Active Context](memory-bank/activeContext.md)
```

### 2. Memory-Bank Summaries in Specs

Include key insights from memory-bank in spec "Additional Context" sections:

```markdown
## Additional Context

**From memory-bank/systemPatterns.md:**
- Uses cooperative shutdown pattern with threading.Event
- Pystray for Windows tray integration with proper threading model
- Rich console output with JSON alternative for scripting

**From memory-bank/techContext.md:**
- Python 3.12+ with Typer, Rich, Pydantic v2, Loguru
- Windows-specific features with proper platform guards
```

### 3. Change Proposals Reference Memory-Bank

When creating new change proposals, reference relevant memory-bank sections:

```markdown
## Related Context

This change builds on the existing service architecture described in:
- [System Patterns - Service Pattern](memory-bank/systemPatterns.md#service-pattern)
- [Active Context - Technical Achievements](memory-bank/activeContext.md#technical-achievements)
```

## Simple Workflow

### For New Features

1. **Check memory-bank first** - Review existing patterns and decisions
2. **Create OpenSpec proposal** - Use standard OpenSpec workflow
3. **Reference memory-bank** - Add links to relevant sections
4. **Implement and archive** - Complete the OpenSpec change process

### For Documentation Updates

1. **Update memory-bank** - Add new insights, patterns, and decisions
2. **Reference in specs** - Add links from relevant OpenSpec specs
3. **Keep both current** - Memory-bank for context, OpenSpec for specs

## Example: Enhanced Spec with Memory-Bank References

```markdown
# Service Management Specification

## Purpose

Provide long-running background services with Windows system tray integration.

## Requirements

### Requirement: Cooperative Service Pattern

The system SHALL implement cooperative services that respond to stop events.

#### Scenario: Service Stops on Event
- **WHEN** service receives stop_event signal
- **THEN** service terminates its main loop and exits

## Additional Context

**Implementation Details:**
- See [System Patterns - Service Pattern](memory-bank/systemPatterns.md#service-pattern)
- Uses threading.Event for graceful shutdown
- 10-second timeout for service termination

**Technical Lessons:**
- From [Active Context - Critical Tray Lessons](memory-bank/activeContext.md#critical-tray-lessons-learned)
- Pystray more reliable than native Win32 on Windows 11
- Menu handlers must run in background threads

**Configuration:**
- See [Tech Context - Configuration Pattern](memory-bank/techContext.md#configuration-pattern)
- Uses BGU_ prefix for environment variables
```

## Maintenance Tips

### When to Update Memory-Bank

- After solving complex technical challenges
- When discovering new patterns or anti-patterns
- After major architecture decisions
- When documenting lessons learned

### When to Update OpenSpec

- For new feature requirements
- When changing existing behavior
- For breaking changes
- When adding new capabilities

### When to Reference Between Them

- **Memory-Bank → OpenSpec**: When memory-bank contains context relevant to specs
- **OpenSpec → Memory-Bank**: When specs need additional technical context

## Simple Automation (Optional)

For those who want minimal automation, add this to your development workflow:

```bash
# After updating memory-bank, validate all specs
echo "📝 Memory-bank updated - validating OpenSpec specs..."
openspec validate --specs --strict

# Before creating new proposals, check memory-bank
echo "🔍 Checking memory-bank for relevant context..."
grep -r "pattern|decision|lesson" memory-bank/
```

## Conclusion

This simple integration approach provides the best of both worlds:
- **Memory-Bank**: Rich historical context and technical insights
- **OpenSpec**: Validated, structured specifications
- **Direct References**: Easy navigation between the two

No complex synchronization needed - just maintain both systems and reference between them as appropriate.