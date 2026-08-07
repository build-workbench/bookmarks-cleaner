# CleanBook

**规则优先 · ML 辅助 · LLM 可选 · 离线优先**

离线书签自动分类引擎。输入浏览器导出的 HTML，一条命令完成去重、分类、组织、导出。全程留在本机，不依赖云服务。

## 它解决什么问题

浏览器书签积累到几百上千条后，手动整理几乎不可能。现有工具要么是纯手动 tag（buku），要么把数据推到云端（Raindrop.io）。CleanBook 选择第三条路：**规则引擎自动分类，可选 ML/LLM 增强，全程离线。**

## 快速开始

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

只走规则路径（不装 ML 依赖）：

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

从源码运行：

```bash
git clone https://github.com/AICL-Lab/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -e ".[dev]"
cleanbook -i examples/sample_bookmarks.html -o output/
```

安装可选能力：

```bash
pip install -e ".[ml]"     # 机器学习分类
pip install -e ".[llm]"    # LLM 分类（需配置 API Key）
```

## 分类效果

使用 `examples/sample_bookmarks.html`（78 条书签，覆盖 8 个分类）测试：

```
输入: 78 条书签
去重: 5 条（URL 精确匹配 + 相似度检测）
分类: 73 条，0 错误
耗时: < 1 秒（规则路径）
```

分类分布示例：

| 分类 | 数量 |
|------|------|
| AI | 11 |
| 编程 | 13 |
| 学习 | 12 |
| 生物 | 5 |
| 社区 | 4 |
| 资讯 | 5 |
| 娱乐 | 6 |
| 其他 | 7 |
| 未分类 | 10 |

## 分类架构

三路融合：规则引擎 -> ML -> LLM，各自独立产出结果，由 FusionEngine 加权融合。

```
BookmarkProcessor (processor.py)
  ├── BookmarkLoader          HTML 书签加载
  ├── BookmarkDeduplicator    两阶段去重（URL 精确 + 相似度）
  ├── BookmarkClassifier
  │     ├── RuleEngine        规则优先，预编译正则
  │     ├── MLClassifier      可选，scikit-learn + jieba 分词
  │     └── LLMClassifier     可选，OpenAI 兼容 API
  │     └── FusionEngine      加权融合，置信度阈值
  ├── OrganizationPipeline    subject/resource_type 两级组织
  └── DataExporter            HTML / JSON / Markdown 导出
```

规则引擎在启动时把所有 keyword 编译为正则，按 category 分桶匹配。去重器先按域名预分组，仅在桶内做 O(m²) 相似度比较，避免全局 O(n²)。

## 配置

默认配置 `config.json` 提供通用分类体系（AI/编程/生物/学习/社区/资讯/娱乐/其他）。个人规则可通过 `-c` 参数加载：

```bash
cleanbook -i bookmarks.html -c config.local.json -o output/
```

`config.local.json` 不入库（已在 `.gitignore` 中），可自行创建并添加个人化分类规则。配置格式参考默认 `config.json`。

## 开发

```bash
pytest -q tests/test_runtime_paths.py   # 快速路径验证
pytest -q                                # 全量测试
```

项目约定详见 `AGENTS.md`。
