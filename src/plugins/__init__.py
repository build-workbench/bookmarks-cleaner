"""
Plugin System for CleanBook Classifier
插件式分类器架构
"""

from .base import ClassifierPlugin, PluginMetadata
from .registry import PluginRegistry

__all__ = ['ClassifierPlugin', 'PluginMetadata', 'PluginRegistry']
