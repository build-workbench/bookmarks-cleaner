"""
Placeholder Modules - Backward Compatibility Forwarding Layer

Original implementations have been split into independent modules:
- semantic_analyzer.py       -> SemanticAnalyzer
- user_profiler.py           -> UserProfiler
- deduplicator.py            -> BookmarkDeduplicator
- bookmark_health_checker.py -> HealthChecker, HealthStatus
- data_exporter.py           -> DataExporter
- performance_optimizer.py   -> PerformanceMonitor
"""

from .semantic_analyzer import SemanticAnalyzer
from .user_profiler import UserProfiler
from .deduplicator import BookmarkDeduplicator
from .bookmark_health_checker import HealthChecker, HealthStatus
from .data_exporter import DataExporter

try:
    from .performance_optimizer import PerformanceMonitor
except Exception:
    class PerformanceMonitor:
        """PerformanceMonitor fallback stub."""
        def __init__(self, **kwargs):
            self.metrics = {}
        def get_summary(self):
            return self.metrics
        def __getattr__(self, name):
            if name.startswith("_"):
                raise AttributeError(name)
            raise AttributeError(name)

# Keep datetime import for any legacy code that did:
#   from .placeholder_modules import datetime
from datetime import datetime

__all__ = [
    "SemanticAnalyzer",
    "UserProfiler",
    "BookmarkDeduplicator",
    "HealthChecker",
    "HealthStatus",
    "DataExporter",
    "PerformanceMonitor",
]
