"""
Bookmark Deduplicator - 书签去重器
高级相似度检测和自动合并
"""

import hashlib
import re
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple
from urllib.parse import parse_qs, urljoin, urlparse


class BookmarkDeduplicator:
    """书签去重器 - 高级相似度检测和去重"""

    def __init__(self):
        # 标题阈值 0.95：字符级相似度对短标题单字符差异（如年份 2018/2019）过于敏感，
        # 低阈值会把内容不同的页面误判为重复，宁保守勿误删
        self.title_threshold = 0.95

        # 初始化去重策略
        self.dedup_strategies = [
            self._exact_url_match,
            self._normalized_url_match,
            self._content_similarity_match,
            self._title_similarity_match,
        ]

    def remove_duplicates(self, bookmarks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """移除重复书签 - 域名预分组 + 组内相似度检测

        优化思路：重复书签几乎总是同域名，因此先按域名分桶，
        仅在同域名桶内做 O(m²) 比较，避免全局 O(n²)。
        """
        if not bookmarks:
            return [], []

        unique_bookmarks = []
        duplicates = []

        # 为每个书签生成唯一标识
        for i, bookmark in enumerate(bookmarks):
            bookmark["_original_index"] = i

        # 按域名预分组
        domain_groups: Dict[str, List[int]] = defaultdict(list)
        for i, bookmark in enumerate(bookmarks):
            try:
                domain = (
                    urlparse(bookmark.get("url", "")).netloc.lower().replace("www.", "")
                )
            except (ValueError, AttributeError):
                domain = ""
            domain_groups[domain].append(i)

        processed_indices: Set[int] = set()

        # 在每个域名组内进行去重
        for _domain, indices in domain_groups.items():
            for idx_pos, i in enumerate(indices):
                if i in processed_indices:
                    continue

                bookmark1 = bookmarks[i]
                similar_group = [bookmark1]
                similar_indices = {i}

                for j in indices[idx_pos + 1 :]:
                    if j in processed_indices:
                        continue

                    if self._are_duplicates(bookmark1, bookmarks[j]):
                        similar_group.append(bookmarks[j])
                        similar_indices.add(j)

                # 处理相似组
                if len(similar_group) > 1:
                    best_bookmark = self._select_best_bookmark(similar_group)
                    unique_bookmarks.append(best_bookmark)

                    for bookmark in similar_group:
                        if bookmark != best_bookmark:
                            bookmark["duplicate_reason"] = self._get_duplicate_reason(
                                best_bookmark, bookmark
                            )
                            duplicates.append(bookmark)
                else:
                    unique_bookmarks.append(bookmark1)

                processed_indices.update(similar_indices)

        return unique_bookmarks, duplicates

    def _are_duplicates(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """判断两个书签是否重复"""
        # 尝试所有去重策略
        for strategy in self.dedup_strategies:
            if strategy(bookmark1, bookmark2):
                return True
        return False

    def _exact_url_match(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """精确URL匹配"""
        return bookmark1.get("url", "") == bookmark2.get("url", "")

    def _normalized_url_match(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """标准化URL匹配：规范化后确定性相等（同页变体判定）

        用相似度阈值（如 0.9）判断"几乎相同"会误杀短路径——"post-1" 与 "post-2"
        的 SequenceMatcher 相似度可达 0.96。规范化（去 tracking/排序 query/去尾斜杠）
        后同页变体应完全一致，直接比较相等即可。
        """
        url1_norm = self._normalize_url(bookmark1.get("url", ""))
        url2_norm = self._normalize_url(bookmark2.get("url", ""))

        if not url1_norm or not url2_norm:
            return False

        # 容忍 http/https 与 www 差异
        return self._strip_scheme_www(url1_norm) == self._strip_scheme_www(url2_norm)

    @staticmethod
    def _strip_scheme_www(url: str) -> str:
        rest = url.split("://", 1)[-1]
        return rest[len("www."):] if rest.startswith("www.") else rest

    def _content_similarity_match(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """内容相似度匹配：同域名 + 标题高度相似 + URL 高度相似（AND 语义）

        旧实现用加权平均（title*0.6 + url*0.4），"标题 0.9 + URL 0.79" 的组合即可过
        0.85 阈值，但两者单独都不够高——短路径的 1 字符差异会被吞掉，造成误删。
        """
        try:
            domain1 = urlparse(bookmark1.get("url", "")).netloc
            domain2 = urlparse(bookmark2.get("url", "")).netloc
            if not domain1 or domain1 != domain2:
                return False
        except (ValueError, AttributeError):
            return False

        title_sim = self._calculate_title_similarity(
            bookmark1.get("title", ""), bookmark2.get("title", "")
        )

        url_sim = self._calculate_url_similarity(
            bookmark1.get("url", ""), bookmark2.get("url", "")
        )

        return title_sim >= self.title_threshold and url_sim >= 0.7

    def _title_similarity_match(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """标题相似度匹配（要求同域名，跨域同标题属于不同站点，不应判定重复）"""
        try:
            domain1 = urlparse(bookmark1.get("url", "")).netloc
            domain2 = urlparse(bookmark2.get("url", "")).netloc
            if not domain1 or domain1 != domain2:
                return False
        except (ValueError, AttributeError):
            return False

        title1 = bookmark1.get("title", "").strip()
        title2 = bookmark2.get("title", "").strip()

        if not title1 or not title2:
            return False

        similarity = self._calculate_title_similarity(title1, title2)
        return similarity >= self.title_threshold

    def _normalize_url(self, url: str) -> str:
        """标准化URL"""
        if not url:
            return ""

        try:
            parsed = urlparse(url.lower().strip())

            # 移除常见的跟踪参数
            tracking_params = {
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_content",
                "utm_term",
                "fbclid",
                "gclid",
                "msclkid",
                "_ga",
                "ref",
                "source",
            }

            # 过滤查询参数
            query_params = parse_qs(parsed.query)
            filtered_params = {
                k: v for k, v in query_params.items() if k not in tracking_params
            }

            # 重建查询字符串
            query_string = "&".join(
                [f"{k}={'&'.join(v)}" for k, v in sorted(filtered_params.items())]
            )

            # 标准化路径（移除末尾斜杠）
            path = parsed.path.rstrip("/")

            # 重构URL
            normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
            if query_string:
                normalized += f"?{query_string}"

            return normalized

        except (ValueError, AttributeError, KeyError):
            return url.lower().strip()

    def _calculate_url_similarity(self, url1: str, url2: str) -> float:
        """计算URL相似度"""
        if not url1 or not url2:
            return 0.0

        try:
            parsed1 = urlparse(url1)
            parsed2 = urlparse(url2)

            # 域名相似度
            domain_sim = 1.0 if parsed1.netloc == parsed2.netloc else 0.0

            # 路径相似度
            path_sim = SequenceMatcher(None, parsed1.path, parsed2.path).ratio()

            # 查询参数相似度：双方都无 query 时取中性 0.5
            # （SequenceMatcher("", "") 恒为 1.0，会把 0.3 权重白送）
            if not parsed1.query and not parsed2.query:
                query_sim = 0.5
            else:
                query_sim = SequenceMatcher(None, parsed1.query, parsed2.query).ratio()

            # 加权平均：路径主导，同域名只给少量基础分（域名相同不该直接算一半相似）
            overall_sim = domain_sim * 0.2 + path_sim * 0.5 + query_sim * 0.3

            return overall_sim

        except (ValueError, AttributeError):
            # 如果解析失败，使用字符串相似度
            return SequenceMatcher(None, url1, url2).ratio()

    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """计算标题相似度"""
        if not title1 or not title2:
            return 0.0

        # 清理标题
        clean_title1 = self._clean_title(title1)
        clean_title2 = self._clean_title(title2)

        if not clean_title1 or not clean_title2:
            return 0.0

        # 计算多种相似度
        sequence_sim = SequenceMatcher(None, clean_title1, clean_title2).ratio()

        # 词级别相似度
        words1 = set(clean_title1.split())
        words2 = set(clean_title2.split())

        if words1 and words2:
            jaccard_sim = len(words1 & words2) / len(words1 | words2)
        else:
            jaccard_sim = 0.0

        # 综合相似度
        combined_sim = sequence_sim * 0.6 + jaccard_sim * 0.4

        return combined_sim

    def _clean_title(self, title: str) -> str:
        """清理标题"""
        if not title:
            return ""

        # 移除常见的网站后缀
        common_suffixes = [
            r"\s*[-|]\s*.*$",  # 移除用-或|分隔的后缀
            r"\s*\|\s*.*$",
            r"\s*\u00b7\s*.*$",  # 中文间隔符
        ]

        cleaned = title.strip()
        for pattern in common_suffixes:
            cleaned = re.sub(pattern, "", cleaned)

        # 清理多余空格
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned.lower()

    def _select_best_bookmark(self, similar_bookmarks: List[Dict]) -> Dict:
        """从相似书签中选择最佳代表"""
        if len(similar_bookmarks) == 1:
            return similar_bookmarks[0]

        # 评分标准
        def score_bookmark(bookmark):
            score = 0.0

            # 1. 标题质量分（长度和信息量）
            title = bookmark.get("title", "")
            if title:
                score += min(len(title) / 100.0, 0.3)  # 最多0.3分

                # 有意义的单词数量
                meaningful_words = len([w for w in title.split() if len(w) > 2])
                score += min(meaningful_words / 10.0, 0.2)  # 最多0.2分

            # 2. URL质量分
            url = bookmark.get("url", "")
            if url:
                # 更短的URL通常更好（无跟踪参数）
                if len(url) < 200:
                    score += 0.1

                # HTTPS加分
                if url.startswith("https://"):
                    score += 0.1

                # 没有跟踪参数加分
                tracking_indicators = ["utm_", "fbclid", "gclid", "ref="]
                if not any(indicator in url for indicator in tracking_indicators):
                    score += 0.2

            # 3. 时间新旧度（如果有时间信息）
            add_date = bookmark.get("add_date", "")
            if add_date and add_date.isdigit():
                # 较新的书签加分
                timestamp = int(add_date)
                if timestamp > 1577836800:  # 2020年以后
                    score += 0.1

            return score

        # 计算每个书签的得分
        scored_bookmarks = [(score_bookmark(b), b) for b in similar_bookmarks]

        # 返回得分最高的
        best_score, best_bookmark = max(scored_bookmarks, key=lambda x: x[0])

        return best_bookmark

    def _get_duplicate_reason(self, original: Dict, duplicate: Dict) -> str:
        """获取重复原因说明"""
        reasons = []

        # 检查各种重复类型
        if self._exact_url_match(original, duplicate):
            reasons.append("完全相同URL")
        elif self._normalized_url_match(original, duplicate):
            reasons.append("标准化URL相似")

        title_sim = self._calculate_title_similarity(
            original.get("title", ""), duplicate.get("title", "")
        )
        if title_sim >= self.title_threshold:
            reasons.append(f"标题高度相似({title_sim:.2f})")

        if not reasons:
            reasons.append("综合相似度较高")

        return ", ".join(reasons)

    def get_duplicate_statistics(self, duplicates: List[Dict]) -> Dict:
        """获取去重统计信息"""
        stats = {
            "total_duplicates": len(duplicates),
            "duplicate_reasons": defaultdict(int),
            "duplicate_domains": defaultdict(int),
        }

        for dup in duplicates:
            reason = dup.get("duplicate_reason", "未知")
            stats["duplicate_reasons"][reason] += 1

            url = dup.get("url", "")
            if url:
                try:
                    domain = urlparse(url).netloc
                    stats["duplicate_domains"][domain] += 1
                except (ValueError, AttributeError):
                    pass

        return dict(stats)
