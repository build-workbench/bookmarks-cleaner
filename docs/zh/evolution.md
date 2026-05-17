# 演进思考

> "软件架构不是设计出来的，而是演化出来的。" —— *Martin Fowler*

本文档记录 Bookmarks Cleaner 从一个粗糙的原型脚本演化为一个具备工程化架构的 CLI 工具的思考过程。

## 阶段一：原型脚本（~200 行）

**时间**: 2024 年末

最初的动机很简单：清理 Chrome 导出的 bookmarks.html，删除重复链接，按域名简单分组。

```python
# 最初的代码大致是这样
from bs4 import BeautifulSoup
import re

with open('bookmarks.html') as f:
    soup = BeautifulSoup(f, 'html.parser')

links = [(a['href'], a.text) for a in soup.find_all('a')]
unique = list(set(links))  # 简单粗暴的去重
# ... 按域名分组 ...
```

**当时的假设**：
- 这是个一次性脚本
- 不需要配置
- 分类只需要按域名前缀判断

**很快发现的问题**：
- `list(set(links))` 只能做精确 URL 去重，无法处理 `?utm_source=...` 等查询参数差异
- 按域名分类太粗糙，无法区分同一域名下的不同内容（如 GitHub 的 repo vs issue）
- 没有错误处理，一个解析异常就导致整个脚本崩溃

## 阶段二：工具化（~600 行）

**时间**: 2025 年初

将脚本工具化，加入了：
- 命令行参数解析（`argparse`）
- 基本的日志记录
- 配置文件支持（JSON）
- 更智能的去重（忽略常见追踪参数）
- 简单的规则匹配分类

**架构特征**：
- 仍然是单文件
- 函数式编程风格
- 全局配置字典到处传递

**产生的新问题**：
- 函数间通过全局状态耦合，测试困难
- 添加新分类方法需要修改多处代码
- 性能瓶颈：逐个处理书签，无法利用多核

## 阶段三：上帝类（~1,148 行）

**时间**: 2025 年 2 月

为了整合越来越多的功能，将所有逻辑封装进一个 `BookmarkProcessor` 类。

```python
class BookmarkProcessor:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        self.ml_model = None
        self.llm_client = None
        # ... 几十个属性

    def process(self, input_path, output_dir):
        # 加载 ... 去重 ... 分类 ... 组织 ... 导出 ...
        # 超过 800 行的方法
```

**当时认为的好处**：
- "所有功能都在一个类里，调用方便"
- "使用者只需要 `processor.process()` 一行代码"

**实际付出的代价**：
- 修改任何一个子功能，都需要阅读和理解整个类
- 单元测试几乎不可能：无法单独测试"去重"逻辑，因为它深嵌在 `process()` 方法中
- 添加 LLM 支持时，不得不修改 20+ 处代码
- 新开发者需要一周才能安全地提交 PR

**代码异味指标**：
- 单个类超过 1,000 行
- 单个方法超过 200 行
- 超过 15 个实例属性
- 导入依赖关系呈网状纠缠

## 阶段四：门面 + Pipeline（当前架构）

**时间**: 2025 年 4 月

一次彻底的重构，核心目标：**让改变局部化**。

### 重构策略

采用**逐步替换**（Strangler Fig Pattern），而非大爆炸重写：

1. 先提取独立的 Pipeline 类（Loader、Deduplicator、Classifier 等）
2. 让 `BookmarkProcessor` 暂时调用这些 Pipeline，但保持外部 API 不变
3. 逐步将 `BookmarkProcessor` 中的内联逻辑迁移到 Pipeline
4. 最终 `BookmarkProcessor` 仅剩门面职责

### 重构后的架构

```
BookmarkProcessor (Facade, ~350 lines)
  └── ProcessorContainer (DI, ~50 lines)
      └── BookmarkProcessorCoordinator (Coordination, ~200 lines)
          ├── BookmarkLoader (Loading, ~80 lines)
          ├── DeduplicationPipeline (Deduplication, ~60 lines)
          ├── ClassificationPipeline (Classification, ~120 lines)
          │   ├── RuleEngine
          │   ├── MLClassifier
          │   ├── SemanticAnalyzer
          │   └── LLMClassifier (optional)
          │   └── FusionEngine (Weighted Vote)
          ├── OrganizationPipeline (Organization, ~50 lines)
          └── ExportPipeline (Export, ~80 lines)
```

### 量化收益

| 指标 | 重构前 | 重构后 | 变化 |
|------|--------|--------|------|
| 最大类行数 | 1,148 | 350 | -70% |
| 最大方法行数 | 840 | 45 | -95% |
| 单元测试覆盖率 | 12% | 78% | +66 pts |
| 新功能开发周期 | ~3 天 | ~4 小时 | -94% |
| 回归缺陷率 | 高 | 低 | 显著改善 |

## 阶段五：未来演进方向

### 近期（6 个月内）

- **插件系统**：开放 `IBookmarkClassifier` 协议，允许社区贡献分类器
- **Web UI**：可选的本地 Web 界面，保持核心 CLI 离线运行
- **增量同步**：支持书签的增量处理（仅处理新增/修改项）

### 中期（1 年内）

- **跨语言扩展**：将核心分类逻辑以 WASM 形式编译，支持浏览器扩展
- **分布式推理**：在保持隐私的前提下，利用本地 GPU 加速 LLM 推理

### 长期（2 年+）

- **联邦学习**：在完全本地的前提下，通过差分隐私技术共享分类器改进
- **知识图谱**：构建个人书签知识图谱，支持语义检索和关联推荐

## 教训与反思

1. **过早抽象是罪恶，过晚抽象是灾难**。上帝类阶段的痛苦告诉我们：当类超过 500 行时，就是重构的信号。

2. **门面模式不是万能药**。门面应该薄，如果门面本身开始积累逻辑，说明抽象层级有问题。

3. **测试是重构的安全网**。没有测试覆盖的重构等于走钢丝。我们在重构前先补测试，虽然辛苦，但避免了无数次回滚。

4. **用户 API 稳定性优先**。整个重构过程中，`BookmarkProcessor(config_path=...).process_files(...)` 的调用方式从未改变，这让外部用户无感知地享受到了架构改进。
