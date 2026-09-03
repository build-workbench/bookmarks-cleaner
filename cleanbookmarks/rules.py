"""规则引擎 - 基于规则的快速分类"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

from cleanbookmarks.url_analyzer import URLAnalyzer


@dataclass
class RuleMatch:
    """规则匹配结果"""
    rule_id: str
    category: str
    confidence: float
    matched_text: str
    rule_type: str


class RuleEngine:
    """规则引擎"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.url_analyzer = URLAnalyzer()
        self.compiled_rules = {}
        ai_settings = (config or {}).get("ai_settings", {}) or {}
        try:
            self.url_analysis_weight = float(ai_settings.get("url_analysis_weight", 15))
        except (TypeError, ValueError):
            self.url_analysis_weight = 15.0
        try:
            self.merge_top_ratio = float(ai_settings.get("merge_top_ratio", 0.4))
        except (TypeError, ValueError):
            self.merge_top_ratio = 0.4
        self._compile_rules()
        self.stats = {
            "total_matches": 0,
            "rule_hits": defaultdict(int),
            "category_predictions": defaultdict(int),
            "url_analysis_hits": 0,
        }

    def _compile_rules(self):
        self.compiled_rules = {}
        processing_order = self.config.get("processing_order")
        if not isinstance(processing_order, list) or not processing_order:
            processing_order = ["priority_rules", "category_rules"]

        for section in processing_order:
            section_rules = self.config.get(section, {})
            if not isinstance(section_rules, dict):
                continue
            for category, category_data in section_rules.items():
                rules = (category_data or {}).get("rules", [])
                if not isinstance(rules, list) or not rules:
                    continue
                if category not in self.compiled_rules:
                    self.compiled_rules[category] = []
                category_weight = (category_data or {}).get("weight", 1.0)
                try:
                    category_weight = float(category_weight)
                except (TypeError, ValueError):
                    category_weight = 1.0

                for i, rule in enumerate(rules):
                    rule_id = f"{section}:{category}_{i}"
                    match_type = (rule or {}).get("match", "")
                    keywords = (rule or {}).get("keywords", [])
                    weight = (rule or {}).get("weight", 1.0)
                    exclusions = (rule or {}).get("must_not_contain", [])
                    match_all_keywords_in = (rule or {}).get("match_all_keywords_in", {})
                    if not isinstance(keywords, list) or not keywords:
                        continue
                    try:
                        weight = float(weight)
                    except (TypeError, ValueError):
                        weight = 1.0
                    weight = weight * category_weight

                    compiled_patterns = []
                    for keyword in keywords:
                        try:
                            escaped = re.escape(keyword).replace(r"\*", ".*").replace(r"\?", ".")
                            if match_type == "url_ends_with":
                                escaped = f"{escaped}$"
                            compiled_patterns.append(re.compile(escaped, re.IGNORECASE))
                        except re.error:
                            self.logger.warning(f"无效的正则表达式: {keyword}")

                    compiled_exclusions = []
                    for exclusion in exclusions:
                        try:
                            compiled_exclusions.append(re.compile(re.escape(exclusion), re.IGNORECASE))
                        except re.error:
                            continue

                    compiled_all_keywords = {}
                    if isinstance(match_all_keywords_in, dict):
                        for field_name, field_keywords in match_all_keywords_in.items():
                            if not isinstance(field_keywords, list):
                                continue
                            field_patterns = []
                            for kw in field_keywords:
                                try:
                                    escaped_kw = re.escape(kw).replace(r"\*", ".*").replace(r"\?", ".")
                                    field_patterns.append(re.compile(escaped_kw, re.IGNORECASE))
                                except re.error:
                                    continue
                            if field_patterns:
                                compiled_all_keywords[str(field_name)] = field_patterns

                    self.compiled_rules[category].append({
                        "rule_id": rule_id,
                        "match_type": match_type,
                        "patterns": compiled_patterns,
                        "exclusions": compiled_exclusions,
                        "weight": weight,
                        "original_keywords": keywords,
                        "match_all_keywords_in": compiled_all_keywords,
                    })

        self.logger.info(
            f"预编译了 {sum(len(rules) for rules in self.compiled_rules.values())} 个规则"
        )

    def classify(self, features) -> Optional[Dict]:
        try:
            matches = self._find_matches(features)
            url_hints = []
            if hasattr(features, "url"):
                try:
                    analysis = self.url_analyzer.analyze(features.url)
                    if analysis.category_hints:
                        self.stats["url_analysis_hits"] += 1
                        for category, confidence in analysis.category_hints:
                            url_hints.append(RuleMatch(
                                rule_id="url_analyzer", category=category,
                                confidence=confidence * self.url_analysis_weight,
                                matched_text=f"{analysis.site_type}:{analysis.content_type}",
                                rule_type="url_analysis",
                            ))
                except Exception as e:
                    self.logger.debug(f"URL 分析失败: {e}")

            all_matches = matches + url_hints
            if not all_matches:
                return None

            category_scores = self._calculate_scores(all_matches)
            if not category_scores:
                return None

            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
            total_score = sum(category_scores.values())
            if total_score > 0:
                confidence = confidence / total_score

            reasoning = self._generate_reasoning(all_matches, best_category)
            alternatives = []
            if total_score > 0:
                alternatives = [
                    (cat, score / total_score)
                    for cat, score in category_scores.items()
                    if cat != best_category
                ]
            alternatives.sort(key=lambda x: x[1], reverse=True)

            self.stats["total_matches"] += 1
            self.stats["category_predictions"][best_category] += 1

            resource_type_hint = self._infer_resource_type(features)
            facets = {"resource_type_hint": resource_type_hint} if resource_type_hint else {}

            return {
                "category": best_category,
                "confidence": confidence,
                "alternatives": alternatives[:3],
                "reasoning": reasoning,
                "method": "rule_engine",
                "facets": facets,
            }
        except Exception as e:
            self.logger.error(f"规则分类失败: {e}")
            return None

    def _infer_resource_type(self, features) -> Optional[str]:
        ct_map = {
            "video": "video", "code_repository": "code_repository",
            "documentation": "documentation", "academic_paper": "paper",
            "news": "news", "online_tool": "tool", "webpage": "webpage",
        }
        hint = ct_map.get(getattr(features, "content_type", "")) if hasattr(features, "content_type") else None
        domain = getattr(features, "domain", "").lower()
        url_lower = getattr(features, "url", "").lower()
        title_lower = getattr(features, "title", "").lower()
        if any(d in domain for d in ["github.com", "gitlab.com", "bitbucket.org", "gitee.com", "sourceforge.net", "github.io"]):
            return "code_repository"
        if any(p in url_lower for p in ["docs.", "/docs", "documentation", "wiki"]):
            return hint or "documentation"
        if any(d in domain for d in ["youtube.com", "bilibili.com", "vimeo.com"]):
            return "video"
        if any(k in title_lower for k in ["news", "新闻", "weekly"]):
            return hint or "news"
        return hint

    def _find_matches(self, features) -> List[RuleMatch]:
        matches = []
        match_texts = {
            "domain": features.domain,
            "title": features.title.lower(),
            "url": features.url.lower(),
            "path": "/".join(features.path_segments).lower(),
            "content_type": features.content_type,
            "url_ends_with": features.url.lower(),
        }
        for category, rules in self.compiled_rules.items():
            for rule in rules:
                match_type = rule["match_type"]
                target_text = match_texts.get(match_type, "")
                if not target_text:
                    continue
                for pattern in rule["patterns"]:
                    match = pattern.search(target_text)
                    if match:
                        excluded = False
                        for exclusion_pattern in rule["exclusions"]:
                            if exclusion_pattern.search(target_text):
                                excluded = True
                                break
                        if not excluded:
                            all_keywords_in = rule.get("match_all_keywords_in") or {}
                            if all_keywords_in:
                                passed = True
                                for field_name, field_patterns in all_keywords_in.items():
                                    field_text = match_texts.get(field_name, "")
                                    if not field_text or not any(fp.search(field_text) for fp in field_patterns):
                                        passed = False
                                        break
                                if not passed:
                                    continue
                            matches.append(RuleMatch(
                                rule_id=rule["rule_id"], category=category,
                                confidence=rule["weight"], matched_text=match.group(),
                                rule_type=match_type,
                            ))
                            self.stats["rule_hits"][rule["rule_id"]] += 1
                            break
        return matches

    def _calculate_scores(self, matches: List[RuleMatch]) -> Dict[str, float]:
        """按权重累加各分类得分（纯权重竞争，无个人化偏好）"""
        category_scores = defaultdict(float)
        for match in matches:
            category_scores[match.category] += match.confidence

        merged_scores = defaultdict(float)
        for category, score in category_scores.items():
            top_category = category.split("/")[0]
            merged_scores[top_category] += score

        if merged_scores:
            top_merged = max(merged_scores, key=merged_scores.get)
            top_merged_score = merged_scores[top_merged]
            total_merged = sum(merged_scores.values())
            if total_merged > 0 and top_merged_score / total_merged > self.merge_top_ratio:
                best_sub = None
                best_sub_score = 0
                for category, score in category_scores.items():
                    if category.startswith(top_merged) and score > best_sub_score:
                        best_sub = category
                        best_sub_score = score
                if best_sub:
                    category_scores[best_sub] = top_merged_score
                    # 移除同主类的其他子类残留，避免稀释合并后的置信度
                    for cat in [c for c in category_scores if c != best_sub and c.startswith(top_merged)]:
                        del category_scores[cat]
        return dict(category_scores)

    def _generate_reasoning(self, matches: List[RuleMatch], best_category: str) -> List[str]:
        return [
            f"规则匹配: {m.rule_type} 包含 '{m.matched_text}' -> {m.category}"
            for m in matches if m.category == best_category
        ]
