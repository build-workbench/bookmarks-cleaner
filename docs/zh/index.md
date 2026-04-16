---
layout: home
hero:
  name: CleanBook
  text: 智能书签清理与分类
  tagline: 规则优先，ML 辅助，LLM 可选；默认离线可用的浏览器书签整理工具
  image:
    src: /logo.svg
    alt: CleanBook Logo
  actions:
    - theme: brand
      text: 快速开始
      link: /zh/quickstart
    - theme: alt
      text: 查看 GitHub
      link: https://github.com/LessUp/bookmarks-cleaner

features:
  - icon: 🚀
    title: 默认离线可用
    details: 不依赖云服务即可完成清理、去重、分类与导出，适合本地批处理和长期维护。规则引擎提供亚毫秒级响应。
    link: /zh/guide/best-practices
  - icon: ⚙️
    title: 配置驱动
    details: 通过 config.json 与词表配置调节规则、阈值和目录组织，不必先改代码。YAML 词表支持受控词表与分面分类。
  - icon: 🤖
    title: 渐进增强
    details: 在规则优先基础上叠加 ML、语义分析和可选 OpenAI 兼容 LLM，失败时自动回退，无需担心服务可用性。
  - icon: 📦
    title: 多格式输出
    details: 支持 HTML、Markdown、JSON 等多种格式导出，兼顾浏览器回导、知识库归档和二次处理需求。
  - icon: 🔧
    title: CLI 优先
    details: 提供 cleanbook 命令行工具和 cleanbook-wizard 交互向导，支持批处理和自动化集成。
  - icon: 📊
    title: 智能分类
    details: 基于域名、标题、URL 多级特征提取，融合规则引擎与机器学习，分类准确率达 91.4%。
---

<script setup>
import HomeHero from '../.vitepress/theme/components/HomeHero.vue'
import TerminalDemo from '../.vitepress/theme/components/TerminalDemo.vue'
import StatsCounter from '../.vitepress/theme/components/StatsCounter.vue'
import PipelineDiagram from '../.vitepress/theme/components/PipelineDiagram.vue'
import ConfigGenerator from '../.vitepress/theme/components/ConfigGenerator.vue'

const terminalLines = [
  { type: 'input', content: 'cleanbook -i bookmarks.html -o output/', delay: 500 },
  { type: 'output', content: '✓ Loaded 1,247 bookmarks from bookmarks.html', delay: 300 },
  { type: 'output', content: '✓ Removed 23 duplicates', delay: 200 },
  { type: 'output', content: '✓ Classified 1,224 bookmarks (91.4% accuracy)', delay: 400 },
  { type: 'output', content: '✓ Generated output/bookmarks_clean.html', delay: 200 },
  { type: 'output', content: '✓ Done in 2.34s', delay: 100 },
  { type: 'input', content: 'cleanbook-wizard', delay: 800 },
]

const pipelineSteps = [
  { 
    title: '数据解析', 
    description: '解析 HTML/JSON 格式的书签文件，提取 URL、标题、文件夹结构',
    icon: '📄',
    meta: ['Netscape HTML', 'JSON', 'Chrome/Firefox']
  },
  { 
    title: '智能去重', 
    description: 'URL 规范化与多维度相似度检测，识别重复和低质量链接',
    icon: '🔍',
    meta: ['URL Norm', 'SimHash', 'Levenshtein']
  },
  { 
    title: '多层级分类', 
    description: '规则引擎 + ML + 语义分析 + LLM 融合分类',
    icon: '🤖',
    meta: ['91.4% Acc', 'Fusion Voting', 'Auto-Fallback']
  },
  { 
    title: '输出生成', 
    description: '生成整理后的书签文件和统计报告',
    icon: '📦',
    meta: ['HTML', 'Markdown', 'JSON']
  },
]
</script>

<HomeHero
  :version="'2.0.0'"
  :statusText="'稳定版'"
  :subtitle="'智能书签清理与分类'"
  :description="'规则优先，ML 辅助，LLM 可选；默认离线可用的浏览器书签整理工具'"
  :actions="[
    { text: '快速开始 →', link: '/zh/quickstart', theme: 'brand' },
    { text: 'GitHub', link: 'https://github.com/LessUp/bookmarks-cleaner', theme: 'alt' }
  ]"
