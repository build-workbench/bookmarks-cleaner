# CleanBook —— 智能书签清理与分类

<p align="center">
  <a href="https://pypi.org/project/cleanbook/">
    <img src="https://img.shields.io/pypi/v/cleanbook.svg?color=blue&logo=pypi&logoColor=white" alt="PyPI 版本">
  </a>
  <a href="https://pypi.org/project/cleanbook/">
    <img src="https://img.shields.io/pypi/dm/cleanbook.svg?color=brightgreen" alt="PyPI 下载量">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python 3.10+">
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
  </a>
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
- [常见问题](#-常见问题)
- [路线图](#-路线图)
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

### 前置要求

- **Python**: 3.10 或更高版本
- **操作系统**: Linux, macOS, Windows

验证 Python 版本：
```bash
python --version  # 应该 >= 3.10
```

### 安装

```bash
# 使用 pipx（推荐 - 隔离环境）
pipx install cleanbook

# 使用 pip
pip install cleanbook

# 从源码安装（开发）
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -r requirements.txt
pip install -e .
```

### 运行

```bash
# 基本用法 - 处理书签
cleanbook -i bookmarks.html -o output/

# 交互式向导模式
cleanbook-wizard

# 批量处理多个文件
cleanbook -i file1.html file2.html file3.html -o output/

# 自定义置信度阈值（越高越严格）
cleanbook -i bookmarks.html -o output/ --threshold 0.8

# 禁用 ML 以节省内存（仅使用规则）
cleanbook -i bookmarks.html -o output/ --no-ml

# 调试模式，限制处理数量
cleanbook -i bookmarks.html -o output/ --limit 100 --log-level DEBUG

# 健康检查 - 验证所有组件
cleanbook --health-check
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

<details>
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

## ❓ 常见问题

<details>
<summary><b>支持哪些浏览器？</b></summary>

CleanBook 支持从以下浏览器导出的书签：
- **Chrome** / **Edge** / **Brave** / **Opera**（HTML 格式）
- **Firefox**（HTML 格式）
- **Safari**（文件 → 导出 → 书签）

只需将书签导出为 HTML，然后使用 `cleanbook -i bookmarks.html` 处理即可。
</details>

<details>
<summary><b>需要单独下载 ML 模型吗？</b></summary>

**不需要。** 所有 ML 模型都已打包在软件包中。首次运行可能因模型加载到内存而稍慢，但无需单独下载。系统开箱即用，支持离线运行。
</details>

<details>
<summary><b>如何使用 LLM 功能？</b></summary>

LLM 是可选功能。启用方法：

1. 从 OpenAI 或兼容提供商获取 API 密钥
2. 设置环境变量：`export OPENAI_API_KEY="your-key"`
3. 在 `config.json` 中启用：`"llm": { "enable": true, "model": "gpt-4o-mini" }`

如果 LLM 不可用，系统会自动降级到其他分类层。
</details>

<details>
<summary><b>处理大量书签时内存不足怎么办？</b></summary>

尝试以下选项：
- 使用 `--no-ml` 参数禁用 ML 组件（节省约 80MB）
- 减少工作线程：`--workers 2`（默认为 4）
- 分批处理：`--limit 500` 每次处理 500 个
- 关闭其他内存密集型应用

使用 `--no-ml` 后，可以在 100MB 内存以内处理 10,000+ 个书签。
</details>

<details>
<summary><b>分类不够准确，如何改进？</b></summary>

1. **自定义规则** - 在 `config.json` 中添加域名/标题模式匹配
2. **调整阈值** - 降低 `--threshold` 以捕获更多项目，提高以获得更高精度
3. **启用 LLM** - 提供最佳准确度但需要 API 密钥
4. **在您的数据上训练** - 使用 `--train` 参数配合预标注的书签

详细的调优指南请参见[最佳实践](https://lessup.github.io/bookmarks-cleaner/zh/guide/best-practices)。
</details>

<details>
<summary><b>支持增量处理吗？</b></summary>

**部分支持。** 系统缓存特征嵌入以加速重新处理。要实现真正的增量更新（仅处理新书签），您可以：
- 仅将新书签从浏览器导出
- 单独处理它们并合并结果

我们计划在未来的版本中增加完整的增量模式。
</details>

<details>
<summary><b>会修改我的原始书签吗？</b></summary>

**不会。** CleanBook 从不修改您的输入文件。它会在输出目录创建新文件：
- `bookmarks_clean.html` - 整理后的书签，可导入回浏览器
- `bookmarks_data.json` - 结构化数据
- `report.md` - 分类报告

请保留原始导出文件作为备份。
</details>

<details>
<summary><b>可以贡献自定义分类规则吗？</b></summary>

当然可以！查看 `config.json` 的结构并提交包含新规则的 PR。我们欢迎以下热门分类：
- 新兴技术主题（AI 框架、新语言）
- 区域性域名（国家特定资源）
- 专业领域（医疗、法律、金融）

详情请参阅[贡献指南](CONTRIBUTING.md)。
</details>

---

## 🗺️ 路线图

### 短期（未来 3 个月）
- [ ] 增量处理模式（仅新书签）
- [ ] 浏览器扩展，一键导出导入
- [ ] 额外的导出格式（Obsidian、Notion API）
- [ ] GUI 桌面应用（Electron/Tauri）

### 长期愿景
- [ ] 自托管 Web UI
- [ ] 团队/协作书签管理
- [ ] 自定义词表的自动标签
- [ ] 书签归档（保存页面快照）

有功能建议？请[提交 Issue](https://github.com/LessUp/bookmarks-cleaner/issues/new) 或为现有 Issue 投票！

---

## 📚 文档

| 资源 | 链接 |
|----------|------|
| **首页** | [lessup.github.io/bookmarks-cleaner](https://lessup.github.io/bookmarks-cleaner/) |
| **快速上手** | [/zh/quickstart](https://lessup.github.io/bookmarks-cleaner/zh/quickstart) |
| **最佳实践** | [/zh/guide/best-practices](https://lessup.github.io/bookmarks-cleaner/zh/guide/best-practices) |
| **架构设计** | [/zh/design/architecture](https://lessup.github.io/bookmarks-cleaner/zh/design/architecture) |
| **LLM 模板** | [/zh/reference/llm-templates](https://lessup.github.io/bookmarks-cleaner/zh/reference/llm-templates) |
| **更新日志** | [CHANGELOG.md](./CHANGELOG.md) |
| **版本发布** | [GitHub Releases](https://github.com/LessUp/bookmarks-cleaner/releases) |

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

### 社区

- 💬 [GitHub Discussions](https://github.com/LessUp/bookmarks-cleaner/discussions) - 提问、分享想法
- 🐛 [Issue Tracker](https://github.com/LessUp/bookmarks-cleaner/issues) - 报告 Bug、请求功能
- 📧 联系：github@lessup.dev

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
