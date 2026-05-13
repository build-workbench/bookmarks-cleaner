"""
Classifier Interfaces - 核心分类器接口定义

使用 Python Protocol 定义结构化子类型，允许现有类隐式实现接口，
支持依赖注入和独立测试。

深度: 高（简单接口，无需实现细节）
接缝: 所有 Protocol 都是可替换的接缝
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)

if TYPE_CHECKING:
    from src.plugins.base import BookmarkFeatures, ClassificationResult


@runtime_checkable
class IClassifier(Protocol):
    """
    分类器接口 Protocol

    所有分类器必须实现此接口。使用 runtime_checkable 允许
    isinstance() 检查，支持现有类隐式实现。

    现有兼容类:
    - AIBookmarkClassifier
    - RuleEngine (需要适配)
    - ClassifierPlugin 子类
    """

    def classify(self, features: "BookmarkFeatures") -> "ClassificationResult":
        """
        执行书签分类

        Args:
            features: 书签特征对象，包含URL、标题、域名等信息

        Returns:
            分类结果，包含类别、置信度、推理过程等
        """
        ...

    def classify_batch(
        self, features_list: List["BookmarkFeatures"]
    ) -> List["ClassificationResult"]:
        """
        批量分类（可选实现）

        Args:
            features_list: 书签特征列表

        Returns:
            分类结果列表，与输入列表一一对应

        Note:
            默认实现可逐个调用 classify()
        """
        ...


@runtime_checkable
class IDeduplicator(Protocol):
    """
    去重器接口 Protocol

    现有兼容类:
    - BookmarkDeduplicator
    """

    def remove_duplicates(
        self, bookmarks: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        移除重复书签

        Args:
            bookmarks: 书签字典列表

        Returns:
            元组 (unique_bookmarks, duplicates)
            - unique_bookmarks: 唯一书签列表
            - duplicates: 重复书签列表
        """
        ...


