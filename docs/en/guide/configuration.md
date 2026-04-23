# Configuration

CleanBook uses `config.json` as the core configuration file.

## Config File Location

Searched in this order:
1. Path specified by `--config`
2. `config.json` in current directory
3. `~/.config/cleanbook/config.json`
4. Built-in defaults

## Quick Generate

```bash
# Generate default config to current directory
cleanbook --init-config

# Generate to specific directory
cleanbook --init-config -o ~/.config/cleanbook/
```

## Core Settings

### ai_settings

```json
{
  "ai_settings": {
    "confidence_threshold": 0.7,
    "use_semantic_analysis": true,
    "cache_size": 10000,
    "max_workers": 4
  }
}
```

### llm

```json
{
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY"
  }
}
```

## Validation

```bash
cleanbook --validate-config
cleanbook --show-config
```
