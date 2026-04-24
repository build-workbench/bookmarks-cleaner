# 快速开始

<CbBadge text="5 分钟上手" type="tip" />

本指南将在 5 分钟内带你完成 CleanBook 的安装和首次使用。

## 安装

::: tip 推荐安装方式
使用 [pipx](https://pipx.pypa.io/) 安装可以确保 CleanBook 在一个独立的虚拟环境中运行，不会与其他 Python 包冲突。
:::

::: code-group

```bash [pipx 推荐]
# 安装 pipx（如果尚未安装）
pip install pipx
pipx ensurepath

# 安装 CleanBook
pipx install cleanbook
```

```bash [pip]
pip install cleanbook
```

```bash [uv]
uv tool install cleanbook
```

:::

验证安装：

```bash
cleanbook --version
# cleanbook, version 2.0.0
```

## 获取书签文件

### Chrome / Edge
1. 打开书签管理器：`chrome://bookmarks` 或 `edge://favorites`
2. 点击右上角菜单 → "导出书签"
3. 保存为 `bookmarks.html`

### Firefox
1. 打开书签管理器：`Ctrl+Shift+O`
2. 点击 "导入和备份" → "导出书签到 HTML"
3. 保存为 `bookmarks.html`

### Safari
1. 文件 → 导出 → 书签
2. 保存为 `bookmarks.html`

## 运行清理

最简单的用法：

```bash
cleanbook -i bookmarks.html -o output/
```

输出文件：

```
output/
├── bookmarks_clean.html    # 清理后的书签（可直接导入浏览器）
├── bookmarks_data.json     # 结构化数据（便于分析）
├── bookmarks_summary.md    # 分类报告
└── taxonomy_summary.yaml   # 词表汇总
```

## 查看结果

### 导入浏览器

打开 `output/bookmarks_clean.html`，使用浏览器的 "导入书签" 功能：

**Chrome**: 书签 → 导入书签和设置 → 以前导出的书签 (HTML 文件)

**Firefox**: 书签 → 管理书签 → 导入和备份 → 从 HTML 导入书签

### 查看报告

```bash
cat output/bookmarks_summary.md
```

示例输出：

```markdown
# CleanBook 处理报告

## 统计概况
- 原始书签: 1,247
- 重复移除: 23
- 成功分类: 1,224 (91.4%)
- 未分类: 0

## 分类分布
| 分类 | 数量 | 占比 |
|------|------|------|
| 💻 编程 | 456 | 37.3% |
| 🤖 AI/ML | 189 | 15.4% |
| 📚 文档 | 234 | 19.1% |
| 🛠️ 工具 | 167 | 13.7% |
| 📰 新闻 | 178 | 14.5% |
```

## 进阶用法

### 启用机器学习

首次使用 `--train` 会下载并训练 ML 模型，后续处理会自动使用：

```bash
cleanbook -i bookmarks.html --train
```

### 交互式向导

```bash
cleanbook-wizard
```

向导会引导你：
1. 选择输入文件
2. 选择输出格式
3. 调整分类阈值
4. 预览处理结果

### 批量处理

```bash
# 处理多个文件
cleanbook -i file1.html file2.html -o output/

# 指定工作进程数
cleanbook -i bookmarks.html --workers 8
```

## 配置简介

CleanBook 内置默认 `config.json`；只有在你需要自定义规则时才需要显式覆盖：

```bash
# 使用内置默认配置
cleanbook -i bookmarks.html -o output/

# 使用本地配置覆盖
cleanbook -i bookmarks.html -o output/ -c ./config.json
```

关键配置项：

```json
{
  "ai_settings": {
    "confidence_threshold": 0.7,    // 分类置信度阈值
    "use_semantic_analysis": true,  // 启用语义分析
    "max_workers": 4                // 并行处理数
  },
  "category_rules": {
    "技术/Python": {
      "rules": [
        { "match": "domain", "keywords": ["python.org", "pypi.org"], "weight": 15 },
        { "match": "title", "keywords": ["django", "flask", "fastapi"], "weight": 10 }
      ]
    }
  }
}
```

更多配置选项参见 [配置详解](/zh/guide/configuration)。

## 常见问题

**Q: 处理大量书签时内存不足？**

```bash
# 限制并行处理数量
cleanbook -i bookmarks.html --workers 1 --no-ml
```

**Q: 如何提高分类准确率？**

1. 根据你的书签领域自定义 `category_rules`
2. 启用 ML（`--train`）
3. 调整 `confidence_threshold`（默认 0.7，降低可获得更多分类）

**Q: 如何切到更稳定的运行模式？**

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

## 下一步

- [安装指南](/zh/guide/installation) — 详细了解安装选项
- [配置详解](/zh/reference/config) — 深度定制分类规则
- [配置指南](/zh/guide/configuration) — 理解配置文件和自定义规则
