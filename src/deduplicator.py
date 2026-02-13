"""
Bookmark Deduplicator - 书签去重器
高级相似度检测和自动合并
"""

import re
import hashlib
from urllib.parse import urlparse, parse_qs, urljoin
from typing import List, Dict, Tuple, Set
from difflib import SequenceMatcher
from collections import defaultdict


class BookmarkDeduplicator:
    """书签去重器 - 高级相似度检测和去重"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.title_threshold = 0.8
        self.url_threshold = 0.9
        
        # 初始化去重策略
        self.dedup_strategies = [
            self._exact_url_match,
            self._normalized_url_match,
            self._content_similarity_match,
            self._title_similarity_match,
            self._domain_path_similarity
        ]
    
    def remove_duplicates(self, bookmarks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """移除重复书签 - 高级算法"""
        if not bookmarks:
            return [], []
        
        unique_bookmarks = []
        duplicates = []
        processed_indices = set()
        
        # 为每个书签生成唯一标识
        for i, bookmark in enumerate(bookmarks):
            bookmark['_original_index'] = i
        
        # 逐一比较书签
        for i, bookmark1 in enumerate(bookmarks):
            if i in processed_indices:
                continue
            
            # 找到所有与当前书签相似的书签
            similar_group = [bookmark1]
            similar_indices = {i}
            
            for j, bookmark2 in enumerate(bookmarks[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                if self._are_duplicates(bookmark1, bookmark2):
                    similar_group.append(bookmark2)
                    similar_indices.add(j)
            
            # 处理相似组
            if len(similar_group) > 1:
                # 选择最佳代表
                best_bookmark = self._select_best_bookmark(similar_group)
                unique_bookmarks.append(best_bookmark)
                
                # 其余的标记为重复
                for bookmark in similar_group:
                    if bookmark != best_bookmark:
                        bookmark['duplicate_reason'] = self._get_duplicate_reason(best_bookmark, bookmark)
                        duplicates.append(bookmark)
            else:
                # 没有重复，直接添加
                unique_bookmarks.append(bookmark1)
            
            # 标记为已处理
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
        return bookmark1.get('url', '') == bookmark2.get('url', '')
    
    def _normalized_url_match(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """标准化URL匹配"""
        url1_norm = self._normalize_url(bookmark1.get('url', ''))
        url2_norm = self._normalize_url(bookmark2.get('url', ''))
        
        if not url1_norm or not url2_norm:
            return False
        
        # 计算URL相似度
        similarity = self._calculate_url_similarity(url1_norm, url2_norm)
        return similarity >= self.url_threshold
    
    def _content_similarity_match(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """内容相似度匹配"""
        # 综合考虑标题和URL的相似度
        title_sim = self._calculate_title_similarity(
            bookmark1.get('title', ''), bookmark2.get('title', '')
        )
        
        url_sim = self._calculate_url_similarity(
            bookmark1.get('url', ''), bookmark2.get('url', '')
        )
        
        # 加权平均
        combined_similarity = (title_sim * 0.6 + url_sim * 0.4)
        return combined_similarity >= self.similarity_threshold
    
    def _title_similarity_match(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """标题相似度匹配"""
        title1 = bookmark1.get('title', '').strip()
        title2 = bookmark2.get('title', '').strip()
        
        if not title1 or not title2:
            return False
        
        similarity = self._calculate_title_similarity(title1, title2)
        return similarity >= self.title_threshold
    
    def _domain_path_similarity(self, bookmark1: Dict, bookmark2: Dict) -> bool:
        """域名和路径相似度匹配"""
        try:
            parsed1 = urlparse(bookmark1.get('url', ''))
            parsed2 = urlparse(bookmark2.get('url', ''))
            
            # 域名必须相同
            if parsed1.netloc != parsed2.netloc:
                return False
            
            # 计算路径相似度
            path_sim = SequenceMatcher(None, parsed1.path, parsed2.path).ratio()
            
            # 如果路径非常相似，认为是重复
            return path_sim >= 0.9
            
        except Exception:
            return False
    
    def _normalize_url(self, url: str) -> str:
        """标准化URL"""
        if not url:
            return ''
        
        try:
            parsed = urlparse(url.lower().strip())
            
            # 移除常见的跟踪参数
            tracking_params = {
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
                'fbclid', 'gclid', 'msclkid', '_ga', 'ref', 'source'
            }
            
            # 过滤查询参数
            query_params = parse_qs(parsed.query)
            filtered_params = {
                k: v for k, v in query_params.items() 
                if k not in tracking_params
            }
            
            # 重建查询字符串
            query_string = '&'.join([f"{k}={'&'.join(v)}" for k, v in sorted(filtered_params.items())])
            
            # 标准化路径（移除末尾斜杠）
            path = parsed.path.rstrip('/')
            
            # 重构URL
            normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
            if query_string:
                normalized += f"?{query_string}"
            
            return normalized
            
        except Exception:
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
            
            # 查询参数相似度
            query_sim = SequenceMatcher(None, parsed1.query, parsed2.query).ratio()
            
            # 加权平均
            overall_sim = domain_sim * 0.5 + path_sim * 0.3 + query_sim * 0.2
            
            return overall_sim
            
        except Exception:
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
            return ''
        
        # 移除常见的网站后缀
        common_suffixes = [
            r'\s*[-|]\s*.*$',  # 移除用-或|分隔的后缀
            r'\s*\|\s*.*$',
            r'\s*\u00b7\s*.*$',  # 中文间隔符
        ]
        
        cleaned = title.strip()
        for pattern in common_suffixes:
            cleaned = re.sub(pattern, '', cleaned)
        
        # 清理多余空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned.lower()
    
    def _select_best_bookmark(self, similar_bookmarks: List[Dict]) -> Dict:
        """从相似书签中选择最佳代表"""
        if len(similar_bookmarks) == 1:
            return similar_bookmarks[0]
        
        # 评分标准
        def score_bookmark(bookmark):
            score = 0.0
            
            # 1. 标题质量分（长度和信息量）
            title = bookmark.get('title', '')
            if title:
                score += min(len(title) / 100.0, 0.3)  # 最多0.3分
                
                # 有意义的单词数量
                meaningful_words = len([w for w in title.split() if len(w) > 2])
                score += min(meaningful_words / 10.0, 0.2)  # 最多0.2分
            
            # 2. URL质量分
            url = bookmark.get('url', '')
            if url:
                # 更短的URL通常更好（无跟踪参数）
                if len(url) < 200:
                    score += 0.1
                
                # HTTPS加分
                if url.startswith('https://'):
                    score += 0.1
                
                # 没有跟踪参数加分
                tracking_indicators = ['utm_', 'fbclid', 'gclid', 'ref=']
                if not any(indicator in url for indicator in tracking_indicators):
                    score += 0.2
            
            # 3. 时间新旧度（如果有时间信息）
            add_date = bookmark.get('add_date', '')
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
            original.get('title', ''), duplicate.get('title', '')
        )
        if title_sim >= self.title_threshold:
            reasons.append(f"标题高度相似({title_sim:.2f})")
        
        if not reasons:
            reasons.append("综合相似度较高")
        
        return ", ".join(reasons)
    
    def get_duplicate_statistics(self, duplicates: List[Dict]) -> Dict:
        """获取去重统计信息"""
        stats = {
            'total_duplicates': len(duplicates),
            'duplicate_reasons': defaultdict(int),
            'duplicate_domains': defaultdict(int)
        }
        
        for dup in duplicates:
            reason = dup.get('duplicate_reason', '未知')
            stats['duplicate_reasons'][reason] += 1
            
            url = dup.get('url', '')
            if url:
                try:
                    domain = urlparse(url).netloc
                    stats['duplicate_domains'][domain] += 1
                except Exception:
                    pass
        
        return dict(stats)
