"""
HTML Parser - HTML解析器

负责解析浏览器导出的书签HTML文件，提取书签信息。
"""

import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class HTMLParser:
    """书签HTML文件解析器

    深度: 高（简单接口，复杂的HTML处理逻辑）
    接口: parse(html_file) -> List[Bookmark]
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse(self, file_path: str) -> List[Dict]:
        """解析HTML书签文件

        Args:
            file_path: HTML文件路径

        Returns:
            书签列表，每个书签包含 url, title, add_date, icon 等字段
        """
        if BeautifulSoup is None:
            raise ImportError("beautifulsoup4 is required for HTML parsing")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()

        soup = BeautifulSoup(content, "lxml")
        bookmarks = []

        for link in soup.find_all("a"):
            href = link.get("href", "").strip()
            if not href or not self._is_valid_url(href):
                continue

            title = link.get_text(strip=True)
            if not title:
                title = href

            bookmark = {
                "url": href,
                "title": title,
                "add_date": link.get("add_date"),
                "icon": link.get("icon"),
                "tags": link.get("tags", ""),
            }

            # 提取父级文件夹路径
            parents = []
            for parent in link.find_parents(["dt", "dl"]):
                if parent.name == "dt":
                    h3 = parent.find("h3")
                    if h3:
                        parents.insert(0, h3.get_text(strip=True))
                        break

            if parents:
                bookmark["folder"] = parents[0]

            bookmarks.append(bookmark)

        self.logger.info(f"从 {file_path} 解析出 {len(bookmarks)} 个书签")
        return bookmarks

    def _is_valid_url(self, url: str) -> bool:
        """检查URL是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
