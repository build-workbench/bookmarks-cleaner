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
    details: 所有核心功能离线运行，数据不离开本地
  - icon: 📏
    title: 规则引擎
    details: 基于域名的智能分类，可自定义规则
  - icon: 🤖
    title: ML 辅助
    details: 可选的机器学习增强，提升分类准确率
  - icon: 🧠
    title: LLM 可选
    details: 支持 OpenAI 等 LLM 增强分类
  - icon: 🔄
    title: 多浏览器
    details: 支持 Chrome、Edge、Firefox、Safari
  - icon: 📊
    title: 多格式报告
    details: HTML、JSON、Markdown 多种输出格式
---

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
