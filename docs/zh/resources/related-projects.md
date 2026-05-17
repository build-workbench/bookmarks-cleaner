# 相关开源项目

本文档列出与 Bookmarks Cleaner 相关的开源项目，供参考和对比。

## 书签管理工具

### linkding

> **GitHub**: [sissbruecker/linkding](https://github.com/sissbruecker/linkding)
> **Star**: 6k+ | **License**: MIT

**特点**：
- 自托管书签管理服务
- 支持标签和分类
- 提供 REST API
- 支持浏览器扩展

**对比**：
| 特性 | linkding | Bookmarks Cleaner |
|------|----------|-------------------|
| 部署方式 | 服务端 | CLI 工具 |
| 数据存储 | 数据库 | 本地文件 |
| 离线使用 | 需要部署 | ✅ 完全离线 |
| ML 分类 | ❌ | ✅ |

### Shaarli

> **GitHub**: [shaarli/Shaarli](https://github.com/shaarli/Shaarli)
> **Star**: 3k+ | **License**: Zlib

**特点**：
- 个人书签管理器
- PHP 实现，轻量级
- 支持插件扩展
- 支持 Markdown 描述

### Browser Bookmark Manager

> **GitHub**: [browser-bookmark-manager](https://github.com/raycast/browser-bookmark-manager)
> **Star**: 500+ | **License**: MIT

**特点**：
- Raycast 扩展
- 快速搜索书签
- 支持多浏览器

## 文本分类工具

### FastText

> **GitHub**: [facebookresearch/fastText](https://github.com/facebookresearch/fastText)
> **Star**: 26k+ | **License**: MIT

**特点**：
- 高效文本分类
- 词向量训练
- 多语言支持

**应用**：Bookmarks Cleaner 的 ML 分类器参考了 FastText 的文本处理方法。

### scikit-learn

> **GitHub**: [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn)
> **Star**: 60k+ | **License**: BSD

**特点**：
- 丰富的机器学习算法
- 文本特征提取
- 模型评估工具

**应用**：Bookmarks Cleaner 使用 scikit-learn 实现 ML 分类器。

## 语义分析工具

### Sentence Transformers

> **GitHub**: [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers)
> **Star**: 15k+ | **License**: Apache 2.0

**特点**：
- 预训练语义模型
- 多语言支持
- 易于微调

**应用**：Bookmarks Cleaner 使用 Sentence Transformers 实现语义分析器。

### spaCy

> **GitHub**: [explosion/spaCy](https://github.com/explosion/spaCy)
> **Star**: 30k+ | **License**: MIT

**特点**：
- 工业级 NLP 库
- 快速文本处理
- 预训练模型

## LLM 工具

### LangChain

> **GitHub**: [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
> **Star**: 90k+ | **License**: MIT

**特点**：
- LLM 应用开发框架
- Prompt 模板管理
- 链式调用

**应用**：Bookmarks Cleaner 的 LLM 集成参考了 LangChain 的设计模式。

### Ollama

> **GitHub**: [ollama/ollama](https://github.com/ollama/ollama)
> **Star**: 80k+ | **License**: MIT

**特点**：
- 本地运行 LLM
- 模型管理
- API 兼容 OpenAI

**应用**：Bookmarks Cleaner 支持通过 Ollama 运行本地 LLM。

## 架构参考

### Clean Architecture

> **GitHub**: [btjung/clean-architecture](https://github.com/btjung/clean-architecture)
> **参考**: Robert C. Martin

**应用**：Bookmarks Cleaner 采用清洁架构原则：
- 依赖注入容器
- Protocol 接口定义
- 分层 Pipeline 设计

### Python Type System

> **文档**: [typing — Support for type hints](https://docs.python.org/3/library/typing.html)

**应用**：Bookmarks Cleaner 使用 Python 类型系统：
- Protocol 结构化子类型
- 泛型和类型注解
- mypy 静态检查

## 性能优化

### cachetools

> **GitHub**: [tkem/cachetools](https://github.com/tkem/cachetools)
> **Star**: 2k+ | **License**: MIT

**应用**：内存缓存实现，支持 LRU/LFU/TTL 淘汰策略。

### joblib

> **GitHub**: [joblib/joblib](https://github.com/joblib/joblib)
> **Star**: 4k+ | **License**: BSD

**应用**：磁盘缓存和并行计算支持。

## 对比总结

| 项目 | 类型 | 离线 | ML | LLM | CLI |
|------|------|------|----|----|-----|
| Bookmarks Cleaner | CLI 工具 | ✅ | ✅ | ✅ | ✅ |
| linkding | Web 服务 | ❌ | ❌ | ❌ | ❌ |
| Shaarli | Web 服务 | ❌ | ❌ | ❌ | ❌ |
| FastText | 库 | ✅ | ✅ | ❌ | ✅ |

## 贡献

如果您发现其他相关项目，欢迎提交 PR 更新此列表。
