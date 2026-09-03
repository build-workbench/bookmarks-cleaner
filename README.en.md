# CleanBookmarks

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#)

[中文](https://github.com/build-workbench/bookmarks-cleaner/blob/main/README.md) | **English**

Too many bookmarks, all over the place? One command to **deduplicate, auto-classify, and organize** — everything runs locally.

## Install

```bash
pipx install cleanbookmarks
```

## Quick Start

1. **Export your bookmarks as HTML from your browser**
   - Chrome / Edge: `Bookmark manager → ⋮ → Export bookmarks`
   - Firefox: `Bookmarks → Manage Bookmarks → Import and Backup → Export Bookmarks to HTML`

2. **Run the classifier**

   ```bash
   cleanbookmarks -i bookmarks.html -o output/
   ```

3. **Import back into your browser**: import any `*.html` file under `output/` via your browser's "Import bookmarks". The same directory also contains `*.json` (structured data) and `*.markdown` (classification report).

![Screenshot](https://raw.githubusercontent.com/build-workbench/bookmarks-cleaner/main/docs/screenshot.png)

No bookmarks file handy? Download the bundled sample and try:

```bash
# Running from source: use the sample in the repo
cleanbookmarks -i examples/sample_bookmarks.html -o output/
# Installed via pipx: download the sample first (or use any exported bookmarks HTML)
curl -O https://raw.githubusercontent.com/build-workbench/bookmarks-cleaner/main/examples/sample_bookmarks.html
cleanbookmarks -i sample_bookmarks.html -o output/
```

## Common Options

```bash
cleanbookmarks -i a.html b.html -o output/ --workers 8   # multiple files + parallel
cleanbookmarks -i "bookmarks/*.html" -o output/          # glob support
cleanbookmarks -i bookmarks.html -c config.local.json    # custom config
cleanbookmarks -i bookmarks.html --limit 20              # small trial run first
```

The default config works out of the box. To tune classification rules, confidence thresholds, title cleaning, etc., copy the default config and pass it with `-c`:

```bash
# Running from source: default config lives at cleanbookmarks/resources/config.json
cp cleanbookmarks/resources/config.json config.local.json
# Installed via pipx: locate the packaged config first (pipx runpip cleanbookmarks show cleanbookmarks prints the path)
cleanbookmarks -i bookmarks.html -c config.local.json
```

See `cleanbookmarks --help` for all options.

## How Classification Works

A **two-level cascade**, rules first, fully explainable:

1. **Rule engine (default)**: regex matching over three signals — site domain, URL path, and title keywords. Each hit adds weighted category scores; scores of the same category are merged and normalized into a confidence value. A URL analyzer (recognizing GitHub, doc sites, video/Bilibili sites, etc.) provides extra hints.
2. **LLM fallback (optional)**: when enabled, bookmarks the rules miss go to the LLM; bookmarks the rules hit only get subcategory and reasoning enriched by the LLM.

Results below the confidence threshold (default 0.4) are marked as "unclassified" — better safe than sorry. The default config ships a bilingual (Chinese/English) vocabulary across 17 categories; pass `-c` with a custom config to tune rules and thresholds.

**Deduplication** is conservative: comparison happens only within the same domain, and a duplicate is declared only when any of 4 checks hit (exact URL, normalized URL, title+URL similarity, title similarity), with the title-similarity threshold set high at 0.95 to avoid dropping genuinely different pages.

## LLM Classification (Optional)

Fully offline by default. To let an AI classify bookmarks the rules miss:

```bash
pip install "cleanbookmarks[llm]"
```

Then enable it in `config.local.json`:

```json
{ "llm": { "enable": true, "base_url": "https://api.openai.com", "model": "gpt-4o-mini", "api_key_env": "OPENAI_API_KEY" } }
```

Set the `OPENAI_API_KEY` environment variable and run again.

### LLM Deep Participation (enhanced mode)

Beyond per-bookmark fallback, the LLM can take part in the whole pipeline in three stages (activated automatically once `llm.enhanced.enable` is on):

1. **Corpus analysis**: first reads the overall profile of your bookmarks (domains/keywords/language distribution) to judge the topic landscape.
2. **Config optimization**: proposes conservative rule additions (only appending keywords/categories, never deleting) based on the analysis, then writes them into the config — with an automatic backup (`config.llm-backup-*.json`, keeping the latest 5) before overwriting.
3. **Result audit**: after classification, audits every result and auto-fixes misclassifications, marking them `audited`.

```json
{ "llm": { "enable": true, "enhanced": { "enable": true, "audit_batch_size": 40 } } }
```

Any stage that fails (network/parse errors) is skipped automatically without breaking the run. Off by default; note token usage grows with bookmark count when enabled.

## FAQ

- **Will it delete bookmarks by mistake?** Deduplication only happens within the same domain, using 4 conservative strategies (exact URL, normalized URL, title+URL similarity, title similarity) — any single hit counts as a duplicate.
- **Privacy?** No network requests by default; only when LLM is enabled are bookmark titles/URLs sent to the API you configured.
- **Does it support Chinese bookmarks?** Yes — the classification vocabulary includes both Chinese and English variants.
- **How do I use the exported files?** Chrome / Edge / Firefox all support importing bookmarks HTML.
