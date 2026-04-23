# AGENTS.md

## OpenSpec Workflow (Spec-Driven Development)

This project uses **OpenSpec** for spec-driven development. All changes flow through the OpenSpec change management system.

### Command Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/opsx:explore "<topic>"` | Think, investigate, clarify | Before any proposal - explore ideas |
| `/opsx:propose "<idea>"` | Create change proposal | When you know what to build |
| `/opsx:apply` | Implement tasks | When proposal is ready |
| `/opsx:archive` | Archive completed change | After all tasks done |

### Development Workflow

```
┌─────────────────┐
│  /opsx:explore  │ ← Think, investigate, clarify
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ /opsx:propose   │ ← Creates: proposal.md, design.md, tasks.md
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /opsx:apply    │ ← Implements tasks from tasks.md
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ /opsx:archive   │ ← Moves to openspec/changes/archive/
└─────────────────┘
```

### Example Session

```
You: I want to add CSV export support

AI: /opsx:explore "CSV export"
    [discusses options, investigates codebase]

You: Let's proceed with the proposal

AI: /opsx:propose "add-csv-export"
    Creates:
    - openspec/changes/add-csv-export/proposal.md
    - openspec/changes/add-csv-export/design.md
    - openspec/changes/add-csv-export/tasks.md

You: Looks good, implement it

AI: /opsx:apply
    [implements each task, marks complete]

You: Done

AI: /opsx:archive
```

### Directory Structure

```
openspec/
├── config.yaml           # Project context and rules
├── specs/                # Persistent capability specifications
│   ├── bookmark-classifier/
│   ├── classification-testing/
│   ├── api/              # (planned)
│   └── database/         # (planned)
└── changes/              # Active and archived changes
    ├── <active-change>/  # Current work
    └── archive/          # Completed changes
        └── 2026-04-23-architecture-upgrade/
```

### Artifact Files

| File | Purpose |
|------|---------|
| `proposal.md` | Why & What - motivation, scope, non-goals |
| `design.md` | How - architecture, decisions, trade-offs |
| `tasks.md` | Implementation checklist with acceptance criteria |
| `specs/<capability>/spec.md` | Capability requirements with scenarios |

### Historical Specs

The `specs/` directory contains historical specifications that have been migrated to OpenSpec format. New specs should be created through `/opsx:propose`.

---

## Project Commands

```bash
# Setup
pip install -e .                    # Creates CLI: cleanbook, cleanbook-wizard
pre-commit install                  # Required for dev workflow

# Test
pytest                              # Full suite
pytest -m "not slow"                # Skip slow tests
pytest -m property                  # Property-based tests only

# Quality (run before committing)
black src/ tests/ && isort src/ tests/ && flake8 src/ tests/ && mypy src/

# Run
python main.py -i bookmarks.html -o output/
python main.py --health-check       # Debug component status
python main.py --no-ml ...          # Disable ML to save ~80MB memory
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│              CLI (main.py, cleanbook)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                        │
│        BookmarkProcessor → ClassifierPipeline               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Plugin Registry                           │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│   │  Rule   │ │   ML    │ │Embedding│ │   LLM   │          │
│   │Classifier│ │Classifier│ │Classifier│ │Classifier│         │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Services Layer                           │
│  EmbeddingService │ ActiveLearning │ TaxonomyService        │
│  FeatureStore     │ IncrTrainer    │ PerformanceMonitor     │
└─────────────────────────────────────────────────────────────┘
```

### Adding a Classifier Plugin

1. Create `src/plugins/classifiers/your_classifier.py`
2. Inherit from `ClassifierPlugin` in `src/plugins/base.py`
3. Implement: `metadata`, `classify(features)`, `initialize(config)`, `shutdown()`
4. Register in `config.json` under `plugins`

---

## Config Rules (`config.json`)

Rule types in `category_rules`:
- `match: domain` - URL domain patterns
- `match: title` - Bookmark title keywords
- `match: url_ends_with` - URL suffixes (e.g., `.pdf`)
- `match_all_keywords_in` - Require all keywords

---

## Conventions

- **Mixed Chinese/English codebase** - accept both in comments/docstrings
- **Type hints** throughout
- **Docstrings** required for public APIs
- **Logger**: Use `logging.getLogger(__name__)`, not `print`
- **OpenSpec-first**: All new features via `/opsx:propose`
