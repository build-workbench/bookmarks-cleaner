"""
AI Bookmark Classifier Core
AI书签分类器核心模块

集成了多种AI技术的智能书签分类器：
- 基于规则的快速匹配
- 机器学习模型预测
- 深度学习语义理解
- 用户行为学习
"""

import hashlib
import json
import logging
import os
import re
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Pre-compiled regex patterns for performance
_CHINESE_REGEX = re.compile(r"[\u4e00-\u9fff]")
_ENGLISH_REGEX = re.compile(r"[a-zA-Z]")

# 导入子模块
try:
    from src.classifiers.ml import MLClassifierWrapper
except ImportError:
    MLClassifierWrapper = None

# LLM 分类器
try:
    from src.classifiers.llm import LLMClassifier
except ImportError:
    LLMClassifier = None

from src.engines.rules import RuleEngine
from src.utils.category import (
    normalize_category_config,
    normalize_category_string,
    strip_category_prefix,
)
from src.utils.resource_loader import load_json_config, resolve_config_path

# 导入智能规则加载器
try:
    from src.engines.smart_loader import SmartRuleLoader, merge_with_main_config
except ImportError:
    SmartRuleLoader = None
    merge_with_main_config = None

# 导入核心分析组件
from src.engines.semantic import SemanticAnalyzer
from src.utils.profiler import UserProfiler

try:
    from src.utils.optimizer import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None  # type: ignore[misc,assignment]


@dataclass
class BookmarkFeatures:
    """书签特征"""

    url: str
    title: str
    domain: str
    path_segments: List[str]
    query_params: Dict[str, str]
    content_type: str
    language: str
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def url_length(self) -> int:
        return len(self.url)

    @property
    def title_length(self) -> int:
        return len(self.title)

    @property
    def is_secure(self) -> bool:
        return self.url.startswith("https://")

    @property
    def has_chinese(self) -> bool:
        return bool(_CHINESE_REGEX.search(self.title))


@dataclass
class ClassificationResult:
    """
    分类结果

    注意：此定义与 src.plugins.base.ClassificationResult 保持一致。
    如需修改，请同步更新两处。
    """

    category: str
    confidence: float
    subcategory: Optional[str] = None
    reasoning: List[str] = field(default_factory=list)
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    processing_time: float = 0.0
    method: str = "unknown"
    facets: Dict[str, str] = field(default_factory=dict)
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    @property
    def alternative_categories(self) -> List[Tuple[str, float]]:
        """兼容旧接口的属性别名"""
        return self.alternatives


