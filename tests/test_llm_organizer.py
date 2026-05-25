import json
import os
import unittest
from unittest.mock import MagicMock, patch

from src.llm.organizer import LLMBookmarkOrganizer


class TestLLMBookmarkOrganizer(unittest.TestCase):
    def setUp(self):
        self.base_config = {
            "llm": {
                "enable": True,
                "provider": "openai",
                "base_url": "https://api.openai.com",
                "model": "gpt-4o-mini",
                "api_key_env": "OPENAI_API_KEY",
                "temperature": 0.0,
                "top_p": 1.0,
                "timeout_seconds": 25,
                "max_retries": 0,
                "organizer": {
                    "enable": True,
                    "max_examples_per_category": 5,
                    "max_domains_per_category": 5,
                    "max_tokens": 512,
                    "force_json": True,
                },
            }
        }

    def test_disabled_by_configuration(self):
        config = {"llm": {"enable": False}}
        organizer = LLMBookmarkOrganizer(config=config)
        self.assertFalse(organizer.enabled())
        self.assertIsNone(organizer.organize([], baseline={}))

    @patch.dict(os.environ, {}, clear=True)
    def test_skips_when_api_key_missing(self):
        organizer = LLMBookmarkOrganizer(config=self.base_config)
        self.assertIsNone(
            organizer.organize(
                bookmarks=[
                    {
                        "url": "https://example.com",
                        "title": "Example",
                        "category": "测试",
                        "confidence": 0.7,
                    }
                ],
                baseline={},
            )
        )

    @patch("src.llm.organizer.requests.post")
    def test_successful_reorganization_and_cache(self, mock_post):
        os.environ["OPENAI_API_KEY"] = "fake-key"
        organizer = LLMBookmarkOrganizer(config=self.base_config)

        bookmarks = [
            {
                "url": "https://openai.com",
                "title": "OpenAI API",
                "category": "🤖 AI/工具",
                "confidence": 0.92,
            },
            {
                "url": "https://docs.python.org",
                "title": "Python 文档",
                "category": "💻 编程/文档",
                "confidence": 0.88,
            },
            {
                "url": "https://realpython.com",
                "title": "Real Python 教程",
                "category": "💻 编程/教程",
                "confidence": 0.84,
            },
        ]

        baseline = {
            "🤖 AI": {"_items": bookmarks[:1], "_subcategories": {}},
            "💻 编程": {
                "_items": [],
                "_subcategories": {"文档": {"_items": [bookmarks[1]]}},
            },
        }

        llm_output = {
            "category_mapping": {
                "🤖 AI/工具": {"primary": "🤖 AI", "secondary": "工具"},
                "💻 编程/文档": {"primary": "💻 编程", "secondary": "文档"},
                "💻 编程/教程": {"primary": "💻 编程", "secondary": "教程"},
            },
            "primary_order": ["💻 编程", "🤖 AI"],
            "secondary_order": {"💻 编程": ["文档", "教程"], "🤖 AI": ["工具"]},
            "fallback_primary": "📂 其他",
            "fallback_secondary_label": "待整理",
            "category_insights": [
                {
                    "primary": "💻 编程",
                    "summary": "聚焦编程学习资源",
                    "recommendations": [],
                }
            ],
            "notes": ["按媒体类型细分效果最佳"],
        }

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "choices": [
                {"message": {"content": json.dumps(llm_output, ensure_ascii=False)}}
            ]
        }
        mock_post.return_value = response

        try:
            result = organizer.organize(bookmarks, baseline=baseline)
            self.assertIsNotNone(result)
            organized = result["organized"]
            self.assertIn("💻 编程", organized)
            self.assertIn("文档", organized["💻 编程"]["_subcategories"])
            self.assertTrue(result["meta"]["organizer_stats"]["calls"] >= 1)

            mock_post.assert_called_once()

            mock_post.reset_mock()
            second = organizer.organize(bookmarks, baseline=baseline)
            self.assertIsNotNone(second)
            mock_post.assert_not_called()
            self.assertEqual(second["organized"], organized)
            stats = organizer.get_stats()
            self.assertGreaterEqual(stats.get("cache_hits", 0), 1)
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
