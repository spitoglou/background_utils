# Quick Reference Guide

## Common Commands

### Git Operations
```bash
git status                   # Check current status
git add .                    # Stage all changes
git commit -m "msg"          # Commit with message
git log --oneline -5         # Show recent commits
git diff                     # Show unstaged changes
git diff --staged            # Show staged changes
```

### OpenSpec Operations
```bash
openspec list --specs        # List all specifications
openspec validate --specs    # Validate all specs
openspec validate spec-name  # Validate specific spec
openspec show spec-name      # Show specific spec details
openspec validate --strict   # Strict validation mode
```

### File Operations
```bash
ls -la                       # List files (detailed)
find . -name "*.md"          # Find markdown files
grep -r "pattern" dir/      # Search for pattern
grep -r "pattern" dir/ | head -10  # Limit results
cat file.md                  # View file content
less file.md                # View large files
```

### Navigation
```bash
cd directory/                # Change directory
pwd                          # Show current directory
ls                           # List files
ls -la                       # List files (detailed)
tree /f                      # Show directory tree (Windows)
```

## Safe Practices

### Git Commit Messages
- Use simple, alphanumeric messages
- Avoid special characters: `()[]{}<>`
- Keep messages short and descriptive

### Command Testing
- Test with simple cases first
- Check command availability with `which`
- Use `--help` flag to check usage

### Validation
- Validate frequently during development
- Use `--strict` flag for comprehensive checks
- Fix format issues immediately

## Error Recovery

### Git Issues
```bash
git status                   # Check what's wrong
git add .                    # Stage all changes
git commit -m "simple-msg"   # Use simple message
git reset --soft HEAD~1      # Undo last commit (keep changes)
git reset --hard HEAD~1      # Undo last commit (discard changes)
```

### Validation Issues
```bash
openspec validate --specs --strict  # See detailed errors
openspec show spec-name --json      # Get structured output
# Edit spec to fix format issues
# Re-validate after fixes
```

### File Problems
```bash
ls -la                       # Check file existence
file file.txt                # Check file type
stat file.txt                # Get file details
# Fix file permissions/encoding as needed
```

## Session Template

```bash
# 1. Setup
echo "Starting session: [description]"
git status
openspec validate --specs

# 2. Implementation
# [Make changes with frequent validation]

# 3. Testing
echo "Testing..."
openspec validate --specs --strict

# 4. Commit
echo "Committing..."
git add .
git commit -m "feat brief-desc"

# 5. Summary
echo "Complete:"
git log --oneline -1
git status
```

## OpenSpec Spec Format

```markdown
# Specification Title

## Purpose
[Brief purpose statement]

## Requirements

### Requirement: [Requirement Name]
[Requirement description]

#### Scenario: [Scenario Name]
- **WHEN** [condition]
- **THEN** [result]

## Additional Context
[Memory-bank references and notes]
```

## Memory-Bank Reference Format

```markdown
**Implementation Details:**
- See [System Patterns - Pattern Name](memory-bank/systemPatterns.md#pattern-name)
- [Key technical details]

**Related Patterns:**
- [Related Pattern](memory-bank/techContext.md#related-pattern)
```