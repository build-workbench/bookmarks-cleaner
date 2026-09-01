# CleanBook

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#环境要求) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Version 4.0.0](https://img.shields.io/badge/version-4.0.0-orange)](#)

**规则优先 · LLM 可选 · 离线优先**

离线书签自动分类引擎。输入浏览器导出的 HTML，一条命令完成去重、分类、组织、导出。默认全程本地运行，不上传任何数据。

## 它解决什么问题

浏览器书签积累到几百上千条后，手动整理成本极高。现有工具要么是纯手动 tag（如 buku），要么把数据托管到云端（如 Raindrop.io）。CleanBook 选择第三条路：**规则引擎确定性分类为主，LLM 仅在未命中时兜底 / 命中时补充子分类，全程可离线。**

## 环境要求

- Python >= 3.10
- 依赖：`beautifulsoup4` / `lxml` / `pyyaml` / `chardet`（`pip install -e .` 自动安装）
- 可选：`requests`（仅 `llm` 能力需要）

## 安装

```bash
# 方式一：已发布版本（若使用 PyPI）
pipx install cleanbook

# 方式二：从源码安装（推荐，始终可用）
git clone https://github.com/vibe-knight/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -e .            # 基础能力
pip install -e ".[dev]"     # 含 pytest，用于开发/验证
pip install -e ".[llm]"     # 可选：启用 LLM 分类
```

> `pip` / `pipx` / `uv pip` 均可，包名均为 `cleanbook`（见 `pyproject.toml:6`）。

验证安装：

```bash
cleanbook --version
cleanbook --health-check
# 等价入口
python main.py --health-check
```

## 快速开始

### 1. 导出书签 HTML

- Chrome / Edge：`书签管理器 → 右上角 ⋮ → 导出书签`
- Firefox：`书签 → 管理书签 → 导入和备份 → 导出书签到 HTML`

### 2. 运行分类

```bash
# 基础用法
cleanbook -i bookmarks.html -o output/

# 使用仓库自带示例（78 条，见下文“分类效果”）
cleanbook -i examples/sample_bookmarks.html -o output/
python main.py -i examples/sample_bookmarks.html -o output/
```

### 3. 查看产物

`output/` 下生成 3 个带时间戳的文件（`exporter.py:227`）：

```
output/bookmarks_20250101_120000.html      # 可直接导入回浏览器
output/bookmarks_20250101_120000.json      # 结构化数据 + statistics
output/bookmarks_20250101_120000.markdown  # 分类报告，含处理统计与目录
```

支持一次处理多文件与 glob：

```bash
cleanbook -i "bookmarks/*.html" -o output/
cleanbook -i a.html b.html -o output/ --workers 8
```

## 分类效果

以 `examples/sample_bookmarks.html` 为例（`loader.py:38` 统计口径）：

```
输入: 78 条书签（<a href> 总数）
去重: 2 条（见“去重策略”）
分类: 76 条，0 错误，平均置信度 ~0.92
耗时: < 1 秒（规则路径，4 线程，见 processor.py:137）
```

按主分类合并后的分布（对 `processor.py` 返回的 `categories_found` 按 `/` 前主类合并；最终导出经 `organizer.py` + `taxonomy.py:80` 标准化，`AI` → `人工智能` 等，见 `cleanbook/resources/taxonomy/subjects.yaml:5`）：

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

> 子分类在 HTML / Markdown 中以二级文件夹呈现（如 `AI/模型平台`、`编程/代码仓库`）。未分类仅当规则与 LLM 均未命中、或置信度低于阈值时产生（`classifier.py:187`）。

更多评估：

```bash
# 使用标注集评估准确率（按主分类对比，见 cli.py:127 run_eval）
cleanbook --eval examples/labeled_bookmarks.json
cleanbook --eval examples/labeled_bookmarks.json -c config.local.json
```

## 分类架构

两级级联：**规则命中即采用规则主分类，LLM 仅补充子分类/facets；规则未命中才由 LLM 兜底**（`classifier.py:155 _cascade_fuse`）。

