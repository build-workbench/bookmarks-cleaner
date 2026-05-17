---
layout: home
hero:
  name: Bookmarks Cleaner
  text: Offline-first Smart Bookmark Cleanup
  tagline: Rules Engine · ML-assisted · LLM-optional · Fully Offline
  actions:
    - theme: brand
      text: Get Started
      link: /en/guide/installation
    - theme: alt
      text: Read Whitepaper
      link: /en/whitepaper
features:
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
    title: Offline-first
    details: All core features run fully offline. Zero data upload. Absolute privacy control.
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
    title: Rule Engine
    details: Domain-pattern deterministic classification. Customizable rules. Millisecond latency.
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>
    title: ML-assisted
    details: Optional machine learning with incremental & active learning. Model versioning.
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
    title: LLM-optional
    details: OpenAI / Ollama local models. On-demand invocation. Semantic understanding.
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
    title: Multi-browser
    details: Native support for Chrome, Edge, Firefox, Safari HTML/JSON export formats.
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
    title: Multi-format Reports
    details: HTML visual reports, JSON structured data, Markdown documentation.
---

<HeroTerminal />

## Quick Start

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

## Core Architecture

<ArchitectureFlow />

## Why Bookmarks Cleaner

| Dimension | Bookmarks Cleaner | linkding | Shaarli | Traditional Scripts |
|-----------|-------------------|----------|---------|---------------------|
| Architecture | Pipeline + DI Container | Monolithic Django | Monolithic PHP | None |
| Offline | Fully offline | Self-hosted required | Self-hosted required | Offline |
| Classification | Rules + ML + LLM Fusion | Manual tags | Manual tags | None |
| Privacy | Local processing, zero upload | Self-hosted controlled | Self-hosted controlled | Local |
| Concurrency | ThreadPoolExecutor | Single-threaded | Single-threaded | None |
| Incremental Learning | Supported | Not supported | Not supported | None |
| Confidence Calibration | Platt / Isotonic | None | None | None |
| License | MIT | MIT | Zlib | Various |

## Technical Depth

<div class="cb-stagger">

- [Technical Whitepaper](/en/whitepaper) — Project positioning, core innovations & tech stack
- [Pipeline Architecture](/en/architecture/pipeline) — Five-stage processing pipeline
- [Fusion Algorithm](/en/algorithms/fusion) — Multi-classifier weighted voting & calibration
- [Architecture Decisions](/en/adr) — Key design trade-offs
- [Evolution](/en/evolution) — From 1,148-line god class to Facade + Pipeline

</div>
