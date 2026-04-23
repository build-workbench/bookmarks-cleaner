#!/usr/bin/env python3
"""
Export LLM Prompt Tool

从分类报告中提取书签，生成用于第二轮大模型分类的提示词。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_markdown_report(
    report_path: str,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    解析 Markdown 格式的分类报告

    Returns:
        (stats, bookmarks) - 统计信息和书签列表
    """
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    stats = {}
    bookmarks = []

    # 解析统计信息
    total_match = re.search(r"\*\*总书签数\*\*:\s*(\d+)", content)
    if total_match:
        stats["total"] = int(total_match.group(1))

    uncategorized_match = re.search(r"未分类:\s*(\d+)\s*个", content)
    if uncategorized_match:
        stats["uncategorized"] = int(uncategorized_match.group(1))

    # 解析书签
    # 格式: - [标题](URL) (置信度)
    bookmark_pattern = re.compile(
        r"^-\s+\[([^\]]+)\]\(([^)]+)\)\s*\(?([\d.]+)?\)?", re.MULTILINE
    )

    current_category = "未分类"
    current_subcategory = ""

    lines = content.split("\n")
    for i, line in enumerate(lines):
        # 检测主分类标题 (## 开头)
        if line.startswith("## ") and not line.startswith("## 📊"):
            current_category = line[3:].strip()
            current_subcategory = ""
            continue

        # 检测子分类标题 (### 开头)
        if line.startswith("### "):
            current_subcategory = line[4:].strip()
            continue

        # 解析书签行
        match = bookmark_pattern.match(line.strip())
        if match:
            title, url, confidence = match.groups()
            conf = float(confidence) if confidence else 0.5

            category = current_category
            if current_subcategory:
                category = f"{current_category}/{current_subcategory}"

            bookmarks.append(
                {
                    "title": title,
                    "url": url,
                    "category": category,
                    "confidence": conf,
                }
            )

    stats["parsed"] = len(bookmarks)
    return stats, bookmarks


def generate_batch_classification_prompt(
    bookmarks: List[Dict[str, Any]],
    *,
    filter_uncategorized: bool = True,
    filter_low_confidence: bool = True,
    confidence_threshold: float = 0.7,
    max_items: int = 100,
) -> str:
    """生成批量分类提示词"""

    # 筛选需要处理的书签
    to_process = []
    for bm in bookmarks:
        cat = bm.get("category", "")
        conf = bm.get("confidence", 0)

        needs_review = False
        if filter_uncategorized and "未分类" in cat:
            needs_review = True
        if filter_low_confidence and conf < confidence_threshold:
            needs_review = True

        if needs_review:
            to_process.append(bm)

    # 限制数量
    to_process = to_process[:max_items]

    if not to_process:
        return "# 没有需要处理的书签\n所有书签已分类且置信度足够。"

    # 构建提示词
    prompt = f"""# 书签智能分类任务

## 背景
这些书签已经过第一轮规则引擎预分类，但存在以下情况需要你帮助处理：
- 未能自动分类的书签
- 分类置信度较低的书签

## 分类体系

### 主分类
- **工作台**: 公司内部系统、项目管理、内部工具
- **人工智能**: AI模型、机器学习、AI编程工具、大模型平台
- **编程**: 代码仓库、编程语言、Web开发、DevOps、技术文档
- **生物**: 生物信息学、基因组学、单细胞分析、生信工具
- **学习**: 教程、文档、课程、书籍、学习资源
- **社区**: 技术社区、论坛、问答平台
- **资讯**: 新闻、博客、周刊、技术动态
- **娱乐**: 影音、游戏、音乐、休闲
- **工具**: 在线工具、软件、效率工具
- **其他**: 无法归类的内容

### 子分类示例
- 人工智能/模型平台: ChatGPT、Claude、Gemini 等
- 人工智能/AI编程: Cursor、Copilot、Kiro 等
- 编程/代码仓库: GitHub、GitLab 项目
- 编程/DevOps运维: Docker、K8s、CI/CD
- 生物/生物信息: BWA、GATK、生信流程

## 待分类书签（共 {len(to_process)} 个）

"""

    for i, bm in enumerate(to_process, 1):
        title = bm["title"][:80]
        url = bm["url"]
        current = bm["category"]
        conf = bm["confidence"]

        prompt += f"""{i}. **{title}**
   - URL: {url}
   - 当前: {current} (置信度: {conf:.2f})

"""

    prompt += """## 输出要求

请以 JSON 数组格式输出分类结果：

```json
[
  {
    "id": 1,
    "title": "书签标题",
    "category": "主分类/子分类",
    "confidence": 0.95,
    "reason": "分类理由（简短）"
  }
]
```

## 分类技巧

1. **看域名**: 
   - github.com → 编程/代码仓库
   - huggingface.co → 人工智能/模型平台
   - *.zego.*/bgi.* → 工作台/司内业务

2. **看标题关键词**:
   - LLM/GPT/Claude/模型 → 人工智能
   - Docker/K8s/CI/CD → 编程/DevOps运维
   - 基因/测序/BWA/GATK → 生物/生物信息

3. **看内容类型**:
   - 文档/教程/指南 → 学习/技术文档
   - 论坛/社区/讨论 → 社区
   - 工具/在线服务 → 工具

请开始分类："""

    return prompt


