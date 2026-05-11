---
layout: home
hero:
  name: CleanBook
  text: Offline-first Bookmark Cleaner
  tagline: Rules-first · ML-assisted · LLM-optional · For developers with too many bookmarks
  image:
    src: /logo.svg
    alt: CleanBook
  actions:
    - theme: brand
      text: Get Started
      link: /en/quickstart
    - theme: alt
      text: 开始使用
      link: /zh/quickstart
features:
  - icon: 🔒
    title: Truly Offline
    details: All processing stays local by default. No cloud account required. Your bookmarks never leave your machine.
  - icon: ⚙️
    title: Config-Driven
    details: Customize categories, thresholds, and taxonomy through config.json and YAML files without touching the code.
  - icon: 🤖
    title: Rules First, AI Enhanced
    details: Stable rule matches first, with ML and optional LLM layers improving coverage—not replacing your logic.
  - icon: 📦
    title: Ready to Ship
    details: Feed browser-exported bookmark HTML, get cleaned HTML, JSON, and reports ready for re-import or analysis.
---

<div class="cb-cta-section">

## One Command to Clean Your Bookmarks

<div class="cb-terminal">
  <div class="cb-terminal-header">
    <span class="cb-terminal-dot red"></span>
    <span class="cb-terminal-dot yellow"></span>
    <span class="cb-terminal-dot green"></span>
  </div>
  <div class="cb-terminal-body">
    <span class="prompt">$</span> <span class="command">pipx install cleanbook</span><br>
    <span class="prompt">$</span> <span class="command">cleanbook -i bookmarks.html -o output/</span><br>
    <span class="output">✓ Processed 3,500 bookmarks</span><br>
    <span class="output">✓ Removed 412 duplicates</span><br>
    <span class="output">✓ Classified into 23 categories</span><br>
    <span class="success">✓ Done! Check output/ for results</span>
  </div>
</div>

</div>

<div class="cb-stats">
  <div class="cb-stat">
    <span class="cb-stat-value">100%</span>
    <span class="cb-stat-label">Offline Processing</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">3,500+</span>
    <span class="cb-stat-label">Bookmarks Tested</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">20+</span>
    <span class="cb-stat-label">Built-in Categories</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">0</span>
    <span class="cb-stat-label">Cloud Dependencies</span>
  </div>
</div>

## Who Is This For?

<div class="cb-personas">
  <div class="cb-persona">
    <div class="cb-persona-icon">📚</div>
    <div class="cb-persona-title">Bookmark Collectors</div>
    <div class="cb-persona-desc">Years of accumulated bookmarks (1000+)? Clean duplicates, fix dead links, and organize in minutes.</div>
  </div>
  <div class="cb-persona">
    <div class="cb-persona-icon">🔒</div>
    <div class="cb-persona-title">Privacy-Conscious Users</div>
    <div class="cb-persona-desc">No cloud, no accounts, no tracking. Your bookmarks stay on your machine.</div>
  </div>
  <div class="cb-persona">
    <div class="cb-persona-icon">⚡</div>
    <div class="cb-persona-title">Development Teams</div>
    <div class="cb-persona-desc">Share classification rules and taxonomy files across your team for consistent categorization.</div>
  </div>
</div>

## Why CleanBook?

**Before CleanBook:**
- 3,500+ unorganized bookmarks accumulated over years
- Hundreds of duplicates and dead links
- No consistent categorization
- Browser slows down under the weight

**After CleanBook:**
- Cleaned to 2,800 unique, active bookmarks
- Organized into 20+ categories with custom rules
- 100% offline, no data leaves your machine
- Export ready for browser re-import in minutes

## What You Get

| Output | Description |
|--------|-------------|
| `cleaned.html` | Browser-ready HTML for re-import |
| `bookmarks.json` | Structured data for automation |
| `report.md` | Human-readable classification report |

## Choose Your Language / 选择语言

<div class="cb-lang-buttons">
  <a href="/bookmarks-cleaner/en/" class="cb-lang-btn">English Documentation</a>
  <a href="/bookmarks-cleaner/zh/" class="cb-lang-btn">中文文档</a>
</div>

<style>
.cb-cta-section {
  text-align: center;
  margin: 2rem 0;
}

.cb-terminal {
  background: #0f172a;
  border-radius: 12px;
  overflow: hidden;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  max-width: 600px;
  margin: 1.5rem auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.cb-terminal-header {
  background: rgba(255, 255, 255, 0.05);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.cb-terminal-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.cb-terminal-dot.red { background: #ff5f56; }
.cb-terminal-dot.yellow { background: #ffbd2e; }
.cb-terminal-dot.green { background: #27c93f; }

.cb-terminal-body {
  padding: 20px;
  color: #e2e8f0;
  text-align: left;
}

.cb-terminal-body .prompt { color: #10b981; }
.cb-terminal-body .command { color: #e2e8f0; }
.cb-terminal-body .output { color: #94a3b8; }
.cb-terminal-body .success { color: #10b981; font-weight: 500; }

.cb-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1.5rem;
  padding: 2rem 0;
  max-width: 800px;
  margin: 0 auto;
}

.cb-stat {
  text-align: center;
  padding: 1.5rem;
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.cb-stat:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(59, 130, 246, 0.15);
}

.cb-stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cb-stat-label {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
  margin-top: 0.25rem;
}

.cb-personas {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.cb-persona {
  padding: 1.5rem;
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  border: 1px solid var(--vp-c-divider);
  transition: all 0.3s ease;
}

.cb-persona:hover {
  border-color: #3b82f6;
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(59, 130, 246, 0.1);
}

.cb-persona-icon { font-size: 2rem; margin-bottom: 1rem; }
.cb-persona-title { font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem; }
.cb-persona-desc { font-size: 0.9375rem; color: var(--vp-c-text-2); line-height: 1.6; }

.cb-lang-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin: 2rem 0;
}

.cb-lang-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.875rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.cb-lang-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

@media (max-width: 768px) {
  .cb-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .cb-terminal {
    font-size: 0.8rem;
  }
}
</style>
