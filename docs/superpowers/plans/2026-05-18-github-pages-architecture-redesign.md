# GitHub Pages Architecture Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the GitHub Pages site into a research-grade architecture and whitepaper portal with stronger information architecture, theme-aware diagrams, deeper technical content, and production-safe GitHub Pages behavior.

**Architecture:** Keep VitePress as the static rendering and deployment foundation, but treat it as a rendering engine rather than a default docs theme. Rebuild the site through three layers: harden config/navigation, replace the visual system with theme-aware components and diagram primitives, then rewrite the high-value content pages around system architecture, algorithms, performance, and references.

**Tech Stack:** VitePress 1.x, Vue 3 SFCs, CSS custom properties, Markdown, Mermaid, GitHub Pages Actions workflow

---

## File Structure Map

### Core config and theme shell

- Modify: `docs/.vitepress/config.ts` — fix locale redirect, rebuild nav/sidebar, remove or replace dead links, align metadata with the new IA
- Modify: `docs/.vitepress/theme/index.ts` — register the new components and remove duplicate home hero injection
- Modify: `docs/.vitepress/theme/style.css` — replace the current theme layer with research-grade tokens, valid overlays, page scaffolding, and diagram styles

### Theme-aware presentation components

- Create: `docs/.vitepress/theme/components/ResearchHero.vue` — architecture-first hero with technical claims and primary entry points
- Create: `docs/.vitepress/theme/components/SystemMap.vue` — theme-aware SVG overview of the full runtime architecture
- Create: `docs/.vitepress/theme/components/EvidenceGrid.vue` — evidence cards for privacy, explainability, extensibility, and deployment characteristics
- Create: `docs/.vitepress/theme/components/ReadingPathGrid.vue` — guided entry points for different reader intents
- Create: `docs/.vitepress/theme/components/BenchmarkStrip.vue` — benchmark and runtime evidence strip
- Create: `docs/.vitepress/theme/components/CitationCluster.vue` — compact bibliography and related-reading cluster
- Create: `docs/.vitepress/theme/components/ThemedFigure.vue` — unified figure wrapper for light/dark images, captions, and diagram framing
- Modify: `docs/.vitepress/theme/components/ArchitectureFlow.vue` — either simplify it into a supporting module or replace it with the new system map usage
- Modify: `docs/.vitepress/theme/components/DarkModeImage.vue` — turn into a compatibility wrapper or redirect to the new figure model
- Modify: `docs/.vitepress/theme/components/HeroTerminal.vue` — reduce visual dominance and fit the new lab-grade style

### Content pages

- Modify: `docs/index.md` — keep root redirect landing behavior minimal
- Modify: `docs/en/index.md`
- Modify: `docs/zh/index.md`
- Modify: `docs/en/whitepaper.md`
- Modify: `docs/zh/whitepaper.md`
- Modify: `docs/en/resources/references.md`
- Modify: `docs/zh/resources/references.md`
- Modify: `docs/en/resources/related-projects.md`
- Modify: `docs/zh/resources/related-projects.md`
- Modify: `docs/en/evolution.md`
- Modify: `docs/zh/evolution.md`
- Modify: `docs/en/architecture/pipeline.md`
- Modify: `docs/zh/architecture/pipeline.md`

### Optional link-resolution follow-up

- Create or remove references for: `docs/en/reference/api.md`, `docs/zh/reference/api.md`

---

### Task 1: Harden config and rebuild information architecture

**Files:**
- Modify: `docs/.vitepress/config.ts`
- Modify: `docs/index.md`
- Modify: `docs/en/index.md`
- Modify: `docs/zh/index.md`

- [ ] **Step 1: Capture the current docs baseline**

Run:

```bash
cd docs && npm run build
```

Expected: VitePress build succeeds so later failures can be attributed to the redesign.

- [ ] **Step 2: Fix the root locale redirect logic in `docs/.vitepress/config.ts`**

Replace the current ternary-or expression with an explicit branch:

```ts
const stored = localStorage.getItem(key)
const prefersZh = (navigator.language || '').toLowerCase().startsWith('zh')
const targetLang = stored ?? (prefersZh ? 'zh' : 'en')
if (!stored) localStorage.setItem(key, targetLang)
location.replace(base + targetLang + '/')
```

- [ ] **Step 3: Reshape the navigation and sidebar around the new reading model**

Drive both locales from the same conceptual order:

