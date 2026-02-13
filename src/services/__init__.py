"""
Services Module
核心服务层

所有服务均为可选组件，缺少依赖时跳过导入而非报错。
"""

__all__ = [
    'FeatureStore',
    'EmbeddingService',
    'ConfidenceCalibrator',
    'ActiveLearningEngine',
    'IncrementalTrainer',
    'TaxonomyService',
    'PerformanceMonitor'
]

def __getattr__(name: str):
    """按需延迟导入，缺少依赖时抛出 ImportError 而非启动时崩溃。"""
    _mapping = {
        'FeatureStore': '.feature_store',
        'EmbeddingService': '.embedding_service',
        'ConfidenceCalibrator': '.confidence_calibrator',
        'ActiveLearningEngine': '.active_learning',
        'IncrementalTrainer': '.incremental_trainer',
        'TaxonomyService': '.taxonomy_service',
        'PerformanceMonitor': '.performance_monitor',
    }
    if name in _mapping:
        import importlib
        module = importlib.import_module(_mapping[name], __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
