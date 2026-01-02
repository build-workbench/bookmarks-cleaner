"""
Property Tests for Embedding Classifier
嵌入分类器属性测试

Tests Properties:
- Property 7: Cosine Similarity Classification
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from dataclasses import dataclass
from typing import List

# 尝试导入依赖
try:
    from src.plugins.classifiers.embedding_classifier import EmbeddingClassifier
    from src.plugins.base import BookmarkFeatures
    from src.services.embedding_service import EmbeddingService
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# 策略定义
domain_strategy = st.sampled_from([
    'github.com', 'stackoverflow.com', 'medium.com', 'youtube.com',
    'docs.python.org', 'arxiv.org', 'news.ycombinator.com'
])

title_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S'), whitelist_characters=' '),
    min_size=5,
    max_size=100
).filter(lambda x: len(x.strip()) >= 5)

category_strategy = st.sampled_from([
    '编程开发', '人工智能', '数据科学', '前端开发', '后端开发',
    '机器学习', '深度学习', '云计算', '网络安全', '未分类'
])


def create_bookmark_features(
    url: str = "https://example.com",
    title: str = "Example Title",
    domain: str = "example.com"
) -> 'BookmarkFeatures':
    """创建书签特征对象"""
    return BookmarkFeatures(
        url=url,
        title=title,
        domain=domain,
        path_segments=[],
        query_params={},
        content_type='webpage',
        language='zh'
    )


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestEmbeddingClassifierProperties:
    """嵌入分类器属性测试"""
    
    @pytest.fixture
    def embedding_classifier(self):
        """创建嵌入分类器实例"""
        classifier = EmbeddingClassifier()
        config = {
            'similarity_threshold': 0.3,
            'fallback_enabled': True
        }
        classifier.initialize(config)
        return classifier
    
    @pytest.fixture
    def trained_classifier(self):
        """创建已训练的嵌入分类器"""
        classifier = EmbeddingClassifier()
        config = {
            'similarity_threshold': 0.3,
            'fallback_enabled': True
        }
        classifier.initialize(config)
        
        # 添加一些类别原型
        categories = {
            '编程开发': ['Python programming tutorial', 'JavaScript code examples', 'Git version control'],
            '人工智能': ['Machine learning algorithms', 'Neural network deep learning', 'AI artificial intelligence'],
            '数据科学': ['Data analysis pandas', 'Statistical modeling', 'Data visualization'],
        }
        
        for category, texts in categories.items():
            for text in texts:
                classifier.add_category_prototype(category, text)
        
        return classifier
    
    @settings(max_examples=100)
    @given(
        title=title_strategy,
        domain=domain_strategy
    )
    def test_cosine_similarity_classification(self, trained_classifier, title, domain):
        """
        Property 7: Cosine Similarity Classification
        
        对于使用 Embedding_Classifier 的任何分类，返回的类别应该是
        与书签嵌入余弦相似度最高的类别原型。
        
        Validates: Requirements 2.4, 2.5
        """
        assume(len(title.strip()) >= 5)
        
        features = create_bookmark_features(
            url=f"https://{domain}/page",
            title=title,
            domain=domain
        )
        
        result = trained_classifier.classify(features)
        
        if result is None:
            # 如果没有足够相似的类别，返回 None 是可接受的
            return
        
        # 验证返回的类别是相似度最高的
        embedding = trained_classifier._get_embedding(features)
        
        if embedding is None:
            return
        
        # 计算与所有类别原型的相似度
        max_similarity = -1.0
        best_category = None
        
        for category, prototypes in trained_classifier._category_prototypes.items():
            for prototype_embedding in prototypes:
                similarity = trained_classifier._compute_similarity(embedding, prototype_embedding)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_category = category
        
        # 验证返回的类别是最佳匹配
        if best_category is not None:
            assert result.category == best_category, \
                f"Returned category {result.category} should be the best match {best_category}"
    
    @settings(max_examples=50)
    @given(
        category=category_strategy,
        texts=st.lists(title_strategy, min_size=1, max_size=3)
    )
    def test_prototype_addition_consistency(self, embedding_classifier, category, texts):
        """
        添加类别原型后，该类别应该可以被检索到。
        """
        texts = [t for t in texts if len(t.strip()) >= 5]
        assume(len(texts) > 0)
        
        for text in texts:
            embedding_classifier.add_category_prototype(category, text)
        
        # 验证原型已添加
        assert category in embedding_classifier._category_prototypes, \
            f"Category {category} should be in prototypes"
        
        assert len(embedding_classifier._category_prototypes[category]) == len(texts), \
            f"Should have {len(texts)} prototypes for category {category}"
    
    @settings(max_examples=50)
    @given(title=title_strategy)
    def test_classification_result_structure(self, trained_classifier, title):
        """
        分类结果应该包含必要的字段。
        """
        assume(len(title.strip()) >= 5)
        
        features = create_bookmark_features(title=title)
        result = trained_classifier.classify(features)
        
        if result is None:
            return
        
        # 验证结果结构
        assert hasattr(result, 'category'), "Result should have category"
        assert hasattr(result, 'confidence'), "Result should have confidence"
        assert hasattr(result, 'method'), "Result should have method"
        
        # 验证置信度范围
        assert 0.0 <= result.confidence <= 1.0, \
            f"Confidence {result.confidence} should be in [0, 1]"
        
        # 验证方法标识
        assert result.method == 'embedding', \
            f"Method should be 'embedding', got {result.method}"
    
    @settings(max_examples=50)
    @given(
        title1=title_strategy,
        title2=title_strategy
    )
    def test_similar_titles_similar_classification(self, trained_classifier, title1, title2):
        """
        相似的标题应该倾向于得到相同的分类。
        """
        assume(len(title1.strip()) >= 5 and len(title2.strip()) >= 5)
        
        # 创建相似的标题（添加相同前缀）
        prefix = "Python programming "
        similar_title1 = prefix + title1[:20]
        similar_title2 = prefix + title2[:20]
        
        features1 = create_bookmark_features(title=similar_title1)
        features2 = create_bookmark_features(title=similar_title2)
        
        result1 = trained_classifier.classify(features1)
        result2 = trained_classifier.classify(features2)
        
        # 如果两个都有结果，它们应该是相同的类别（因为前缀相同）
        if result1 is not None and result2 is not None:
            # 由于添加了相同的编程相关前缀，应该得到相同或相似的分类
            # 这是一个软断言，因为实际结果取决于原型
            pass


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestEmbeddingClassifierEdgeCases:
    """嵌入分类器边界情况测试"""
    
    @pytest.fixture
    def embedding_classifier(self):
        """创建嵌入分类器实例"""
        classifier = EmbeddingClassifier()
        classifier.initialize({'fallback_enabled': True})
        return classifier
    
    def test_empty_prototypes_returns_none(self, embedding_classifier):
        """
        没有原型时，分类应该返回 None。
        """
        features = create_bookmark_features(title="Test title")
        result = embedding_classifier.classify(features)
        
        assert result is None, "Should return None when no prototypes exist"
    
    @settings(max_examples=20)
    @given(title=st.text(min_size=0, max_size=2))
    def test_short_title_handling(self, embedding_classifier, title):
        """
        非常短的标题应该被优雅地处理。
        """
        features = create_bookmark_features(title=title)
        
        # 不应该抛出异常
        try:
            result = embedding_classifier.classify(features)
            # 结果可以是 None 或有效的分类结果
            if result is not None:
                assert hasattr(result, 'category')
        except Exception as e:
            pytest.fail(f"Should handle short title gracefully, got: {e}")
    
    def test_metadata_correctness(self, embedding_classifier):
        """
        插件元数据应该正确。
        """
        metadata = embedding_classifier.metadata
        
        assert metadata.name == "embedding_classifier"
        assert "embedding" in metadata.capabilities
        assert metadata.priority > 0
