"""
Pipeline Configuration - 管道配置

定义分类器管道的配置结构，支持多种后端和策略。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class BackendType(Enum):
    """分类器后端类型"""

    RULE = "rule"
    ML = "ml"
    LLM = "llm"
    EMBEDDING = "embedding"
    SEMANTIC = "semantic"


class FusionStrategy(Enum):
    """融合策略"""

    WEIGHTED_VOTING = "weighted_voting"
    FIRST_CONFIDENT = "first_confident"
    HIGHEST_CONFIDENCE = "highest_confidence"
    STACKING = "stacking"


@dataclass
class StageConfig:
    """单个分类阶段的配置"""

    backend: BackendType
    enabled: bool = True
    priority: int = 10
    confidence_threshold: float = 0.0
    timeout_ms: int = 5000
    fallback_on_error: bool = True
    params: Dict = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """分类器管道配置

    深度: 高（配置结构简单，但支持复杂的管道编排）
    """

    stages: List[StageConfig] = field(default_factory=list)
    fusion_strategy: FusionStrategy = FusionStrategy.FIRST_CONFIDENT
    default_confidence_threshold: float = 0.7
    enable_caching: bool = True
    max_parallel_stages: int = 4
    method_weights: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> "PipelineConfig":
        """从字典创建配置"""
        stages = []
        for stage_data in data.get("stages", []):
            backend = BackendType(stage_data.get("backend", "rule"))
            stage = StageConfig(
                backend=backend,
                enabled=stage_data.get("enabled", True),
                priority=stage_data.get("priority", 10),
                confidence_threshold=stage_data.get("confidence_threshold", 0.0),
                timeout_ms=stage_data.get("timeout_ms", 5000),
                fallback_on_error=stage_data.get("fallback_on_error", True),
                params=stage_data.get("params", {}),
            )
            stages.append(stage)

        fusion_strat = data.get("fusion_strategy", "first_confident")
        try:
            fusion = FusionStrategy(fusion_strat)
        except ValueError:
            fusion = FusionStrategy.FIRST_CONFIDENT

        return cls(
            stages=stages,
            fusion_strategy=fusion,
            default_confidence_threshold=data.get("default_confidence_threshold", 0.7),
            enable_caching=data.get("enable_caching", True),
            max_parallel_stages=data.get("max_parallel_stages", 4),
            method_weights=data.get("method_weights", {}),
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "stages": [
                {
                    "backend": stage.backend.value,
                    "enabled": stage.enabled,
                    "priority": stage.priority,
                    "confidence_threshold": stage.confidence_threshold,
                    "timeout_ms": stage.timeout_ms,
                    "fallback_on_error": stage.fallback_on_error,
                    "params": stage.params,
                }
                for stage in self.stages
            ],
            "fusion_strategy": self.fusion_strategy.value,
            "default_confidence_threshold": self.default_confidence_threshold,
            "enable_caching": self.enable_caching,
            "max_parallel_stages": self.max_parallel_stages,
            "method_weights": self.method_weights,
        }

    def get_default_config(self) -> "PipelineConfig":
        """获取默认配置"""
        return PipelineConfig(
            stages=[
                StageConfig(
                    backend=BackendType.RULE,
                    priority=10,
                    confidence_threshold=0.8,
                ),
                StageConfig(
                    backend=BackendType.ML,
                    priority=20,
                    confidence_threshold=0.7,
                ),
                StageConfig(
                    backend=BackendType.LLM,
                    priority=30,
                    enabled=False,  # 默认禁用
                    confidence_threshold=0.9,
                ),
                StageConfig(
                    backend=BackendType.EMBEDDING,
                    priority=40,
                    enabled=False,  # 默认禁用
                    confidence_threshold=0.85,
                ),
            ],
            fusion_strategy=FusionStrategy.FIRST_CONFIDENT,
            default_confidence_threshold=0.7,
            enable_caching=True,
            max_parallel_stages=4,
            method_weights={
                "rule": 1.0,
                "ml": 0.8,
                "llm": 1.0,
                "embedding": 0.7,
            },
        )
