# CleanBookmarks

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#)

**中文** | [English](https://github.com/build-workbench/bookmarks-cleaner/blob/main/README.en.md)

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

![运行示例](https://raw.githubusercontent.com/build-workbench/bookmarks-cleaner/main/docs/screenshot.png)

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

## 常见问题

- **会误删吗？** 只在相同域名内判重，4 种策略（精确 URL、规范化 URL、标题+URL 相似度、标题相似度）任一命中才算重复，阈值保守。
- **隐私？** 默认不发起任何网络请求；仅开启 LLM 后，书签标题/URL 才会发送给你配置的 API。
- **支持中文书签吗？** 支持，分类词表含中英变体。
- **导出文件怎么用？** Chrome / Edge / Firefox 均支持导入书签 HTML。
