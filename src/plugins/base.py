"""
Plugin Base Classes and Interfaces
插件基类和接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

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
        """验证元数据"""
        if not self.name:
            raise ValueError("Plugin name cannot be empty")
        if not self.version:
            raise ValueError("Plugin version cannot be empty")
        if not isinstance(self.capabilities, list):
            raise ValueError("Capabilities must be a list")
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")

class ClassifierPlugin(ABC):
    """分类器插件接口"""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """返回插件元数据"""
        pass
    
    @abstractmethod
    def classify(self, features: 'BookmarkFeatures') -> Optional['ClassificationResult']:
        """
        执行分类
        
        Args:
            features: 书签特征对象
            
        Returns:
            分类结果，如果无法分类则返回 None
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件
        
        Args:
            config: 插件配置字典
            
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """关闭插件，释放资源"""
        pass
    
    def supports_batch(self) -> bool:
        """是否支持批量处理"""
        return False
    
    def classify_batch(self, features_list: List['BookmarkFeatures']) -> List[Optional['ClassificationResult']]:
        """
        批量分类（默认实现）
        
        Args:
            features_list: 书签特征列表
            
        Returns:
            分类结果列表
        """
        return [self.classify(f) for f in features_list]
