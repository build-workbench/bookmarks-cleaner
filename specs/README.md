# Historical Specifications

> **Note**: This directory contains historical specification documents that have been migrated to the OpenSpec structure.

## Migration Status

**Migration Date**: 2026-04-23

All specifications have been migrated to OpenSpec format:

| Original Location | New Location |
|-------------------|--------------|
| `specs/product/bookmark-classifier-system.md` | `openspec/specs/bookmark-classifier/spec.md` |
| `specs/rfc/0001-architecture-algorithm-upgrade.md` | `openspec/changes/archive/2026-04-23-architecture-upgrade/` |
| `specs/testing/classification-tests.md` | `openspec/specs/classification-testing/spec.md` |
| `specs/api/README.md` | `openspec/specs/api/spec.md` |
| `specs/db/README.md` | `openspec/specs/database/spec.md` |

## Current Spec Locations

```
openspec/
├── specs/                    # Persistent capability specifications
│   ├── bookmark-classifier/
│   ├── classification-testing/
│   ├── api/
│   └── database/
└── changes/                  # Change management
    ├── <active-change>/      # Current work
    └── archive/              # Completed changes
```

## Creating New Specs

For **new features**, use the OpenSpec workflow:

```
/opsx:propose "feature description"
```

This will create:
- `openspec/changes/<name>/proposal.md`
- `openspec/changes/<name>/design.md`
- `openspec/changes/<name>/tasks.md`

## Reference

- OpenSpec configuration: `openspec/config.yaml`
- Workflow guide: `AGENTS.md`
