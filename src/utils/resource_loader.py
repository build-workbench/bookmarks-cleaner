"""Compatibility wrapper for the canonical runtime resource loader."""

from src.resource_loader import (
    ResourceResolutionError,
    default_config_path,
    load_json_config,
    resolve_config_path,
    resolve_taxonomy_path,
)

__all__ = [
    "ResourceResolutionError",
    "default_config_path",
    "load_json_config",
    "resolve_config_path",
    "resolve_taxonomy_path",
]
