# .kiro Directory - DEPRECATED

⚠️ **This directory has been deprecated.**

All specification documents have been migrated to the new `/specs` directory structure following the Spec-Driven Development (SDD) methodology.

## Migration Map

| Old Location (.kiro) | New Location (specs) |
|----------------------|----------------------|
| `.kiro/specs/architecture-algorithm-upgrade/requirements.md` | `specs/product/bookmark-classifier-system.md` |
| `.kiro/specs/architecture-algorithm-upgrade/design.md` | `specs/rfc/0001-architecture-algorithm-upgrade.md` |
| `.kiro/specs/architecture-algorithm-upgrade/tasks.md` | Tracked in project task management |

## New Spec Structure

```
specs/
├── product/          # Product requirements and user stories
│   └── bookmark-classifier-system.md
├── rfc/              # Technical design documents (RFCs)
│   └── 0001-architecture-algorithm-upgrade.md
├── api/              # API interface definitions
├── db/               # Database schemas
└── testing/          # Test specifications (BDD format)
    └── classification-tests.md
```

For more information, see:
- `AGENTS.md` - AI agent workflow instructions
- `CONTRIBUTING.md` - Contribution guidelines
- `specs/` - All specification documents

This directory will be removed in a future release.
