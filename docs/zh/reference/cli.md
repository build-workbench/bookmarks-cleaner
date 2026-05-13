# CLI 参考

<CbBadge text="命令行" type="info" />

CleanBook 的命令行工具 `cleanbook` 提供了完整的书签处理流水线。

## 基本用法

```bash
cleanbook -i bookmarks.html -o output/
```

## 全局选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-V, --version` | flag | — | 显示版本号并退出 |
| `-i, --input` | file[] | — | 输入的 HTML 书签文件，支持多个文件和 glob 模式 |
| `-o, --output` | dir | `output` | 输出目录 |
| `-c, --config` | file | 内置 | 配置文件路径；默认使用内置配置 |
| `--workers` | int | 4 | 并行处理线程数 |
| `--threshold` | float | 0.7 | 分类置信度阈值 |
| `--no-ml` | flag | — | 禁用机器学习功能 |
| `--log-level` | enum | `INFO` | 日志级别：`DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `--limit` | int | 0 | 限制处理的书签数量（调试用，0 = 不限） |

## 处理模式

### 标准处理

最基本的处理模式，使用规则引擎分类书签：

```bash
cleanbook -i bookmarks.html -o output/
```

### 交互模式

启动交互式向导，逐步引导操作：

```bash
cleanbook --interactive
```

### ML 训练模式

首次使用会下载并训练 ML 模型，后续处理自动使用：

```bash
cleanbook -i bookmarks.html --train
```

### 健康检查

检查系统依赖和配置是否正常：

```bash
cleanbook --health-check
```

## 反馈管道

CleanBook 提供了离线反馈管道，用于增量改进分类质量。

### 导出待审核结果

将低置信度分类结果导出为 review queue JSON：

```bash
cleanbook -i bookmarks.html -o output/ --export-review-queue review.json
```

### 应用反馈

导入离线 feedback JSON 并应用到本地反馈管道：

```bash
cleanbook --apply-feedback feedback.json
```

### 训练反馈

使用离线 feedback JSON 触发增量训练并保存版本：

```bash
cleanbook --train-feedback feedback.json
```

### 审计反馈

审核 feedback JSON 数据质量：

```bash
cleanbook --audit-feedback feedback.json --audit-output audit.json
```

| 选项 | 说明 |
|------|------|
| `--export-review-queue` | 导出低置信度结果为 JSON |
| `--apply-feedback` | 应用反馈文件 |
| `--train-feedback` | 使用反馈数据增量训练 |
| `--audit-feedback` | 审计反馈数据质量 |
| `--audit-output` | 审计结果输出路径 |

## 常用命令示例

### 基础处理

```bash
# 最简单的用法
cleanbook -i bookmarks.html -o output/

# 使用自定义配置
cleanbook -i bookmarks.html -o output/ -c ./config.json

# 禁用 ML，纯规则模式
cleanbook -i bookmarks.html -o output/ --no-ml
```

### 批量处理

```bash
# 处理多个文件
cleanbook -i file1.html file2.html -o output/

# 使用 glob 模式
cleanbook -i "bookmarks/*.html" -o output/

# 指定并行数
cleanbook -i bookmarks.html --workers 8
```

### 调试与调优

```bash
# 限制处理数量（快速测试）
cleanbook -i bookmarks.html --limit 50

# 开启调试日志
cleanbook -i bookmarks.html --log-level DEBUG

# 调整置信度阈值
cleanbook -i bookmarks.html --threshold 0.5
```

### 完整工作流

```bash
# 1. 健康检查
cleanbook --health-check

# 2. 首次处理 + 训练
cleanbook -i bookmarks.html -o output/ --train

# 3. 导出低置信度结果供人工审核
cleanbook -i bookmarks.html -o output/ --export-review-queue review.json

# 4. 人工审核后应用反馈
cleanbook --apply-feedback reviewed.json

# 5. 使用反馈增量训练
cleanbook --train-feedback reviewed.json
```

## 输出文件

处理完成后，输出目录包含：

| 文件 | 说明 |
|------|------|
| `bookmarks_clean.html` | 清理后的书签（可直接导入浏览器） |
| `bookmarks_data.json` | 结构化数据（便于二次分析） |
| `bookmarks_summary.md` | 分类报告 |
| `taxonomy_summary.yaml` | 词表汇总 |

## 退出码

| 退出码 | 说明 |
|--------|------|
| 0 | 正常完成 |
| 1 | 程序被中断或执行失败 |
| 2 | 配置或资源错误 |
| 3 | 依赖缺失 |

## 下一步

- [安装指南](/zh/guide/installation) — 详细了解安装选项
- [配置详解](/zh/reference/config) — 深度定制分类规则
- [进阶用法](/zh/guide/advanced) — ML、批量处理和反馈管道
