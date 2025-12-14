## ADDED Requirements

### Requirement: Documentation Hygiene

The project SHALL maintain clean documentation without orphaned or duplicate files in the repository root.

#### Scenario: No orphaned implementation summaries
- **WHEN** an OpenSpec change is archived
- **THEN** all related summary files are contained within the archive directory
- **AND** no implementation progress files remain in the project root

#### Scenario: Single source of AI assistant instructions
- **WHEN** AI assistants need project guidance
- **THEN** instructions are consolidated in CLAUDE.md
- **AND** no duplicate instruction stubs exist in the project root