```ts
nav: [
  { text: 'Overview', link: '/en/' },
  { text: 'Architecture', link: '/en/architecture/pipeline' },
  { text: 'Algorithms', link: '/en/algorithms/fusion' },
  { text: 'Performance', link: '/en/performance/optimization' },
  { text: 'Whitepaper', link: '/en/whitepaper' },
  { text: 'References', link: '/en/resources/references' },
]
```

The Chinese locale should mirror this structure with translated labels.

- [ ] **Step 4: Resolve the `Python API` dead-link risk**

Choose one of these concrete outcomes and implement it consistently in both locales:

```ts
// Option A: remove the nav/sidebar entry
items: [
  { text: 'CLI', link: '/en/reference/cli' },
  { text: 'Configuration', link: '/en/reference/config' },
  { text: 'Taxonomy', link: '/en/reference/taxonomy' },
]
```

or

```md
# Python API

Bookmarks Cleaner currently exposes the CLI as the stable public entry point.
This page documents the thin Python surface around `BookmarkProcessor`.
```

- [ ] **Step 5: Rewrite the home page frontmatter so the landing pages become architecture-first**

Target shape for both locales:

```md
---
layout: home
title: Bookmarks Cleaner
hero:
  name: Bookmarks Cleaner
  text: Offline-first Bookmark Systems Engineering
  tagline: Rules-first classification, fusion-based inference, and whitepaper-grade documentation.
  actions:
    - theme: brand
      text: Read the Whitepaper
      link: /en/whitepaper
    - theme: alt
      text: Explore Architecture
      link: /en/architecture/pipeline
---
```

- [ ] **Step 6: Rebuild and confirm navigation integrity**

Run:

```bash
cd docs && npm run build
```

Expected: PASS with no broken page generation from removed or added links.

- [ ] **Step 7: Commit the IA/config pass**

```bash
git add docs/.vitepress/config.ts docs/index.md docs/en/index.md docs/zh/index.md
git commit -m "feat(docs): harden pages config and restructure navigation"
```

### Task 2: Replace the theme shell with a research-grade visual system

**Files:**
- Modify: `docs/.vitepress/theme/index.ts`
- Modify: `docs/.vitepress/theme/style.css`
- Modify: `docs/.vitepress/theme/components/DarkModeImage.vue`
- Modify: `docs/.vitepress/theme/components/HeroTerminal.vue`
- Create: `docs/.vitepress/theme/components/ThemedFigure.vue`

- [ ] **Step 1: Stop duplicate hero content injection**

Reduce `Layout` to a plain extension or only keep slots that are not duplicated in Markdown:

```ts
const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ThemedFigure', ThemedFigure)
    app.component('HeroTerminal', HeroTerminal)
  },
}
```

- [ ] **Step 2: Replace invalid overlay variables in `style.css`**

Use explicit RGB triplets for translucent surfaces instead of `rgba(var(--cb-bg), 0.85)`:

```css
:root {
  --cb-surface-rgb: 255, 255, 255;
}

.dark {
  --cb-surface-rgb: 11, 15, 23;
}

.VPNav {
  background: rgba(var(--cb-surface-rgb), 0.85);
}
```

- [ ] **Step 3: Rescope the theme from “cyberpunk glow” to “systems-lab precision”**

The token layer should move toward calmer contrast and denser information rhythm:

```css
:root {
  --cb-accent: #2563eb;
  --cb-accent-2: #0f766e;
  --cb-paper: #f8fafc;
  --cb-elevated: #ffffff;
  --cb-chart-1: #2563eb;
  --cb-chart-2: #0f766e;
  --cb-chart-3: #7c3aed;
}
```

- [ ] **Step 4: Introduce the unified figure wrapper**

Create `ThemedFigure.vue` around `picture`, `img`, caption, and frame chrome:

```vue
<picture>
  <source v-if="darkSrc" media="(prefers-color-scheme: dark)" :srcset="darkSrc" />
  <img :src="lightSrc" :alt="alt" class="cb-figure-image" />
</picture>
```

- [ ] **Step 5: Make `DarkModeImage.vue` a compatibility shim**

```vue
<ThemedFigure
  :light-src="lightSrc"
  :dark-src="darkSrc"
  :alt="alt"
  :caption="caption"
/>
```

- [ ] **Step 6: Tone down `HeroTerminal.vue` so it supports the story instead of dominating it**

Apply narrower shadows, quieter hover behavior, and stronger typography contrast:

```css
.cb-terminal {
  box-shadow: var(--cb-shadow-lg);
  border: 1px solid var(--cb-border);
}
```

- [ ] **Step 7: Rebuild the site**

Run:

```bash
cd docs && npm run build
```

