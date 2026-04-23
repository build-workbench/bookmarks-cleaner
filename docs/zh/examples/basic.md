# 基础用法示例

本页展示 CleanBook 的常见使用场景。

## 场景一：首次清理

清理从浏览器导出的书签文件：

```bash
# 基础清理（推荐）
cleanbook -i ~/Downloads/bookmarks.html -o ~/clean-bookmarks/

# 启用机器学习（准确率更高，首次较慢）
cleanbook -i ~/Downloads/bookmarks.html -o ~/clean-bookmarks/ --train
```

输出目录结构：

```
~/clean-bookmarks/
├── bookmarks_clean.html       # 可直接导入浏览器
├── bookmarks_data.json        # 结构化的 JSON 数据
├── bookmarks_summary.md       # 分类统计报告
└── taxonomy_summary.yaml      # 词表汇总
```

## 场景二：批量处理

处理多个书签文件：

```bash
# 处理多个文件
cleanbook -i work.html personal.html -o output/

# 处理整个目录
cleanbook -i ./bookmarks-backup/ -o output/
```

## 场景三：自定义输出

```bash
# 只输出 HTML 格式
cleanbook -i bookmarks.html -o output/ --format html

# 只输出 JSON（用于数据分析）
cleanbook -i bookmarks.html -o output/ --format json

# 输出所有格式
cleanbook -i bookmarks.html -o output/ --format html,json,markdown
```

## 场景四：调整分类严格度

通过配置文件调整分类阈值：

```json
{
  "ai_settings": {
    "confidence_threshold": 0.5   // 降低阈值，获得更积极的分类
  }
}
```

或使用命令行：

```bash
# 宽松的分类（更多内容会被分类）
cleanbook -i bookmarks.html -o output/ --threshold 0.5

# 严格的分类（只有高置信度才分类）
cleanbook -i bookmarks.html -o output/ --threshold 0.9
```

## 场景五：限制资源使用

```bash
# 单线程处理（低内存占用）
cleanbook -i bookmarks.html -o output/ --workers 1

# 禁用 ML（更快但准确率略低）
cleanbook -i bookmarks.html -o output/ --no-ml

# 禁用缓存（测试用）
cleanbook -i bookmarks.html -o output/ --no-cache
```

## 场景六：处理特定分类

只关注和处理特定类型的书签：

```bash
# 先预览分类统计
cleanbook -i bookmarks.html -o output/ --dry-run

# 查看统计后，只提取编程相关的书签
cleanbook -i bookmarks.html -o output/ \
    --include-categories "编程,Development,Python"
```

## 场景七：交互式向导

适合首次使用的用户：

```bash
cleanbook-wizard
```

向导会依次询问：
1. 输入文件路径
2. 输出目录
3. 是否启用 ML
4. 输出格式选择

## 场景八：自动化脚本

```bash
#!/bin/bash
# clean-bookmarks.sh

EXPORT_DIR="$HOME/bookmark-exports"
OUTPUT_DIR="$HOME/clean-bookmarks/$(date +%Y-%m-%d)"
LOG_FILE="$OUTPUT_DIR/clean.log"

mkdir -p "$OUTPUT_DIR"

for file in "$EXPORT_DIR"/*.html; do
    echo "Processing: $file"
    cleanbook -i "$file" -o "$OUTPUT_DIR" --train 2>&1 | tee -a "$LOG_FILE"
done

echo "Done! Results in: $OUTPUT_DIR"
```

添加到 crontab 定期执行：

```cron
# 每周日凌晨 2 点清理书签
0 2 * * 0 /home/user/clean-bookmarks.sh
```

## 场景九：数据分析

使用输出的 JSON 进行数据分析：

```python
import json

# 读取分类数据
with open('output/bookmarks_data.json') as f:
    data = json.load(f)

# 统计分类分布
from collections import Counter
categories = Counter(b['category'] for b in data['bookmarks'])
print(categories.most_common(10))

# 查找未分类的书签
uncategorized = [b for b in data['bookmarks'] if b['category'] == '未分类']
print(f"未分类: {len(uncategorized)}")
```

## 场景十：合并多个浏览器的书签

```bash
# 导出各浏览器书签
# Chrome → chrome.html
# Firefox → firefox.html
# Safari → safari.html

# 合并清理
cleanbook -i chrome.html firefox.html safari.html -o merged/

# 查看重复统计
cat merged/bookmarks_summary.md | grep "重复"
```

## 更多资源

- [自定义规则](./custom-rules) — 编写自己的分类规则
- [团队配置](/zh/examples/team) — 在团队中共享配置
