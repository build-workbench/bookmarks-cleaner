"""
Smart Rule Loader - 智能规则加载器

从 agent/config 目录加载域名规则和关键词规则，
并将其转换为规则引擎可用的格式。

特性：
1. 支持分组的域名规则（带注释）
2. 支持带权重和上下文的关键词规则
3. 支持排除规则（must_not_contain）
4. 支持上下文依赖（context_required）
5. 自动合并到主配置
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class SmartRuleLoader:
    """智能规则加载器"""
    
    # 分类名称映射 - 将 agent/config 中的名称映射到 config.json 中的标准名称
    CATEGORY_MAPPING = {
        'AI·大模型': 'AI',
        'AI·工具': 'AI',
        'Web·前端': '编程/Web开发',
        '后端开发': '编程/后端',
        'DevOps·运维': '编程/DevOps运维',
        '数据库': '编程/数据库',
        '技术社区': '社区',
        '学习资源': '学习/技术文档',
        'Homelab·服务器': 'Homelab',
        '在线工具': '其他/在线服务',
        '生物信息': '生物',
    }
    
    def __init__(self, config_dir: str = "agent/config"):
        self.config_dir = Path(config_dir)
        self.domain_rules_file = self.config_dir / "domain_rules.json"
        self.keyword_rules_file = self.config_dir / "keyword_rules.json"
        
        self._domain_rules: Dict[str, Dict] = {}
        self._keyword_rules: Dict[str, Dict] = {}
        self._compiled_rules: Dict[str, List[Dict]] = {}
        
    def load_all(self) -> Dict[str, Any]:
        """加载所有规则并返回合并后的配置"""
        self._load_domain_rules()
        self._load_keyword_rules()
        return self._compile_to_config()
    
    def _load_domain_rules(self):
        """加载域名规则"""
        if not self.domain_rules_file.exists():
            logger.warning(f"域名规则文件不存在: {self.domain_rules_file}")
            return
            
        try:
            with open(self.domain_rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理分组格式
            for key, value in data.items():
                if key.startswith('_'):  # 跳过注释字段
                    continue
                    
                if isinstance(value, dict):
                    # 检查是否是分组（包含多个域名）
                    if 'top' in value:
                        # 单个域名规则
                        self._domain_rules[key] = value
                    else:
                        # 分组，展开所有域名
                        for domain, rule in value.items():
                            if isinstance(rule, dict) and 'top' in rule:
                                self._domain_rules[domain] = rule
                                
            logger.info(f"加载了 {len(self._domain_rules)} 条域名规则")
            
        except Exception as e:
            logger.error(f"加载域名规则失败: {e}")
    
    def _load_keyword_rules(self):
        """加载关键词规则"""
        if not self.keyword_rules_file.exists():
            logger.warning(f"关键词规则文件不存在: {self.keyword_rules_file}")
            return
            
        try:
            with open(self.keyword_rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理分组格式
            for key, value in data.items():
                if key.startswith('_'):  # 跳过注释字段
                    continue
                    
                if isinstance(value, dict):
                    if 'top' in value:
                        # 单个关键词规则
                        self._keyword_rules[key] = value
                    else:
                        # 分组，展开所有关键词
                        for keyword, rule in value.items():
                            if isinstance(rule, dict) and 'top' in rule:
                                self._keyword_rules[keyword] = rule
                                
            logger.info(f"加载了 {len(self._keyword_rules)} 条关键词规则")
            
        except Exception as e:
            logger.error(f"加载关键词规则失败: {e}")
    
    def _compile_to_config(self) -> Dict[str, Any]:
        """编译规则为配置格式"""
        # 按分类组织规则
        category_rules: Dict[str, Dict] = defaultdict(lambda: {"rules": []})
        priority_rules: Dict[str, Dict] = defaultdict(lambda: {"weight": 100, "rules": []})
        
        # 处理域名规则
        domain_by_category: Dict[str, List[str]] = defaultdict(list)
        for domain, rule in self._domain_rules.items():
            top = rule.get('top', '未分类')
            # 应用分类映射
            top = self.CATEGORY_MAPPING.get(top, top)
            second = rule.get('second')
            category = f"{top}/{second}" if second else top
            domain_by_category[category].append(domain)
        
        # 生成域名匹配规则
        for category, domains in domain_by_category.items():
            rule_entry = {
                "match": "domain",
                "keywords": domains,
                "weight": 25  # 域名匹配权重较高
            }
            category_rules[category]["rules"].append(rule_entry)
        
        # 处理关键词规则
        keyword_by_category: Dict[str, List[Dict]] = defaultdict(list)
        for keyword, rule in self._keyword_rules.items():
            top = rule.get('top', '未分类')
            # 应用分类映射
            top = self.CATEGORY_MAPPING.get(top, top)
            second = rule.get('second')
            category = f"{top}/{second}" if second else top
            
            keyword_entry = {
                "keyword": keyword,
                "weight": rule.get('weight', 10),
                "must_not_contain": rule.get('must_not_contain', []),
                "context_required": rule.get('context_required', [])
            }
            keyword_by_category[category].append(keyword_entry)
        
        # 生成关键词匹配规则
        for category, keywords in keyword_by_category.items():
            # 按权重分组
            high_weight = [k for k in keywords if k['weight'] >= 80]
            medium_weight = [k for k in keywords if 60 <= k['weight'] < 80]
            low_weight = [k for k in keywords if k['weight'] < 60]
            
            # 高权重关键词
            if high_weight:
                rule_entry = {
                    "match": "title",
                    "keywords": [k['keyword'] for k in high_weight],
                    "weight": 20,
                    "must_not_contain": self._merge_exclusions(high_weight)
                }
                category_rules[category]["rules"].append(rule_entry)
            
            # 中等权重关键词
            if medium_weight:
                rule_entry = {
                    "match": "title",
                    "keywords": [k['keyword'] for k in medium_weight],
                    "weight": 12,
                    "must_not_contain": self._merge_exclusions(medium_weight)
                }
                category_rules[category]["rules"].append(rule_entry)
            
            # 低权重关键词
            if low_weight:
                rule_entry = {
                    "match": "title",
                    "keywords": [k['keyword'] for k in low_weight],
                    "weight": 6,
                    "must_not_contain": self._merge_exclusions(low_weight)
                }
                category_rules[category]["rules"].append(rule_entry)
        
        # 识别优先级规则（工作相关）
        for category in list(category_rules.keys()):
            if category.startswith('工作'):
                priority_rules[category] = {
                    "weight": 100,
                    "rules": category_rules[category]["rules"]
                }
                del category_rules[category]
        
        return {
            "priority_rules": dict(priority_rules),
            "category_rules": dict(category_rules),
            "_meta": {
                "domain_count": len(self._domain_rules),
                "keyword_count": len(self._keyword_rules),
                "category_count": len(category_rules) + len(priority_rules)
            }
        }
    
    def _merge_exclusions(self, keywords: List[Dict]) -> List[str]:
        """合并排除规则"""
        exclusions = set()
        for k in keywords:
            exclusions.update(k.get('must_not_contain', []))
        return list(exclusions)
    
    def get_domain_rule(self, domain: str) -> Optional[Dict]:
        """获取域名规则"""
        # 精确匹配
        if domain in self._domain_rules:
            return self._domain_rules[domain]
        
        # 子域名匹配
        parts = domain.split('.')
        for i in range(len(parts)):
            parent = '.'.join(parts[i:])
            if parent in self._domain_rules:
                return self._domain_rules[parent]
        
        return None
    
    def get_keyword_matches(self, text: str) -> List[Dict]:
        """获取文本中匹配的关键词规则"""
        text_lower = text.lower()
        matches = []
        
        for keyword, rule in self._keyword_rules.items():
            if keyword.lower() in text_lower:
                # 检查排除规则
                exclusions = rule.get('must_not_contain', [])
                excluded = any(exc.lower() in text_lower for exc in exclusions)
                
                if not excluded:
                    # 检查上下文依赖
                    context_required = rule.get('context_required', [])
                    if context_required:
                        has_context = any(ctx.lower() in text_lower for ctx in context_required)
                        if not has_context:
                            continue
                    
                    matches.append({
                        "keyword": keyword,
                        "rule": rule,
                        "weight": rule.get('weight', 10)
                    })
        
        # 按权重排序
        matches.sort(key=lambda x: x['weight'], reverse=True)
        return matches


def merge_with_main_config(main_config: Dict, smart_rules: Dict) -> Dict:
    """将智能规则合并到主配置"""
    merged = dict(main_config)
    
    # 合并优先级规则
    if 'priority_rules' not in merged:
        merged['priority_rules'] = {}
    for category, rules in smart_rules.get('priority_rules', {}).items():
        if category not in merged['priority_rules']:
            merged['priority_rules'][category] = rules
        else:
            # 合并规则列表
            existing_rules = merged['priority_rules'][category].get('rules', [])
            new_rules = rules.get('rules', [])
            merged['priority_rules'][category]['rules'] = existing_rules + new_rules
    
    # 合并分类规则
    if 'category_rules' not in merged:
        merged['category_rules'] = {}
    for category, rules in smart_rules.get('category_rules', {}).items():
        if category not in merged['category_rules']:
            merged['category_rules'][category] = rules
        else:
            # 合并规则列表
            existing_rules = merged['category_rules'][category].get('rules', [])
            new_rules = rules.get('rules', [])
            merged['category_rules'][category]['rules'] = existing_rules + new_rules
    
    return merged


# 便捷函数
def load_smart_rules(config_dir: str = "agent/config") -> Dict:
    """加载智能规则"""
    loader = SmartRuleLoader(config_dir)
    return loader.load_all()
