# Agent Reports

Reports produced by agent workflows, organized by category.

## Structure

```
reports/
├── _registry.md        # Index of all active reports
├── _tech-debt.md       # Tracked improvements
├── README.md           # This file
├── archive/            # Old reports (moved, not deleted)
├── ci/                 # CI pipeline results
├── review/             # Code reviews, PR reviews
├── rfc/                # Design proposals
├── security/           # Security scans, threat models
├── sre/                # SLOs, postmortems, capacity plans
└── tests/              # Test plans, results, coverage
```

## Naming Convention

`[category]-[topic]-YYYYMMDD.md`

## Registry Management

- Reports are added to `_registry.md` after each agent produces output
- Use `/archive` to move entries older than N days to `archive/`
- Use `/debt` to view and manage the tech debt registry
