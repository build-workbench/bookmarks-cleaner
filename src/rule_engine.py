"""
Rule Engine - 基于规则的快速分类引擎

提供高效的基于规则的书签分类，作为AI分类的基础组件
"""

import re
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
from urllib.parse import urlparse

# 导入 URL 分析器
try:
    from .url_analyzer import URLAnalyzer, URLAnalysis
except ImportError:
    URLAnalyzer = None
    URLAnalysis = None

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
        
        # URL 分析器
        self.url_analyzer = URLAnalyzer() if URLAnalyzer else None
        
        # 预编译规则
        self.compiled_rules = {}
        self._compile_rules()
        
        # 性能统计
        self.stats = {
            'total_matches': 0,
            'rule_hits': defaultdict(int),
            'category_predictions': defaultdict(int),
            'url_analysis_hits': 0
        }
    
    def _compile_rules(self):
        """预编译规则以提高性能"""
        self.compiled_rules = {}

        processing_order = self.config.get('processing_order')
        if not isinstance(processing_order, list) or not processing_order:
            processing_order = ['priority_rules', 'category_rules']

        for section in processing_order:
            section_rules = self.config.get(section, {})
            if not isinstance(section_rules, dict):
                continue

            for category, category_data in section_rules.items():
                rules = (category_data or {}).get('rules', [])
                if not isinstance(rules, list) or not rules:
                    continue

                if category not in self.compiled_rules:
                    self.compiled_rules[category] = []

                category_weight = (category_data or {}).get('weight', 1.0)
                try:
                    category_weight = float(category_weight)
                except Exception:
                    category_weight = 1.0

                for i, rule in enumerate(rules):
                    rule_id = f"{section}:{category}_{i}"
                    match_type = (rule or {}).get('match', '')
                    keywords = (rule or {}).get('keywords', [])
                    weight = (rule or {}).get('weight', 1.0)
                    exclusions = (rule or {}).get('must_not_contain', [])
                    match_all_keywords_in = (rule or {}).get('match_all_keywords_in', {})

                    try:
                        weight = float(weight)
                    except Exception:
                        weight = 1.0
                    weight = weight * category_weight

                    compiled_patterns = []
                    for keyword in keywords:
                        try:
                            escaped_keyword = re.escape(keyword).replace(r'\*', '.*').replace(r'\?', '.')
                            if match_type == 'url_ends_with':
                                escaped_keyword = f"{escaped_keyword}$"
                            pattern = re.compile(escaped_keyword, re.IGNORECASE)
                            compiled_patterns.append(pattern)
                        except re.error:
                            self.logger.warning(f"无效的正则表达式: {keyword}")
                            continue

                    compiled_exclusions = []
                    for exclusion in exclusions:
                        try:
                            pattern = re.compile(re.escape(exclusion), re.IGNORECASE)
                            compiled_exclusions.append(pattern)
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
                                    escaped_kw = re.escape(kw).replace(r'\*', '.*').replace(r'\?', '.')
                                    field_patterns.append(re.compile(escaped_kw, re.IGNORECASE))
                                except re.error:
                                    continue
                            if field_patterns:
                                compiled_all_keywords[str(field_name)] = field_patterns

                    compiled_rule = {
                        'rule_id': rule_id,
                        'match_type': match_type,
                        'patterns': compiled_patterns,
                        'exclusions': compiled_exclusions,
                        'weight': weight,
                        'original_keywords': keywords,
                        'match_all_keywords_in': compiled_all_keywords,
                    }

                    self.compiled_rules[category].append(compiled_rule)

        self.logger.info(f"预编译了 {sum(len(rules) for rules in self.compiled_rules.values())} 个规则")
    
    def classify(self, features) -> Optional[Dict]:
        """基于规则进行分类"""
        try:
            matches = self._find_matches(features)
            
            # 使用 URL 分析器增强分类
            url_hints = []
            if self.url_analyzer and hasattr(features, 'url'):
                try:
                    analysis = self.url_analyzer.analyze(features.url)
                    if analysis.category_hints:
                        self.stats['url_analysis_hits'] += 1
                        for category, confidence in analysis.category_hints:
                            url_hints.append(RuleMatch(
                                rule_id='url_analyzer',
                                category=category,
                                confidence=confidence * 15,  # 增加权重
                                matched_text=f"{analysis.site_type}:{analysis.content_type}",
                                rule_type='url_analysis'
                            ))
                except Exception as e:
                    self.logger.debug(f"URL 分析失败: {e}")
            
            # 合并匹配结果
            all_matches = matches + url_hints
            
            if not all_matches:
                return None
            
            # 计算分类得分
            category_scores = self._calculate_scores(all_matches)
            
            if not category_scores:
                return None
            
            # 选择最佳分类
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
            
            # 归一化置信度
            total_score = sum(category_scores.values())
            if total_score > 0:
                confidence = confidence / total_score
            
            # 生成推理过程
            reasoning = self._generate_reasoning(all_matches, best_category)
            
            # 生成备选分类
            alternatives = []
            if total_score > 0:
                alternatives = [(cat, score/total_score) for cat, score in category_scores.items() 
                              if cat != best_category]
            alternatives.sort(key=lambda x: x[1], reverse=True)
            
            self.stats['total_matches'] += 1
            self.stats['category_predictions'][best_category] += 1
            
            # 分面提示：推断资源类型
            resource_type_hint = None
            try:
                ct_map = {
                    'video': 'video',
                    'code_repository': 'code_repository',
                    'documentation': 'documentation',
                    'academic_paper': 'paper',
                    'news': 'news',
                    'online_tool': 'tool',
                    'webpage': 'webpage'
                }
                if hasattr(features, 'content_type'):
                    resource_type_hint = ct_map.get(features.content_type)

                domain = getattr(features, 'domain', '').lower()
                url_lower = getattr(features, 'url', '').lower()
                title_lower = getattr(features, 'title', '').lower()

                if any(d in domain for d in ['github.com', 'gitlab.com', 'bitbucket.org', 'gitee.com', 'sourceforge.net', 'github.io']):
                    resource_type_hint = 'code_repository'
                elif any(p in url_lower for p in ['docs.', '/docs', 'documentation', 'wiki']):
                    resource_type_hint = resource_type_hint or 'documentation'
                elif any(d in domain for d in ['youtube.com', 'bilibili.com', 'vimeo.com']):
                    resource_type_hint = 'video'
                elif any(k in title_lower for k in ['news', '新闻', 'weekly']):
                    resource_type_hint = resource_type_hint or 'news'
            except Exception:
                resource_type_hint = resource_type_hint or None

            facets = {'resource_type_hint': resource_type_hint} if resource_type_hint else {}

            return {
                'category': best_category,
                'confidence': confidence,
                'alternatives': alternatives[:3],
                'reasoning': reasoning,
                'method': 'rule_engine',
                'facets': facets
            }
            
        except Exception as e:
            self.logger.error(f"规则分类失败: {e}")
            return None
    
    def _find_matches(self, features) -> List[RuleMatch]:
        """查找匹配的规则"""
        matches = []
        
        # 准备匹配文本
        match_texts = {
            'domain': features.domain,
            'title': features.title.lower(),
            'url': features.url.lower(),
            'path': '/'.join(features.path_segments).lower(),
            'content_type': features.content_type,
            'url_ends_with': features.url.lower(),
        }
        
        for category, rules in self.compiled_rules.items():
            for rule in rules:
                match_type = rule['match_type']
                target_text = match_texts.get(match_type, '')
                
                if not target_text:
                    continue
                
                # 检查模式匹配
                for pattern in rule['patterns']:
                    match = pattern.search(target_text)
                    if match:
                        # 检查排除条件
                        excluded = False
                        for exclusion_pattern in rule['exclusions']:
                            if exclusion_pattern.search(target_text):
                                excluded = True
                                break
                        
                        if not excluded:
                            all_keywords_in = rule.get('match_all_keywords_in') or {}
                            if all_keywords_in:
                                passed = True
                                for field_name, field_patterns in all_keywords_in.items():
                                    field_text = match_texts.get(field_name, '')
                                    if not field_text:
                                        passed = False
                                        break
                                    field_ok = False
                                    for fp in field_patterns:
                                        try:
                                            if fp.search(field_text):
                                                field_ok = True
                                                break
                                        except Exception:
                                            continue
                                    if not field_ok:
                                        passed = False
                                        break
                                if not passed:
                                    continue
                            rule_match = RuleMatch(
                                rule_id=rule['rule_id'],
                                category=category,
                                confidence=rule['weight'],
                                matched_text=match.group(),
                                rule_type=match_type
                            )
                            matches.append(rule_match)
                            self.stats['rule_hits'][rule['rule_id']] += 1
                            break  # 每个规则只匹配一次
        
        return matches
    
    def _calculate_scores(self, matches: List[RuleMatch]) -> Dict[str, float]:
        """计算分类得分"""
        category_scores = defaultdict(float)
        
        # 检查是否有特定类型的匹配
        has_ai_match = any('AI' in m.category for m in matches)
        has_code_repo_match = any('代码仓库' in m.category for m in matches)
        
        for match in matches:
            score = match.confidence
            
            # 如果同时有 AI 和代码仓库匹配，根据内容调整权重
            if has_ai_match and has_code_repo_match:
                if 'AI' in match.category:
                    score *= 1.3  # 适度提升 AI 分类权重
                elif '代码仓库' in match.category:
                    score *= 0.8  # 适度降低代码仓库权重
            
            category_scores[match.category] += score
        
        # 合并相似分类的得分（同一顶级分类下的子分类）
        merged_scores = defaultdict(float)
        for category, score in category_scores.items():
            # 提取顶级分类
            top_category = category.split('/')[0]
            merged_scores[top_category] += score
        
        # 如果某个顶级分类的合并得分明显高于其他分类，选择该分类下得分最高的子分类
        if merged_scores:
            top_merged = max(merged_scores, key=merged_scores.get)
            top_merged_score = merged_scores[top_merged]
            
            # 如果顶级分类得分占比超过 40%，选择该分类下的最佳子分类
            total_merged = sum(merged_scores.values())
            if total_merged > 0 and top_merged_score / total_merged > 0.4:
                # 找到该顶级分类下得分最高的子分类
                best_sub = None
                best_sub_score = 0
                for category, score in category_scores.items():
                    if category.startswith(top_merged):
                        if score > best_sub_score:
                            best_sub = category
                            best_sub_score = score
                
                if best_sub:
                    # 将合并得分赋给最佳子分类
                    category_scores[best_sub] = top_merged_score
        
        return dict(category_scores)
    
    def _generate_reasoning(self, matches: List[RuleMatch], best_category: str) -> List[str]:
        """生成推理过程"""
        reasoning = []
        
        category_matches = [m for m in matches if m.category == best_category]
        
        for match in category_matches:
            reasoning.append(
                f"规则匹配: {match.rule_type} 包含 '{match.matched_text}' -> {match.category}"
            )
        
        return reasoning
    
    def add_dynamic_rule(self, category: str, match_type: str, keyword: str, weight: float = 1.0):
        """动态添加规则"""
        if category not in self.compiled_rules:
            self.compiled_rules[category] = []
        
        rule_id = f"{category}_dynamic_{len(self.compiled_rules[category])}"
        
        try:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            
            compiled_rule = {
                'rule_id': rule_id,
                'match_type': match_type,
                'patterns': [pattern],
                'exclusions': [],
                'weight': weight,
                'original_keywords': [keyword]
            }
            
            self.compiled_rules[category].append(compiled_rule)
            self.logger.info(f"添加动态规则: {category} - {match_type}:{keyword}")
            
        except re.error as e:
            self.logger.error(f"无效的动态规则: {keyword}, 错误: {e}")
    
    def update_rule_weight(self, rule_id: str, new_weight: float):
        """更新规则权重"""
        for category, rules in self.compiled_rules.items():
            for rule in rules:
                if rule['rule_id'] == rule_id:
                    old_weight = rule['weight']
                    rule['weight'] = new_weight
                    self.logger.info(f"更新规则权重: {rule_id} {old_weight} -> {new_weight}")
                    return True
        
        self.logger.warning(f"未找到规则: {rule_id}")
        return False
    
    def get_rule_performance(self) -> Dict:
        """获取规则性能统计"""
        total_hits = sum(self.stats['rule_hits'].values())
        
        return {
            'total_matches': self.stats['total_matches'],
            'total_rule_hits': total_hits,
            'top_rules': dict(sorted(self.stats['rule_hits'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]),
            'category_distribution': dict(self.stats['category_predictions']),
            'rules_count': sum(len(rules) for rules in self.compiled_rules.values())
        }
    
    def export_rules(self) -> Dict:
        """导出规则配置"""
        exported_rules = {}
        
        for category, rules in self.compiled_rules.items():
            exported_rules[category] = []
            
            for rule in rules:
                exported_rule = {
                    'match': rule['match_type'],
                    'keywords': rule['original_keywords'],
                    'weight': rule['weight']
                }
                exported_rules[category].append(exported_rule)
        
        return {
            'category_rules': exported_rules,
            'performance_stats': self.get_rule_performance()
        }
    
    def validate_rules(self) -> List[str]:
        """验证规则配置"""
        errors = []
        
        for category, rules in self.compiled_rules.items():
            if not rules:
                errors.append(f"分类 '{category}' 没有定义规则")
                continue
            
            for rule in rules:
                if not rule['patterns']:
                    errors.append(f"分类 '{category}' 包含无效的模式")
                
                if rule['weight'] <= 0:
                    errors.append(f"分类 '{category}' 包含无效的权重: {rule['weight']}")
        
        return errors