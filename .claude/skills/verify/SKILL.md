---
name: verify
description: Run type checking and tests to verify changes. Use when you want to check that code is correct before committing or after making changes.
---

Run full verification suite for this Python project.

## What This Does

1. **Type checking**: `mypy src/ main.py --ignore-missing-imports`
2. **Tests**: `pytest -q` (quiet mode for fast feedback)

## Usage

```bash
/verify              # Full verification
/verify --coverage   # Include coverage report
/verify -k "test_name"  # Run specific test
```

## Execution

Run these commands in sequence:

```bash
# 1. Type check
mypy src/ main.py --ignore-missing-imports

# 2. Run tests
pytest -q
```

If either fails, report the errors and stop. If both pass, report success.

## Optional: Coverage

If `--coverage` flag is provided, run:

```bash
pytest --cov=src --cov-report=term -q
```

## Notes

- This project uses property-based testing with Hypothesis
- Use `-m "not slow"` to skip slow tests: `pytest -q -m "not slow"`
- The existing pre-commit hooks also run flake8 on critical errors only
