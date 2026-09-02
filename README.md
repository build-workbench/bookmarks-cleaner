# CleanBook

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#环境要求) [![Version 4.0.0](https://img.shields.io/badge/version-4.0.0-orange)](#)

**规则优先 · LLM 可选 · 离线优先**

浏览器书签积累到上千条后，手动整理成本极高。CleanBook 输入浏览器导出的 HTML，一条命令完成**去重、分类、组织、导出**。默认全程本地运行，不上传任何数据。

## 安装

```bash
# PyPI 发布版
pipx install cleanbook

# 源码安装
git clone https://github.com/vibe-knight/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -e .
```

验证安装：`cleanbook --version`、`cleanbook --health-check`。

## 快速开始

**1. 在浏览器导出书签 HTML**

- Chrome / Edge：`书签管理器 → 右上角 ⋮ → 导出书签`
- Firefox：`书签 → 管理书签 → 导入和备份 → 导出书签到 HTML`

**2. 运行分类**

```bash
cleanbook -i bookmarks.html -o output/
# 先用仓库自带示例试跑
cleanbook -i examples/sample_bookmarks.html -o output/
```

**3. 查看产物**

`output/` 下生成 3 个带时间戳的文件：

| 文件 | 内容 |
|------|------|
| `*.html` | 整理后的书签，按主分类/子分类两级组织，可直接导入回浏览器 |
| `*.json` | 结构化数据 + 处理统计 |
| `*.markdown` | 分类报告（目录与统计） |

也支持一次处理多文件与 glob：

```bash
cleanbook -i "bookmarks/*.html" -o output/     # glob
cleanbook -i a.html b.html -o output/ --workers 8   # 多文件 + 并行
```

## 配置

默认配置打包在包内，开箱即用。需要个性化时复制一份再通过 `-c` 指定（`config.local.json` 已在 `.gitignore` 中）：

```bash
cleanbook -i bookmarks.html -c config.local.json -o output/
```

常用配置节：

| 配置节 | 作用 |
|--------|------|
| `category_rules` / `priority_rules` | 分类规则：域名 / 标题 / URL 匹配 + 关键词权重 |
| `ai_settings` | `confidence_threshold` 分类阈值（默认 0.4）等 |
| `title_cleaning_rules` | 标题前后缀移除与字符替换 |
| `llm` | LLM 分类开关与 API 参数（默认关闭） |
| `taxonomy` | 分类词表路径（subjects / resource_types） |

置信度低于 `ai_settings.confidence_threshold` 的结果回退为「未分类」；规则处理默认先 `priority_rules` 后 `category_rules`。

> 修改规则后建议先小样本验证：`cleanbook -i examples/sample_bookmarks.html --limit 20 -o /tmp/test --log-level DEBUG`

## 使用 LLM 分类（可选）

默认关闭，启用后仅在规则未命中时兜底、命中时补充子分类，不会覆盖规则主分类。

```bash
pip install -e ".[llm]"          # PyPI 用户：pip install "cleanbook[llm]"
export OPENAI_API_KEY="sk-..."
```

在 `config.local.json` 中开启（`base_url` / `model` 直接在配置中修改，API key 经 `api_key_env` 指向环境变量）：

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

LLM 按书签计费，建议先用 `--limit` 小批量试跑。

## CLI 参考

| 参数 | 说明 | 默认 |
|------|------|------|
| `-i, --input` | 输入 HTML，支持多文件与 glob | 必填 |
| `-o, --output` | 输出目录 | `output` |
| `-c, --config` | 配置文件 | 内置默认配置 |
| `--workers` | 并行线程数（上限 32） | `4` |
| `--threshold` | 覆盖配置中的置信度阈值 | 配置值 |
| `--limit` | 限制处理数量（调试用） | `0` |
| `--health-check` | 运行健康检查 | - |
| `--eval FILE` | 用标注 JSON 评估分类准确率 | - |
| `--log-level` | 日志级别 | `INFO` |
| `-V, --version` | 显示版本 | - |

提供 `-i` 时，日志同时输出到控制台与 `logs/cleanbook.log`。

## 常见问题

**去重会误删吗？** 仅在相同域名内判定，4 种策略任一命中即视为重复：精确 URL、规范化 URL（去 tracking 参数等）、标题 + URL 相似度、标题相似度。阈值偏保守（标题 ≥ 0.95），不会因短标题的单字符差异误判。

**隐私与离线？** 默认不发起任何网络请求。仅当 `llm.enable = true` 时，书签标题/URL 才会发送给你配置的 API 网关。

**中文书签支持吗？** 支持。分类器检测中英文，标题清洗与词表均含中英变体。

**导出的 HTML 能导回浏览器吗？** 能。Chrome / Edge / Firefox 的书签管理器均支持导入书签 HTML。
