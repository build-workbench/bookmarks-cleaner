import json
from pathlib import Path
from unittest.mock import Mock, patch

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
            "persist_path": str(tmp_path / "active_learning"),
        },
    }

    with patch("src.bookmark_processor.load_json_config") as mock_load:
        mock_load.return_value = (config, None, True)
        return BookmarkProcessor()


def test_export_review_queue_writes_deterministic_low_confidence_artifact(tmp_path):
    processor = _make_processor(tmp_path)
    classified_bookmarks = [
        {
            "url": "https://example.com/llm",
            "title": "LLM notes",
            "category": "AI",
            "confidence": 0.31,
            "alternatives": [("编程", 0.22)],
            "reasoning": ["low confidence"],
            "method": "embedding",
            "score_breakdown": {"raw_confidence": 0.31},
        },
        {
            "url": "https://github.com/user/repo",
            "title": "Repo",
            "category": "编程",
            "confidence": 0.91,
            "alternatives": [],
            "reasoning": ["high confidence"],
            "method": "rule_engine",
            "score_breakdown": {"raw_confidence": 0.91},
        },
    ]

    review_path = tmp_path / "review_queue.json"

    summary = processor.export_review_queue(classified_bookmarks, str(review_path))
    payload = json.loads(review_path.read_text(encoding="utf-8"))

    assert summary["items_exported"] == 1
    assert payload["items"][0]["url"] == "https://example.com/llm"
    assert payload["items"][0]["score_breakdown"]["raw_confidence"] == 0.31
    assert payload["items"][0]["alternatives"] == [["编程", 0.22]]

    processor.export_review_queue(classified_bookmarks, str(review_path))
    payload_again = json.loads(review_path.read_text(encoding="utf-8"))
    assert payload == payload_again


def test_apply_feedback_file_preserves_bookmark_attribution(tmp_path):
    from unittest.mock import MagicMock

    # 创建 mock 分类器
    mock_classifier = MagicMock()

    # 创建处理器并注入 mock 分类器
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
            "persist_path": str(tmp_path / "active_learning"),
        },
    }

    from src.container import ProcessorContainer

    container = ProcessorContainer(config=config, _classifier=mock_classifier)

    with patch("src.bookmark_processor.load_json_config") as mock_load:
        mock_load.return_value = (config, None, True)
        processor = BookmarkProcessor(container=container)

    feedback_path = tmp_path / "feedback.json"
    feedback_path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "bookmark_id": "bookmark-1",
                        "url": "https://example.com/llm",
                        "title": "LLM notes",
                        "predicted_category": "AI",
                        "correct_category": "编程",
                        "original_confidence": 0.31,
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    summary = processor.apply_feedback_file(str(feedback_path))
    labeled_samples = processor.active_learning_engine.get_labeled_samples()

    assert summary["applied_count"] == 1
    assert labeled_samples[0]["bookmark_id"] == "bookmark-1"
    mock_classifier.learn_from_feedback.assert_called_once_with(
        "https://example.com/llm",
        "LLM notes",
        "编程",
        "AI",
    )


def test_apply_feedback_file_skips_invalid_items_and_applies_valid_ones(tmp_path):
    from unittest.mock import MagicMock

    mock_classifier = MagicMock()
    from src.services.active_learning import ActiveLearningEngine

    engine = ActiveLearningEngine(
        {
            "enabled": True,
            "persist_path": str(tmp_path / "active_learning"),
        }
    )
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
        },
    }

    from src.container import ProcessorContainer

    container = ProcessorContainer(
        config=config,
        _classifier=mock_classifier,
        _active_learning_engine=engine,
    )

    with patch("src.bookmark_processor.load_json_config") as mock_load:
        mock_load.return_value = (config, None, True)
        processor = BookmarkProcessor(container=container)

    feedback_path = tmp_path / "feedback.json"
    feedback_path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "bookmark_id": "bookmark-1",
                        "url": "https://example.com/llm",
                        "title": "LLM notes",
                        "predicted_category": "AI",
                        "correct_category": "编程",
                        "original_confidence": 0.31,
                    },
                    {
                        "bookmark_id": "bookmark-2",
                        "url": "https://invalid.example.com",
                        "title": "Broken item",
                        "predicted_category": "AI",
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    summary = processor.apply_feedback_file(str(feedback_path))
    applied_payload = json.loads(
        (tmp_path / "applied_feedback.json").read_text(encoding="utf-8")
    )

    assert summary["applied_count"] == 1
    assert summary["skipped_count"] == 1
    assert applied_payload["summary"]["applied_count"] == 1
    assert applied_payload["items"][0]["bookmark_id"] == "bookmark-1"
    assert len(processor.active_learning_engine.get_labeled_samples()) == 1
    mock_classifier.learn_from_feedback.assert_called_once_with(
        "https://example.com/llm",
        "LLM notes",
        "编程",
        "AI",
    )
