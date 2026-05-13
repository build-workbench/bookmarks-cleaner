# 进阶用法

<CbBadge text="高级功能" type="warning" />

本指南介绍 CleanBook 的高级功能和进阶工作流。

## 启用机器学习

CleanBook 支持可选的机器学习增强分类。首次使用 `--train` 会下载并训练 ML 模型，后续处理会自动使用：

```bash
cleanbook -i bookmarks.html --train
```

### ML 模型说明

- 模型会在首次运行时自动下载到本地缓存
- 后续处理会自动加载已训练的模型
- 如需重新训练，删除缓存后再次运行 `--train`

### 禁用 ML

如果需要纯规则模式（更快、更稳定）：

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

## 交互式向导

CleanBook 提供交互式向导，逐步引导操作：

```bash
cleanbook --interactive
```

或使用独立命令：

```bash
cleanbook-wizard
```

向导会引导你：

1. 选择输入文件
2. 选择输出格式
3. 调整分类阈值
4. 预览处理结果

## 批量处理

### 处理多个文件

```bash
# 指定多个文件
cleanbook -i file1.html file2.html -o output/

# 使用 glob 模式
cleanbook -i "bookmarks/*.html" -o output/
```

### 并行处理

```bash
# 指定并行进程数
cleanbook -i bookmarks.html --workers 8
```

### 资源控制

处理大量书签时的内存优化：

```bash
# 限制并行处理数量
cleanbook -i bookmarks.html --workers 1 --no-ml
```

## 反馈管道

CleanBook 提供离线反馈管道，用于增量改进分类质量。

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

### 相关命令

| 命令 | 说明 |
|------|------|
| `--export-review-queue` | 导出低置信度结果为 JSON |
| `--apply-feedback` | 应用反馈文件到本地管道 |
| `--train-feedback` | 使用反馈数据增量训练 |
| `--audit-feedback` | 审计反馈数据质量 |

## 调试与调优

### 调试模式

```bash
# 开启调试日志
cleanbook -i bookmarks.html --log-level DEBUG

# 限制处理数量（快速测试）
cleanbook -i bookmarks.html --limit 50
```

### 调整置信度

```bash
# 降低阈值获得更多分类
cleanbook -i bookmarks.html --threshold 0.5

# 提高阈值获得更精准分类
cleanbook -i bookmarks.html --threshold 0.8
```

### 审计反馈数据

```bash
cleanbook --audit-feedback feedback.json --audit-output audit.json
```

## 提高分类准确率

1. **自定义规则** - 根据你的书签领域自定义 `category_rules`
2. **启用 ML** - 使用 `--train` 启用机器学习
3. **调整阈值** - 调整 `confidence_threshold`（默认 0.7）
4. **使用反馈管道** - 通过人工审核改进分类

## 下一步

- [CLI 参考](/zh/reference/cli) — 完整命令行选项
- [配置项](/zh/reference/config) — 深度定制分类规则
- [配置指南](/zh/guide/configuration) — 理解配置文件
