"""
Feedback Learner - 反馈学习器

负责处理用户反馈，增量训练模型。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


class FeedbackIncrementalModel:
    """轻量级反馈增量模型，用于离线 feedback 训练与版本化。"""

    def __init__(self):
        self.classes_: List[str] = []
        self._label_by_signature: Dict[str, str] = {}
        self._label_counts: Dict[str, int] = {}

    def partial_fit(self, X, y, classes=None):
        if classes:
            merged = set(self.classes_) | set(classes)
            self.classes_ = sorted(str(label) for label in merged)

        for features, label in zip(X, y):
            label = str(label)
            signature = self._signature(features)
            self._label_by_signature[signature] = label
            self._label_counts[label] = self._label_counts.get(label, 0) + 1

    def predict(self, X):
        default_label = max(
            self._label_counts,
            key=self._label_counts.get,
            default="未分类",
        )
        return [
            self._label_by_signature.get(self._signature(features), default_label)
            for features in X
        ]

    def _signature(self, features: Dict) -> str:
        url = str(features.get("url", ""))
        title = str(features.get("title", "")).strip().lower()
        domain = urlparse(url).netloc.lower().replace("www.", "")
        return f"{domain}::{title}"


class FeedbackLearner:
    """反馈学习器

    深度: 高（简单接口，复杂的增量学习逻辑）
    接口: learn(feedback) -> ModelUpdate
    """

    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # 增量模型
        self.incremental_model = FeedbackIncrementalModel()
        self.model_version = 0

        # 反馈缓存
        self._feedback_cache: List[Dict] = []
        self._version_file = self.model_dir / "feedback_version.txt"

        self._load_version()

    def learn(self, feedback: List[Dict]) -> Dict:
        """从反馈学习

        Args:
            feedback: 反馈列表，每项包含 url, title, correct_category

        Returns:
            学习统计信息
        """
        if not feedback:
            return {"learned": 0, "version": self.model_version}

        # 准备训练数据
        X = []
        y = []

        for item in feedback:
            features = {
                "url": item.get("url", ""),
                "title": item.get("title", ""),
            }
            label = item.get("correct_category")

            if label:
                X.append(features)
                y.append(label)
                self._feedback_cache.append(item)

        # 增量训练
        if X:
            self.incremental_model.partial_fit(X, y)
            self._increment_version()

            self.logger.info(f"增量学习: {len(X)} 个样本, 版本 {self.model_version}")

        return {
            "learned": len(X),
            "version": self.model_version,
            "total_samples": len(self._feedback_cache),
        }

    def predict(self, url: str, title: str) -> Optional[str]:
        """使用增量模型预测"""
        features = {"url": url, "title": title}
        predictions = self.incremental_model.predict([features])

        if predictions and predictions[0] != "未分类":
            return predictions[0]

        return None

    def apply_feedback_file(self, feedback_path: str) -> Dict:
        """应用反馈文件"""
        feedback = self._load_feedback_file(feedback_path)
        return self.learn(feedback)

    def train_feedback_file(self, feedback_path: str) -> Dict:
        """训练反馈文件（触发模型保存）"""
        feedback = self._load_feedback_file(feedback_path)
        result = self.learn(feedback)

        # 保存模型
        self._save_model()

        return result

    def _load_feedback_file(self, feedback_path: str) -> List[Dict]:
        """加载反馈文件"""
        path = Path(feedback_path)

        if not path.exists():
            raise FileNotFoundError(f"反馈文件不存在: {feedback_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 支持多种格式
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "items" in data:
                return data["items"]
            elif "feedback" in data:
                return data["feedback"]

        return []

    def _save_model(self):
        """保存增量模型"""
        import joblib

        model_file = self.model_dir / f"feedback_model_v{self.model_version}.pkl"
        joblib.dump(
            {
                "model": self.incremental_model,
                "version": self.model_version,
                "timestamp": datetime.now().isoformat(),
            },
            model_file,
        )

        self.logger.info(f"模型已保存: {model_file}")

    def _load_version(self):
        """加载版本号"""
        if self._version_file.exists():
            try:
                self.model_version = int(self._version_file.read_text().strip())
            except Exception:
                self.model_version = 0

    def _increment_version(self):
        """增加版本号"""
        self.model_version += 1
        self._version_file.write_text(str(self.model_version))

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "version": self.model_version,
            "classes": len(self.incremental_model.classes_),
            "samples": len(self._feedback_cache),
        }
