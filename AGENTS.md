# AGENTS.md - AI Agent Workflow Instructions

## Project Philosophy: Spec-Driven Development (SDD)

This project strictly follows the **Spec-Driven Development (SDD)** paradigm. All code implementations must use the specification documents in the `/specs` directory as the single source of truth.

## Directory Context

### Specifications (`/specs`)
- `/specs/product/`: Product feature definitions and acceptance criteria
- `/specs/rfc/`: Technical design documents and architecture proposals
- `/specs/api/`: API interface specifications (OpenAPI, GraphQL schemas)
- `/specs/db/`: Database schema definitions and migration scripts
- `/specs/testing/`: BDD test specifications and acceptance test definitions

### Documentation (`/docs`)
- `/docs/setup/`: Environment setup guides
- `/docs/tutorials/`: User tutorials and how-to guides
- `/docs/architecture/`: High-level architecture documentation
- `/docs/assets/`: Static assets (images, diagrams, etc.)

### Project Root
- `README.md`: Project entry point (English)
- `README.zh-CN.md`: Chinese translation of README
- `CONTRIBUTING.md`: Contribution guidelines
- `CHANGELOG.md`: Change log
- `CLAUDE.md`: AI assistant context for Claude Code
- `QWEN.md`: AI assistant context for Qwen Code

## AI Agent Workflow Instructions

When you (the AI) are asked to develop a new feature, modify an existing feature, or fix a bug, **you MUST strictly follow this workflow. Do NOT skip any steps**:

### Step 1: Review Specifications (Review Specs)
- **First**, read the relevant specification documents in the `/specs` directory:
  - Product requirements in `/specs/product/`
  - Technical designs in `/specs/rfc/`
  - API definitions in `/specs/api/`
  - Test specifications in `/specs/testing/`
- If the user's instruction conflicts with existing specs, **immediately stop coding** and point out the conflict. Ask the user whether to update the spec first.

### Step 2: Spec-First Update
- If this is a **new feature** or requires **changes to existing interfaces/database structures**, **you MUST first propose modifying or creating spec documents** (e.g., `openapi.yaml` or RFC documents).
- **Wait for user confirmation** on the spec modifications before proceeding to code implementation.
- This ensures **document-code synchronization** and prevents documentation drift.

### Step 3: Code Implementation (Implementation)
- When writing code, **100% comply** with the definitions in the specs (including variable names, API paths, data types, status codes, etc.).
- **Do NOT add features not defined in the specs** (No Gold-Plating).
- Follow the project's coding standards:
  - PEP8 Python coding standards
  - Use type hints throughout
  - Complete docstrings for functions and classes
  - High-value comments explaining **why**, not **what**

### Step 4: Test Verification (Test against Spec)
- Write unit tests and integration tests based on the **acceptance criteria** in `/specs/`.
- Ensure test cases cover **all boundary conditions** described in the specs.
- Run the test suite to verify: `python tests/test_suite.py`
- **All tests must pass** before considering the task complete.

## Code Generation Rules

1. **API Changes**: Any externally exposed API changes **MUST** be synchronized with `/specs/api/openapi.yaml` (or equivalent spec files).
2. **Database Changes**: Any database schema changes **MUST** be synchronized with `/specs/db/`.
3. **Uncertainty Handling**: If you encounter uncertain technical details, **consult** the architecture conventions in `/specs/rfc/`. **Do NOT invent design patterns**.
4. **No Spec, No Code**: **Do NOT write code without corresponding spec documentation**. If a spec doesn't exist, propose creating one first.
5. **Spec Traceability**: All code implementations should be traceable back to specific requirements in the specs.

## Development Commands

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run health check
python main.py --health-check

# Process bookmarks (CLI mode)
python main.py -i examples/demo_bookmarks.html

# Start interactive mode
python main.py --interactive

# Run tests
python tests/test_suite.py
```

### Key Components
- `src/rule_engine.py` - Keyword-based fast classification
- `src/ml_classifier.py` - Machine learning classification using scikit-learn
- `src/ai_classifier.py` - AI main classifier coordinating multiple methods
- `src/bookmark_processor.py` - Batch bookmark processing
- `src/cli_interface.py` - CLI user interface
- `config.json` - Configuration file with category rules, AI settings, etc.

### Output Formats
Processing completes generates three output formats:
1. **HTML**: Importable to browsers
2. **JSON**: Detailed classification metadata and statistics
3. **Markdown**: Readable classification report

## Performance Optimization Guidelines

- Multi-threaded parallel processing
- Intelligent caching (LRU cache)
- Batch processing mechanism
- Lazy initialization of components

## Important Notes

1. Machine learning features require additional dependencies (scikit-learn, jieba, etc.)
2. When processing large numbers of bookmarks, adjust thread count for performance
3. Classification rules and weights can be customized via configuration
4. System supports both Chinese and English content processing
5. System has learning capability and can optimize classification based on user feedback

## Preventing AI Hallucinations

This declaration prevents AI from "freestyling" without context:
- **Mandatory spec review first**: Anchors your thinking to existing documentation
- **Spec-first approach**: Ensures documentation and code stay synchronized
- **No gold-plating**: Only implement what's specified
- **Test against spec**: Verify against defined acceptance criteria

When in doubt, **reference the specs, don't invent**.
