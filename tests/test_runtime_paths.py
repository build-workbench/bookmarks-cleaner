import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest

from src.cli_interface import CLIInterface
from src.enhanced_cli import main as enhanced_main
from src.health_checker import run_health_check
from src.resource_loader import (
    load_json_config,
    resolve_config_path,
    resolve_taxonomy_path,
)

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main.py"
EXAMPLE = ROOT / "examples" / "demo_bookmarks.html"
PYPROJECT = ROOT / "pyproject.toml"


def test_default_config_and_taxonomy_resolve_without_repo_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config, config_path, explicit = load_json_config(None)
    assert config_path.is_file()
    assert explicit is False
    assert "category_rules" in config

    subjects = resolve_taxonomy_path(config, "subjects_file", "taxonomy/subjects.yaml")
    resource_types = resolve_taxonomy_path(
        config, "resource_types_file", "taxonomy/resource_types.yaml"
    )
    assert subjects.is_file()
    assert resource_types.is_file()


def test_health_check_is_read_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert run_health_check() is True
    assert not (tmp_path / "logs").exists()
    assert not (tmp_path / "models").exists()


def test_cli_interface_uses_resolved_config_path():
    cli = CLIInterface()
    resolved, _ = resolve_config_path(None)
    assert cli.config_path == str(resolved)


def test_enhanced_cli_main_runs_interactive_manager():
    with patch("src.enhanced_cli.InteractiveBookmarkManager") as manager_cls:
        manager = manager_cls.return_value
        enhanced_main()
        manager.run.assert_called_once()


def test_main_help_does_not_create_logs(tmp_path):
    result = subprocess.run(
        [sys.executable, str(MAIN), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert not (tmp_path / "logs").exists()


def test_main_rejects_missing_explicit_config(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(MAIN),
            "--health-check",
            "-c",
            str(tmp_path / "missing.json"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "配置或资源错误" in (result.stderr + result.stdout)


def test_main_batch_smoke(tmp_path):
    output_dir = tmp_path / "out"
    result = subprocess.run(
        [
            sys.executable,
            str(MAIN),
            "-i",
            str(EXAMPLE),
            "-o",
            str(output_dir),
            "--no-ml",
            "--limit",
            "10",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    exported = list(output_dir.glob("*.json"))
    assert exported, "expected JSON export file"
    payload = json.loads(exported[0].read_text(encoding="utf-8"))
    assert "bookmarks" in payload
    assert payload["metadata"]["processor_version"] == __import__("src").__version__


def test_package_metadata_version_matches_runtime_version():
    with PYPROJECT.open("rb") as f:
        data = tomllib.load(f)

    assert data["project"]["version"] == __import__("src").__version__


def test_optional_dependency_groups_cover_semantic_and_audit_support():
    with PYPROJECT.open("rb") as f:
        data = tomllib.load(f)

    optional = data["project"]["optional-dependencies"]

    assert "semantic" in optional
    assert "audit" in optional
    assert any(dep.startswith("sentence-transformers") for dep in optional["semantic"])
    assert any(dep.startswith("hnswlib") for dep in optional["semantic"])
    assert any(dep.startswith("cleanlab") for dep in optional["audit"])


def test_default_config_exposes_hybrid_runtime_hooks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config, _, _ = load_json_config(None)

    assert "embedding" in config
    assert "confidence_calibration" in config
    assert "feedback_loop" in config

    assert config["embedding"]["backend"] == "auto"
    assert config["confidence_calibration"]["method"] == "platt"
    assert config["feedback_loop"]["review_queue_path"]
