"""
Plugin Registry - 插件注册中心
管理所有可插拔分类器的注册与发现
"""

import threading
import logging
from typing import Dict, List, Set, Callable, Optional
from .base import ClassifierPlugin, PluginMetadata

class PluginRegistry:
    """插件注册中心"""
    
    def __init__(self):
        self._plugins: Dict[str, ClassifierPlugin] = {}
        self._enabled: Set[str] = set()
        self._lock = threading.RLock()
        self._listeners: List[Callable] = []
        self.logger = logging.getLogger(__name__)
    
    def register(self, plugin: ClassifierPlugin) -> bool:
        """
        注册插件
        
        Args:
            plugin: 分类器插件实例
            
        Returns:
            注册是否成功
        """
        with self._lock:
            if not self._validate_plugin(plugin):
                self.logger.error(f"Plugin validation failed")
                return False
            
            name = plugin.metadata.name
            if name in self._plugins:
                self.logger.warning(f"Plugin '{name}' already registered, replacing")
            
            self._plugins[name] = plugin
            self._notify_listeners('registered', name)
            self.logger.info(f"Plugin '{name}' registered successfully")
            return True
    
    def unregister(self, name: str) -> bool:
        """
        注销插件
        
        Args:
            name: 插件名称
            
        Returns:
            注销是否成功
        """
        with self._lock:
            if name not in self._plugins:
                self.logger.warning(f"Plugin '{name}' not found")
                return False
            
            try:
                self._plugins[name].shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down plugin '{name}': {e}")
            
            del self._plugins[name]
            self._enabled.discard(name)
            self._notify_listeners('unregistered', name)
            self.logger.info(f"Plugin '{name}' unregistered")
            return True
    
    def enable(self, name: str) -> bool:
        """
        启用插件
        
        Args:
            name: 插件名称
            
        Returns:
            启用是否成功
        """
        with self._lock:
            if name not in self._plugins:
                self.logger.error(f"Cannot enable: plugin '{name}' not registered")
                return False
            
            self._enabled.add(name)
            self._notify_listeners('enabled', name)
            self.logger.info(f"Plugin '{name}' enabled")
            return True
    
    def disable(self, name: str) -> bool:
        """
        禁用插件
        
        Args:
            name: 插件名称
            
        Returns:
            禁用是否成功
        """
        with self._lock:
            if name not in self._enabled:
                self.logger.warning(f"Plugin '{name}' is not enabled")
                return False
            
            self._enabled.discard(name)
            self._notify_listeners('disabled', name)
            self.logger.info(f"Plugin '{name}' disabled")
            return True
    
    def get_enabled_plugins(self) -> List[ClassifierPlugin]:
        """
        获取已启用的插件（按优先级排序）
        
        Returns:
            已启用插件列表，按优先级升序排列
        """
        with self._lock:
            plugins = [
                self._plugins[name] 
                for name in self._enabled 
                if name in self._plugins
            ]
            return sorted(plugins, key=lambda p: p.metadata.priority)
    
    def get_plugin(self, name: str) -> Optional[ClassifierPlugin]:
        """
        获取指定插件
        
        Args:
            name: 插件名称
            
        Returns:
            插件实例，如果不存在则返回 None
        """
        with self._lock:
            return self._plugins.get(name)
    
    def is_enabled(self, name: str) -> bool:
        """
        检查插件是否已启用
        
        Args:
            name: 插件名称
            
        Returns:
            是否已启用
        """
        with self._lock:
            return name in self._enabled
    
    def list_plugins(self) -> List[str]:
        """
        列出所有已注册的插件名称
        
        Returns:
            插件名称列表
        """
        with self._lock:
            return list(self._plugins.keys())
    
    def add_listener(self, listener: Callable[[str, str], None]):
        """
        添加事件监听器
        
        Args:
            listener: 监听器函数，接收 (event, plugin_name) 参数
        """
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[str, str], None]):
        """
        移除事件监听器
        
        Args:
            listener: 监听器函数
        """
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)
    
    def _validate_plugin(self, plugin: ClassifierPlugin) -> bool:
        """
        验证插件实现
        
        Args:
            plugin: 插件实例
            
        Returns:
            验证是否通过
        """
        # 检查必需方法
        required_methods = ['classify', 'initialize', 'shutdown']
        for method in required_methods:
            if not callable(getattr(plugin, method, None)):
                self.logger.error(f"Plugin missing required method: {method}")
                return False
        
        # 检查元数据
        try:
            metadata = plugin.metadata
            if not isinstance(metadata, PluginMetadata):
                self.logger.error("Plugin metadata is not a PluginMetadata instance")
                return False
        except Exception as e:
            self.logger.error(f"Error accessing plugin metadata: {e}")
            return False
        
        return True
    
    def _notify_listeners(self, event: str, plugin_name: str):
        """
        通知监听器
        
        Args:
            event: 事件类型
            plugin_name: 插件名称
        """
        for listener in self._listeners:
            try:
                listener(event, plugin_name)
            except Exception as e:
                self.logger.error(f"Error in listener: {e}")
