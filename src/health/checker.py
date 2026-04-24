"""Compatibility exports for system health checks."""

from src.health_checker import run_health_check

from .bookmark_checker import HealthChecker

__all__ = ["HealthChecker", "run_health_check"]
