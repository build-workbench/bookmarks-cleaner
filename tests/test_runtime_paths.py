import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.cli_interface import CLIInterface
from src.enhanced_cli import main as enhanced_main
from src.health_checker import run_health_check
from src.resource_loader import load_json_config, resolve_taxonomy_path, resolve_config_path


ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main.py"
EXAMPLE = ROOT / "examples" / "demo_bookmarks.html"


def test_default_config_and_taxonomy_resolve_without_repo_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config, config_path, explicit = load_json_config(None)
    assert config_path.is_file()
    assert explicit is False
    assert "category_rules" in config

    subjects = resolve_taxonomy_path(config, "subjects_file", "taxonomy/subjects.yaml")
    resource_types = resolve_taxonomy_path(config, "resource_types_file", "taxonomy/resource_types.yaml")
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
        [sys.executable, str(MAIN), "--health-check", "-c", str(tmp_path / "missing.json")],
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