def generate_review_prompt(
    bookmarks: List[Dict[str, Any]],
    *,
    sample_per_category: int = 5,
) -> str:
    """生成分类审查提示词"""

    # 按分类分组
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for bm in bookmarks:
        cat = bm.get("category", "未分类")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(bm)

    prompt = """# 书签分类审查任务

## 任务说明
请审查以下分类结果，检查是否存在：
1. 分类错误的书签
2. 可以合并的相似分类
3. 分类体系的优化建议

## 当前分类统计

"""

    for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
        prompt += f"### {cat} ({len(items)} 个)\n"
        for item in items[:sample_per_category]:
            title = item["title"][:50]
            prompt += f"- {title}\n"
        if len(items) > sample_per_category:
            prompt += f"- ... 还有 {len(items) - sample_per_category} 个\n"
        prompt += "\n"

    prompt += """## 输出要求

```json
{
  "misclassified": [
    {"title": "书签标题", "current": "当前分类", "suggested": "建议分类", "reason": "理由"}
  ],
  "merge_suggestions": [
    {"from": ["分类A", "分类B"], "to": "合并后分类", "reason": "理由"}
  ],
  "new_categories": [
    {"name": "新分类名", "reason": "需要新增的理由"}
  ],
  "general_feedback": "整体反馈和建议"
}
```

请开始审查："""

    return prompt


def generate_html_export_prompt(
    bookmarks: List[Dict[str, Any]],
) -> str:
    """生成用于导出为浏览器书签 HTML 的提示词"""

    # 按分类分组
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for bm in bookmarks:
        cat = bm.get("category", "未分类").split("/")[0]  # 只取主分类
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(bm)

    prompt = """# 书签整理与导出任务

## 任务说明
请帮我整理以下书签，并生成可以导入浏览器的 HTML 格式。

## 当前书签

"""

    for cat, items in sorted(by_category.items()):
        prompt += f"### {cat}\n"
        for item in items:
            prompt += f"- [{item['title']}]({item['url']})\n"
        prompt += "\n"

    prompt += """## 输出要求

1. 按分类整理书签
2. 去除重复项
3. 优化分类结构
4. 生成浏览器书签 HTML 格式

HTML 格式示例：
```html
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3>分类名称</H3>
    <DL><p>
        <DT><A HREF="url">标题</A>
    </DL><p>
</DL><p>
```

请生成整理后的书签 HTML："""

    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="从分类报告生成大模型提示词",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python export_llm_prompt.py output/report.md
  python export_llm_prompt.py output/report.md -m review
  python export_llm_prompt.py output/report.md -m batch --max 50
  python export_llm_prompt.py output/report.md -o prompt.txt
        """,
    )

    parser.add_argument("report", help="分类报告文件路径")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["batch", "review", "export"],
        default="batch",
        help="提示词模式: batch(批量分类), review(审查), export(导出HTML)",
    )
    parser.add_argument("-o", "--output", help="输出文件路径，不指定则输出到控制台")
    parser.add_argument(
        "--max", type=int, default=100, help="最大处理书签数量 (默认: 100)"
    )
    parser.add_argument(
        "--threshold", type=float, default=0.7, help="置信度阈值 (默认: 0.7)"
    )
    parser.add_argument(
        "--all", action="store_true", help="处理所有书签，不仅是未分类/低置信度的"
    )

    args = parser.parse_args()

    # 检查文件存在
    if not Path(args.report).exists():
        print(f"错误: 文件不存在 - {args.report}", file=sys.stderr)
        sys.exit(1)

    # 解析报告
    print(f"正在解析报告: {args.report}", file=sys.stderr)
    stats, bookmarks = parse_markdown_report(args.report)
    print(f"解析完成: 共 {stats.get('parsed', 0)} 个书签", file=sys.stderr)

    # 生成提示词
    if args.mode == "batch":
        prompt = generate_batch_classification_prompt(
            bookmarks,
            filter_uncategorized=not args.all,
            filter_low_confidence=not args.all,
            confidence_threshold=args.threshold,
            max_items=args.max,
        )
    elif args.mode == "review":
        prompt = generate_review_prompt(bookmarks)
    elif args.mode == "export":
        prompt = generate_html_export_prompt(bookmarks)
    else:
        print(f"未知模式: {args.mode}", file=sys.stderr)
        sys.exit(1)

    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"提示词已保存到: {args.output}", file=sys.stderr)
    else:
        print(prompt)


if __name__ == "__main__":
    main()
