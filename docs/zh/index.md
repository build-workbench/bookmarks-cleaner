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

CleanBook 适合已经积累了大量浏览器书签、又不想把数据交给在线服务的用户。它的目标不是做一个”云端收藏平台”，而是把现有书签 **快速清理、去重、分类、导出**。

**适合人群：**
- 📚 积累了数年书签的开发者（1000+条）
- 🔒 注重隐私，希望完全离线处理的用户
- ⚡ 需要共享分类规则的团队
- 🛠️ 研究书签处理流水线的研究者

## 实际效果

**使用前：**
- 3,500+ 条杂乱书签，积累5年
- 数百个重复链接和失效链接
- 没有一致的分类标准
- 浏览器卡顿，体验极差

**使用后：**
- 精简至 2,800 条唯一有效书签
- 使用自定义规则分类到 20+ 个类别
- 100% 离线处理，数据不离开本地
- 几分钟内即可导出，重新导入浏览器

## 它是怎么工作的

1. 从浏览器导出书签 HTML
2. 运行 `cleanbook -i bookmarks.html -o output/`
3. 先走稳定规则，再按需叠加 ML 和可选 LLM
4. 输出适合继续整理、导入和分析的结果文件

## 你会得到什么

- **清理后的 HTML**：方便再次导入浏览器
- **JSON 数据**：便于二次分析和自动化处理
- **报告型输出**：适合检查分类结果和后续人工微调

<div class="cb-stats">
  <div class="cb-stat">
    <span class="cb-stat-value">3500+</span>
    <span class="cb-stat-label">书签处理量</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">100%</span>
    <span class="cb-stat-label">离线处理</span>
  </div>
  <div class="cb-stat">
    <span class="cb-stat-value">20+</span>
    <span class="cb-stat-label">自定义分类</span>
  </div>
</div>

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

## 为什么它值得长期保留

- **真正离线**：默认不依赖云端账号或托管服务
- **规则优先**：稳定、可解释、可复现
- **扩展有边界**：ML 和 LLM 是增强层，不会吞掉整个处理流程

## 下一步

- [快速开始](/zh/quickstart)
- [安装指南](/zh/guide/installation)
- [配置说明](/zh/reference/config)
- [词表格式](/zh/reference/taxonomy)
