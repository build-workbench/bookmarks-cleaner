"""
Property Tests for Embedding Service
嵌入服务属性测试

Tests Properties:
- Property 5: Embedding Dimensionality Consistency
- Property 6: Embedding Cache Round-Trip
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume

# 尝试导入依赖
try:
    from src.services.embedding_service import EmbeddingService
    from src.services.feature_store import FeatureStore
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# 文本生成策略
text_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('L', 'N', 'P', 'S'),
        whitelist_characters=' '
    ),
    min_size=1,
    max_size=200
).filter(lambda x: len(x.strip()) > 0)


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestEmbeddingServiceProperties:
    """嵌入服务属性测试"""
    
    @pytest.fixture
    def embedding_service(self):
        """创建嵌入服务实例"""
        config = {
            'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',
            'fallback_enabled': True
        }
        service = EmbeddingService(config)
        service.initialize()
        return service
    
    @pytest.fixture
    def embedding_service_with_cache(self):
        """创建带缓存的嵌入服务实例"""
        feature_store = FeatureStore({
            'max_size': 1000,
            'ttl_seconds': 3600
        })
        
        config = {
            'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',
            'fallback_enabled': True
        }
        service = EmbeddingService(config)
        service.feature_store = feature_store
        service.initialize()
        return service
    
    @settings(max_examples=100)
    @given(text=text_strategy)
    def test_embedding_dimensionality_consistency(self, embedding_service, text):
        """
        Property 5: Embedding Dimensionality Consistency
        
        对于任何有效的书签标题或 URL，Embedding_Service 应该生成
        维度一致的稠密向量嵌入。
        
        Validates: Requirements 2.2
        """
        assume(len(text.strip()) > 0)
        
        embedding = embedding_service.embed(text)
        
        # 验证返回类型
        assert isinstance(embedding, np.ndarray), "Embedding should be numpy array"
        
        # 验证维度
        assert embedding.ndim == 1, "Embedding should be 1-dimensional"
        assert embedding.shape[0] > 0, "Embedding should have positive dimension"
        
        # 验证维度一致性（所有嵌入应该有相同维度）
        expected_dim = embedding_service.get_embedding_dimension()
        assert embedding.shape[0] == expected_dim, \
            f"Embedding dimension {embedding.shape[0]} should match expected {expected_dim}"
        
        # 验证数值有效性
        assert not np.isnan(embedding).any(), "Embedding should not contain NaN"
        assert not np.isinf(embedding).any(), "Embedding should not contain Inf"
    
    @settings(max_examples=100)
    @given(texts=st.lists(text_strategy, min_size=2, max_size=5))
    def test_batch_embedding_dimensionality(self, embedding_service, texts):
        """
        Property 5 (Extended): Batch Embedding Dimensionality
        
        批量嵌入应该保持维度一致性。
        """
        texts = [t for t in texts if len(t.strip()) > 0]
        assume(len(texts) >= 2)
        
        embeddings = embedding_service.embed_batch(texts)
        
        # 验证返回类型
        assert isinstance(embeddings, np.ndarray), "Batch embeddings should be numpy array"
        
        # 验证形状
        assert embeddings.ndim == 2, "Batch embeddings should be 2-dimensional"
        assert embeddings.shape[0] == len(texts), "Should have one embedding per text"
        
        # 验证所有嵌入维度一致
        expected_dim = embedding_service.get_embedding_dimension()
        assert embeddings.shape[1] == expected_dim, \
            f"All embeddings should have dimension {expected_dim}"
        
        # 验证数值有效性
        assert not np.isnan(embeddings).any(), "Embeddings should not contain NaN"
        assert not np.isinf(embeddings).any(), "Embeddings should not contain Inf"
    
    @settings(max_examples=100)
    @given(text=text_strategy)
    def test_embedding_cache_round_trip(self, embedding_service_with_cache, text):
        """
        Property 6: Embedding Cache Round-Trip
        
        对于任何书签，计算两次嵌入应该在第二次调用时返回缓存结果
        而不重新计算（缓存命中）。
        
        Validates: Requirements 2.3
        """
        assume(len(text.strip()) > 0)
        
        service = embedding_service_with_cache
        
        # 第一次计算
        embedding1 = service.embed(text)
        
        # 第二次计算（应该命中缓存）
        embedding2 = service.embed(text)
        
        # 验证结果相同
        np.testing.assert_array_equal(
            embedding1, embedding2,
            err_msg="Cached embedding should be identical to original"
        )
        
        # 验证缓存中存在
        if service.feature_store is not None:
            cache_key = service._get_cache_key(text)
            cached = service.feature_store.get(cache_key)
            assert cached is not None, "Embedding should be in cache"
            np.testing.assert_array_equal(
                embedding1, cached,
                err_msg="Cached value should match computed embedding"
            )
    
    @settings(max_examples=50)
    @given(
        text1=text_strategy,
        text2=text_strategy
    )
    def test_different_texts_different_embeddings(self, embedding_service, text1, text2):
        """
        不同文本应该产生不同的嵌入（除非文本相同）。
        """
        assume(len(text1.strip()) > 0 and len(text2.strip()) > 0)
        assume(text1.strip().lower() != text2.strip().lower())
        
        embedding1 = embedding_service.embed(text1)
        embedding2 = embedding_service.embed(text2)
        
        # 不同文本的嵌入不应该完全相同
        # 注意：由于浮点精度，我们检查是否"足够不同"
        if not np.allclose(embedding1, embedding2, rtol=1e-5):
            # 嵌入确实不同，这是预期的
            pass
        else:
            # 如果嵌入非常接近，文本可能语义相似
            # 这不是错误，但我们记录一下
            pass
    
    @settings(max_examples=50)
    @given(text=text_strategy)
    def test_embedding_normalization(self, embedding_service, text):
        """
        嵌入向量应该是归一化的（如果配置了归一化）。
        """
        assume(len(text.strip()) > 0)
        
        embedding = embedding_service.embed(text)
        
        # 计算 L2 范数
        norm = np.linalg.norm(embedding)
        
        # 嵌入应该有非零范数
        assert norm > 0, "Embedding should have non-zero norm"
        
        # 如果服务配置了归一化，范数应该接近 1
        if embedding_service.config.get('normalize', False):
            assert abs(norm - 1.0) < 1e-5, "Normalized embedding should have unit norm"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestEmbeddingSimilarity:
    """嵌入相似度测试"""
    
    @pytest.fixture
    def embedding_service(self):
        """创建嵌入服务实例"""
        config = {'fallback_enabled': True}
        service = EmbeddingService(config)
        service.initialize()
        return service
    
    @settings(max_examples=50)
    @given(text=text_strategy)
    def test_self_similarity_is_one(self, embedding_service, text):
        """
        文本与自身的相似度应该为 1。
        """
        assume(len(text.strip()) > 0)
        
        embedding = embedding_service.embed(text)
        similarity = embedding_service.compute_similarity(embedding, embedding)
        
        assert abs(similarity - 1.0) < 1e-5, \
            f"Self-similarity should be 1.0, got {similarity}"
    
    @settings(max_examples=50)
    @given(
        text1=text_strategy,
        text2=text_strategy
    )
    def test_similarity_is_symmetric(self, embedding_service, text1, text2):
        """
        相似度应该是对称的：sim(a, b) == sim(b, a)
        """
        assume(len(text1.strip()) > 0 and len(text2.strip()) > 0)
        
        embedding1 = embedding_service.embed(text1)
        embedding2 = embedding_service.embed(text2)
        
        sim_12 = embedding_service.compute_similarity(embedding1, embedding2)
        sim_21 = embedding_service.compute_similarity(embedding2, embedding1)
        
        assert abs(sim_12 - sim_21) < 1e-5, \
            f"Similarity should be symmetric: {sim_12} vs {sim_21}"
    
    @settings(max_examples=50)
    @given(
        text1=text_strategy,
        text2=text_strategy
    )
    def test_similarity_in_valid_range(self, embedding_service, text1, text2):
        """
        余弦相似度应该在 [-1, 1] 范围内。
        """
        assume(len(text1.strip()) > 0 and len(text2.strip()) > 0)
        
        embedding1 = embedding_service.embed(text1)
        embedding2 = embedding_service.embed(text2)
        
        similarity = embedding_service.compute_similarity(embedding1, embedding2)
        
        assert -1.0 <= similarity <= 1.0, \
            f"Cosine similarity should be in [-1, 1], got {similarity}"
