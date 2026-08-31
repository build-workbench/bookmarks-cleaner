# CleanBook

**规则优先 · LLM 可选 · 离线优先**

离线书签自动分类引擎。输入浏览器导出的 HTML，一条命令完成去重、分类、组织、导出。全程留在本机，不依赖云服务。

## 它解决什么问题

浏览器书签积累到几百上千条后，手动整理几乎不可能。现有工具要么是纯手动 tag（buku），要么把数据推到云端（Raindrop.io）。CleanBook 选择第三条路：**规则引擎自动分类，可选 LLM 增强，全程离线。**

## 快速开始

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

从源码运行：

```bash
git clone https://github.com/vibe-knight/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -e ".[dev]"
cleanbook -i examples/sample_bookmarks.html -o output/
```

安装可选能力：

```bash
pip install -e ".[llm]"    # LLM 分类（需配置 API Key）
```

## 分类效果

使用 `examples/sample_bookmarks.html`（80 条书签，覆盖 8 个分类）测试：

```
输入: 80 条书签
去重: 2 条（URL 精确匹配 + 规范化匹配）
分类: 76 条，0 错误
耗时: < 1 秒（规则路径）
```

分类分布示例（按主分类合并）：

| 主分类 | 数量 |
|--------|------|
| 学习 | 17 |
| 编程 | 17 |
| AI | 11 |
| 生物 | 6 |
| 社区 | 5 |
| 资讯 | 5 |
| 娱乐 | 6 |
| 其他 | 8 |
| 未分类 | 1 |

## 分类架构

两级级联：规则引擎给出确定性主分类，LLM（可选）在规则未命中时兜底、命中时补充子分类。

```
BookmarkProcessor (processor.py)
  ├── BookmarkLoader          HTML 书签加载
  ├── BookmarkDeduplicator    两阶段去重（URL 精确 + 相似度）
  ├── BookmarkClassifier
  │     ├── RuleEngine        规则优先，预编译正则
  │     └── LLMClassifier     可选，OpenAI 兼容 API
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

配置节说明：

| 配置节 | 作用 |
|--------|------|
| `category_rules` / `priority_rules` | 分类规则（match 域名/标题/URL，keywords + weight） |
| `ai_settings` | `confidence_threshold` 分类阈值、`cache_size` 缓存大小、`url_analysis_weight` URL 分析权重、`merge_top_ratio` 主类合并占比 |
| `title_cleaning_rules` | 标题清理：站点前缀/后缀移除与字符替换 |
| `llm` | LLM 分类开关与 OpenAI 兼容 API 参数（默认关闭） |
| `taxonomy` | 受控词表路径（subjects / resource_types） |

## 开发

```bash
pytest -q tests/test_runtime_paths.py   # 快速路径验证
pytest -q                                # 全量测试
```

项目约定详见 `AGENTS.md`。
