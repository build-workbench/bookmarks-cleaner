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
      text: 系统架构
      link: /zh/design/architecture
    - theme: alt
      text: GitHub
      link: https://github.com/LessUp/bookmarks-cleaner

features:
  - icon: 🚀
    title: 默认离线可用
    details: 不依赖云服务即可完成清理、去重、分类与导出，适合本地批处理和长期维护。规则引擎提供亚毫秒级响应。
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

## 项目定位

CleanBook 面向"长期维护浏览器书签"的场景：先完成清理、去重和规范化，再根据规则与模型把链接组织成稳定、可读、可持续演进的分类结构。

## 适合谁

- **个人用户**: 想先离线整理书签，再视需要引入 ML / LLM 的浏览器重度使用者
- **团队维护者**: 需要统一团队书签分类规则、词表和输出格式的技术负责人
- **开发者**: 想了解书签处理流水线、分类融合与配置驱动设计的开源贡献者

## 从哪里开始

1. 先看 [**快速上手**](/zh/quickstart)，完成一次最小运行
2. 再看 [**书签管理最佳实践**](/zh/guide/best-practices)，确定分类规则和整理习惯
3. 需要理解实现时，继续阅读 [**系统架构**](/zh/design/architecture) 与 [**开发指南**](/zh/guide/development)

## 推荐阅读路径

::: tip 我只想把书签整理好
- [快速上手](/zh/quickstart)
- [书签管理最佳实践](/zh/guide/best-practices)
- [LLM 提示词模板](/zh/reference/llm-templates)
:::

::: tip 我想理解系统怎么工作
- [设计概述](/zh/design/overview)
- [系统架构](/zh/design/architecture)
- [ML 设计](/zh/design/ml-design)
:::

::: tip 我准备参与开发
- [开发指南](/zh/guide/development)
- [设计概述](/zh/design/overview)
- [技术报告](/zh/advanced/technical-report)
:::

## 核心文档

| 类别 | 页面 | 说明 |
|------|------|------|
| 快速开始 | [快速上手](/zh/quickstart) | 安装、最小示例、常用参数 |
| 使用指南 | [书签管理最佳实践](/zh/guide/best-practices) | 配置思路、目录组织与日常维护建议 |
| 架构设计 | [设计概述](/zh/design/overview) / [系统架构](/zh/design/architecture) | 流水线、模块边界与分类策略 |
| 开发指南 | [开发指南](/zh/guide/development) | 环境搭建、测试与扩展入口 |
| 参考 | [LLM 提示词模板](/zh/reference/llm-templates) | 提示词结构与可选接口配置 |
| 归档 | [技术报告](/zh/advanced/technical-report) | 历史补充材料与扩展说明 |

---

<footer style="text-align: center; margin-top: 4rem; padding: 2rem 0; border-top: 1px solid var(--vp-c-divider);">
  <p>基于 MIT 许可发布 · Copyright © 2025-2026 LessUp</p>
  <p style="margin-top: 0.5rem;">
    <a href="/en/">English</a> · <a href="https://github.com/LessUp/bookmarks-cleaner">GitHub</a> · <a href="https://github.com/LessUp/bookmarks-cleaner/releases">Releases</a>
  </p>
</footer>