Expected: PASS and no component registration/runtime compilation errors.

- [ ] **Step 8: Commit the theme shell pass**

```bash
git add docs/.vitepress/theme/index.ts docs/.vitepress/theme/style.css docs/.vitepress/theme/components/DarkModeImage.vue docs/.vitepress/theme/components/HeroTerminal.vue docs/.vitepress/theme/components/ThemedFigure.vue
git commit -m "feat(docs): rebuild theme shell for research-grade presentation"
```

### Task 3: Build the new homepage and key architecture visuals

**Files:**
- Create: `docs/.vitepress/theme/components/ResearchHero.vue`
- Create: `docs/.vitepress/theme/components/SystemMap.vue`
- Create: `docs/.vitepress/theme/components/EvidenceGrid.vue`
- Create: `docs/.vitepress/theme/components/ReadingPathGrid.vue`
- Create: `docs/.vitepress/theme/components/BenchmarkStrip.vue`
- Create: `docs/.vitepress/theme/components/CitationCluster.vue`
- Modify: `docs/.vitepress/theme/components/ArchitectureFlow.vue`
- Modify: `docs/en/index.md`
- Modify: `docs/zh/index.md`

- [ ] **Step 1: Create the architecture-first hero component**

Seed `ResearchHero.vue` with a grid that separates thesis, metric strip, and entry points:

```vue
<section class="cb-research-hero">
  <p class="cb-kicker">Offline-first systems paper for bookmark cleanup</p>
  <h1>Rules-first classification with fusion-based intelligence.</h1>
  <div class="cb-hero-actions">
    <a href="/en/whitepaper">Whitepaper</a>
    <a href="/en/architecture/pipeline">Architecture</a>
    <a href="/en/performance/optimization">Performance</a>
  </div>
</section>
```

- [ ] **Step 2: Create the system map as a theme-aware SVG**

Use grouped layers for entry, orchestration, pipeline, classifiers, and outputs:

```vue
<svg viewBox="0 0 1200 720" class="cb-system-map">
  <g data-layer="entry">...</g>
  <g data-layer="orchestration">...</g>
  <g data-layer="pipeline">...</g>
  <g data-layer="intelligence">...</g>
  <g data-layer="outputs">...</g>
</svg>
```

- [ ] **Step 3: Add evidence and reader-path blocks**

Concrete cards should encode technical claims instead of marketing copy:

```ts
const evidence = [
  { title: 'Offline Guarantee', detail: 'Core execution stays local; LLM remains optional.' },
  { title: 'Explainable Fusion', detail: 'Classifier weights and confidence flow are visible.' },
  { title: 'Composable Runtime', detail: 'Facade + pipeline + protocols isolate change.' },
]
```

- [ ] **Step 4: Rework `docs/en/index.md` and `docs/zh/index.md` to use the new components**

Replace the current feature-card homepage with a whitepaper landing skeleton:

```md
<ResearchHero />
<BenchmarkStrip />
<SystemMap />
<EvidenceGrid />
<ReadingPathGrid />
<CitationCluster />
```

- [ ] **Step 5: Relegate `ArchitectureFlow.vue` to a secondary role or fold its content into `SystemMap.vue`**

If it remains, make it a smaller supporting figure for architecture pages rather than the home page anchor.

- [ ] **Step 6: Build and inspect the rendered homepage**

Run:

```bash
cd docs && npm run build
```

Expected: PASS and generated home pages contain the new component content.

- [ ] **Step 7: Commit the new home system**

```bash
git add docs/.vitepress/theme/components/ResearchHero.vue docs/.vitepress/theme/components/SystemMap.vue docs/.vitepress/theme/components/EvidenceGrid.vue docs/.vitepress/theme/components/ReadingPathGrid.vue docs/.vitepress/theme/components/BenchmarkStrip.vue docs/.vitepress/theme/components/CitationCluster.vue docs/.vitepress/theme/components/ArchitectureFlow.vue docs/en/index.md docs/zh/index.md
git commit -m "feat(docs): rebuild homepage around architecture and evidence"
```

### Task 4: Rewrite the whitepaper and references into a technical evidence chain

**Files:**
- Modify: `docs/en/whitepaper.md`
- Modify: `docs/zh/whitepaper.md`
- Modify: `docs/en/resources/references.md`
- Modify: `docs/zh/resources/references.md`
- Modify: `docs/en/resources/related-projects.md`
- Modify: `docs/zh/resources/related-projects.md`
- Modify: `docs/en/evolution.md`
- Modify: `docs/zh/evolution.md`

