"""CleanBookmarks - 智能书签清理与分类

统一的包入口，提供主要公共API。

Example:
    >>> from cleanbook import AIBookmarkClassifier, BookmarkProcessor
    >>> classifier = AIBookmarkClassifier()
    >>> result = classifier.classify("https://github.com", "GitHub")
"""

from ..ai_classifier import AIBookmarkClassifier, BookmarkFeatures, ClassificationResult
from ..bookmark_processor import BookmarkProcessor
from ..rule_engine import RuleEngine

__all__ = [
    "AIBookmarkClassifier",
    "BookmarkFeatures",
    "ClassificationResult",
    "BookmarkProcessor",
    "RuleEngine",
]

__version__ = "2.0.1"
