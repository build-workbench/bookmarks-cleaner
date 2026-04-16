# CleanBook —— 智能书签清理与分类

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
  <a href="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml">
    <img src="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://lessup.github.io/bookmarks-cleaner/">
    <img src="https://img.shields.io/badge/文档-VitePress-blue.svg" alt="Documentation">
  </a>
</p>

<p align="center">
  <b>规则优先 · ML 辅助 · LLM 可选 · 离线可用</b>
</p>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="https://lessup.github.io/bookmarks-cleaner/">文档</a> |
  <a href="https://github.com/LessUp/bookmarks-cleaner/releases">发布</a>
</p>

---

CleanBook 是一款**开源、离线优先**的书签清理与分类工具。它采用混合策略，优先使用规则、辅以机器学习、可选接入大模型，将混乱的浏览器书签整理成结构化的分类库。

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 🚀 **离线优先** | 完整的本地处理流程，无需云服务。适合本地批量处理和长期维护 |
| 🤖 **混合分类** | 规则引擎 + ML 分类器（91.4% 准确率）+ 可选 LLM 兜底。服务不可用时自动降级 |
| ⚙️ **配置驱动** | 通过 JSON/YAML 自定义规则、阈值和词表，无需修改代码 |
| 📦 **多格式导出** | 支持 HTML（Netscape）、Markdown（报告）、JSON（结构化数据） |
| 🔧 **CLI + 向导** | 命令行工具支持自动化，交互式向导提供引导式体验 |
| 🎯 **智能去重** | URL 标准化和多维度相似度检测 |
| 💾 **LRU 缓存** | 智能缓存配合自动淘汰策略，优化性能 |

## 🚀 快速开始

### 安装

```bash
# 使用 pipx（推荐，隔离环境）
pipx install cleanbook

# 使用 pip
pip install cleanbook

# 从源码安装
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install .
```

### 基本用法

```bash
# 处理书签 HTML 文件
cleanbook -i bookmarks.html -o output/

# 交互式向导模式
cleanbook-wizard

# 启用 ML 训练
cleanbook -i bookmarks.html --train

# 健康检查
cleanbook --health-check
```

## 📊 分类流水线

```
HTML 书签
    ↓
┌─────────────────────────────────────────────────────┐
│  1. 规则引擎（快速，0.1ms，权重：0.3）              │
│     域名/标题/URL 模式匹配                          │
├─────────────────────────────────────────────────────┤
│  2. ML 分类器（91.4% 准确率，权重：0.25）           │
│     TF-IDF + 集成模型（RF + LR + 朴素贝叶斯）       │
├─────────────────────────────────────────────────────┤
│  3. 语义分析（权重：0.2）                           │
│     词向量、TF-IDF 相似度                           │
├─────────────────────────────────────────────────────┤
│  4. LLM 分类器（可选，权重：0.15）                  │
│     OpenAI 兼容接口，失败自动回退                   │
└─────────────────────────────────────────────────────┘
    ↓
加权投票融合 → 结构化输出
```

## 🏗️ 架构

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│    输入      │───▶│   处理       │───▶│     输出         │
│  bookmarks   │    │  ┌────────┐  │    │  bookmarks.html  │
│   .html      │    │  │ 解析   │  │    │  bookmarks.json  │
└──────────────┘    │  │ 去重   │  │    │  report.md       │
                    │  │ 分类   │  │    └──────────────────┘
                    │  │ 组织   │  │
                    │  └────────┘  │
                    └──────────────┘
                         ↓
                    ┌──────────────┐
                    │  配置        │
                    │  ├─ 规则     │
                    │  ├─ ML 模型  │
                    │  └─ 词表     │
                    └──────────────┘
```

## 📖 文档

| 资源 | 链接 |
|------|------|
| **首页** | [lessup.github.io/bookmarks-cleaner](https://lessup.github.io/bookmarks-cleaner/) |
| **快速上手** | [/zh/quickstart](https://lessup.github.io/bookmarks-cleaner/zh/quickstart) |
| **最佳实践** | [/zh/guide/best-practices](https://lessup.github.io/bookmarks-cleaner/zh/guide/best-practices) |
| **系统架构** | [/zh/design/architecture](https://lessup.github.io/bookmarks-cleaner/zh/design/architecture) |
| **开发指南** | [/zh/guide/development](https://lessup.github.io/bookmarks-cleaner/zh/guide/development) |
| **API 参考** | [/zh/reference/llm-templates](https://lessup.github.io/bookmarks-cleaner/zh/reference/llm-templates) |

## ⚙️ 配置示例

```json
{
  "category_rules": {
    "技术/人工智能": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["openai.com", "huggingface.co", "arxiv.org"],
          "weight": 15
        },
        {
          "match": "title",
          "keywords": ["GPT", "LLM", "神经网络", "深度学习"],
          "weight": 10
        }
      ]
    }
  },
  "ai_settings": {
    "confidence_threshold": 0.7,
    "cache_size": 10000,
    "max_workers": 4
  },
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

## 🔬 性能基准

| 指标 | 数值 |
|------|------|
| 分类准确率 | 91.4% |
| 处理速度 | ~50 书签/秒 |
| 缓存命中率 | 87-92% |
| 内存占用（基准） | ~45MB |
| 内存占用（1000 书签） | ~125MB |

## 🛠️ 开发

```bash
# 克隆仓库
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行测试
pytest

# 运行覆盖率测试
pytest --cov=src --cov-report=html
```

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。对于重大变更，请先开 Issue 讨论您想要改变的内容。

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/新功能`
3. 提交变更：`git commit -m 'feat: 添加新功能'`
4. 推送到分支：`git push origin feature/新功能`
5. 打开 Pull Request

## 📝 许可

本项目采用 [MIT 许可](LICENSE)。

## 🙏 致谢

- 灵感来源于高效个人知识管理的需求
- 使用 [scikit-learn](https://scikit-learn.org/)、[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)、[Rich](https://github.com/Textualize/rich) 构建

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/LessUp">LessUp</a>
</p>