```
BookmarkProcessor (processor.py:22)
  ├── BookmarkLoader              HTML 解析 + title 清洗 (loader.py + text_utils.py)
  │     └── TextCleaner           title_cleaning_rules: prefixes/suffixes/replacements
  ├── BookmarkDeduplicator        域名分桶 + 桶内 4 策略去重 (deduplicator.py:23)
  │     ├── 精确 URL 匹配
  │     ├── 规范化 URL 匹配（去 tracking 参数/尾斜杠，容忍 http/https、www 差异，见 deduplicator.py:120）
  │     ├── 内容相似度（同域 + 标题≥0.95 且 URL≥0.7，AND 语义）
  │     └── 标题相似度（同域 + 标题≥0.95）
  ├── BookmarkClassifier          规则优先 + LLM 可选 (classifier.py:23)
  │     ├── RuleEngine            预编译正则，按 category 分桶匹配 (rules.py:50)
  │     │     └── URLAnalyzer     辅助 URL 形态/站点类型提示 (rules.py:31)
  │     ├── LLMClassifier         OpenAI 兼容 API，默认关闭 (llm.py)
  │     └── CacheManager          LRU：特征缓存 + 分类结果缓存 (cache.py，见 classifier.py:55)
  ├── TaxonomyService             受控词表标准化 subjects/resource_types (taxonomy.py:18)
  │     └── 例：AI → 人工智能、AI/模型平台 → 人工智能/code_repository（见 taxonomy/subjects.yaml:5）
  ├── OrganizationPipeline        subject/resource_type 两级组织与排序 (organizer.py:28)
  └── DataExporter                HTML / JSON / Markdown 导出 (exporter.py:15)
```

关键优化：

- 去重按域名预分组，仅桶内 `O(m²)` 比较，避免全局 `O(n²)`（`deduplicator.py:30`）。
- 规则引擎启动时将 `keywords` 编译为正则，按 `category` 分桶匹配（`rules.py:50`）。
- 分类结果与特征分别做 LRU 缓存（`classifier.py:55`），`cache_size` 来自 `ai_settings`。

## 配置

默认配置打包在 `cleanbook/resources/config.json`（`config.py:23 _packaged_path`），pip 安装后无需在仓库根目录创建 `config.json`。个人化覆盖通过 `-c` 指定：

```bash
cleanbook -i bookmarks.html -c config.local.json -o output/
```

`config.local.json` 已在 `.gitignore:18` 中忽略，可自行创建，格式与默认配置一致。

### 配置节

| 配置节 | 作用 | 备注 |
|--------|------|------|
| `category_rules` / `priority_rules` | 分类规则（`match` 主要为 `domain`/`title`/`url_ends_with`，代码还支持 `url`/`path`/`content_type`；`keywords + weight`，支持 `must_not_contain` / `match_all_keywords_in`） | `processing_order` 决定优先级，先 `priority_rules` 后 `category_rules` |
| `category_order` | 导出时的主分类顺序 | 与 `resources/config.json:60` 一致 |
| `processing_order` | 规则处理顺序 | 默认 `["priority_rules", "category_rules"]` |
| `ai_settings` | `confidence_threshold` 分类阈值（配置默认 0.4，缺省时代码回退 0.7 见 `classifier.py:134`）、`cache_size` 缓存大小、`url_analysis_weight` URL 分析权重、`merge_top_ratio` 主类合并占比 | 低于阈值的结果回退为 `未分类`（`classifier.py:187`） |
| `title_cleaning_rules` | 标题清理：`prefixes` 前缀移除、`suffixes` 后缀移除、`replacements` 字符替换 | 由 `TextCleaner` 在加载时应用（`loader.py:28`） |
| `show_confidence_indicator` | 是否在 HTML/Markdown 标题前显示置信度色点 `🟢/🟡/🟠/🔴` | `exporter.py:91`，默认 `false` |
| `llm` | LLM 开关与 OpenAI 兼容 API 参数（`enable/base_url/model/api_key_env/temperature/timeout_seconds` 等） | 默认 `enable: false` |
| `taxonomy` | 受控词表路径 `subjects_file` / `resource_types_file` | 默认 `taxonomy/subjects.yaml` 等（`config.py:69 resolve_taxonomy_path`），支持打包/仓库/绝对路径多级解析 |
| `category_hierarchy` | 可选：主分类 → 子分类标题关键词映射，用于无 LLM 时的兜底子分类 | `classifier.py:221 _determine_subcategory` |

