# CleanBook

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#环境要求) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Version 4.0.0](https://img.shields.io/badge/version-4.0.0-orange)](#)

**规则优先 · LLM 可选 · 离线优先**

浏览器书签积累到上千条后，手动整理成本极高。CleanBook 输入浏览器导出的 HTML，一条命令完成**去重、分类、组织、导出**，全程本地运行、不上传数据。规则引擎确定性分类为主，LLM 仅在规则未命中时兜底、命中时补充子分类，默认关闭。

## 环境要求

- Python >= 3.10
- 依赖（安装时自动处理）：`beautifulsoup4` / `lxml` / `pyyaml` / `chardet`
- 可选：`requests`（仅 LLM 分类需要）

## 安装

```bash
# PyPI 发布版
pipx install cleanbook

# 源码安装（推荐）
git clone https://github.com/vibe-knight/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -e .            # 基础能力
pip install -e ".[dev]"     # 开发/测试（pytest）
pip install -e ".[llm]"     # 可选：启用 LLM 分类
```

验证安装：`cleanbook --version`、`cleanbook --health-check`（等价入口 `python main.py`）。

## 快速开始

1. 在浏览器导出书签 HTML：
   - Chrome / Edge：`书签管理器 → 右上角 ⋮ → 导出书签`
   - Firefox：`书签 → 管理书签 → 导入和备份 → 导出书签到 HTML`

2. 运行分类：

   ```bash
   cleanbook -i bookmarks.html -o output/
   # 或使用仓库自带示例
   cleanbook -i examples/sample_bookmarks.html -o output/
   ```

3. `output/` 下生成 3 个带时间戳的文件：
   - `*.html` — 可直接导入回浏览器
   - `*.json` — 结构化数据 + statistics
   - `*.markdown` — 分类报告（处理统计与目录）

支持多文件与 glob：`cleanbook -i "bookmarks/*.html" -o output/`，可用 `--workers 8` 并行。

### 效果示例

以 `examples/sample_bookmarks.html` 为例：78 条输入 → 去重 2 条 → 76 条分类（其中 1 条未分类），平均置信度约 0.92，规则路径耗时 < 1 秒。导出按主分类/子分类组织为二级结构。

使用标注集评估准确率：

```bash
cleanbook --eval examples/labeled_bookmarks.json
```

## 架构

```
BookmarkProcessor
  ├── BookmarkLoader        解析 HTML + 标题清洗
  ├── BookmarkDeduplicator  按域名分桶，桶内 4 策略去重
  ├── BookmarkClassifier    两级级联：规则优先，LLM 可选兜底
  │     ├── RuleEngine      预编译正则，按分类分桶匹配
  │     ├── LLMClassifier   OpenAI 兼容 API，默认关闭
  │     └── CacheManager    LRU 特征/结果缓存
  ├── TaxonomyService       受控词表标准化（AI → 人工智能）
  ├── OrganizationPipeline  两级组织与排序
  └── DataExporter          HTML / JSON / Markdown 导出
```

关键优化：去重按域名预分组，避免全局 O(n²) 比较；规则预编译为正则并按分类分桶匹配；特征与分类结果均做 LRU 缓存。

## 配置

默认配置打包在包内（`cleanbook/resources/config.json`），无需在仓库根目录创建 `config.json`。个人化覆盖用 `-c` 指定（`config.local.json` 已在 `.gitignore` 中）：

```bash
cleanbook -i bookmarks.html -c config.local.json -o output/
```

常用配置节：

| 配置节 | 作用 |
|--------|------|
| `category_rules` / `priority_rules` | 分类规则（domain / title / URL 匹配 + 关键词权重） |
| `ai_settings` | 置信度阈值、缓存大小、URL 分析权重等 |
| `title_cleaning_rules` | 标题前缀/后缀移除与字符替换 |
| `llm` | LLM 开关与 OpenAI 兼容 API 参数（默认关闭） |
| `taxonomy` | 受控词表路径（subjects / resource_types） |

其余 `category_order`、`processing_order`、`show_confidence_indicator` 等见默认配置。规则处理默认先 `priority_rules` 后 `category_rules`；置信度低于 `ai_settings.confidence_threshold`（默认 0.4）的分类回退为「未分类」。

> 修改规则后建议先小样本验证：`cleanbook -i examples/sample_bookmarks.html --limit 20 -o /tmp/test --log-level DEBUG`

## LLM 可选增强

默认关闭，全程可离线。启用后仅在规则未命中时兜底、命中时补充子分类，不会覆盖规则主分类。

```bash
pip install -e ".[llm]"
export OPENAI_API_KEY="sk-..."
```

在 `config.local.json` 中开启（`base_url` / `model` 均在配置中修改；API key 经 `api_key_env` 指向环境变量）：

```json
{
  "llm": {
    "enable": true,
    "base_url": "https://api.openai.com",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY"
  }
}
```

LLM 按书签计费，建议先用 `--limit` 小批量试跑，并关注 `output/*.markdown` 中的分类方法统计。

## CLI 参考

| 参数 | 说明 | 默认 |
|------|------|------|
| `-i, --input` | 输入 HTML，支持多文件与 glob | 必填 |
| `-o, --output` | 输出目录 | `output` |
| `-c, --config` | 配置文件 | 内置默认配置 |
| `--health-check` | 运行健康检查 | - |
| `--eval FILE` | 用标注 JSON 评估分类准确率 | - |
| `--workers` | 并行线程数（上限 32） | `4` |
| `--threshold` | 覆盖配置中的置信度阈值 | 配置值 |
| `--limit` | 限制处理数量（调试用） | `0` |
| `--log-level` | 日志级别 | `INFO` |
| `-V, --version` | 显示版本 | - |

提供 `-i` 时，日志同时输出到控制台与 `logs/cleanbook.log`。

## 开发

```bash
pytest -q                    # 全量测试
cleanbook --health-check     # 健康检查
```

项目结构与约定见 `AGENTS.md`。

## 常见问题

**去重会误删吗？** 仅在相同域名内判定，4 种策略任一命中即视为重复：精确 URL、规范化 URL（去 tracking 参数等）、标题 + URL 相似度、标题相似度。阈值偏保守（标题 ≥ 0.95），不会因短标题的单字符差异误判。

**隐私与离线？** 默认不发起任何网络请求。仅当 `llm.enable = true` 时，书签标题/URL 才会发送给你配置的 API 网关。

**中文书签支持吗？** 支持。分类器检测中英文，标题清洗与 taxonomy 均含中英变体。

**导出的 HTML 能导回浏览器吗？** 能。Chrome / Edge / Firefox 的书签管理器均支持导入书签 HTML。

## 许可

[MIT](LICENSE) © 2024 shuai

仓库：<https://github.com/vibe-knight/bookmarks-cleaner> · 问题反馈：<https://github.com/vibe-knight/bookmarks-cleaner/issues>
