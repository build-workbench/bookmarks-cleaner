---
layout: home
hero:
  name: CleanBook
  text: Smart Bookmark Tool for Developers
  tagline: Rules-first · ML-assisted · LLM-optional · Offline-ready<br>Transform chaotic browser bookmarks into structured knowledge
  image:
    src: /logo.svg
    alt: CleanBook Logo
  actions:
    - theme: brand
      text: Quick Start
      link: /en/quickstart
    - theme: alt
      text: GitHub
      link: https://github.com/LessUp/bookmarks-cleaner

features:
  - icon: 🚀
    title: Offline by Default
    details: No cloud services required. All processing happens locally. Your bookmark data never leaves your device, perfect for privacy-sensitive scenarios.
  - icon: ⚙️
    title: Config-Driven
    details: Customize categories, rules, and output formats via config.json and YAML taxonomies. Adapt to your workflow without touching code.
  - icon: 🤖
    title: Smart Classification
    details: Multi-layer fusion of Rule Engine + ML + Semantic Analysis achieves 91.4% accuracy with automatic fallback for reliability.
  - icon: 📦
    title: Multi-Format Export
    details: Support HTML (browser import), JSON (data analysis), Markdown (knowledge base), and more formats for different use cases.
  - icon: 💻
    title: CLI-First
    details: Provides cleanbook CLI and cleanbook-wizard interactive mode. Perfect for batch processing and automation integration.
  - icon: 🔧
    title: Open Source
    details: MIT licensed and completely free. Extensible plugin architecture with customizable taxonomies, rules, and export templates.
---

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Terminal typing effect
const terminalLines = ref([])
const fullOutput = [
  { text: '$ cleanbook -i bookmarks.html -o output/', type: 'input', delay: 50 },
  { text: '✓ Loaded 1,247 bookmarks', type: 'output', delay: 30 },
  { text: '✓ Removed 23 duplicates (1.8%)', type: 'output', delay: 30 },
  { text: '✓ Classified 1,224 bookmarks with 91.4% accuracy', type: 'output', delay: 30 },
  { text: '✓ Generated bookmarks_clean.html', type: 'success', delay: 30 },
  { text: '✓ Done in 2.34s', type: 'success', delay: 100 },
]

let currentLine = 0
let currentChar = 0
let timeout = null

function typeNext() {
  if (currentLine >= fullOutput.length) {
    setTimeout(() => {
      terminalLines.value = []
      currentLine = 0
      currentChar = 0
      typeNext()
    }, 5000)
    return
  }
  
  const line = fullOutput[currentLine]
  
  if (currentChar === 0) {
    terminalLines.value.push({ text: '', type: line.type })
  }
  
  if (currentChar < line.text.length) {
    terminalLines.value[currentLine].text += line.text[currentChar]
    currentChar++
    timeout = setTimeout(typeNext, line.delay)
  } else {
    currentLine++
    currentChar = 0
    timeout = setTimeout(typeNext, line.type === 'input' ? 300 : 100)
  }
}

onMounted(() => {
  setTimeout(typeNext, 500)
})

onUnmounted(() => {
  if (timeout) clearTimeout(timeout)
})
</script>

## Try It

<div class="cb-terminal">
  <div class="cb-terminal-header">
    <span class="cb-terminal-dot red"></span>
    <span class="cb-terminal-dot yellow"></span>
    <span class="cb-terminal-dot green"></span>
    <span style="margin-left: auto; color: #64748b; font-size: 0.75rem;">bash</span>
  </div>
  <div class="cb-terminal-body">
    <div v-for="(line, i) in terminalLines" :key="i" :class="line.type">
      <template v-if="line.type === 'input'">
        <span class="prompt">$ </span><span class="command">{{ line.text.slice(2) }}</span>
      </template>
      <template v-else-if="line.type === 'success'">
        <span class="success">{{ line.text }}</span>
      </template>
      <template v-else>
        <span class="output">{{ line.text }}</span>
      </template>
    </div>
  </div>
</div>

## At a Glance

<div class="cb-stats">
  <div class="cb-stat">
    <span class="cb-stat-value">91.4%</span>
    <span class="cb-stat-label">Classification Accuracy</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">50+</span>
    <span class="cb-stat-label">Bookmarks/sec</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">0</span>
    <span class="cb-stat-label">Network Required</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">3</span>
    <span class="cb-stat-label">Output Formats</span>
  </div>
</div>

## Who Is It For?

<div class="cb-personas">
  <div class="cb-persona">
    <div class="cb-persona-icon">👤</div>
    <div class="cb-persona-title">Individual Users</div>
    <div class="cb-persona-desc">
      Technical users with thousands of accumulated bookmarks who want offline cleaning before deciding on ML/LLM enhancements.
    </div>
  </div>
  <div class="cb-persona">
    <div class="cb-persona-icon">👥</div>
    <div class="cb-persona-title">Team Maintainers</div>
    <div class="cb-persona-desc">
      Technical leads who need unified team bookmark standards through shared config.json and taxonomy files.
    </div>
  </div>
  <div class="cb-persona">
    <div class="cb-persona-icon">🔧</div>
    <div class="cb-persona-title">Developers</div>
    <div class="cb-persona-desc">
      Open source enthusiasts studying bookmark processing pipelines, classification fusion, or contributing plugins.
    </div>
  </div>
</div>

## Installation

::: code-group

```bash [pipx (recommended)]
pipx install cleanbook
```

```bash [pip]
pip install cleanbook
```

```bash [uv]
uv tool install cleanbook
```

:::

## Quick Start

```bash
# Clean a single file
cleanbook -i bookmarks.html -o output/

# With ML training
cleanbook -i bookmarks.html --train

# Interactive wizard
cleanbook-wizard
```

## Next Steps

<div style="margin-top: 2rem;">

- [Quick Start](/en/quickstart) — Get started in 10 minutes
- [Installation](/en/guide/installation) — Detailed setup instructions
- [Configuration](/en/reference/config) — Customize classification rules
- [Design](/en/design/overview) — Understand system architecture

</div>

---

<div style="text-align: center; padding: 2rem 0; color: var(--vp-c-text-2);">

Built with ❤️ by [LessUp](https://github.com/LessUp)

[MIT Licensed](https://github.com/LessUp/bookmarks-cleaner/blob/master/LICENSE)

</div>
