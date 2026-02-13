"""
Semantic Analyzer - 语义分析器
基于词向量和语义相似度的书签分类
"""

import re
import math
from collections import Counter
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse


class SemanticAnalyzer:
    """语义分析器 - 基于词向量和语义相似度的分类"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.category_keywords = self._load_category_keywords()
        self.stopwords = self._load_stopwords()
        self.word_vectors = {}  # 简化的词向量存储
        self._initialize_semantic_rules()
    
    def _load_category_keywords(self) -> Dict[str, List[str]]:
        """加载分类关键词库"""
        return {
            "AI/机器学习": [
                "artificial", "intelligence", "machine", "learning", "neural", "network", 
                "deep", "tensorflow", "pytorch", "algorithm", "model", "training",
                "人工智能", "机器学习", "深度学习", "神经网络", "模型", "算法"
            ],
            "技术/编程": [
                "programming", "coding", "development", "software", "code", "developer",
                "python", "javascript", "java", "github", "api", "framework",
                "编程", "开发", "代码", "软件", "技术", "程序"
            ],
            "学习/教育": [
                "tutorial", "course", "education", "learning", "study", "guide",
                "documentation", "reference", "manual", "book", "article",
                "教程", "课程", "学习", "教育", "文档", "指南", "手册"
            ],
            "资讯": [
                "news", "article", "blog", "post", "update", "information",
                "media", "press", "report", "story", "breaking",
                "新闻", "资讯", "博客", "文章", "报道", "媒体"
            ],
            "工具/软件": [
                "tool", "software", "application", "utility", "program", "service",
                "platform", "system", "interface", "dashboard", "app",
                "工具", "软件", "应用", "平台", "系统", "服务"
            ]
        }
    
    def _load_stopwords(self) -> Set[str]:
        """加载停用词列表"""
        return {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "this", "that", "these", "those", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do",
            "does", "did", "will", "would", "could", "should", "may", "might",
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
            "一", "也", "上", "他", "她", "它", "们", "来", "去", "说", "要"
        }
    
    def _initialize_semantic_rules(self):
        """初始化语义规则"""
        self.domain_patterns = {
            r'github\.com': '技术/编程',
            r'stackoverflow\.com': '技术/编程',
            r'medium\.com': '学习/教育',
            r'youtube\.com': '娱乐/视频', 
            r'news\.|bbc\.|cnn\.|reuters\.': '新闻/资讯',
            r'wikipedia\.org': '学习/教育',
            r'docs\.|documentation': '学习/教育'
        }
    
    def classify(self, features) -> Optional[Dict]:
        """基于语义分析的分类"""
        try:
            url = features.url
            title = features.title
            domain = features.domain
            
            # 1. 域名语义分析
            domain_score = self._analyze_domain_semantics(domain)
            
            # 2. 标题语义分析
            title_score = self._analyze_title_semantics(title)
            
            # 3. URL路径语义分析
            path_score = self._analyze_path_semantics(url)
            
            # 4. 综合语义评分
            combined_scores = self._combine_semantic_scores(
                domain_score, title_score, path_score
            )
            
            if not combined_scores:
                return None
            
            # 选择最高分的分类
            best_category = max(combined_scores, key=combined_scores.get)
            confidence = combined_scores[best_category]
            
            if confidence < 0.3:  # 置信度阈值
                return None
            
            return {
                'category': best_category,
                'confidence': confidence,
                'reasoning': [f'语义分析: {best_category} (置信度: {confidence:.2f})'],
                'method': 'semantic_analyzer',
                'semantic_scores': combined_scores
            }
            
        except Exception as e:
            return None
    
    def _analyze_domain_semantics(self, domain: str) -> Dict[str, float]:
        """分析域名语义"""
        scores = {}
        
        # 检查域名模式
        for pattern, category in self.domain_patterns.items():
            if re.search(pattern, domain, re.IGNORECASE):
                scores[category] = scores.get(category, 0) + 0.8
        
        # 检查域名中的关键词
        domain_words = re.findall(r'[a-zA-Z]+', domain.lower())
        for word in domain_words:
            if len(word) > 2 and word not in self.stopwords:
                for category, keywords in self.category_keywords.items():
                    if word in [kw.lower() for kw in keywords]:
                        scores[category] = scores.get(category, 0) + 0.3
        
        return scores
    
    def _analyze_title_semantics(self, title: str) -> Dict[str, float]:
        """分析标题语义"""
        scores = {}
        
        if not title:
            return scores
        
        # 提取关键词
        title_words = self._extract_keywords(title)
        
        # 计算TF-IDF相似度
        for category, keywords in self.category_keywords.items():
            similarity = self._calculate_similarity(title_words, keywords)
            if similarity > 0:
                scores[category] = similarity
        
        return scores
    
    def _analyze_path_semantics(self, url: str) -> Dict[str, float]:
        """分析URL路径语义"""
        scores = {}
        
        try:
            parsed = urlparse(url)
            path_words = re.findall(r'[a-zA-Z]+', parsed.path.lower())
            
            for word in path_words:
                if len(word) > 2 and word not in self.stopwords:
                    for category, keywords in self.category_keywords.items():
                        if word in [kw.lower() for kw in keywords]:
                            scores[category] = scores.get(category, 0) + 0.2
        
        except Exception:
            pass
        
        return scores
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'[a-zA-Z\u4e00-\u9fff]+', text.lower())
        keywords = []
        
        for word in words:
            if len(word) > 2 and word not in self.stopwords:
                keywords.append(word)
        
        return keywords
    
    def _calculate_similarity(self, text_words: List[str], category_keywords: List[str]) -> float:
        """计算文本与分类关键词的相似度"""
        if not text_words or not category_keywords:
            return 0.0
        
        # 转换为小写进行比较
        text_words_lower = [w.lower() for w in text_words]
        category_keywords_lower = [w.lower() for w in category_keywords]
        
        # 计算交集
        intersection = set(text_words_lower) & set(category_keywords_lower)
        
        if not intersection:
            return 0.0
        
        # 计算Jaccard相似度
        union = set(text_words_lower) | set(category_keywords_lower)
        jaccard = len(intersection) / len(union)
        
        # 增加权重，考虑匹配词的重要性
        importance_weight = len(intersection) / max(len(text_words_lower), 1)
        
        return min(jaccard * 2 + importance_weight * 0.5, 1.0)
    
    def _combine_semantic_scores(self, domain_scores: Dict, title_scores: Dict, path_scores: Dict) -> Dict[str, float]:
        """综合语义评分"""
        combined = {}
        all_categories = set(domain_scores.keys()) | set(title_scores.keys()) | set(path_scores.keys())
        
        for category in all_categories:
            domain_score = domain_scores.get(category, 0) * 0.4  # 域名权重40%
            title_score = title_scores.get(category, 0) * 0.5   # 标题权重50% 
            path_score = path_scores.get(category, 0) * 0.1     # 路径权重10%
            
            combined[category] = domain_score + title_score + path_score
        
        # 归一化
        if combined:
            max_score = max(combined.values())
            if max_score > 0:
                combined = {k: v / max_score for k, v in combined.items()}
        
        return combined
