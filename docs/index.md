---
layout: home

hero:
  name: CleanBook
  text: 智能书签清理与分类
  tagline: 规则优先，ML 辅助，LLM 可选；默认离线可用的浏览器书签整理工具
  actions:
    - theme: brand
      text: 快速开始
      link: /quickstart_zh
    - theme: alt
      text: 系统架构
      link: /design/system_architecture
    - theme: alt
      text: 开发指南
      link: /guides/development_guide

features:
  - title: 默认离线可用
    details: 不依赖云服务即可完成清理、去重、分类与导出，适合本地批处理和长期维护。
  - title: 配置驱动
    details: 通过 `config.json` 与词表配置调节规则、阈值和目录组织，不必先改代码。
  - title: 渐进增强
    details: 在规则优先基础上叠加 ML、语义分析和可选 OpenAI 兼容 LLM，失败时自动回退。
  - title: 多格式输出
    details: 支持 HTML、Markdown、JSON，兼顾浏览器回导、知识库归档和二次处理。
---

## 项目定位

CleanBook 面向“长期维护浏览器书签”的场景：先完成清理、去重和规范化，再根据规则与模型把链接组织成稳定、可读、可持续演进的分类结构。

## 适合谁

- 想先离线整理书签，再视需要引入 ML / LLM 的个人用户
- 需要统一团队书签分类规则、词表和输出格式的维护者
- 想了解书签处理流水线、分类融合与配置驱动设计的开发者

## 从哪里开始

1. 先看 [快速上手](/quickstart_zh)，完成一次最小运行。
2. 再看 [书签管理最佳实践](/design/bookmark_best_practices_zh)，确定分类规则和整理习惯。
3. 需要理解实现时，继续阅读 [系统架构](/design/system_architecture) 与 [开发指南](/guides/development_guide)。

## 推荐阅读路径

### 我只想把书签整理好

- [快速上手](/quickstart_zh)
- [书签管理最佳实践](/design/bookmark_best_practices_zh)
- [LLM 提示词模板](/llm_prompt_templates)

### 我想理解系统怎么工作

- [设计说明](/DESIGN)
- [系统架构](/design/system_architecture)
- [ML 设计](/design/ml_design_zh)

### 我准备参与开发

- [开发指南](/guides/development_guide)
- [设计说明](/DESIGN)
- [技术报告](/technical_report)

## 核心文档

| 类别 | 页面 | 说明 |
|------|------|------|
| 快速开始 | [快速上手](/quickstart_zh) | 安装、最小示例、常用参数 |
| 使用指南 | [书签管理最佳实践](/design/bookmark_best_practices_zh) | 配置思路、目录组织与日常维护建议 |
| 架构设计 | [设计说明](/DESIGN) / [系统架构](/design/system_architecture) | 流水线、模块边界与分类策略 |
| 开发指南 | [开发指南](/guides/development_guide) | 环境搭建、测试与扩展入口 |
| 参考 | [LLM 提示词模板](/llm_prompt_templates) | 提示词结构与可选接口配置 |
| 归档 | [技术报告](/technical_report) | 历史补充材料与扩展说明 |