/>

## 为什么选择 CleanBook？

<StatsCounter
  :stats="[
    { value: 91.4, suffix: '%', label: '分类准确率', description: '在 10000+ 书签样本上测试' },
    { value: 50, suffix: '+', label: '书签/秒', description: '单核处理速度' },
    { value: 0, suffix: '', label: '网络依赖', description: '默认离线运行' },
    { value: 3, suffix: '', label: '输出格式', description: 'HTML / JSON / Markdown' },
  ]"
/>

## 一键体验

<TerminalDemo
  :lines="terminalLines"
  :title="'cleanbook — bash'"
  :prompt="'$'"
/>

## 处理流水线

<PipelineDiagram
  :steps="pipelineSteps"
/>

## 核心特性

### 🚀 默认离线可用

CleanBook 的核心设计理念是"离线优先"。**不依赖任何云服务**即可完成书签的清理、去重、分类与导出。您的书签数据永远不会离开您的设备。

### ⚙️ 配置驱动设计

所有功能都可通过配置文件调节，无需修改代码：

```json
{
  "category_rules": {
    "技术/AI": {
      "rules": [
        { "match": "domain", "keywords": ["openai.com", "huggingface.co"], "weight": 15 }
      ]
    }
  },
  "ai_settings": {
    "confidence_threshold": 0.7,
    "cache_size": 10000
  }
}
```

### 🤖 渐进式智能

系统采用多层分类策略，自动降级保证可用性：

```
规则引擎 (30%) + ML分类器 (25%) + 语义分析 (20%) + LLM (15%) + 用户画像 (10%)
```

当某一层级不可用时，系统会自动将权重重新分配给其他层级，确保分类质量。

### 📦 多格式导出

支持多种输出格式，满足不同场景需求：

| 格式 | 用途 | 特点 |
|------|------|------|
| HTML | 浏览器导入 | 标准 Netscape 格式，兼容所有浏览器 |
| JSON | 数据分析 | 结构化数据，便于二次处理 |
| Markdown | 知识库 | 适合 Notion/Obsidian 等工具 |

## 开始使用

### 安装

::: code-group

```bash [pipx 推荐]
pipx install cleanbook
```

```bash [pip]
pip install cleanbook
```

```bash [源码]
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner && pip install .
```

:::

### 首次运行

```bash
# 基础清理
cleanbook -i bookmarks.html -o output/

# 带 ML 训练
cleanbook -i bookmarks.html --train

# 交互式向导
cleanbook-wizard
```

## 项目定位

CleanBook 面向"长期维护浏览器书签"的场景：

- **个人用户**: 想先离线整理书签，再视需要引入 ML / LLM 的浏览器重度使用者
- **团队维护者**: 需要统一团队书签分类规则、词表和输出格式的技术负责人
- **开发者**: 想了解书签处理流水线、分类融合与配置驱动设计的开源贡献者

## 推荐学习路径

### 我只想把书签整理好
1. [快速上手](/zh/quickstart) - 安装和基本使用
2. [书签管理最佳实践](/zh/guide/best-practices) - 分类策略和整理习惯
3. [LLM 提示词模板](/zh/reference/llm-templates) - 优化分类质量

### 我想理解系统怎么工作
1. [设计概述](/zh/design/overview) - 整体架构理念
2. [系统架构](/zh/design/architecture) - 模块设计和数据流
3. [ML 设计](/zh/design/ml-design) - 分类算法和模型

### 我准备参与开发
1. [开发指南](/zh/guide/development) - 环境搭建和贡献规范
2. [设计概述](/zh/design/overview) - 理解核心设计决策
3. [技术报告](/zh/advanced/technical-report) - 深入技术细节

---

<p align="center" style="margin-top: 4rem;">
  <a href="https://github.com/LessUp/bookmarks-cleaner" target="_blank">
    <img src="https://img.shields.io/github/stars/LessUp/bookmarks-cleaner?style=social" alt="GitHub Stars">
  </a>
</p>

<p align="center" style="color: var(--vp-c-text-3); margin-top: 1rem;">
  Made with ❤️ by <a href="https://github.com/LessUp">LessUp</a>
</p>