- [ ] **Step 1: Rewrite the whitepaper structure around thesis, system boundary, algorithms, performance, failure modes, and references**

Target top-level shape:

```md
# Technical Whitepaper
## Abstract
## System Thesis
## Runtime Boundary
## Architecture Model
## Fusion and Confidence
## Performance Methodology
## Failure Modes and Fallbacks
## References
```

- [ ] **Step 2: Add explicit evidence-driven language instead of generic capability claims**

Use statements like:

```md
- **Why weighted voting instead of stacking:** heterogeneous outputs, zero extra training requirement, traceable decision path.
- **Why ThreadPoolExecutor instead of asyncio:** library compatibility and CPU-adjacent workloads.
```

- [ ] **Step 3: Turn `related-projects.md` into a comparative research note**

Anchor comparisons on deployment model, offline guarantees, extensibility, and intelligence stack:

```md
| Project | Runtime model | Offline-first | Classification strategy | Operational cost |
|---------|---------------|---------------|-------------------------|------------------|
| Bookmarks Cleaner | Local CLI | Yes | Rules + ML + LLM fusion | Very low |
```

- [ ] **Step 4: Make `references.md` serve the whitepaper**

Group citations by problem space and include a short “why it matters here” line per cluster.

- [ ] **Step 5: Rewrite `evolution.md` as an engineering narrative**

Preserve the god-class-to-pipeline story, but connect it directly to the current site’s architecture claims.

- [ ] **Step 6: Rebuild the docs**

Run:

```bash
cd docs && npm run build
```

Expected: PASS and no malformed Markdown/Vue hybrid content.

- [ ] **Step 7: Commit the content deepening pass**

```bash
git add docs/en/whitepaper.md docs/zh/whitepaper.md docs/en/resources/references.md docs/zh/resources/references.md docs/en/resources/related-projects.md docs/zh/resources/related-projects.md docs/en/evolution.md docs/zh/evolution.md
git commit -m "feat(docs): deepen whitepaper and reference content"
```

### Task 5: Align secondary architecture pages and finish release validation

**Files:**
- Modify: `docs/en/architecture/pipeline.md`
- Modify: `docs/zh/architecture/pipeline.md`
- Modify: `docs/.vitepress/config.ts`
- Optional Create: `docs/en/reference/api.md`
- Optional Create: `docs/zh/reference/api.md`

- [ ] **Step 1: Make the pipeline page match the new system-map vocabulary**

Refactor the opening section to use the same layer labels as the homepage:

```md
## Runtime Layers
### Entry and orchestration
### Processing pipeline
### Intelligence layer
### Output surfaces
```

- [ ] **Step 2: Resolve any remaining navigation or reference mismatch**

If `Python API` was retained in config, create the concrete pages:

```md
# Python API

`BookmarkProcessor` remains the canonical Python entry point.
This surface mirrors the CLI pipeline and is intentionally thin.
```

- [ ] **Step 3: Run the maintained repository verification baseline**

Run:

```bash
python3 -m pytest -q tests/test_runtime_paths.py
python3 -m pytest -q
cd docs && npm run build
```

Expected: all commands pass.

- [ ] **Step 4: Inspect git diff for accidental generated artifacts**

Run:

```bash
git --no-pager status --short
git --no-pager diff -- docs/.vitepress/dist
```

Expected: only maintained source files are staged; generated build output is not introduced.

- [ ] **Step 5: Commit the final docs release**

```bash
git add docs/.vitepress/config.ts docs/en/architecture/pipeline.md docs/zh/architecture/pipeline.md docs/en/reference/api.md docs/zh/reference/api.md
git commit -m "feat(docs): complete whitepaper-grade pages redesign"
```

- [ ] **Step 6: Push the final result**

```bash
git push origin master
```

Expected: remote accepts the direct-push workflow and GitHub Pages workflow can deploy from master.

---

## Self-Review

### Spec coverage

- Config hardening and IA: covered by Task 1 and Task 5
- Theme/token and dark-mode fixes: covered by Task 2 and Task 3
- Diagram overhaul: covered by Task 3 and Task 5
- Whitepaper/performance/reference deepening: covered by Task 4 and Task 5
- Production-safe verification and push: covered by Task 5

### Placeholder scan

- No `TODO`, `TBD`, “implement later”, or “same as above” placeholders remain.
- Every task lists exact file paths and concrete commands.

### Type and naming consistency

- New component names stay consistent across theme registration, Markdown usage, and task references.
- The plan treats `ThemedFigure` as the new canonical wrapper and `DarkModeImage` as a compatibility path.
