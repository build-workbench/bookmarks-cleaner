**English** | [中文](#chinese)

<a id="top"></a>

# CleanBookmarks

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#)

Too many bookmarks, all over the place? One command to **deduplicate, auto-classify, and organize** — everything runs locally.

## Install

```bash
pipx install cleanbookmarks
```

## Quick Start

1. **Export your bookmarks as HTML from your browser**
   - Chrome / Edge: `Bookmark manager → ⋮ → Export bookmarks`
   - Firefox: `Bookmarks → Manage Bookmarks → Import and Backup → Export Bookmarks to HTML`

2. **Run the classifier**

   ```bash
   cleanbookmarks -i bookmarks.html -o output/
   ```

3. **Import back into your browser**: import any `*.html` file under `output/` via your browser's "Import bookmarks". The same directory also contains `*.json` (structured data) and `*.markdown` (classification report).

![Screenshot](https://raw.githubusercontent.com/build-workbench/bookmarks-cleaner/main/docs/screenshot.png?v=2)

No bookmarks file handy? Download the bundled sample and try:

```bash
# Running from source: use the sample in the repo
cleanbookmarks -i examples/sample_bookmarks.html -o output/
# Installed via pipx: download the sample first (or use any exported bookmarks HTML)
curl -O https://raw.githubusercontent.com/build-workbench/bookmarks-cleaner/main/examples/sample_bookmarks.html
cleanbookmarks -i sample_bookmarks.html -o output/
```

## Common Options

```bash
cleanbookmarks -i a.html b.html -o output/ --workers 8   # multiple files + parallel
cleanbookmarks -i "bookmarks/*.html" -o output/          # glob support
cleanbookmarks -i bookmarks.html -c config.local.json    # custom config
cleanbookmarks -i bookmarks.html --limit 20              # small trial run first
```

The default config works out of the box. To tune classification rules, confidence thresholds, title cleaning, etc., copy the default config and pass it with `-c`:

```bash
# Running from source: default config lives at cleanbookmarks/resources/config.json
cp cleanbookmarks/resources/config.json config.local.json
# Installed via pipx: locate the packaged config first (pipx runpip cleanbookmarks show cleanbookmarks prints the path)
cleanbookmarks -i bookmarks.html -c config.local.json
```

See `cleanbookmarks --help` for all options.

## How Classification Works

A **two-level cascade**, rules first, fully explainable:

1. **Rule engine (default)**: regex matching over three signals — site domain, URL path, and title keywords. Each hit adds weighted category scores; scores of the same category are merged and normalized into a confidence value. A URL analyzer (recognizing GitHub, doc sites, video/Bilibili sites, etc.) provides extra hints.
2. **LLM fallback (optional)**: when enabled, bookmarks the rules miss go to the LLM; bookmarks the rules hit only get subcategory and reasoning enriched by the LLM.

Results below the confidence threshold (default 0.4) are marked as "unclassified" — better safe than sorry. The default config ships a bilingual (Chinese/English) vocabulary across 17 categories; pass `-c` with a custom config to tune rules and thresholds.

**Deduplication** is conservative: comparison happens only within the same domain, and a duplicate is declared only when any of 4 checks hit (exact URL, normalized URL, title+URL similarity, title similarity), with the title-similarity threshold set high at 0.95 to avoid dropping genuinely different pages.

## LLM Classification (Optional)

Fully offline by default. To let an AI classify bookmarks the rules miss:

```bash
pip install "cleanbookmarks[llm]"
```

Then enable it in `config.local.json`:

```json
{ "llm": { "enable": true, "base_url": "https://api.openai.com", "model": "gpt-4o-mini", "api_key_env": "OPENAI_API_KEY" } }
```

Set the `OPENAI_API_KEY` environment variable and run again.

### LLM Deep Participation (enhanced mode)

Beyond per-bookmark fallback, the LLM can take part in the whole pipeline in three stages (activated automatically once `llm.enhanced.enable` is on):

1. **Corpus analysis**: first reads the overall profile of your bookmarks (domains/keywords/language distribution) to judge the topic landscape.
2. **Config optimization**: proposes conservative rule additions (only appending keywords/categories, never deleting) based on the analysis, then writes them into the config — with an automatic backup (`config.llm-backup-*.json`, keeping the latest 5) before overwriting.
3. **Result audit**: after classification, audits every result and auto-fixes misclassifications, marking them `audited`.

```json
{ "llm": { "enable": true, "enhanced": { "enable": true, "audit_batch_size": 40 } } }
```

Any stage that fails (network/parse errors) is skipped automatically without breaking the run. Off by default; note token usage grows with bookmark count when enabled.

## FAQ

- **Will it delete bookmarks by mistake?** Deduplication only happens within the same domain, using 4 conservative strategies (exact URL, normalized URL, title+URL similarity, title similarity) — any single hit counts as a duplicate.
- **Privacy?** No network requests by default; only when LLM is enabled are bookmark titles/URLs sent to the API you configured.
- **Does it support Chinese bookmarks?** Yes — the classification vocabulary includes both Chinese and English variants.
- **How do I use the exported files?** Chrome / Edge / Firefox all support importing bookmarks HTML.

---

<a id="chinese"></a>
[English](#top) | **中文**

# CleanBookmarks

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#)

书签太多太乱？一条命令帮你**去重、自动分类、整理导出**，全程本地运行。

## 安装

```bash
pipx install cleanbookmarks
```

## 快速上手

1. **在浏览器导出书签 HTML**
   - Chrome / Edge：`书签管理器 → ⋮ → 导出书签`
   - Firefox：`书签 → 管理书签 → 导入和备份 → 导出书签到 HTML`

2. **运行分类**

   ```bash
   cleanbookmarks -i bookmarks.html -o output/
   ```

3. **导入回浏览器**：把 `output/` 下生成的 `*.html` 用浏览器的「导入书签」导回即可。同目录还有 `*.json`（结构化数据）和 `*.markdown`（分类报告）。

![运行示例](https://raw.githubusercontent.com/build-workbench/bookmarks-cleaner/main/docs/screenshot.png?v=2)

没有书签文件？下载仓库自带的示例试跑：

```bash
# 源码运行：直接使用仓库内示例
cleanbookmarks -i examples/sample_bookmarks.html -o output/
# pipx 安装：先下载示例（或任意浏览器导出的书签 HTML）
curl -O https://raw.githubusercontent.com/build-workbench/bookmarks-cleaner/main/examples/sample_bookmarks.html
cleanbookmarks -i sample_bookmarks.html -o output/
```

## 常用选项

```bash
cleanbookmarks -i a.html b.html -o output/ --workers 8   # 多个文件 + 并行
cleanbookmarks -i "bookmarks/*.html" -o output/          # 支持 glob
cleanbookmarks -i bookmarks.html -c config.local.json    # 自定义配置
cleanbookmarks -i bookmarks.html --limit 20              # 先小批量试跑
```

默认配置开箱即用。想调整分类规则、置信度阈值、标题清理等，把默认配置复制为本地文件再修改，用 `-c` 指定：

```bash
# 源码运行：默认配置在 cleanbookmarks/resources/config.json
cp cleanbookmarks/resources/config.json config.local.json
# pipx 安装：先找到安装包内配置（pipx runpip cleanbookmarks show cleanbookmarks 可查路径）
cleanbookmarks -i bookmarks.html -c config.local.json
```

完整参数见 `cleanbookmarks --help`。

## 分类算法说明

采用**两级级联**架构，规则优先、全程可解释：

1. **规则引擎（默认）**：基于「站点域名 + URL 路径 + 标题关键词」三类信号做正则匹配，每个命中按权重累加分类得分，同类目分数合并后归一化为置信度。另有 URL 智能分析器（识别 GitHub/文档站/视频站/B站 等站点形态）作为补充线索。
2. **LLM 兜底（可选）**：开启后，规则未命中的书签交给 LLM 分类，规则命中的则仅由 LLM 补充子分类与理由。

置信度低于阈值（默认 0.4）的结果会标记为「未分类」，宁缺毋滥。默认配置内置 17 个类目的中英双语词表，可用 `-c` 传入自定义配置调整规则与阈值。

**去重**采用保守策略：仅在相同域名内比较，4 种判定（精确 URL、标准化 URL、标题+URL 双相似、标题相似）任一命中才算重复，标题相似阈值高达 0.95，避免误删内容不同的页面。

## LLM 分类（可选）

默认全离线。若想让规则未命中的书签由 AI 兜底分类：

```bash
pip install "cleanbookmarks[llm]"
```

然后在 `config.local.json` 中开启：

```json
{ "llm": { "enable": true, "base_url": "https://api.openai.com", "model": "gpt-4o-mini", "api_key_env": "OPENAI_API_KEY" } }
```

设置 `OPENAI_API_KEY` 环境变量后重新运行即可。

### LLM 深度参与（enhanced 模式）

除单条兜底外，LLM 还能以三阶段强势参与全流程（`llm.enhanced.enable` 开启后自动生效）：

1. **语料分析**：先整体读取你的书签画像（域名/关键词/语言分布），判断主题分布
2. **配置优化**：基于语料分析结果产出规则增量建议（只追加关键词/类目，不删改），自动写入配置——覆写前自动备份为 `config.llm-backup-*.json`（保留最近 5 份）
3. **结果审核**：分类完成后逐条审核分类结果，误判自动修正并标注 `audited`

```json
{ "llm": { "enable": true, "enhanced": { "enable": true, "audit_batch_size": 40 } } }
```

任何阶段失败（网络/解析错误）都会自动跳过、不影响整体流程。默认关闭，开启后注意 token 消耗随书签量增长。

## 常见问题

- **会误删吗？** 只在相同域名内判重，4 种策略（精确 URL、规范化 URL、标题+URL 相似度、标题相似度）任一命中才算重复，阈值保守。
- **隐私？** 默认不发起任何网络请求；仅开启 LLM 后，书签标题/URL 才会发送给你配置的 API。
- **支持中文书签吗？** 支持，分类词表含中英变体。
- **导出文件怎么用？** Chrome / Edge / Firefox 均支持导入书签 HTML。
