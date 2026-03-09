# CleanBook — Smart Bookmark Cleaning & Classification

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://lessup.github.io/bookmarks-cleaner/)

English | [简体中文](README.zh-CN.md)

KISS: Rules + ML + optional LLM, offline-ready by default. Unified title emoji cleanup, powerful deduplication, outputs HTML/Markdown/JSON.

## Features

- Rules first, ML/semantic assist, optional LLM integration (auto-fallback on failure)
- Unified title cleaning to avoid stacked emoji prefixes
- Always-on deduplication for stable cross-browser export merging
- Output classification limited to two levels for cleaner results

## Installation (pipx Recommended)

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
pipx install .
```

Two commands available after installation:

- `cleanbook`: Command-line processing (equivalent to `python main.py`)
- `cleanbook-wizard`: Interactive wizard experience

## Quick Example

```powershell
cleanbook -i examples/demo_bookmarks.html -o output
cleanbook -i "tests/input/*.html" --train
cleanbook-wizard
```

Common flags: `--workers` parallel, `--train` train ML, `--no-ml` disable ML, `--health-check` reachability check.

## LLM (Optional)

Edit `config.json` to enable:

```json
"llm": {
  "enable": true,
  "provider": "openai",
  "base_url": "https://api.openai.com",
  "model": "gpt-4o-mini",
  "api_key_env": "OPENAI_API_KEY"
}
```

Set environment variable:

```powershell
$env:OPENAI_API_KEY = "your_api_key"
```

Falls back to offline classification when key is unset or API fails.

With `organizer.enable`, a secondary LLM pass clusters, sorts and summarizes categories after classification.

## Project Structure

```
.
├─ src/
│  ├─ cleanbook/            # Unified CLI wrapper
│  │  └─ cli.py
│  ├─ ai_classifier.py      # Rules + ML + semantic + user profile + LLM
│  ├─ enhanced_classifier.py
│  ├─ enhanced_clean_tidy.py
│  ├─ bookmark_processor.py
│  ├─ emoji_cleaner.py       # Title emoji cleaning
│  └─ ...
├─ models/                  # Models & cache
├─ examples/
├─ docs/
├─ config.json
├─ main.py                  # Top-level entry
├─ pyproject.toml           # Packaging & CLI entry points
└─ changelog/
```

## Distribution

- **Local/Team**: `pipx install .` for isolated global commands
- **Open Source**: GitHub Release with example data; optionally publish to PyPI
- **Windows standalone**: Optional PyInstaller single-file EXE

## License

MIT — see `LICENSE`.
