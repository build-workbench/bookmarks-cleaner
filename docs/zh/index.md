---
layout: home
hero:
  name: Bookmarks Cleaner
  text: 离线优先的书签系统工程
  tagline: 规则优先分类、融合推断架构，以及白皮书级技术文档。
  actions:
    - theme: brand
      text: 阅读白皮书
      link: /zh/whitepaper
    - theme: alt
      text: 探索架构
      link: /zh/architecture/pipeline
features:
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
    title: 离线优先
    details: 所有核心功能完全离线运行，数据零上传，隐私绝对掌控
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
    title: 规则引擎
    details: 基于域名模式的确定性分类，可自定义规则，毫秒级响应零延迟
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>
    title: ML 辅助
    details: 可选机器学习增强，支持增量学习与主动学习，模型版本管理
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
    title: LLM 可选
    details: 支持 OpenAI / Ollama 本地模型，按需调用，智能理解书签语义
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
    title: 多浏览器
    details: 原生支持 Chrome、Edge、Firefox、Safari 书签 HTML/JSON 导出格式
  - icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
    title: 多格式报告
    details: HTML 可视化报告、JSON 结构化数据、Markdown 文档三种输出
---

<HeroTerminal />

## 快速上手

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

## 核心架构

<ArchitectureFlow />

## 为什么选择 Bookmarks Cleaner

| 维度 | Bookmarks Cleaner | linkding | Shaarli | 传统脚本 |
|------|-------------------|----------|---------|----------|
| 架构模式 | Pipeline + DI 容器 | 单体 Django | 单体 PHP | 无架构 |
| 离线运行 | 完全离线 | 需自托管 | 需自托管 | 离线 |
| 分类引擎 | 规则 + ML + LLM 融合 | 手动标签 | 手动标签 | 无 |
| 隐私保护 | 本地处理，零上传 | 自托管可控 | 自托管可控 | 本地 |
| 并发处理 | ThreadPoolExecutor | 单线程 | 单线程 | 无 |
| 增量学习 | 支持 | 不支持 | 不支持 | 无 |
| 置信度校准 | Platt / Isotonic | 无 | 无 | 无 |
| 开源协议 | MIT | MIT | Zlib | 不定 |

## 技术深度

<div class="cb-stagger">

- [技术白皮书](/zh/whitepaper) — 项目定位、核心创新点与技术栈全景
- [Pipeline 架构](/zh/architecture/pipeline) — 五阶段处理管道与数据流转
- [融合算法](/zh/algorithms/fusion) — 多分类器加权投票与置信度校准
- [架构决策记录](/zh/adr) — 关键设计决策的技术权衡
- [演进思考](/zh/evolution) — 从 1148 行上帝类到门面模式 + Pipeline 的演进

</div>
