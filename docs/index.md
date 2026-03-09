---
layout: home

hero:
  name: CleanBook
  text: 智能书签清理与分类
  tagline: 规则 + ML + 可选 LLM · 默认离线可用 · Python 3.10+
  actions:
    - theme: brand
      text: 快速上手
      link: /quickstart_zh
    - theme: alt
      text: 系统架构
      link: /design/system_architecture
    - theme: alt
      text: GitHub
      link: https://github.com/LessUp/bookmarks-cleaner

features:
  - title: 🎯 规则优先 · 配置驱动
    details: 基于受控词表（Controlled Vocabulary）与分面分类（Faceted Classification），在 config.json 和 taxonomy/*.yaml 中定义规则与权重，无需改代码即可定制。
  - title: 🤖 ML 辅助 · 自动沉淀
    details: 高置信度样本自动沉淀为训练集，轻量 scikit-learn 模型渐进增强分类准确率；--train 一键训练。
  - title: 💡 LLM 可选 · 自动降级
    details: 支持 OpenAI 兼容接口（GPT-4o-mini 等），含二次聚类组织器；未配置或调用失败时自动回退到离线路径。
  - title: 📦 多格式导出
    details: 输出 HTML（Netscape 格式可直接导入浏览器）、Markdown、JSON；分类结构最多两级，结果简洁可读。
  - title: 🧹 统一 Emoji 清理
    details: 读入 → 标准化 → 导出三处兜底清理标题 emoji 前缀，避免跨浏览器导出时叠加重复。
  - title: 🔗 去重 · 健康巡检
    details: 快速去重 + 高级去重全时开启，合并跨浏览器导出更稳；可选 --health-check 链接可达性巡检。
---

## 处理流水线

```
浏览器书签 HTML
    │
    ▼
┌─────────────────────────────────────────────┐
│  BookmarkProcessor                          │
│  加载 → 快速去重 → 高级去重 → emoji 清理    │
├─────────────────────────────────────────────┤
│  AIBookmarkClassifier                       │
│  ┌──────┐ ┌────┐ ┌──────┐ ┌────┐ ┌─────┐  │
│  │ 规则 │→│ ML │→│ 语义 │→│画像│→│ LLM │  │
│  └──────┘ └────┘ └──────┘ └────┘ └─────┘  │
│           加权投票 → 融合置信度              │
├─────────────────────────────────────────────┤
│  TaxonomyStandardizer                       │
│  受控词表映射 → subject + resource_type     │
├─────────────────────────────────────────────┤
│  DataExporter                               │
│  HTML · Markdown · JSON                     │
└─────────────────────────────────────────────┘
```

## 最小示例

```powershell
# 安装（推荐 pipx）
pipx install .

# 处理书签
cleanbook -i examples/demo_bookmarks.html -o output

# 批处理 + 训练 ML
cleanbook -i "tests/input/*.html" --train

# 交互向导
cleanbook-wizard
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| CLI | Click + Rich（交互向导） |
| 解析 | BeautifulSoup4 + lxml |
| ML | scikit-learn · jieba · langdetect |
| LLM | OpenAI 兼容接口（可选） |
| 导出 | HTML (Netscape) · Markdown · JSON |
| 分类体系 | 受控词表 + 分面分类（YAML 配置） |
| 质量 | pytest · flake8 · mypy |
