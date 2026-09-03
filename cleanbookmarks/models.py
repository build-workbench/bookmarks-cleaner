"""核心数据结构"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from cleanbookmarks.text_utils import CHINESE_REGEX


@dataclass
class BookmarkFeatures:
    """书签特征"""

    url: str
    title: str
    domain: str
    path_segments: List[str]
    query_params: Dict[str, str]
    content_type: str
    language: str
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_secure(self) -> bool:
        return self.url.startswith("https://")

    @property
    def has_chinese(self) -> bool:
        return bool(CHINESE_REGEX.search(self.title))

    @classmethod
    def from_url_title(cls, url: str, title: str, content_type: str = "webpage", language: str = "unknown") -> "BookmarkFeatures":
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        path_segments = [seg for seg in parsed.path.split("/") if seg]
        query_params: Dict[str, str] = {}
        if parsed.query:
            for param in parsed.query.split("&"):
                if "=" in param:
                    k, v = param.split("=", 1)
                    query_params[k] = v
        return cls(
            url=url, title=title, domain=domain,
            path_segments=path_segments, query_params=query_params,
            content_type=content_type, language=language,
        )


@dataclass
class ClassificationResult:
    """分类结果"""

    category: str
    confidence: float
    subcategory: Optional[str] = None
    reasoning: List[str] = field(default_factory=list)
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    processing_time: float = 0.0
    method: str = "unknown"
    facets: Dict[str, str] = field(default_factory=dict)

    @property
    def alternative_categories(self) -> List[Tuple[str, float]]:
        return self.alternatives
