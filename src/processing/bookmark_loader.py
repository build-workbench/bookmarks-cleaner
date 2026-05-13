"""
Bookmark Loader - 书签加载器

负责从 HTML 文件加载书签数据。

深度: 高（简单接口，复杂的 HTML 解析逻辑）
接缝: IBookmarkLoader Protocol
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class BookmarkLoader:
    """
    书签加载器

    从浏览器导出的 HTML 文件中加载书签数据。

    示例:
        loader = BookmarkLoader()
        bookmarks = loader.load("bookmarks.html")
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load(self, path: str) -> List[Dict[str, Any]]:
        """
        从文件加载书签

        Args:
            path: 书签 HTML 文件路径

        Returns:
            书签字典列表，每个字典包含 url, title, add_date 等
        """
        if BeautifulSoup is None:
            raise ImportError(
                "缺少依赖 beautifulsoup4（bs4），请先安装：pip install beautifulsoup4"
            )

        file_path = Path(path)
        if not file_path.exists():
            self.logger.error(f"文件不存在: {path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            soup = BeautifulSoup(content, "html.parser")
            bookmarks = []

            for link in soup.find_all("a"):
                href = link.get("href", "")
                title = link.string or link.get_text() or ""

                if not href or href.startswith("javascript:"):
                    continue

                bookmark = {
                    "url": href,
                    "title": title.strip(),
                    "add_date": link.get("add_date", ""),
                    "icon": link.get("icon", ""),
                }

                # 尝试获取父级文件夹作为分类提示
                parent = link.find_parent("dt")
                if parent:
                    folder = parent.find_previous("h3")
                    if folder:
                        bookmark["folder_hint"] = folder.string or folder.get_text()

                bookmarks.append(bookmark)

            self.logger.info(f"从 {path} 加载了 {len(bookmarks)} 个书签")
            return bookmarks

        except Exception as e:
            self.logger.error(f"加载书签文件失败 {path}: {e}")
            return []

    def load_batch(self, paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量加载书签

        Args:
            paths: 文件路径列表

        Returns:
            合并后的书签列表
        """
        all_bookmarks = []
        for path in paths:
            bookmarks = self.load(path)
            all_bookmarks.extend(bookmarks)
        return all_bookmarks

    def parse_bookmark_html(self, content: str) -> List[Dict[str, Any]]:
        """
        解析书签 HTML 内容

        Args:
            content: HTML 内容字符串

        Returns:
            书签列表
        """
        if BeautifulSoup is None:
            return []

        soup = BeautifulSoup(content, "html.parser")
        bookmarks = []

        for link in soup.find_all("a"):
            href = link.get("href", "")
            title = link.string or link.get_text() or ""

            if not href or href.startswith("javascript:"):
                continue

            bookmarks.append(
                {
                    "url": href,
                    "title": title.strip(),
                    "add_date": link.get("add_date", ""),
                }
            )

        return bookmarks