@runtime_checkable
class IExporter(Protocol):
    """
    导出器接口 Protocol

    现有兼容类:
    - DataExporter
    """

    def export(
        self,
        bookmarks: Dict[str, List[Dict[str, Any]]],
        output_dir: str,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        导出书签到多种格式

        Args:
            bookmarks: 分类后的书签字典，按类别组织
            output_dir: 输出目录
            formats: 输出格式列表，默认 ["html", "json", "md"]

        Returns:
            导出文件路径字典，格式 -> 文件路径
        """
        ...

    def export_json(
        self,
        bookmarks: Dict[str, List[Dict[str, Any]]],
        output_path: str,
    ) -> str:
        """
        导出为 JSON 格式

        Args:
            bookmarks: 分类后的书签字典
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        ...

    def export_html(
        self,
        bookmarks: Dict[str, List[Dict[str, Any]]],
        output_path: str,
    ) -> str:
        """
        导出为 HTML 格式

        Args:
            bookmarks: 分类后的书签字典
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        ...


@runtime_checkable
class IConfigProvider(Protocol):
    """
    配置提供者接口 Protocol

    提供统一的配置访问入口，支持点号路径解析。

    现有兼容类（需添加方法）:
    - EnhancedConfigManager
    """

    def get(self, path: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            path: 点号分隔的路径，如 "ai_settings.confidence_threshold"
            default: 默认值

        Returns:
            配置值或默认值
        """
        ...

    def get_section(self, path: str) -> Dict[str, Any]:
        """
        获取配置节

        Args:
            path: 点号分隔的路径

        Returns:
            配置节字典
        """
        ...

    def get_config(self) -> Dict[str, Any]:
        """
        获取完整配置字典

        Returns:
            完整配置字典
        """
        ...


@runtime_checkable
class IBookmarkLoader(Protocol):
    """
    书签加载器接口 Protocol

    从文件加载书签数据。
    """

    def load(self, path: str) -> List[Dict[str, Any]]:
        """
        从文件加载书签

        Args:
            path: 书签 HTML 文件路径

        Returns:
            书签字典列表，每个字典包含 url, title, add_date 等
        """
        ...

    def load_batch(self, paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量加载书签

        Args:
            paths: 文件路径列表

        Returns:
            合并后的书签列表
        """
        ...


@runtime_checkable
class IFusionEngine(Protocol):
    """
    融合引擎接口 Protocol

    融合多个分类器的结果，生成最终分类决策。
    """

    def fuse(
        self,
        results: List["ClassificationResult"],
        features: "BookmarkFeatures",
        confidence_threshold: float = 0.7,
    ) -> "ClassificationResult":
        """
        融合多个分类结果

        Args:
            results: 分类结果列表
            features: 书签特征（用于上下文）
            confidence_threshold: 置信度阈值

        Returns:
            融合后的分类结果
        """
        ...


@runtime_checkable
class ICoordinator(Protocol):
    """
    处理器协调器接口 Protocol

    协调各个 Pipeline 模块完成整个书签处理流程。
    深度: 高（简单接口，复杂的 Pipeline 协调逻辑）

    现有兼容类:
    - BookmarkProcessorCoordinator
    """

    def process_files(
        self,
        input_files: List[str],
        output_dir: str = "output",
        train_models: bool = False,
        limit: int = 0,
        review_queue_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        处理多个书签文件

        Args:
            input_files: HTML 文件路径列表
            output_dir: 输出目录
            train_models: 是否训练模型
            limit: 限制处理的书签数量
            review_queue_path: 复核队列输出路径

        Returns:
            处理统计信息
        """
        ...

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取处理统计信息

        Returns:
            统计信息字典
        """
        ...

    def export_review_queue(
        self,
        classified_bookmarks: List[Dict[str, Any]],
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        导出低置信度复核队列

        Args:
            classified_bookmarks: 已分类的书签列表
            output_path: 输出文件路径

        Returns:
            导出统计信息
        """
        ...

    def apply_feedback(self, feedback_path: str) -> Dict[str, Any]:
        """
        应用反馈数据

        Args:
            feedback_path: 反馈文件路径

        Returns:
            应用统计信息
        """
        ...

    def train_feedback(self, feedback_path: str) -> Dict[str, Any]:
        """
        使用反馈数据训练模型

        Args:
            feedback_path: 反馈文件路径

        Returns:
            训练统计信息
        """
        ...

    def audit_feedback(
        self, feedback_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        审核反馈数据质量

        Args:
            feedback_path: 反馈文件路径
            output_path: 审核报告输出路径

        Returns:
            审核统计信息
        """
        ...


@runtime_checkable
class IHealthChecker(Protocol):
    """
    健康检查器接口 Protocol

    检测书签链接的可用性。

    现有兼容类:
    - HealthChecker
    """

    def check_bookmarks(
        self, bookmarks: List[Dict[str, Any]], max_workers: int = 10
    ) -> Dict[str, Any]:
        """
        检查书签链接可用性

        Args:
            bookmarks: 书签列表
            max_workers: 最大并发数

        Returns:
            健康检查结果
        """
        ...


@runtime_checkable
class IProcessor(Protocol):
    """
    书签处理器门面接口 Protocol

    提供书签处理的完整功能入口，保持向后兼容。
    深度: 高（简单接口，隐藏复杂的处理流程）

    现有兼容类:
    - BookmarkProcessor
    """

    def process_files(
        self,
        input_files: List[str],
        output_dir: str = "output",
        train_models: bool = False,
        limit: int = 0,
        review_queue_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        处理多个书签文件

        Args:
            input_files: HTML 文件路径列表
            output_dir: 输出目录
            train_models: 是否训练模型
            limit: 限制处理的书签数量
            review_queue_path: 复核队列输出路径

        Returns:
            处理统计信息
        """
        ...

    def health_check(self, bookmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        健康检查

        Args:
            bookmarks: 书签列表

        Returns:
            健康检查结果
        """
        ...

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取处理统计信息

        Returns:
            统计信息字典
        """
        ...

    def export_review_queue(
        self,
        classified_bookmarks: List[Dict[str, Any]],
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        导出低置信度复核队列

        Args:
            classified_bookmarks: 已分类的书签列表
            output_path: 输出文件路径

        Returns:
            导出统计信息
        """
        ...

    def apply_feedback_file(self, feedback_path: str) -> Dict[str, Any]:
        """
        应用反馈数据

        Args:
            feedback_path: 反馈文件路径

        Returns:
            应用统计信息
        """
        ...

    def train_feedback_file(self, feedback_path: str) -> Dict[str, Any]:
        """
        使用反馈数据训练模型

        Args:
            feedback_path: 反馈文件路径

        Returns:
            训练统计信息
        """
        ...

    def audit_feedback_file(
        self, feedback_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        审核反馈数据质量

        Args:
            feedback_path: 反馈文件路径
            output_path: 审核报告输出路径

        Returns:
            审核统计信息
        """
        ...


# 导出所有 Protocol
__all__ = [
    "IClassifier",
    "IDeduplicator",
    "IExporter",
    "IConfigProvider",
    "IBookmarkLoader",
    "IFusionEngine",
    "ICoordinator",
    "IHealthChecker",
    "IProcessor",
]
