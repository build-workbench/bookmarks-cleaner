"""
Plugin Base Classes and Interfaces
插件基类和接口定义
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Forward declaration for type hints - actual import in TYPE_CHECKING block
if TYPE_CHECKING:
    pass


@dataclass
class BookmarkFeatures:
    """书签特征数据类"""

    url: str
    title: str
    domain: str
    path_segments: List[str]
    query_params: Dict[str, str]
    content_type: str
    language: str

    @property
    def url_length(self) -> int:
        """URL长度"""
        return len(self.url)

    @property
    def title_length(self) -> int:
        """标题长度"""
        return len(self.title)

    @property
    def is_secure(self) -> bool:
        """是否为HTTPS安全链接"""
        return self.url.startswith("https://")


@dataclass
class ClassificationResult:
    """
    分类结果数据类

    统一的分类结果定义，被所有分类器插件使用。

    Attributes:
        category: 分类结果
        confidence: 置信度 (0.0-1.0)
        subcategory: 可选的子分类
        reasoning: 分类推理过程
        alternatives: 备选分类列表，每项为 (分类名, 置信度) 元组
        processing_time: 处理耗时（秒）
        method: 分类方法标识
        facets: 额外的分面信息字典
        score_breakdown: 各维度得分明细（兼容旧接口）
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


@dataclass
class PluginMetadata:
    """插件元数据"""

    name: str
    version: str
    capabilities: List[str]
    author: str = ""
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    priority: int = 100  # 数值越小优先级越高

    def __post_init__(self):
        """验证元数据有效性"""
        if not self.name:
            raise ValueError("Plugin name cannot be empty")
        if not self.version:
            raise ValueError("Plugin version cannot be empty")
        if not isinstance(self.capabilities, list):
            raise ValueError("Capabilities must be a list")
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")


class ClassifierPlugin(ABC):
    """
    分类器插件抽象基类

    所有分类器插件必须继承此类并实现抽象方法。
    插件通过 initialize() 初始化，通过 classify() 执行分类，
    最后通过 shutdown() 清理资源。
    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        返回插件元数据

        Returns:
            PluginMetadata: 包含插件名称、版本、能力等信息的元数据对象
        """
        ...

    @abstractmethod
    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        """
        执行书签分类

        Args:
            features: 书签特征对象，包含URL、标题、域名等信息

        Returns:
            分类结果，如果无法分类则返回 None

        Note:
            实现者应确保此方法线程安全，因为可能在并发环境中被调用。
        """
        ...

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件

        Args:
            config: 插件配置字典，通常来自 config.json

        Returns:
            初始化是否成功

        Note:
            初始化失败时，插件应记录错误日志并返回 False，
            系统将跳过此插件继续执行其他分类器。
        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """
        关闭插件，释放资源

        Note:
            实现者应在此方法中保存模型状态、关闭连接等清理工作。
        """
        ...

    def supports_batch(self) -> bool:
        """
        检查是否支持批量处理

        Returns:
            默认返回 False，支持批量处理的插件应重写此方法
        """
        return False

    def classify_batch(
        self, features_list: List[BookmarkFeatures]
    ) -> List[Optional[ClassificationResult]]:
        """
        批量分类（默认实现）

        Args:
            features_list: 书签特征列表

        Returns:
            分类结果列表，与输入列表一一对应

        Note:
            这是默认的顺序实现。支持高效批量处理的插件应重写此方法
            以利用批处理优化（如GPU加速、批量API调用等）。
        """
        return [self.classify(f) for f in features_list]
