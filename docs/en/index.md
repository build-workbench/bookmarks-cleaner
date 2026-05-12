---
layout: home
hero:
  name: CleanBook
  text: Offline-first bookmark cleanup for developers
  tagline: Rules-first · ML-assisted · LLM-optional · built for people with too many bookmarks
  image:
    src: /logo.svg
    alt: CleanBook
  actions:
    - theme: brand
      text: Start in 10 minutes
      link: /en/quickstart
    - theme: alt
      text: View on GitHub
      link: https://github.com/LessUp/bookmarks-cleaner
features:
  - icon: 🔒
    title: Actually offline
    details: Processing stays local by default. Your bookmarks and rules do not need a cloud account.
  - icon: ⚙️
    title: Config-driven
    details: Adjust categories, thresholds, and taxonomy files without rebuilding the tool.
  - icon: 🤖
    title: Rules first, AI where it helps
    details: Stable rule matches come first, with ML and optional LLM layers improving recall rather than replacing the whole pipeline.
  - icon: 📦
    title: Built to ship results
    details: Feed it browser-exported bookmark HTML and get cleaned HTML, JSON, and report-friendly output back.
---

## Why CleanBook

CleanBook is for people who already have a large bookmark pile and want to clean it up **without handing it to a hosted platform**. It is meant to help you deduplicate, classify, and export the collection you already own.

**Perfect for:**
- 📚 Developers with years of accumulated bookmarks (1000+)
- 🔒 Privacy-conscious users who want offline processing
- ⚡ Teams sharing classification rules and taxonomy files
- 🛠️ Researchers studying bookmark-processing pipelines

## Real-World Results

**Before CleanBook:**
- 3,500+ unorganized bookmarks accumulated over 5 years
- Hundreds of duplicates and dead links
- No consistent categorization
- Browser becomes slow and unusable

**After CleanBook:**
- Cleaned to 2,800 unique, active bookmarks
- Organized into 20+ categories using custom rules
- 100% offline processing, no data leaves your machine
- Export ready for browser re-import in minutes

## How it works

1. Export bookmark HTML from your browser
2. Run `cleanbook -i bookmarks.html -o output/`
3. Let stable rules run first, with ML and optional LLM layers only where they add value
4. Review the cleaned outputs and keep iterating on your own taxonomy

## What you get back

- **Cleaned HTML** for browser re-import
- **JSON output** for analysis and automation
- **Report-style artifacts** for review and manual refinement

<div class="cb-stats">
  <div class="cb-stat">
    <span class="cb-stat-value">3500+</span>
    <span class="cb-stat-label">Bookmarks Processed</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">100%</span>
    <span class="cb-stat-label">Offline Processing</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">20+</span>
    <span class="cb-stat-label">Custom Categories</span>
  </div>
</div>

## Fastest path

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

For the most stable execution path:

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

## Who it fits

- **Individuals** cleaning years of saved browser bookmarks
- **Team maintainers** sharing classification rules and taxonomy files
- **Developers** studying bookmark-processing pipelines and CLI design

## Why it stays trustworthy

- **Actually offline**: no hosted account is required for the default path
- **Rules first**: stable matches remain explainable and reproducible
- **Bounded AI usage**: ML and LLM layers improve recall instead of replacing the whole pipeline

## Next steps

- [Quick Start](/en/quickstart)
- [Installation](/en/guide/installation)
- [Configuration](/en/reference/config)
- [Taxonomy](/en/reference/taxonomy)
