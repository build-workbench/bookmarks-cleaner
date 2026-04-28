import json
from pathlib import Path
from unittest.mock import patch

from src.bookmark_processor import BookmarkProcessor


def _make_processor(tmp_path: Path) -> BookmarkProcessor:
    config = {
        "category_rules": {
            "编程": {
                "rules": [{"match": "domain", "keywords": ["github.com"], "weight": 15}]
            }
        },
        "ai_settings": {"confidence_threshold": 0.7},
        "category_order": ["编程"],
        "feedback_loop": {
            "enabled": True,
            "review_queue_path": str(tmp_path / "review_queue.json"),
            "applied_feedback_path": str(tmp_path / "applied_feedback.json"),
            "model_dir": str(tmp_path / "models" / "incremental"),
            "audit": {
                "enabled": True,
                "output_path": str(tmp_path / "feedback_audit.json"),
            },
        },
    }

    with patch("src.bookmark_processor.load_json_config") as mock_load:
        mock_load.return_value = (config, None, True)
        return BookmarkProcessor()


def _write_feedback_file(path: Path):
    path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "bookmark_id": "bookmark-1",
                        "url": "https://example.com/llm",
                        "title": "LLM notes",
                        "predicted_category": "AI",
                        "correct_category": "编程",
                        "confidence": 0.31,
                        "alternatives": [["编程", 0.22]],
                    },
                    {
                        "bookmark_id": "bookmark-2",
                        "url": "https://github.com/user/repo",
                        "title": "Repo",
                        "predicted_category": "编程",
                        "correct_category": "编程",
                        "confidence": 0.92,
                        "alternatives": [],
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def test_train_feedback_file_creates_incremental_version_history(tmp_path):
    processor = _make_processor(tmp_path)
    feedback_path = tmp_path / "feedback.json"
    _write_feedback_file(feedback_path)

    summary = processor.train_feedback_file(str(feedback_path))
    history_path = tmp_path / "models" / "incremental" / "version_history.json"

    assert summary["trained_samples"] == 2
    assert summary["version_count"] >= 1
    assert summary["current_version"]
    assert history_path.exists()


def test_audit_feedback_file_gracefully_falls_back_without_cleanlab(tmp_path):
    processor = _make_processor(tmp_path)
    feedback_path = tmp_path / "feedback.json"
    _write_feedback_file(feedback_path)
    audit_path = tmp_path / "audit.json"

    with patch.object(
        BookmarkProcessor,
        "_get_cleanlab_find_label_issues",
        return_value=None,
        create=True,
    ):
        summary = processor.audit_feedback_file(str(feedback_path), str(audit_path))

    payload = json.loads(audit_path.read_text(encoding="utf-8"))

    assert summary["audit_backend"] == "builtin"
    assert payload["summary"]["total_items"] == 2
    assert payload["summary"]["disagreement_count"] == 1
