---
layout: home
hero:
  name: Bookmarks Cleaner
  text: 离线优先的智能书签清理工具
  tagline: 规则优先 · ML 辅助 · LLM 可选
  actions:
    - theme: brand
      text: 安装使用
      link: /zh/guide/installation
features:
  - icon: 🔒
    title: 离线优先
    details: 所有核心功能离线运行，数据不离开本地，隐私安全有保障
  - icon: 📏
    title: 规则引擎
    details: 基于域名的智能分类，可自定义规则，毫秒级响应
  - icon: 🤖
    title: ML 辅助
    details: 可选的机器学习增强，支持增量学习和主动学习
  - icon: 🧠
    title: LLM 可选
    details: 支持 OpenAI、本地 LLM 增强分类，智能理解书签内容
  - icon: 🔄
    title: 多浏览器
    details: 支持 Chrome、Edge、Firefox、Safari 主流浏览器
  - icon: 📊
    title: 多格式报告
    details: HTML、JSON、Markdown 多种输出格式，灵活导出
---

<HeroTerminal />

## 快速上手

安装：

```bash
pipx install cleanbook
```

使用：

```bash
cleanbook -i bookmarks.html -o output/
```

详细指南请参阅 [安装指南](/zh/guide/installation)。

## 核心架构

<ArchitectureFlow />

## 为什么选择 Bookmarks Cleaner

| 特性 | Bookmarks Cleaner | 传统工具 |
|------|-------------------|----------|
| 离线使用 | ✅ 完全离线 | ❌ 需要联网 |
| 智能分类 | ✅ 规则 + ML + LLM | ❌ 手动分类 |
| 数据隐私 | ✅ 本地处理 | ❌ 上传云端 |
| 开源免费 | ✅ MIT 协议 | ❌ 付费订阅 |

## 深入了解

- [Pipeline 架构](/zh/architecture/pipeline) - 了解 5 阶段处理管道
- [融合算法](/zh/algorithms/fusion) - 多分类器加权融合原理
- [性能特性](/zh/performance/concurrency) - 并发处理与缓存优化
