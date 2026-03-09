"""
Embedding Service - 嵌入服务
提供基于 Transformer 模型的文本向量化能力
"""

import logging
from typing import Optional, Dict, List, Any
import numpy as np

class EmbeddingService:
    """Transformer 嵌入服务"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化嵌入服务
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.model = None
        self.model_name = config.get('model_name', 'paraphrase-multilingual-MiniLM-L12-v2')
        self.feature_store: Optional['FeatureStore'] = None
        self._fallback_vectorizer = None
        self._fallback_fitted = False
        self._embedding_dim = config.get('embedding_dim', 384)
        self.logger = logging.getLogger(__name__)
        self._use_transformer = True
    
    def initialize(self) -> bool:
        """
        初始化嵌入模型
        
        Returns:
            初始化是否成功
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self._embedding_dim = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Loaded Transformer model: {self.model_name}")
            self._use_transformer = True
            return True
        except Exception as e:
            self.logger.warning(f"Failed to load Transformer model: {e}")
            self._init_fallback()
            self._use_transformer = False
            return False
    
    def _init_fallback(self):
        """初始化 TF-IDF 降级方案"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._fallback_vectorizer = TfidfVectorizer(
                max_features=self._embedding_dim,
                analyzer='char_wb',
                ngram_range=(1, 3),
                lowercase=True
            )
            self.logger.info("Initialized TF-IDF fallback vectorizer")
        except ImportError:
            self.logger.error("sklearn not available for TF-IDF fallback")
            self._fallback_vectorizer = None
    
    def set_feature_store(self, feature_store: 'FeatureStore'):
        """
        设置特征存储
        
        Args:
            feature_store: 特征存储实例
        """
        self.feature_store = feature_store
    
    def embed(self, text: str) -> np.ndarray:
        """
        生成文本嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if not text:
            return np.zeros(self._embedding_dim)
        
        # 检查缓存
        if self.feature_store:
            cached = self.feature_store.get(text)
            if cached is not None:
                return cached
        
        # 生成嵌入
        embedding = self._compute_embedding(text)
        
        # 缓存结果
        if self.feature_store:
            self.feature_store.put(text, embedding)
        
        return embedding
    
    def _compute_embedding(self, text: str) -> np.ndarray:
        """
        计算嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if self.model:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        elif self._fallback_vectorizer:
            return self._compute_tfidf_embedding(text)
        else:
            # 返回随机向量作为最后手段
            self.logger.warning("No embedding model available, returning random vector")
            return np.random.rand(self._embedding_dim).astype(np.float32)
    
    def _compute_tfidf_embedding(self, text: str) -> np.ndarray:
        """
        使用 TF-IDF 计算嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            TF-IDF 向量
        """
        if not self._fallback_fitted:
            try:
                self._fallback_vectorizer.fit([text])
                self._fallback_fitted = True
            except ValueError:
                # 文本太短或全是停用词，无法构建词汇表
                return np.zeros(self._embedding_dim, dtype=np.float32)
        
        try:
            embedding = self._fallback_vectorizer.transform([text]).toarray()[0]
            # 填充到目标维度
            if len(embedding) < self._embedding_dim:
                embedding = np.pad(embedding, (0, self._embedding_dim - len(embedding)))
            return embedding.astype(np.float32)
        except Exception as e:
            self.logger.error(f"TF-IDF embedding failed: {e}")
            return self._hash_embedding(text)

    def _hash_embedding(self, text: str) -> np.ndarray:
        """基于哈希的确定性嵌入，作为最终降级方案。"""
        import hashlib
        h = hashlib.sha256(text.encode('utf-8')).digest()
        rng = np.random.RandomState(int.from_bytes(h[:4], 'little'))
        vec = rng.randn(self._embedding_dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        批量生成嵌入
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入矩阵 (n_texts, embedding_dim)
        """
        if not texts:
            return np.zeros((0, self._embedding_dim))
        
        if self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.astype(np.float32)
        elif self._fallback_vectorizer:
            embeddings = []
            for text in texts:
                embeddings.append(self._compute_tfidf_embedding(text))
            return np.array(embeddings)
        else:
            return np.random.rand(len(texts), self._embedding_dim).astype(np.float32)
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        计算余弦相似度
        
        Args:
            embedding1: 向量1
            embedding2: 向量2
            
        Returns:
            余弦相似度
        """
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        sim = float(np.dot(embedding1, embedding2) / (norm1 * norm2))
        return max(-1.0, min(1.0, sim))
    
    def get_embedding_dim(self) -> int:
        """
        获取嵌入维度
        
        Returns:
            嵌入维度
        """
        return self._embedding_dim

    # 别名，保持与测试/外部代码兼容
    get_embedding_dimension = get_embedding_dim

    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return text
    
    def is_transformer_available(self) -> bool:
        """
        检查 Transformer 模型是否可用
        
        Returns:
            是否可用
        """
        return self.model is not None
