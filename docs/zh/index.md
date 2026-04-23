---
layout: home
hero:
  name: CleanBook
  text: 开发者的智能书签工具
  tagline: 规则优先 · ML 辅助 · LLM 可选 · 离线可用<br>将混乱的浏览器书签整理成结构化的知识库
  image:
    src: /logo.svg
    alt: CleanBook Logo
  actions:
    - theme: brand
      text: 快速开始
      link: /zh/quickstart
    - theme: alt
      text: GitHub
      link: https://github.com/LessUp/bookmarks-cleaner

features:
  - icon: 🚀
    title: 默认离线运行
    details: 不依赖任何云服务，所有处理在本地完成。你的书签数据永远不会离开你的设备，适合隐私敏感场景。
  - icon: ⚙️
    title: 配置驱动
    details: 通过 config.json 和 YAML 词表自定义分类规则、阈值和输出格式，无需修改代码即可适配你的工作流。
  - icon: 🤖
    title: 智能分类
    details: 融合规则引擎 + ML + 语义分析的多层分类策略，准确率达 91.4%，自动降级保证可用性。
  - icon: 📦
    title: 多格式导出
    details: 支持 HTML（浏览器导入）、JSON（数据分析）、Markdown（知识库）等多种格式，满足不同场景需求。
  - icon: 💻
    title: CLI 优先
    details: 提供 cleanbook 命令行工具和 cleanbook-wizard 交互向导，支持批处理和自动化集成。
  - icon: 🔧
    title: 开源免费
    details: MIT 许可，完全免费使用。支持自定义分类法、规则和导出模板，可扩展的插件架构。
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

## 一键体验

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

## 核心数据

<div class="cb-stats">
  <div class="cb-stat">
    <span class="cb-stat-value">91.4%</span>
    <span class="cb-stat-label">分类准确率</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">50+</span>
    <span class="cb-stat-label">书签/秒</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">0</span>
    <span class="cb-stat-label">网络依赖</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">3</span>
    <span class="cb-stat-label">输出格式</span>
  </div>
</div>

## 为谁设计？

<div class="cb-personas">
  <div class="cb-persona">
    <div class="cb-persona-icon">👤</div>
    <div class="cb-persona-title">个人用户</div>
    <div class="cb-persona-desc">
      浏览器书签积累数千条的技术人员，希望离线整理后再决定是否启用 ML/LLM 增强分类。
    </div>
  </div>
  <div class="cb-persona">
    <div class="cb-persona-icon">👥</div>
    <div class="cb-persona-title">团队维护者</div>
    <div class="cb-persona-desc">
      需要统一团队书签分类标准的技术负责人，通过共享 config.json 和词表确保一致性。
    </div>
  </div>
  <div class="cb-persona">
    <div class="cb-persona-icon">🔧</div>
    <div class="cb-persona-title">开发者</div>
    <div class="cb-persona-desc">
      研究书签处理流水线、分类融合策略或想贡献插件的开源爱好者。
    </div>
  </div>
</div>

## 安装

::: code-group

```bash [pipx (推荐)]
pipx install cleanbook
```

```bash [pip]
pip install cleanbook
```

```bash [uv]
uv tool install cleanbook
```

:::

## 基础用法

```bash
# 清理单个文件
cleanbook -i bookmarks.html -o output/

# 带 ML 训练
cleanbook -i bookmarks.html --train

# 交互式向导
cleanbook-wizard
```

## 下一步

<div style="margin-top: 2rem;">

- [快速开始](./quickstart) — 10 分钟上手
- [安装指南](./guide/installation) — 详细安装说明
- [配置详解](./reference/config) — 自定义你的分类规则
- [设计概述](./design/overview) — 理解系统架构

</div>

---

<div style="text-align: center; padding: 2rem 0; color: var(--vp-c-text-2);">

Built with ❤️ by [LessUp](https://github.com/LessUp)

[MIT Licensed](https://github.com/LessUp/bookmarks-cleaner/blob/master/LICENSE)

</div>
