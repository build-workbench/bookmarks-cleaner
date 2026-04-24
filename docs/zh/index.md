---
layout: home
hero:
  name: CleanBook
  text: 离线优先的智能书签清理工具
  tagline: 规则优先 · ML 辅助 · LLM 可选 · 适合开发者与重度书签用户
  image:
    src: /logo.svg
    alt: CleanBook
  actions:
    - theme: brand
      text: 10 分钟上手
      link: /zh/quickstart
    - theme: alt
      text: 查看 GitHub
      link: https://github.com/LessUp/bookmarks-cleaner
features:
  - icon: 🔒
    title: 真正离线
    details: 默认本地处理，不依赖云端服务；你的书签和分类规则不会被上传。
  - icon: ⚙️
    title: 配置驱动
    details: 通过 config.json 和 taxonomy YAML 定义分类规则、阈值和输出行为。
  - icon: 🤖
    title: 规则优先，AI 增强
    details: 先用稳定规则命中，再用 ML 和可选 LLM 提升覆盖率，而不是把全部流程交给黑盒。
  - icon: 📦
    title: 可直接落地
    details: 处理浏览器导出的 HTML 书签，并输出可复用的 HTML、JSON 与报告数据。
---

## 为什么是 CleanBook

CleanBook 适合已经积累了大量浏览器书签、又不想把数据交给在线服务的用户。它的目标不是做一个“云端收藏平台”，而是把现有书签 **快速清理、去重、分类、导出**。

## 最快体验

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

如果你只想走稳定路径：

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

## 适合谁

- **个人用户**：清理历史书签堆积
- **团队维护者**：共享分类规则与 taxonomy
- **开发者**：研究书签处理流水线、规则融合与 CLI 工程化

## 下一步

- [快速开始](/zh/quickstart)
- [安装指南](/zh/guide/installation)
- [配置说明](/zh/reference/config)
- [词表格式](/zh/reference/taxonomy)
