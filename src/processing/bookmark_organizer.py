"""
Bookmark Organizer - 书签组织器
负责书签的分类组织和排序
"""

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from src.utils.standardizer import TaxonomyStandardizer


class BookmarkOrganizer:
    """
    书签组织器

    将书签按照主题和资源类型组织成层次结构，
    并支持分类标准化和排序。
    """

    def organize(
        self,
        bookmarks: List[Dict],
        taxonomy_standardizer: "TaxonomyStandardizer" = None,
    ) -> Dict[str, Dict[str, List]]:
        """
        组织书签到分类结构

        Args:
            bookmarks: 书签列表，每个书签包含 subject、resource_type 等字段
            taxonomy_standardizer: 可选的分类法标准化器

        Returns:
            组织后的结构: {subject: {resource_type: [bookmarks]}}
        """
        organized = defaultdict(lambda: defaultdict(list))

        for bookmark in bookmarks:
            # 提取分类信息
            subject = bookmark.get("subject", "未分类")
            resource_type = bookmark.get("resource_type", "网页")

            # 标准化分类
            if taxonomy_standardizer:
                subject = taxonomy_standardizer.normalize_subject(subject)
                resource_type = taxonomy_standardizer.normalize_resource_type(
                    resource_type
                )

            # 组织到结构中
            organized[subject][resource_type].append(bookmark)

        # 排序
        self._sort_organized(organized)

        return dict(organized)

    def _sort_organized(self, organized: Dict):
        """
        对组织后的书签进行排序

        Args:
            organized: 组织后的书签结构（原地修改）
        """
        for subject in organized:
            for resource_type in organized[subject]:
                organized[subject][resource_type].sort(
                    key=lambda b: b.get("title", "").lower()
                )

    def get_statistics(self, organized: Dict) -> Dict:
        """
        获取组织后的统计信息

        Args:
            organized: 组织后的书签结构

        Returns:
            统计信息字典，包含总数、各主题数量等
        """
        total = 0
        subject_counts = {}
        resource_type_counts = {}

        for subject, types in organized.items():
            subject_count = sum(len(bookmarks) for bookmarks in types.values())
            subject_counts[subject] = subject_count
            total += subject_count

            for resource_type, bookmarks in types.items():
                resource_type_counts[resource_type] = resource_type_counts.get(
                    resource_type, 0
                ) + len(bookmarks)

        return {
            "total": total,
            "subject_count": len(organized),
            "subjects": subject_counts,
            "resource_types": resource_type_counts,
        }