class AIBookmarkClassifier:
    """AI智能书签分类器"""

    def __init__(
        self,
        config_path: str | None = None,
        enable_ml: bool = True,
        config: Optional[Dict] = None,
    ):
        resolved_path, self._explicit_config = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        self.enable_ml = enable_ml
        self.logger = logging.getLogger(__name__)

        # 延迟初始化组件
        self._config: Optional[Dict] = (
            self._normalize_category_config(config)
            if isinstance(config, dict)
            else None
        )
        self._rule_engine: Optional[RuleEngine] = None
        self._semantic_analyzer: Optional[SemanticAnalyzer] = None
        self._user_profiler: Optional[UserProfiler] = None
        self._performance_monitor: Optional[PerformanceMonitor] = None
        self._ml_classifier: Optional[MLClassifierWrapper] = None
        self._llm_classifier: Optional[LLMClassifier] = None

        # 缓存（OrderedDict 实现 LRU 淘汰）
        self.feature_cache: OrderedDict[str, BookmarkFeatures] = OrderedDict()
        self.classification_cache: OrderedDict[str, ClassificationResult] = (
            OrderedDict()
        )
        # 从配置读取缓存大小，默认值作为后备
        self._max_cache_size = 5000
        self._max_feature_cache_size = 10000

        # 统计
        self.stats = {
            "total_classified": 0,
            "rule_engine": 0,
            "ml_classifier": 0,
            "semantic_analyzer": 0,
            "user_profiler": 0,
            "fallback": 0,
            "cache_hits": 0,
            "average_confidence": 0.0,
            "llm": 0,
        }

    @property
    def config(self) -> Dict:
        if self._config is None:
            self._config = self._load_config()
        # 从配置更新缓存大小
        ai_settings = self._config.get("ai_settings", {})
        if "cache_size" in ai_settings:
            self._max_cache_size = ai_settings["cache_size"]
        if "feature_cache_size" in ai_settings:
            self._max_feature_cache_size = ai_settings["feature_cache_size"]
        return self._config

    @property
    def rule_engine(self) -> RuleEngine:
        if self._rule_engine is None:
            self._rule_engine = RuleEngine(self.config)
        return self._rule_engine

    @property
    def semantic_analyzer(self) -> SemanticAnalyzer:
        if self._semantic_analyzer is None:
            self._semantic_analyzer = SemanticAnalyzer()
        return self._semantic_analyzer

    @property
    def user_profiler(self) -> UserProfiler:
        if self._user_profiler is None:
            self._user_profiler = UserProfiler()
        return self._user_profiler

    @property
    def performance_monitor(self) -> Optional["PerformanceMonitor"]:
        if self._performance_monitor is None and PerformanceMonitor is not None:
            try:
                self._performance_monitor = PerformanceMonitor()
            except Exception as e:
                self.logger.warning(f"性能监控器初始化失败: {e}")
        return self._performance_monitor

    @property
    def ml_classifier(self) -> Optional[MLClassifierWrapper]:
        if self._ml_classifier is None and self.enable_ml:
            try:
                self._ml_classifier = MLClassifierWrapper()
                self.logger.info("机器学习组件已启用")
            except Exception as e:
                self.logger.warning(f"机器学习组件初始化失败: {e}")
        return self._ml_classifier

    @property
    def llm_classifier(self) -> Optional[LLMClassifier]:
        if self._llm_classifier is None and LLMClassifier is not None:
            try:
                self._llm_classifier = LLMClassifier(self.config_path)
            except Exception as e:
                self.logger.warning(f"LLM 分类器初始化失败: {e}")
        return self._llm_classifier

    def _load_config(self) -> Dict:
        config, _, explicit = load_json_config(self.config_path)

        if SmartRuleLoader is not None and merge_with_main_config is not None:
            try:
                loader = SmartRuleLoader()
                smart_rules = loader.load_all()
                config = merge_with_main_config(config, smart_rules)
                self.logger.info(f"已加载智能规则: {smart_rules.get('_meta', {})}")
            except Exception as e:
                self.logger.warning(f"智能规则加载失败，保留主配置: {e}")

        normalized = self._normalize_category_config(config)
        if not isinstance(normalized.get("category_rules"), dict) or not normalized.get(
            "category_rules"
        ):
            source = "显式配置" if explicit else "默认配置"
            raise ValueError(f"{source}缺少有效的 category_rules: {self.config_path}")
        return normalized

    @staticmethod
    def _strip_category_prefix(text: str) -> str:
        return strip_category_prefix(text)

    def _normalize_category_string(self, category: str) -> str:
        return normalize_category_string(category)

    def _normalize_category_config(self, config: Dict) -> Dict:
        return normalize_category_config(config)

    def _get_default_config(self) -> Dict:
        config, _, _ = load_json_config(None)
        return self._normalize_category_config(config)

    def extract_features(self, url: str, title: str) -> BookmarkFeatures:
        cache_key = f"{url}::{title}"
        if cache_key in self.feature_cache:
            self.feature_cache.move_to_end(cache_key)  # LRU 更新
            return self.feature_cache[cache_key]

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            path_segments = [seg for seg in parsed.path.split("/") if seg]

            # 解析查询参数
            query_params: Dict[str, str] = {}
            if parsed.query:
                for param in parsed.query.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        query_params[key] = value

            content_type = self._detect_content_type(url, title)
            language = self._detect_language(title)

            features = BookmarkFeatures(
                url=url,
                title=title,
                domain=domain,
                path_segments=path_segments,
                query_params=query_params,
                content_type=content_type,
                language=language,
            )

            # LRU 缓存淘汰
            if len(self.feature_cache) >= self._max_feature_cache_size:
                self.feature_cache.popitem(last=False)
            self.feature_cache[cache_key] = features

            return features
        except Exception as e:
            self.logger.error(f"特征提取失败 {url}: {e}")
            return BookmarkFeatures(
                url=url,
                title=title,
                domain="",
                path_segments=[],
                query_params={},
                content_type="unknown",
                language="unknown",
            )

    def classify(self, url: str, title: str) -> ClassificationResult:
        start_time = datetime.now()

        # 缓存命中
        cache_key = hashlib.md5(f"{url}::{title}".encode()).hexdigest()
        if cache_key in self.classification_cache:
            self.stats["cache_hits"] += 1
            self.classification_cache.move_to_end(cache_key)  # LRU 更新
            cached = self.classification_cache[cache_key]
            cached.processing_time = (datetime.now() - start_time).total_seconds()
            return cached

        # 特征提取
        features = self.extract_features(url, title)

        # 多方法融合
        results: List[ClassificationResult] = []

        def _collect(raw):
            """将 dict / ClassificationResult / None 统一追加到 results。"""
            if raw is None:
                return
            results.append(self._to_classification_result(raw))

        # 1) 规则引擎
        _collect(self.rule_engine.classify(features))

        # 2) 机器学习
        if self.ml_classifier:
            _collect(self.ml_classifier.classify(features))

        # 3) 语义分析
        if self.config.get("ai_settings", {}).get("use_semantic_analysis", True):
            _collect(self.semantic_analyzer.classify(features))

        # 4) 用户画像
        if self.config.get("ai_settings", {}).get("use_user_profiling", True):
            _collect(self.user_profiler.classify(features))

        # 5) LLM（可选）
        if self.llm_classifier and self.llm_classifier.enabled():
            try:
                _collect(
                    self.llm_classifier.classify(
                        url,
                        title,
                        context={
                            "domain": features.domain,
                            "content_type": features.content_type,
                            "language": features.language,
                        },
                    )
                )
            except Exception as e:
                self.logger.warning(f"LLM 分类调用失败: {e}")

        # 融合
        final_result = self._ensemble_classification(results, features)

        # 方法统计
        final_method = final_result.method
        if "rule_engine" in final_method:
            self.stats["rule_engine"] += 1
        if "machine_learning" in final_method:
            self.stats["ml_classifier"] += 1
        if "semantic_analyzer" in final_method:
            self.stats["semantic_analyzer"] += 1
        if "user_profiler" in final_method:
            self.stats["user_profiler"] += 1
        if "llm" in final_method:
            self.stats["llm"] += 1
        if final_method == "fallback":
            self.stats["fallback"] += 1

        # 时间统计
        final_result.processing_time = (datetime.now() - start_time).total_seconds()

        # 更新全局统计 & 缓存
        self._update_stats(final_result)
        self._cache_result(cache_key, final_result)
        return final_result

    @staticmethod
    def _to_classification_result(raw) -> ClassificationResult:
        """将 dict 或 ClassificationResult 统一为 ClassificationResult。"""
        if isinstance(raw, ClassificationResult):
            return raw
        if isinstance(raw, dict):
            return ClassificationResult(
                category=raw.get("category", "未分类"),
                confidence=float(raw.get("confidence", 0.0)),
                subcategory=raw.get("subcategory"),
                reasoning=raw.get("reasoning", []),
                alternatives=raw.get("alternatives", []),
                processing_time=float(raw.get("processing_time", 0.0)),
                method=raw.get("method", "unknown"),
                facets=raw.get("facets", {}),
            )
        raise TypeError(f"Unexpected classification result type: {type(raw)}")

    def _cache_result(self, cache_key: str, result: ClassificationResult):
        if cache_key in self.classification_cache:
            self.classification_cache.move_to_end(cache_key)
        else:
            if len(self.classification_cache) >= self._max_cache_size:
                self.classification_cache.popitem(last=False)  # 淘汰最久未使用
            self.classification_cache[cache_key] = result

    def _ensemble_classification(
        self, results: List[ClassificationResult], features: BookmarkFeatures
    ) -> ClassificationResult:
        if not results:
            return ClassificationResult(
                category="未分类",
                confidence=0.0,
                reasoning=["没有找到合适的分类方法"],
                method="fallback",
            )

        # 加权投票
        category_scores = defaultdict(float)
        all_reasoning: List[str] = []
        methods_used: List[str] = []
        merged_facets: Dict[str, str] = {}

        method_weights = {
            "rule_engine": 0.50,  # 提高规则引擎权重
            "machine_learning": 0.15,  # 降低 ML 权重（因为模型可能过时）
            "semantic_analyzer": 0.10,
            "user_profiler": 0.10,
            "llm": 0.50,
        }

        for res in results:
            method = res.method
            category = self._normalize_category_string(res.category) or "未分类"
            confidence = res.confidence
            reasoning = res.reasoning
            facets = res.facets or {}

            weight = method_weights.get(method, 0.1)
            category_scores[category] += confidence * weight
            all_reasoning.extend(reasoning)
            methods_used.append(method)
            # 合并分面提示（保留先到先得，避免覆盖更强信号）
            for k, v in facets.items():
                if v and k not in merged_facets:
                    merged_facets[k] = v

        if not category_scores:
            return ClassificationResult(
                category="未分类",
                confidence=0.0,
                reasoning=["所有分类方法都失败"],
                method="error",
            )

        best_category = max(category_scores, key=category_scores.get)
        top_score = category_scores[best_category]
        total_score = sum(category_scores.values())
        confidence = top_score / total_score if total_score > 0 else 0.0

        alternatives = [
            (cat, score / total_score)
            for cat, score in category_scores.items()
            if cat != best_category and total_score > 0
        ]
        alternatives.sort(key=lambda x: x[1], reverse=True)

        subcategory = self._determine_subcategory(best_category, features)

        final_method = "+".join(set(methods_used)) if methods_used else "unknown"

        threshold = self.config.get("ai_settings", {}).get("confidence_threshold", 0.7)
        try:
            threshold = float(threshold)
        except Exception:
            threshold = 0.7
        if threshold < 0:
            threshold = 0.0
        if threshold > 1:
            threshold = 1.0

        if best_category != "未分类" and confidence < threshold:
            threshold_reasoning = list(all_reasoning)
            threshold_reasoning.append(
                f"最终置信度 {confidence:.2f} 低于阈值 {threshold:.2f}，标记为未分类"
            )

            threshold_alternatives = [(best_category, confidence)]
            for alt in alternatives:
                if alt[0] != best_category:
                    threshold_alternatives.append(alt)

            return ClassificationResult(
                category="未分类",
                subcategory=None,
                confidence=confidence,
                reasoning=threshold_reasoning,
                alternatives=threshold_alternatives[:3],
                method=final_method,
                facets=merged_facets,
            )

        return ClassificationResult(
            category=best_category,
            subcategory=subcategory,
            confidence=confidence,
            reasoning=all_reasoning,
            alternatives=alternatives[:3],
            method=final_method,
            facets=merged_facets,
        )

    def _determine_subcategory(
        self, category: str, features: BookmarkFeatures
    ) -> Optional[str]:
        hierarchy = self.config.get("category_hierarchy", {})
        if isinstance(hierarchy, dict) and category in hierarchy:
            subs = hierarchy[category]
            title_lower = features.title.lower()
            for sub in subs:
                if sub.lower() in title_lower:
                    return sub
        return None

    def _detect_content_type(self, url: str, title: str) -> str:
        url_lower = url.lower()
        title_lower = title.lower()

        if any(
            domain in url_lower
            for domain in ["youtube.com", "bilibili.com", "vimeo.com"]
        ):
            return "video"
        if any(domain in url_lower for domain in ["github.com", "gitlab.com"]):
            return "code_repository"
        if any(pattern in url_lower for pattern in ["docs.", "documentation", "wiki"]):
            return "documentation"
        if any(domain in url_lower for domain in ["arxiv.org", "acm.org", "ieee.org"]):
            return "academic_paper"
        if any(keyword in title_lower for keyword in ["news", "新闻", "breaking"]):
            return "news"
        if any(
            keyword in title_lower
            for keyword in ["tool", "工具", "online", "generator"]
        ):
            return "online_tool"
        return "webpage"

    def _detect_language(self, title: str) -> str:
        if _CHINESE_REGEX.search(title):
            return "zh"
        elif _ENGLISH_REGEX.search(title):
            return "en"
        else:
            return "unknown"

    def _update_stats(self, result: ClassificationResult):
        self.stats["total_classified"] += 1
        total = self.stats["total_classified"]
        old_avg = self.stats["average_confidence"]
        self.stats["average_confidence"] = (
            old_avg * (total - 1) + result.confidence
        ) / total

    def learn_from_feedback(
        self, url: str, title: str, correct_category: str, predicted_category: str
    ):
        features = self.extract_features(url, title)
        self.user_profiler.update_preferences(features, correct_category)
        if self.ml_classifier:
            self.ml_classifier.online_learn(features, correct_category)
        # Invalidate both caches
        feature_cache_key = f"{url}::{title}"
        if feature_cache_key in self.feature_cache:
            del self.feature_cache[feature_cache_key]
        classification_cache_key = hashlib.md5(f"{url}::{title}".encode()).hexdigest()
        if classification_cache_key in self.classification_cache:
            del self.classification_cache[classification_cache_key]
        self.logger.debug(f"学习反馈: {predicted_category} -> {correct_category}")

    def get_statistics(self) -> Dict:
        total_predictions = (
            self.stats["rule_engine"]
            + self.stats["ml_classifier"]
            + self.stats["semantic_analyzer"]
            + self.stats["user_profiler"]
            + self.stats["llm"]
            + self.stats["fallback"]
        )
        return {
            "total_classified": self.stats["total_classified"],
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": self.stats["cache_hits"]
            / max(self.stats["total_classified"], 1),
            "average_confidence": self.stats["average_confidence"],
            "classification_methods": {
                "rule_engine": self.stats["rule_engine"],
                "ml_classifier": self.stats["ml_classifier"],
                "semantic_analyzer": self.stats["semantic_analyzer"],
                "user_profiler": self.stats["user_profiler"],
                "llm": self.stats["llm"],
                "unclassified (fallback)": self.stats["fallback"],
                "total": total_predictions,
            },
            "ml_enabled": self.ml_classifier is not None,
        }

    def save_model(self, path: str = "models/ai_classifier.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        model_data = {
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "user_profile": self.user_profiler.export_profile(),
            "config": self.config,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        if self.ml_classifier:
            self.ml_classifier.save_model()
        self.logger.info(f"模型已保存到: {path}")

    def load_model(self, path: str = "models/ai_classifier.json"):
        if not os.path.exists(path):
            self.logger.warning(f"模型文件不存在: {path}")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                model_data = json.load(f)
            self.stats = model_data.get("stats", self.stats)
            self.user_profiler.import_profile(model_data.get("user_profile", {}))
            if self.ml_classifier:
                self.ml_classifier.load_model()
            self.logger.info(f"模型已从 {path} 加载")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
