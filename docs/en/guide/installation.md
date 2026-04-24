# Installation

<CbBadge text="Stable v2.0.0" type="tip" />

## System Requirements

- **Python**: 3.10 or higher
- **OS**: Linux, macOS, Windows
- **Memory**: Minimum 512MB, recommended 2GB+ (when using ML)
- **Disk**: ~200MB (includes ML model cache)

## Installation Methods

### Method 1: pipx (Recommended)

[pipx](https://pipx.pypa.io/) installs CleanBook in an isolated virtual environment, avoiding dependency conflicts.

```bash
# Install pipx
pip install pipx
pipx ensurepath

# Install CleanBook
pipx install cleanbook

# Verify
which cleanbook
cleanbook --version
```

**Upgrade**: `pipx upgrade cleanbook`
**Uninstall**: `pipx uninstall cleanbook`

### Method 2: pip

```bash
# Install to current Python environment
pip install cleanbook

# Verify
cleanbook --version
```

::: warning Note
pip installation may conflict with other Python packages, especially when using system Python.
:::

### Method 3: uv

Using [uv](https://github.com/astral-sh/uv) provides faster installation:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install CleanBook
uv tool install cleanbook

# Verify
cleanbook --version
```

### Method 4: From Source

For modifying code or contributing:

```bash
# Clone repository
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -e ".[dev]"

# Verify
cleanbook --version
```

## Verification

Run these commands to verify successful installation:

```bash
# Check version
cleanbook --version

# Show help
cleanbook --help

# Run health check
cleanbook --health-check
```

## Optional Dependencies

### Enable Machine Learning (Recommended)

```bash
# Install scikit-learn for best classification results
pip install scikit-learn numpy

# Or inject with pipx
pipx inject cleanbook scikit-learn numpy
```

### Enable LLM (Optional)

```bash
# If you need LLM-enhanced classification
pip install openai

# pipx inject
pipx inject cleanbook openai
```

## Environment Setup

### Use a custom config

CleanBook uses its built-in default config unless you explicitly override it:

```bash
cleanbook -i bookmarks.html -o output/ -c ./config.json
```

## FAQ

### Q: Installation fails with "No module named 'sklearn'"?

```bash
# Install scikit-learn
pip install scikit-learn

# Or disable ML when using
cleanbook -i bookmarks.html --no-ml
```

### Q: cleanbook command not found on Windows?

```bash
# Check if Scripts directory is in PATH
pip show cleanbook

# Or use Python module directly
python -m cleanbook --help
```

### Q: "Cannot verify developer" on macOS?

Go to **System Settings → Privacy & Security**, click "Allow Anyway".

### Q: How to completely uninstall?

```bash
# pipx install
pipx uninstall cleanbook

# pip install
pip uninstall cleanbook

# Clean up config
rm -rf ~/.config/cleanbook
rm -rf ~/.cache/cleanbook
```

## Next Steps

- [Quick Start](../quickstart) — Get started in 5 minutes
- [Configuration](/en/reference/config) — Learn about config.json
- [Configuration Guide](/en/guide/configuration) — Learn how to override config safely