> 修改规则后建议先用小样本验证：`cleanbook -i examples/sample_bookmarks.html --limit 20 -o /tmp/test --log-level DEBUG`

## LLM 可选增强

默认关闭，全程可离线。启用后仅在规则未命中时兜底、命中时补充子分类与 `facets`，不会覆盖规则主分类。

```bash
pip install -e ".[llm]"
export OPENAI_API_KEY="sk-..."
```

在 `config.local.json` 中开启并配置（`base_url`/`model` 均在配置中修改，不读取 `OPENAI_BASE_URL` 环境变量；仅 `api_key` 通过 `api_key_env` 指向环境变量，见 `llm.py:115`）：

```json
{
  "llm": {
    "enable": true,
    "base_url": "https://api.openai.com",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.0,
    "timeout_seconds": 25
  }
}
```

提示：LLM 调用按书签计费，建议先用 `--limit` 小批量试跑，并关注 `output/*.markdown` 中的“分类方法统计”。

## CLI 参考

`cleanbook --help`（`cli.py:30`）完整参数：

| 参数 | 说明 | 默认 |
|------|------|------|
| `-i, --input` | 输入 HTML 文件，支持多文件与 `*`/`?` glob | 必填（除 `--health-check` / `--eval` 外） |
| `-o, --output` | 输出目录 | `output` |
| `-c, --config` | 配置文件路径 | 内置 `cleanbook/resources/config.json` |
| `--health-check` | 运行健康检查（Python/依赖/配置/taxonomy/示例数据） | - |
| `--eval FILE` | 使用标注 JSON 评估分类准确率 | - |
| `--workers` | 并行线程数（上限 32，`processor.py:28`） | `4` |
| `--threshold` | 覆盖配置中的 `confidence_threshold` | 配置值（默认 0.4） |
| `--limit` | 限制处理数量，调试用 | `0`（不限） |
| `--log-level` | `DEBUG/INFO/WARNING/ERROR` | `INFO` |
| `-V, --version` | 显示版本 | - |

日志默认同时输出到控制台与 `logs/cleanbook.log`（当提供 `-i` 时，`cli.py:57`）。

## 开发

```bash
# 健康检查
cleanbook --health-check
python main.py --health-check

# 测试
pytest -q tests/test_runtime_paths.py   # 快速路径验证（配置与 taxonomy 解析）
pytest -q                                # 全量测试

# 端到端自检
cleanbook -i examples/sample_bookmarks.html -o /tmp/cb_out --limit 10 --log-level DEBUG
ls -lh /tmp/cb_out
```

项目约定见 `AGENTS.md`：类型注解贯穿、公共 API 写 docstring、`logging.getLogger(__name__)` 替代 `print`。

目录速览：

```
cleanbook/
  cli.py / processor.py / loader.py / deduplicator.py
  classifier.py / rules.py / url_analyzer.py / llm.py
  organizer.py / exporter.py / taxonomy.py / text_utils.py
  config.py / cache.py / models.py / health.py
  resources/config.json  resources/taxonomy/*.yaml
examples/sample_bookmarks.html  examples/labeled_bookmarks.json
```

## 常见问题

**Q: 重复如何判定？会误删吗？**

`deduplicator.py:23` 仅在同域名桶内判定，4 策略任一命中即视为重复：精确 URL、规范化 URL（去 utm 等 tracking 参数与尾斜杠）、标题+URL 联合相似度、标题相似度。阈值偏保守（标题 0.95），短标题的单字符差异不会被误判为重复。

**Q: 隐私与离线？**

默认不发起任何网络请求。仅当 `llm.enable=true` 且安装 `requests` 时才会调用你配置的 `base_url`。书签标题/URL 仅在该场景下发送给 LLM 网关。

**Q: 中文书签支持？**

支持。分类器会检测 `zh/en`（`classifier.py:253`），标题清理与 taxonomy 均含中英变体。

**Q: 导出的 HTML 如何导回浏览器？**

Chrome/Edge/Firefox 的书签管理器均支持“导入书签”选择 HTML 文件。

## 许可

[MIT](LICENSE) © 2024 shuai

仓库：<https://github.com/vibe-knight/bookmarks-cleaner> · 问题反馈：<https://github.com/vibe-knight/bookmarks-cleaner/issues>
