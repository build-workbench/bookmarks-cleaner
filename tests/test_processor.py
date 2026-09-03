"""处理器集成测试"""

import os
from cleanbookmarks.processor import BookmarkProcessor


class TestBookmarkProcessor:
    def test_process_demo(self):
        processor = BookmarkProcessor()
        results = processor.process_files(
            input_files=["examples/demo_bookmarks.html"],
            output_dir="output_test",
        )
        assert results["total_bookmarks"] > 0
        assert results["processed_bookmarks"] > 0
        assert results["processed_bookmarks"] <= results["total_bookmarks"]
        # Check output files exist
        files = os.listdir("output_test")
        assert any(f.endswith(".html") for f in files)
        assert any(f.endswith(".json") for f in files)
        assert any(f.endswith(".markdown") for f in files)

    def test_classifier_stats(self):
        processor = BookmarkProcessor()
        stats = processor.get_classifier_statistics()
        assert "total_classified" in stats
        assert "classification_methods" in stats
