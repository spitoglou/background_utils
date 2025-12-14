# OpenSpec + Memory-Bank Usage Guide

## Simple Integration Approach

This guide shows how to use OpenSpec and memory-bank together effectively.

### The Two Systems

**OpenSpec** - *What the system does*
- ✅ Validated specifications
- ✅ Current capabilities
- ✅ Requirements and scenarios
- ✅ Change proposals and archiving

**Memory-Bank** - *How it works and why*
- ✅ Technical patterns and decisions
- ✅ Historical context
- ✅ Lessons learned
- ✅ Implementation details

## Daily Workflow

### 1. Starting New Work

```bash
# 1. Check existing specs
openspec list --specs

# 2. Review relevant memory-bank context
grep -r "pattern|decision" memory-bank/

# 3. Create new proposal if needed
openspec change create add-new-feature
```

### 2. During Development

```bash
# Reference memory-bank for patterns
cat memory-bank/systemPatterns.md

# Validate specs frequently
openspec validate --specs

# Update memory-bank with new insights
# Edit memory-bank/activeContext.md
```

### 3. Completing Work

```bash
# Update specs with new capabilities
# Edit openspec/specs/new-feature/spec.md

# Add memory-bank references
# Add "Additional Context" section with links

# Validate and archive
openspec validate new-feature --strict
openspec archive new-feature
```

## Common Tasks

### Finding Information

**"What does the CLI system do?"**
```bash
openspec show cli
```

**"How is the CLI implemented?"**
```bash
cat memory-bank/systemPatterns.md | grep -A 10 "CLI"
```

**"What are the current services?"**
```bash
openspec show services
```

**"What lessons were learned about services?"**
```bash
cat memory-bank/activeContext.md | grep -A 20 "Service"
```

### Creating New Specs

```bash
# 1. Check if capability exists
openspec spec list

# 2. Review memory-bank for related patterns
find memory-bank -name "*.md" -exec grep -l "related-pattern" {} \;

# 3. Create new spec
mkdir -p openspec/specs/new-capability

# 4. Add basic structure
cat > openspec/specs/new-capability/spec.md << 'EOF'
# New Capability Specification

## Purpose

[Brief purpose statement]

## Requirements

### Requirement: Basic Functionality

The system SHALL provide [functionality].

#### Scenario: Basic Operation
- **WHEN** user interacts with system
- **THEN** system responds appropriately

## Additional Context

**Related Memory-Bank Sections:**
- [System Patterns - Related Pattern](memory-bank/systemPatterns.md)
- [Active Context - Implementation Notes](memory-bank/activeContext.md)
EOF

# 5. Validate
openspec validate new-capability --strict
```

### Updating Memory-Bank

```bash
# After solving a complex problem
echo "## New Pattern Discovered" >> memory-bank/activeContext.md
echo "" >> memory-bank/activeContext.md
echo "- Problem: [description]" >> memory-bank/activeContext.md
echo "- Solution: [solution]" >> memory-bank/activeContext.md
echo "- Lessons: [key insights]" >> memory-bank/activeContext.md

# Reference in relevant specs
sed -i '/## Additional Context/a\\n**New Pattern:**\\n- See [Active Context - New Pattern](memory-bank/activeContext.md#new-pattern-discovered)' \
    openspec/specs/related-capability/spec.md
```

## Best Practices

### When to Use Each System

**Use OpenSpec when:**
- Defining new requirements
- Documenting current capabilities
- Creating change proposals
- Validating system behavior

**Use Memory-Bank when:**
- Documenting technical decisions
- Recording lessons learned
- Explaining implementation details
- Tracking progress and achievements

### Keeping Systems in Sync

1. **Reference, don't duplicate** - Add links between systems instead of copying content
2. **Update memory-bank first** - Document technical insights as you work
3. **Reference in specs later** - Add memory-bank links when creating/updating specs
4. **Validate frequently** - Ensure specs remain valid after updates

### Example: Adding a New Service

```bash
# 1. Document the pattern in memory-bank
cat >> memory-bank/systemPatterns.md << 'EOF'

### New Service Pattern

**Problem:** [Problem statement]
**Solution:** [Solution approach]
**Implementation:** [Key implementation details]
**Lessons:** [What we learned]
EOF

# 2. Create the spec
mkdir -p openspec/specs/new-service

# 3. Add spec with memory-bank reference
cat > openspec/specs/new-service/spec.md << 'EOF'
# New Service Specification

## Purpose

Provide [service functionality].

## Requirements

### Requirement: Core Functionality

The system SHALL provide [specific functionality].

#### Scenario: Normal Operation
- **WHEN** service is started
- **THEN** service performs its function

## Additional Context

**Implementation Details:**
- See [System Patterns - New Service Pattern](memory-bank/systemPatterns.md#new-service-pattern)
- [Key technical details]

**Related Patterns:**
- [Cooperative Service Pattern](memory-bank/systemPatterns.md#service-pattern)
- [Configuration Pattern](memory-bank/techContext.md#configuration-pattern)
EOF

# 4. Validate
openspec validate new-service --strict
```

## Simple Automation

Add these helpers to your `.bashrc` or `.zshrc`:

```bash
# Quick spec validation
function validate-specs() {
    echo "🔍 Validating OpenSpec specs..."
    openspec validate --specs --strict
}

# Search memory-bank
function mb-search() {
    echo "🔍 Searching memory-bank for: $1"
    grep -r "$1" memory-bank/
}

# Show spec with memory-bank references
function show-spec() {
    echo "📖 Showing spec: $1"
    openspec show "$1"
    echo -e "\n🔗 Related memory-bank content:"
    grep -r "$1" memory-bank/ | head -5
}
```

## Conclusion

This simple integration approach gives you:
- **Structured specs** in OpenSpec for current capabilities
- **Rich context** in memory-bank for implementation details
- **Easy navigation** between the two systems via references
- **No complex synchronization** needed

Just maintain both systems and reference between them as appropriate!