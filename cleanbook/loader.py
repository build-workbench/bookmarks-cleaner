"""书签加载器 - 从 HTML 文件加载书签"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

from cleanbook.text_utils import clean_title as clean_emoji_title

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # type: ignore[assignment]


class BookmarkLoader:
    """书签加载器，支持并行加载和 URL 验证"""

    _INVALID_URL_PREFIXES = (
        "javascript:", "data:", "chrome:", "about:", "file:", "mailto:",
    )

    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        self.stats = {
            "files_loaded": 0, "files_failed": 0,
            "total_bookmarks": 0, "invalid_urls_skipped": 0,
        }

    def load_from_files(self, input_files: List[str], limit: int = 0) -> Tuple[List[Dict], Dict]:
        self._reset_stats()
        all_bookmarks: List[Dict] = []
        with ThreadPoolExecutor(max_workers=min(len(input_files), self.max_workers)) as executor:
            futures = {executor.submit(self.load_from_file, fp): fp for fp in input_files}
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    bookmarks = future.result()
                    all_bookmarks.extend(bookmarks)
                    self.stats["files_loaded"] += 1
                except Exception as e:
                    self.logger.error(f"加载文件失败 {file_path}: {e}")
                    self.stats["files_failed"] += 1
        if limit > 0 and len(all_bookmarks) > limit:
            self.logger.info(f"应用 --limit={limit}，截断 {len(all_bookmarks)} -> {limit} 个书签")
            all_bookmarks = all_bookmarks[:limit]
        self.stats["total_bookmarks"] = len(all_bookmarks)
        return all_bookmarks, self.stats.copy()

    def load_from_file(self, file_path: str) -> List[Dict]:
        bookmarks: List[Dict] = []
        try:
            if BeautifulSoup is None:
                raise ImportError("缺少依赖 beautifulsoup4，请先安装：pip install beautifulsoup4")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            try:
                soup = BeautifulSoup(content, "lxml")
            except Exception:
                soup = BeautifulSoup(content, "html.parser")
            links = soup.find_all("a", href=True)
            for link in links:
                url = link.get("href", "").strip()
                title_raw = (link.string or link.get_text() or "").strip()
                title = clean_emoji_title(title_raw)
                if url and title and self._is_valid_url(url):
                    bookmarks.append({
                        "url": url, "title": title, "source_file": file_path,
                        "add_date": link.get("add_date", ""),
                        "last_modified": link.get("last_modified", ""),
                    })
                elif url and title:
                    self.stats["invalid_urls_skipped"] += 1
            self.logger.info(f"从 {file_path} 加载了 {len(bookmarks)} 个书签")
        except Exception as e:
            self.logger.error(f"加载文件失败 {file_path}: {e}")
            raise
        return bookmarks

    def _is_valid_url(self, url: str) -> bool:
        if not url:
            return False
        if url.lower().startswith(self._INVALID_URL_PREFIXES):
            return False
        return url.startswith(("http://", "https://"))

    def _reset_stats(self):
        self.stats = {
            "files_loaded": 0, "files_failed": 0,
            "total_bookmarks": 0, "invalid_urls_skipped": 0,
        }
