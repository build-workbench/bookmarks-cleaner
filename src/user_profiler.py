"""
User Profiler - 用户画像分析器
基于用户行为的个性化书签分类
"""

import json
import logging
import math
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Pre-compiled regex pattern for performance
_WORD_REGEX = re.compile(r"[a-zA-Z\u4e00-\u9fff]{2,}")


class UserProfiler:
    """用户画像分析器 - 基于用户行为的个性化分类"""

    def __init__(self, profile_file: str = "user_profile.json"):
        """
        初始化用户画像分析器

        Args:
            profile_file: 用户画像文件路径
        """
        self.profile_file = profile_file
        self.logger = logging.getLogger(__name__)
        self.preferences = self._load_preferences()
        self.learning_rate = 0.1
        self.decay_factor = 0.95  # 时间衰减因子
        self._initialize_profile_structure()

    def _load_preferences(self) -> Dict:
        """加载用户偏好数据"""
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, PermissionError) as e:
                self.logger.warning(f"加载用户偏好失败: {e}")

        return self._create_default_profile()

    def _create_default_profile(self) -> Dict:
        """创建默认用户画像"""
        return {
            "category_preferences": {},  # 分类偏好
            "domain_preferences": {},  # 域名偏好
            "keyword_preferences": {},  # 关键词偏好
            "time_patterns": {},  # 时间模式
            "interaction_history": [],  # 交互历史
            "confidence_adjustments": {},  # 置信度调整
            "last_updated": datetime.now().isoformat(),
            "profile_version": "1.0",
        }

    def _initialize_profile_structure(self):
        """初始化画像结构"""
        required_keys = [
            "category_preferences",
            "domain_preferences",
            "keyword_preferences",
            "time_patterns",
            "interaction_history",
            "confidence_adjustments",
        ]

        for key in required_keys:
            if key not in self.preferences:
                self.preferences[key] = {} if key != "interaction_history" else []

    def classify(self, features) -> Optional[Dict]:
        """
        基于用户画像的分类

        Args:
            features: 书签特征对象

        Returns:
            分类结果字典，失败时返回 None
        """
        try:
            url = features.url
            title = features.title
            domain = features.domain

            # 1. 基于历史偏好计算分类得分
            category_scores = self._calculate_category_scores(features)

            # 2. 基于域名偏好调整
            domain_adjustments = self._get_domain_adjustments(domain)

            # 3. 基于关键词偏好调整
            keyword_adjustments = self._get_keyword_adjustments(title)

            # 4. 基于时间模式调整
            time_adjustments = self._get_time_adjustments()

            # 5. 综合计算最终得分
            final_scores = self._combine_scores(
                category_scores,
                domain_adjustments,
                keyword_adjustments,
                time_adjustments,
            )

            if not final_scores:
                return None

            # 选择最佳分类
            best_category = max(final_scores, key=final_scores.get)
            confidence = final_scores[best_category]

            # 应用置信度调整
            confidence = self._apply_confidence_adjustments(best_category, confidence)

            if confidence < 0.2:  # 用户画像的阈值较低
                return None

            return {
                "category": best_category,
                "confidence": confidence,
                "reasoning": [
                    f"用户画像分析: {best_category} (个性化置信度: {confidence:.2f})"
                ],
                "method": "user_profiler",
                "profile_scores": final_scores,
            }

        except (AttributeError, TypeError) as e:
            self.logger.error(f"用户画像分类失败: {e}")
            return None

    def _calculate_category_scores(self, features) -> Dict[str, float]:
        """计算分类基础得分"""
        scores = {}
        category_prefs = self.preferences.get("category_preferences", {})

        # 基于历史分类频率
        total_interactions = sum(category_prefs.values())
        if total_interactions > 0:
            for category, count in category_prefs.items():
                scores[category] = count / total_interactions

        return scores

    def _get_domain_adjustments(self, domain: str) -> Dict[str, float]:
        """获取域名偏好调整"""
        adjustments = {}
        domain_prefs = self.preferences.get("domain_preferences", {})

        if domain in domain_prefs:
            # 基于域名历史分类的加权
            domain_data = domain_prefs[domain]
            total_visits = (
                sum(domain_data.values()) if isinstance(domain_data, dict) else 0
            )

            if total_visits > 0:
                for category, count in domain_data.items():
                    if isinstance(count, (int, float)):
                        adjustments[category] = (count / total_visits) * 0.3

        return adjustments

    def _get_keyword_adjustments(self, title: str) -> Dict[str, float]:
        """获取关键词偏好调整"""
        adjustments = {}
        keyword_prefs = self.preferences.get("keyword_preferences", {})

        if not title:
            return adjustments

        # 提取标题中的关键词
        title_words = self._extract_words(title)

        for word in title_words:
            if word in keyword_prefs:
                keyword_data = keyword_prefs[word]
                if isinstance(keyword_data, dict):
                    total_occurrences = sum(keyword_data.values())
                    if total_occurrences > 0:
                        for category, count in keyword_data.items():
                            if isinstance(count, (int, float)):
                                weight = (count / total_occurrences) * 0.2
                                adjustments[category] = (
                                    adjustments.get(category, 0) + weight
                                )

        return adjustments

    def _get_time_adjustments(self) -> Dict[str, float]:
        """获取时间模式调整"""
        adjustments = {}
        time_patterns = self.preferences.get("time_patterns", {})

        current_hour = datetime.now().hour
        time_slot = self._get_time_slot(current_hour)

        if time_slot in time_patterns:
            slot_data = time_patterns[time_slot]
            if isinstance(slot_data, dict):
                total_activities = sum(slot_data.values())
                if total_activities > 0:
                    for category, count in slot_data.items():
                        if isinstance(count, (int, float)):
                            adjustments[category] = (count / total_activities) * 0.1

        return adjustments

    def _get_time_slot(self, hour: int) -> str:
        """获取时间段"""
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 24:
            return "evening"
        else:
            return "night"

    def _combine_scores(
        self, base_scores: Dict, domain_adj: Dict, keyword_adj: Dict, time_adj: Dict
    ) -> Dict[str, float]:
        """综合所有得分"""
        combined = defaultdict(float)

        # 合并所有得分
        for category, score in base_scores.items():
            combined[category] += score

        for category, adjustment in domain_adj.items():
            combined[category] += adjustment

        for category, adjustment in keyword_adj.items():
            combined[category] += adjustment

        for category, adjustment in time_adj.items():
            combined[category] += adjustment

        return dict(combined)

    def _apply_confidence_adjustments(self, category: str, confidence: float) -> float:
        """应用置信度调整"""
        adjustments = self.preferences.get("confidence_adjustments", {})

        if category in adjustments:
            adjustment_factor = adjustments[category]
            confidence *= 1 + adjustment_factor

        return min(max(confidence, 0.0), 1.0)

    def _extract_words(self, text: str) -> List[str]:
        """提取文本中的单词"""
        words = _WORD_REGEX.findall(text.lower())
        return [w for w in words if len(w) > 2]

    def update_preferences(self, features, category: str, confidence: float = 1.0):
        """
        更新用户偏好

        Args:
            features: 书签特征对象
            category: 分类结果
            confidence: 置信度
        """
        try:
            url = features.url
            title = features.title
            domain = features.domain

            # 1. 更新分类偏好
            category_prefs = self.preferences["category_preferences"]
            category_prefs[category] = category_prefs.get(category, 0) + confidence

            # 2. 更新域名偏好
            domain_prefs = self.preferences["domain_preferences"]
            if domain not in domain_prefs:
                domain_prefs[domain] = {}
            domain_prefs[domain][category] = (
                domain_prefs[domain].get(category, 0) + confidence
            )

            # 3. 更新关键词偏好
            if title:
                words = self._extract_words(title)
                keyword_prefs = self.preferences["keyword_preferences"]

                for word in words[:5]:  # 只取前5个关键词
                    if word not in keyword_prefs:
                        keyword_prefs[word] = {}
                    keyword_prefs[word][category] = (
                        keyword_prefs[word].get(category, 0) + confidence * 0.5
                    )

            # 4. 更新时间模式
            current_hour = datetime.now().hour
            time_slot = self._get_time_slot(current_hour)
            time_patterns = self.preferences["time_patterns"]

            if time_slot not in time_patterns:
                time_patterns[time_slot] = {}
            time_patterns[time_slot][category] = (
                time_patterns[time_slot].get(category, 0) + confidence * 0.3
            )

            # 5. 记录交互历史
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "title": title,
                "domain": domain,
                "category": category,
                "confidence": confidence,
            }

            history = self.preferences["interaction_history"]
            history.append(interaction)

            # 保持历史记录在合理范围内（最多1000条）
            if len(history) > 1000:
                self.preferences["interaction_history"] = history[-1000:]

            # 6. 更新时间戳
            self.preferences["last_updated"] = datetime.now().isoformat()

            # 7. 应用时间衰减
            self._apply_time_decay()

            # 8. 保存更新
            self._save_preferences()

        except (AttributeError, KeyError, TypeError) as e:
            self.logger.warning(f"更新用户偏好失败: {e}")

    def _apply_time_decay(self):
        """应用时间衰减因子"""
        try:
            last_updated = datetime.fromisoformat(
                self.preferences.get("last_updated", datetime.now().isoformat())
            )
            days_elapsed = (datetime.now() - last_updated).days

            if days_elapsed > 0:
                decay_rate = self.decay_factor**days_elapsed

                # 对数值型偏好应用衰减
                for pref_type in [
                    "category_preferences",
                    "domain_preferences",
                    "keyword_preferences",
                    "time_patterns",
                ]:
                    prefs = self.preferences.get(pref_type, {})
                    self._apply_decay_to_nested_dict(prefs, decay_rate)

        except (ValueError, TypeError) as e:
            self.logger.debug(f"时间衰减计算失败: {e}")

    def _apply_decay_to_nested_dict(self, data: Dict, decay_rate: float):
        """对嵌套字典应用衰减"""
        for key, value in data.items():
            if isinstance(value, dict):
                self._apply_decay_to_nested_dict(value, decay_rate)
            elif isinstance(value, (int, float)):
                data[key] = value * decay_rate

    def _save_preferences(self):
        """保存用户偏好"""
        try:
            with open(self.profile_file, "w", encoding="utf-8") as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
        except (IOError, PermissionError) as e:
            self.logger.warning(f"保存用户偏好失败: {e}")

    def export_profile(self) -> Dict:
        """导出用户画像"""
        return self.preferences.copy()

    def import_profile(self, profile: Dict):
        """导入用户画像"""
        if isinstance(profile, dict):
            self.preferences = profile
            self._initialize_profile_structure()
            self._save_preferences()

    def get_user_insights(self) -> Dict:
        """获取用户行为洞察"""
        insights = {
            "total_interactions": len(self.preferences.get("interaction_history", [])),
            "favorite_categories": {},
            "favorite_domains": {},
            "activity_patterns": {},
            "last_active": self.preferences.get("last_updated", ""),
        }

        # 分析最喜欢的分类
        category_prefs = self.preferences.get("category_preferences", {})
        if category_prefs:
            total = sum(category_prefs.values())
            insights["favorite_categories"] = {
                k: round(v / total * 100, 1)
                for k, v in sorted(
                    category_prefs.items(), key=lambda x: x[1], reverse=True
                )[:5]
            }

        # 分析最常访问的域名
        domain_prefs = self.preferences.get("domain_preferences", {})
        domain_totals = {}
        for domain, categories in domain_prefs.items():
            if isinstance(categories, dict):
                domain_totals[domain] = sum(categories.values())

        if domain_totals:
            insights["favorite_domains"] = dict(
                sorted(domain_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            )

        # 分析活动模式
        time_patterns = self.preferences.get("time_patterns", {})
        if time_patterns:
            for time_slot, activities in time_patterns.items():
                if isinstance(activities, dict):
                    insights["activity_patterns"][time_slot] = sum(activities.values())

        return insights
