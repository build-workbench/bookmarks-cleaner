# 相关项目研究

这不是一个普通的链接列表，而是一份围绕 Bookmarks Cleaner 关心维度展开的对照页：运行时模型、隐私边界、可扩展性，以及智能分类策略。

## 对比框架

| 项目 | 运行时模型 | 数据边界 | 智能模型 | 运维负担 | 对本项目的启发 |
|------|------------|----------|----------|----------|----------------|
| Bookmarks Cleaner | 本地 CLI | 本地文件不离开设备 | 规则优先的混合融合 | 很低 | 本页要论证的基线 |
| linkding | 自托管 Web 应用 | 用户控制的服务器 | 标签与检索，不强调分类器融合 | 中等 | 对照“自托管所有权”与“本地优先执行”的差异 |
| Shaarli | 轻量自托管 Web 应用 | 用户控制的服务器 | 手工组织为主 | 低到中等 | 对照“轻量书签服务”与“自动分类 CLI”的差异 |
| 浏览器原生导出 | 浏览器功能，不构成系统 | 完全本地 | 无智能层 | 很低 | 作为下界：只解决导出，不解决组织 |

## 邻近书签系统

### linkding

- **仓库**: [sissbruecker/linkding](https://github.com/sissbruecker/linkding)
- **为什么值得研究**：它很好地回答了“如何自托管并长期保存书签”，但产品形态与本项目不同。
- **核心差异**：linkding 把书签管理塑造成一个长期在线服务；Bookmarks Cleaner 把它当作一次次本地处理任务。

### Shaarli

- **仓库**: [shaarli/Shaarli](https://github.com/shaarli/Shaarli)
- **为什么值得研究**：它展示了手工策展与轻量部署在个人书签工具中的上限。
- **核心差异**：Shaarli 优化的是持续存储与轻量托管，而不是自动分类或系统级白皮书表达。

## 支撑性技术栈

### scikit-learn

- **仓库**: [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn)
- **在本项目中的位置**：代表可在本地执行、且足够成熟的经典 ML 分类能力底座。

### Sentence Transformers

- **仓库**: [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers)
- **在本项目中的位置**：让语义相似度与 embedding 相关增强能够被纳入本地运行时。

### Ollama

- **仓库**: [ollama/ollama](https://github.com/ollama/ollama)
- **在本项目中的位置**：说明可选 LLM 支持如何在用户选择本地模型宿主时，仍与本地优先边界兼容。

## 解释

最值得记住的对比，不是“哪个工具功能更多”，而是“每个工具接受了什么样的问题形态”：

- 自托管书签系统优化的是长期访问与共享；
- 浏览器原生导出优化的是可迁移性；
- Bookmarks Cleaner 优化的是一次次本地清理、分类与导出，同时保持明确的架构边界。
