"""
BookmarkLoader - 书签加载器

负责从 HTML 文件加载书签，支持并行加载和 URL 验证。

特性：
- 并行加载多个文件
- 自动清理标题中的 emoji 前缀
- URL 有效性验证
- 详细的加载统计
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

from src.utils.text_cleaner import clean_title as clean_emoji_title

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class BookmarkLoader:
    """书签加载器
    
    深度: 高（简单接口，复杂的 HTML 解析和并行加载逻辑）
    接口: load_from_files(input_files) -> List[Dict]
    
    示例:
        loader = BookmarkLoader()
        
        # 从多个文件加载
        bookmarks = loader.load_from_files(["bookmarks1.html", "bookmarks2.html"])
        
        # 从单个文件加载
        bookmarks = loader.load_from_file("bookmarks.html")
    """
    
    # 不允许的 URL 前缀
    _INVALID_URL_PREFIXES = (
        "javascript:",
        "data:",
        "chrome:",
        "about:",
        "file:",
        "mailto:",
    )
    
    def __init__(self, max_workers: int = 8):
        """初始化书签加载器
        
        Args:
            max_workers: 并行加载的最大线程数
        """
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # 统计信息
        self.stats = {
            "files_loaded": 0,
            "files_failed": 0,
            "total_bookmarks": 0,
            "invalid_urls_skipped": 0,
        }
    
    def load_from_files(
        self,
        input_files: List[str],
        limit: int = 0
    ) -> Tuple[List[Dict], Dict]:
        """并行加载多个文件
        
        Args:
            input_files: HTML 文件路径列表
            limit: 限制加载的书签数量（0 表示不限制）
            
        Returns:
            (bookmarks, stats) 元组
        """
        self._reset_stats()
        all_bookmarks: List[Dict] = []
        
        with ThreadPoolExecutor(max_workers=min(len(input_files), self.max_workers)) as executor:
            futures = {
                executor.submit(self.load_from_file, file_path): file_path
                for file_path in input_files
            }
            
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    bookmarks = future.result()
                    all_bookmarks.extend(bookmarks)
                    self.stats["files_loaded"] += 1
                except Exception as e:
                    self.logger.error(f"加载文件失败 {file_path}: {e}")
                    self.stats["files_failed"] += 1
        
        # 应用 limit 截断
        if limit > 0 and len(all_bookmarks) > limit:
            self.logger.info(
                f"应用 --limit={limit}，截断 {len(all_bookmarks)} -> {limit} 个书签"
            )
            all_bookmarks = all_bookmarks[:limit]
        
        self.stats["total_bookmarks"] = len(all_bookmarks)
        return all_bookmarks, self.stats.copy()
    
    def load_from_file(self, file_path: str) -> List[Dict]:
        """从单个 HTML 文件加载书签
        
        Args:
            file_path: HTML 文件路径
            
        Returns:
            书签字典列表
        """
        bookmarks: List[Dict] = []
        
        try:
            if BeautifulSoup is None:
                raise ImportError(
                    "缺少依赖 beautifulsoup4（bs4），请先安装：pip install beautifulsoup4"
                )
            
            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 使用更快的解析器（lxml 如果可用）
            try:
                soup = BeautifulSoup(content, "lxml")
            except (ImportError, Exception):
                soup = BeautifulSoup(content, "html.parser")
            
            # 查找所有链接
            links = soup.find_all("a", href=True)
            
            for link in links:
                url = link.get("href", "").strip()
                title_raw = (link.string or link.get_text() or "").strip()
                
                # 清理标题中的 emoji 前缀
                title = clean_emoji_title(title_raw)
                
                # 验证 URL 有效性
                if url and title and self._is_valid_url(url):
                    bookmarks.append({
                        "url": url,
                        "title": title,
                        "source_file": file_path,
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
        """验证 URL 有效性
        
        Args:
            url: 要验证的 URL
            
        Returns:
            URL 是否有效
        """
        if not url:
            return False
        
        url_lower = url.lower()
        
        # 检查不允许的前缀
        if url_lower.startswith(self._INVALID_URL_PREFIXES):
            return False
        
        # 必须以 http:// 或 https:// 开头
        return url.startswith(("http://", "https://"))
    
    def _reset_stats(self) -> None:
        """重置统计信息"""
        self.stats = {
            "files_loaded": 0,
            "files_failed": 0,
            "total_bookmarks": 0,
            "invalid_urls_skipped": 0,
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
