"""
User Profiler Plugin - 用户画像分类器插件
将现有 UserProfiler 封装为 ClassifierPlugin 接口
"""

import logging
from typing import Any, Dict, Optional

from ..base import (
    BookmarkFeatures,
    ClassificationResult,
    ClassifierPlugin,
    PluginMetadata,
)


class UserProfilerPlugin(ClassifierPlugin):
    """用户画像分类器插件"""

    def __init__(self, user_profiler=None):
        """
        初始化用户画像分类器插件

        Args:
            user_profiler: 可选的 UserProfiler 实例
        """
        self._user_profiler = user_profiler
        self._config: Dict[str, Any] = {}
        self._initialized = False
        self.logger = logging.getLogger(__name__)

    @property
    def metadata(self) -> PluginMetadata:
        """返回插件元数据"""
        return PluginMetadata(
            name="user_profiler",
            version="1.0.0",
            capabilities=["user_profiling", "preference_learning", "time_decay"],
            author="CleanBook",
            description="基于用户历史偏好和行为的分类器",
            dependencies=[],
            priority=70,  # 中等优先级
        )

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        Args:
            config: 配置字典

        Returns:
            初始化是否成功
        """
        try:
            self._config = config

            if self._user_profiler is None:
                from src.utils.profiler import UserProfiler
                self._user_profiler = UserProfiler()

            self._initialized = True
            self.logger.info("UserProfilerPlugin initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize UserProfilerPlugin: {e}")
            return False

    def shutdown(self) -> None:
        """关闭插件"""
        self._user_profiler = None
        self._initialized = False
        self.logger.info("UserProfilerPlugin shutdown")

    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        """
        执行分类

        Args:
            features: 书签特征

        Returns:
            分类结果，如果无法分类则返回 None
        """
        if not self._initialized or self._user_profiler is None:
            return None

        try:
            result = self._user_profiler.classify(features)

            if result is None:
                return None

            # 如果已经是 ClassificationResult，直接返回
            if isinstance(result, ClassificationResult):
                return result

            # 转换字典结果
            if isinstance(result, dict):
                return ClassificationResult(
                    category=result.get("category", "未分类"),
                    confidence=float(result.get("confidence", 0.0)),
                    reasoning=result.get("reasoning", []),
                    method="user_profiler",
                    facets=result.get("facets", {}),
                )

            return None

        except Exception as e:
            self.logger.debug(f"User profiler classification failed: {e}")
            return None
