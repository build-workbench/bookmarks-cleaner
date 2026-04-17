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

**CleanBook** 是一款开源、离线优先的书签清理与分类工具。它采用混合策略，优先使用规则、辅以机器学习、可选接入大模型，将混乱的浏览器书签整理成结构化的分类库。

> 你的书签留在本地。无需上传云端，没有隐私顾虑。

---

## 📖 目录

- [为什么选择 CleanBook？](#为什么选择-cleanbook)
- [快速开始](#-快速开始)
- [工作原理](#-工作原理)
- [功能特性](#-功能特性)
- [目标用户](#-目标用户)
- [性能指标](#-性能指标)
- [文档](#-文档)
- [开发](#-开发)
- [贡献](#-贡献)

---

## 为什么选择 CleanBook？

| 痛点 | CleanBook 解决方案 |
|---------|-------------------|
| 🔍 **书签堆积如山**，成百上千个却找不到需要的内容 | 智能分类到你定义的目录，准确率达 91.4% |
| ⏱️ **手动整理太耗时**，难以长期坚持 | 全自动批量处理——指定输入，直接获得整理好的结果 |
| 🔒 **担心隐私**对上传到云端的书签管理工具有顾虑 | 100% 离线处理。你的数据永远不会离开本机 |
| ⚙️ **通用工具**不符合个人或团队的工作流 | 配置驱动：通过 JSON/YAML 自定义分类、规则和阈值 |

---

## 🚀 快速开始

### 安装

```bash
# 使用 pipx（推荐 - 隔离环境）
pipx install cleanbook

# 使用 pip
pip install cleanbook

# 从源码安装
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner && pip install .
```

### 运行

```bash
# 处理你的书签文件
cleanbook -i bookmarks.html -o output/

# 交互式向导模式
cleanbook-wizard
```

### 示例输出

```
✓ 从 bookmarks.html 加载了 1,247 个书签
✓ 移除了 23 个重复项 (1.8%)
✓ 分类了 1,224 个书签 (准确率 91.4%)
✓ 已生成：
    output/bookmarks_clean.html    # 导入浏览器
    output/bookmarks_data.json     # 结构化数据
    output/report.md               # 分类报告
✓ 耗时 2.34s
```

---

## 🏗️ 工作原理

```
                    ┌─────────────────────────────────────┐
  bookmarks.html ──▶│  1. 解析与提取                       │
                    │     URL、标题、元数据                │
                    └─────────────┬───────────────────────┘
                                  ▼
                    ┌─────────────────────────────────────┐
                    │  2. 智能去重                         │
                    │     URL 标准化、相似度检测           │
                    └─────────────┬───────────────────────┘
                                  ▼
┌───────────────────┬─────────────────────────────────────┬───────────────────┐
│                   │  3. 多层分类架构                     │                   │
│  高优先级         │     ┌─────────────────────────┐     │                   │
│  ═════════════    │     │ 规则引擎  (30%)         │◀────┤ 域名、关键词      │
│                   │     │ ML 分类器 (25%)         │◀────┤ TF-IDF + 集成模型 │
│  自动             │     │ 语义分析 (20%)          │◀────┤ 词向量            │
│  降级 ────────────┼────▶│ 用户画像 (10%)          │     │                   │
│                   │     │ LLM (15%, 可选)         │◀────┤ OpenAI 兼容 API   │
│                   │     └───────────┬─────────────┘     │   (如已配置)      │
└───────────────────┴─────────────────┼───────────────────┴───────────────────┘
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  4. 加权投票融合                     │
                    │     综合各层结果，计算置信度         │
                    └─────────────┬───────────────────────┘
                                  ▼
                    ┌─────────────────────────────────────┐
                    │  5. 多格式导出                       │
                    │     HTML | JSON | Markdown          │
                    └─────────────────────────────────────┘
```

**核心设计**：每一层都输出置信度评分。如果 ML 或 LLM 不可用，系统自动将权重重新分配给其他层——分类始终能够完成。

---

## ✨ 功能特性

<details open>
<summary><b>🚀 离线优先设计</b></summary>

完整的本地处理流程，无需任何云服务。规则引擎亚毫秒级响应。适用于：
- 隔离网络环境
- 隐私敏感用户
- 大规模批量处理

</details>

<details open>
<summary><b>🤖 混合分类 (91.4% 准确率)</b></summary>

多层架构，自动降级：
| 层级 | 优先级 | 速度 | 兜底方案 |
|------|----------|-------|----------|
| 规则引擎 | 高 | 0.1ms | 永不失败 |
| ML 分类器 | 中 | ~5ms | 规则引擎 |
| 语义分析 | 中 | ~3ms | 规则引擎 |
| LLM (可选) | 低 | ~500ms | 以上全部 |

</details>

<details open>
<summary><b>⚙️ 配置驱动</b></summary>

通过 `config.json` 自定义一切——无需修改代码：

```json
{
  "category_rules": {
    "技术/人工智能": {
      "rules": [
        { "match": "domain", "keywords": ["openai.com", "huggingface.co"], "weight": 15 },
        { "match": "title", "keywords": ["GPT", "LLM", "深度学习"], "weight": 10 }
      ]
    }
  }
}
```

</details>

<details>
<summary><b>📦 多格式导出</b></summary>

| 格式 | 用途 | 浏览器支持 |
|--------|----------|-----------------|
| HTML (Netscape) | 重新导入浏览器 | Chrome、Firefox、Safari、Edge |
| JSON | 数据分析、二次处理 | 通用 |
| Markdown | 知识库、文档 | Notion、Obsidian、GitHub |

</details>

<details>
<summary><b>🎯 智能去重</b></summary>

- URL 标准化（HTTP → HTTPS、去除 www、统一尾部斜杠）
- 多维度相似度检测（SimHash、Levenshtein 距离）
- 合并重复项时保留最完整的元数据

</details>

<details>
<summary><b>💾 性能优化</b></summary>

- LRU 缓存重复操作
- 可配置工作线程的并行处理
- ML 组件懒加载初始化

</details>

---

## 🎯 目标用户

| 用户类型 | 使用场景 | 推荐配置 |
|------|----------|-------------------|
| **个人用户** | 个人书签整理维护 | `pipx install cleanbook`，自定义分类配置 |
| **团队维护者** | 统一团队书签标准 | 共享 config.json + 词表 YAML 文件，CI 流水线 |
| **开发者** | 研究书签处理流水线 | Fork 仓库，探索 `/specs`，扩展分类器插件 |

---

## 🔬 性能指标

```
┌─────────────────────┬────────────┐
│ 指标                │ 数值       │
├─────────────────────┼────────────┤
│ 分类准确率          │ 91.4%      │
│ 处理速度            │ ~50+ /秒   │
│ 缓存命中率          │ 87-92%     │
│ 内存占用（基准）    │ ~45MB      │
│ 内存占用（1K书签）  │ ~125MB     │
└─────────────────────┴────────────┘
```

测试环境：Intel i7-1165G7, Python 3.11, scikit-learn 1.4.2

---

## 📚 文档

| 资源 | 链接 |
|----------|------|
| **首页** | [lessup.github.io/bookmarks-cleaner](https://lessup.github.io/bookmarks-cleaner/) |
| **快速上手** | [/zh/quickstart](https://lessup.github.io/bookmarks-cleaner/zh/quickstart) |
| **最佳实践** | [/zh/guide/best-practices](https://lessup.github.io/bookmarks-cleaner/zh/guide/best-practices) |
| **架构设计** | [/zh/design/architecture](https://lessup.github.io/bookmarks-cleaner/zh/design/architecture) |
| **LLM 模板** | [/zh/reference/llm-templates](https://lessup.github.io/bookmarks-cleaner/zh/reference/llm-templates) |

---

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

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

详见 [开发指南](https://lessup.github.io/bookmarks-cleaner/zh/guide/development)。

---

## 🤝 贡献

欢迎贡献！请阅读我们的[贡献指南](CONTRIBUTING.md)了解详情。

本项目遵循**规范驱动开发（SDD）**。编写代码前，请先查看 `/specs` 目录下的规范文档。完整工作流程请参见 [AGENTS.md](AGENTS.md)。

---

## 📝 许可

本项目采用 [MIT 许可](LICENSE)。

---

## 🙏 致谢

- 灵感来源于高效个人知识管理的需求
- 使用 [scikit-learn](https://scikit-learn.org/)、[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)、[Rich](https://github.com/Textualize/rich) 构建

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/LessUp">LessUp</a>
</p>
