"""
LLM Second Pass Prompt Generator

为第二轮大模型分类生成优化的提示词。
用于将第一轮（规则+ML模型）分类结果导出后，在外部平台进行精细化整理。
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class SecondPassPromptGenerator:
    """生成第二轮大模型分类的提示词"""

    # 主分类体系
    CATEGORY_SYSTEM = {
        "工作台": ["司内业务", "内部工具", "项目管理"],
        "人工智能": ["模型平台", "AI编程", "机器学习", "应用工具", "Claude中转"],
        "编程": ["代码仓库", "编程语言", "Web开发", "DevOps运维", "技术文档"],
        "生物": ["生物信息", "基因组学", "单细胞", "工具软件"],
        "学习": ["技术文档", "教育", "课程讲座", "书籍资料"],
        "社区": ["技术社区", "论坛", "问答"],
        "资讯": ["新闻", "周刊", "博客"],
        "娱乐": ["影音", "游戏", "音乐"],
        "工具": ["软件", "在线服务", "效率工具"],
        "其他": ["在线服务", "软件下载", "文档资料"],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.custom_categories = self.config.get("custom_categories", {})
        # 合并自定义分类
        self.categories = {**self.CATEGORY_SYSTEM, **self.custom_categories}

    def generate_batch_prompt(
        self,
        bookmarks: List[Dict[str, Any]],
        *,
        focus_on_uncategorized: bool = True,
        include_low_confidence: bool = True,
        confidence_threshold: float = 0.7,
        batch_size: int = 50,
    ) -> str:
        """
        生成批量分类的提示词
        
        Args:
            bookmarks: 书签列表，每个书签包含 title, url, category, confidence 等
            focus_on_uncategorized: 是否重点处理未分类项
            include_low_confidence: 是否包含低置信度项
            confidence_threshold: 置信度阈值
            batch_size: 每批处理数量
        """
        # 筛选需要处理的书签
        to_process = []
        for bm in bookmarks:
            cat = bm.get("category", "未分类")
            conf = bm.get("confidence", 0)
            
            if focus_on_uncategorized and "未分类" in cat:
                to_process.append(bm)
            elif include_low_confidence and conf < confidence_threshold:
                to_process.append(bm)
        
        # 限制批次大小
        to_process = to_process[:batch_size]
        
        return self._build_batch_prompt(to_process)

    def _build_batch_prompt(self, bookmarks: List[Dict[str, Any]]) -> str:
        """构建批量处理提示词"""
        category_tree = self._format_category_tree()
        bookmark_list = self._format_bookmark_list(bookmarks)
        
        prompt = f"""# 书签智能分类任务

## 任务说明
你是一位专业的信息架构师，需要对以下书签进行精准分类。这些书签已经过第一轮规则引擎预分类，现在需要你进行精细化整理。

## 分类体系
{category_tree}

## 待分类书签
{bookmark_list}

## 输出要求
请以 JSON 数组格式输出，每个书签包含：
```json
[
  {{
    "id": 1,
    "category": "主分类/子分类",
    "confidence": 0.95,
    "reason": "简短分类理由"
  }}
]
```

## 分类原则
1. **精准匹配**：优先使用最具体的子分类
2. **领域优先**：技术类内容优先按技术领域分类（如 AI、编程、生物）
3. **用途次之**：同领域内按用途细分（如文档、工具、社区）
4. **置信度诚实**：不确定时降低置信度，可标注为"其他"
5. **保持一致**：相似内容应归入同一分类

## 特殊处理
- GitHub/GitLab 仓库 → 编程/代码仓库
- 官方文档 → 学习/技术文档
- AI 相关工具 → 人工智能/应用工具
- 公司内部链接 → 工作台/司内业务
- 生物信息相关 → 生物/生物信息

请开始分类："""
        
        return prompt

    def generate_review_prompt(
        self,
        categorized_bookmarks: Dict[str, List[Dict[str, Any]]],
        *,
        check_consistency: bool = True,
        suggest_merges: bool = True,
    ) -> str:
        """
        生成分类审查提示词，用于检查分类一致性和建议合并
        
        Args:
            categorized_bookmarks: 按分类组织的书签字典
            check_consistency: 是否检查一致性
            suggest_merges: 是否建议合并相似分类
        """
        summary = self._format_category_summary(categorized_bookmarks)
        
        prompt = f"""# 书签分类审查任务

## 当前分类统计
{summary}

## 审查要求
"""
        if check_consistency:
            prompt += """
### 一致性检查
1. 检查同一分类下的书签是否主题一致
2. 识别可能分类错误的书签
3. 标注需要人工复核的项目
"""
        
        if suggest_merges:
            prompt += """
### 合并建议
1. 识别可以合并的相似分类
2. 建议更合理的分类层级
3. 提出分类体系优化建议
"""
        
        prompt += """
## 输出格式
```json
{
  "consistency_issues": [
    {"category": "分类名", "bookmark": "书签标题", "issue": "问题描述", "suggestion": "建议"}
  ],
  "merge_suggestions": [
    {"from": ["分类A", "分类B"], "to": "合并后分类", "reason": "理由"}
  ],
  "optimization_tips": ["优化建议1", "优化建议2"]
}
```

