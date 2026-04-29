"""Backward Compatibility Forwarding Layer (DEPRECATED)

此模块已弃用。请直接从对应模块导入：

    from src.engines.semantic import SemanticAnalyzer
    from src.utils.profiler import UserProfiler
    from src.data.deduplicator import BookmarkDeduplicator
    from src.health.bookmark_checker import HealthChecker, HealthStatus
    from src.data.exporter import DataExporter
    from src.utils.optimizer import PerformanceMonitor
"""

import warnings as _warnings

_warnings.warn(
    "placeholder_modules is deprecated; import from the real modules directly.",
    DeprecationWarning,
    stacklevel=2,
)

from src.data.deduplicator import BookmarkDeduplicator  # noqa: F401
from src.data.exporter import DataExporter  # noqa: F401
from src.engines.semantic import SemanticAnalyzer  # noqa: F401
from src.health.bookmark_checker import HealthChecker, HealthStatus  # noqa: F401
from src.utils.profiler import UserProfiler  # noqa: F401

try:
    from src.utils.optimizer import PerformanceMonitor  # noqa: F401
except Exception:
    PerformanceMonitor = None  # type: ignore[misc,assignment]

__all__ = [
    "SemanticAnalyzer",
    "UserProfiler",
    "BookmarkDeduplicator",
    "HealthChecker",
    "HealthStatus",
    "DataExporter",
    "PerformanceMonitor",
]