请开始审查："""
        
        return prompt

    def generate_reorganize_prompt(
        self,
        bookmarks: List[Dict[str, Any]],
        *,
        target_structure: Optional[Dict[str, List[str]]] = None,
        max_depth: int = 2,
    ) -> str:
        """
        生成重新组织提示词，用于按新结构重新整理书签
        
        Args:
            bookmarks: 所有书签列表
            target_structure: 目标分类结构，None 则使用默认
            max_depth: 最大分类深度
        """
        structure = target_structure or self.categories
        structure_text = self._format_target_structure(structure)
        bookmark_text = self._format_all_bookmarks(bookmarks)
        
        prompt = f"""# 书签重新组织任务

## 目标分类结构
{structure_text}

## 所有书签（共 {len(bookmarks)} 个）
{bookmark_text}

## 任务要求
1. 将所有书签重新分配到目标分类结构中
2. 每个书签只能属于一个分类
3. 分类深度不超过 {max_depth} 层
4. 保持分类均衡，避免某个分类过于庞大

## 输出格式
按分类输出，每个分类下列出书签：
```json
{{
  "分类名": [
    {{"title": "书签标题", "url": "链接"}}
  ]
}}
```

请开始重新组织："""
        
        return prompt

    def _format_category_tree(self) -> str:
        """格式化分类树"""
        lines = []
        for main_cat, sub_cats in self.categories.items():
            lines.append(f"- {main_cat}")
            for sub in sub_cats:
                lines.append(f"  - {main_cat}/{sub}")
        return "\n".join(lines)

    def _format_bookmark_list(self, bookmarks: List[Dict[str, Any]]) -> str:
        """格式化书签列表"""
        lines = []
        for i, bm in enumerate(bookmarks, 1):
            title = bm.get("title", "无标题")
            url = bm.get("url", "")
            current_cat = bm.get("category", "未分类")
            conf = bm.get("confidence", 0)
            
            lines.append(f"{i}. [{title}]({url})")
            lines.append(f"   当前分类: {current_cat} (置信度: {conf:.2f})")
        
        return "\n".join(lines)

    def _format_category_summary(
        self, categorized: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """格式化分类统计"""
        lines = []
        for cat, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
            lines.append(f"- {cat}: {len(items)} 个")
            # 显示前3个示例
            for item in items[:3]:
                lines.append(f"  - {item.get('title', '无标题')[:50]}")
            if len(items) > 3:
                lines.append(f"  - ... 还有 {len(items) - 3} 个")
        return "\n".join(lines)

    def _format_target_structure(self, structure: Dict[str, List[str]]) -> str:
        """格式化目标结构"""
        lines = []
        for main_cat, sub_cats in structure.items():
            lines.append(f"## {main_cat}")
            for sub in sub_cats:
                lines.append(f"  - {sub}")
        return "\n".join(lines)

    def _format_all_bookmarks(self, bookmarks: List[Dict[str, Any]]) -> str:
        """格式化所有书签（简洁版）"""
        lines = []
        for bm in bookmarks:
            title = bm.get("title", "无标题")[:60]
            url = bm.get("url", "")
            lines.append(f"- {title} | {url}")
        return "\n".join(lines)


def generate_prompt_for_export(
    report_path: str,
    output_path: Optional[str] = None,
    *,
    mode: str = "batch",
    **kwargs,
) -> str:
    """
    从报告文件生成提示词并可选保存
    
    Args:
        report_path: 分类报告路径
        output_path: 输出提示词文件路径，None 则只返回不保存
        mode: 模式 - batch(批量分类), review(审查), reorganize(重组)
        **kwargs: 传递给对应方法的参数
    
    Returns:
        生成的提示词
    """
    # 这里需要解析报告文件，提取书签信息
    # 简化实现，实际使用时需要完善解析逻辑
    generator = SecondPassPromptGenerator()
    
    # 根据模式生成不同提示词
    if mode == "batch":
        prompt = generator.generate_batch_prompt([], **kwargs)
    elif mode == "review":
        prompt = generator.generate_review_prompt({}, **kwargs)
    elif mode == "reorganize":
        prompt = generator.generate_reorganize_prompt([], **kwargs)
    else:
        raise ValueError(f"Unknown mode: {mode}")
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(prompt)
    
    return prompt


# 便捷函数：生成常用提示词模板
def get_quick_prompt_templates() -> Dict[str, str]:
    """获取常用提示词模板"""
    return {
        "uncategorized": """请帮我分类以下未分类的书签：

{bookmarks}

分类体系：
- 人工智能（模型平台、AI编程、机器学习、应用工具）
- 编程（代码仓库、编程语言、Web开发、DevOps运维）
- 生物（生物信息、基因组学、单细胞）
- 学习（技术文档、教育、课程讲座）
- 工具（软件、在线服务）
- 其他

请以 JSON 格式输出：[{"title": "标题", "category": "分类", "reason": "理由"}]""",

        "review": """请审查以下分类结果，指出可能的错误：

{categorized_bookmarks}

请检查：
1. 分类是否准确
2. 是否有更合适的分类
3. 是否有重复或相似的书签

输出格式：[{"title": "标题", "current": "当前分类", "suggested": "建议分类", "reason": "理由"}]""",

        "merge": """以下分类可能需要合并或调整：

{categories}

请建议：
1. 哪些分类可以合并
2. 如何优化分类层级
3. 是否需要新增分类

输出格式：{"merges": [...], "new_categories": [...], "suggestions": [...]}""",
    }
