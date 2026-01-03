"""
URL Analyzer - URL 智能分析器

提供更精细的 URL 分析能力：
1. GitHub/GitLab 仓库识别
2. 文档站点识别
3. API 文档识别
4. 博客/文章识别
5. 视频平台识别
"""

import re
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass


@dataclass
class URLAnalysis:
    """URL 分析结果"""
    domain: str
    subdomain: str
    path: str
    path_segments: List[str]
    query_params: Dict[str, str]
    
    # 识别结果
    site_type: str  # github, gitlab, docs, blog, video, api, tool, etc.
    content_type: str  # repo, issue, pr, wiki, article, video, etc.
    
    # 额外信息
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    is_official_docs: bool = False
    language_hint: Optional[str] = None
    
    # 分类提示
    category_hints: List[Tuple[str, float]] = None  # [(category, confidence), ...]
    
    def __post_init__(self):
        if self.category_hints is None:
            self.category_hints = []


class URLAnalyzer:
    """URL 智能分析器"""
    
    # GitHub 路径模式
    GITHUB_PATTERNS = {
        'repo': re.compile(r'^/([^/]+)/([^/]+)/?$'),
        'blob': re.compile(r'^/([^/]+)/([^/]+)/blob/'),
        'tree': re.compile(r'^/([^/]+)/([^/]+)/tree/'),
        'issues': re.compile(r'^/([^/]+)/([^/]+)/issues'),
        'pull': re.compile(r'^/([^/]+)/([^/]+)/pull'),
        'releases': re.compile(r'^/([^/]+)/([^/]+)/releases'),
        'wiki': re.compile(r'^/([^/]+)/([^/]+)/wiki'),
        'actions': re.compile(r'^/([^/]+)/([^/]+)/actions'),
        'discussions': re.compile(r'^/([^/]+)/([^/]+)/discussions'),
    }
    
    # 文档站点模式
    DOCS_PATTERNS = [
        re.compile(r'docs?\.([\w-]+)\.(com|org|io|dev)'),
        re.compile(r'([\w-]+)\.readthedocs\.(io|org)'),
        re.compile(r'/docs?(/|$)'),
        re.compile(r'/documentation(/|$)'),
        re.compile(r'/guide(/|$)'),
        re.compile(r'/manual(/|$)'),
        re.compile(r'/reference(/|$)'),
        re.compile(r'/api-docs?(/|$)'),
    ]
    
    # 博客/文章模式
    BLOG_PATTERNS = [
        re.compile(r'/blog(/|$)'),
        re.compile(r'/posts?(/|$)'),
        re.compile(r'/articles?(/|$)'),
        re.compile(r'/news(/|$)'),
        re.compile(r'/\d{4}/\d{2}/'),  # 日期格式路径
    ]
    
    # 视频平台
    VIDEO_PLATFORMS = {
        'youtube.com': 'YouTube',
        'youtu.be': 'YouTube',
        'bilibili.com': 'Bilibili',
        'vimeo.com': 'Vimeo',
        'twitch.tv': 'Twitch',
    }
    
    # 编程语言文件扩展名
    LANG_EXTENSIONS = {
        'py': 'Python', 'pyw': 'Python', 'pyx': 'Python',
        'js': 'JavaScript', 'jsx': 'JavaScript', 'mjs': 'JavaScript',
        'ts': 'TypeScript', 'tsx': 'TypeScript',
        'go': 'Go',
        'rs': 'Rust',
        'java': 'Java', 'kt': 'Kotlin', 'kts': 'Kotlin',
        'cpp': 'C++', 'cc': 'C++', 'cxx': 'C++', 'hpp': 'C++',
        'c': 'C', 'h': 'C',
        'swift': 'Swift',
        'rb': 'Ruby',
        'php': 'PHP',
        'cs': 'C#',
        'vue': 'Vue', 'svelte': 'Svelte',
        'zig': 'Zig',
        'ex': 'Elixir', 'exs': 'Elixir',
    }
    
    def __init__(self):
        pass
    
    def analyze(self, url: str) -> URLAnalysis:
        """分析 URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 提取子域名
            subdomain = ''
            domain_parts = domain.split('.')
            if len(domain_parts) > 2:
                subdomain = '.'.join(domain_parts[:-2])
                domain = '.'.join(domain_parts[-2:])
            
            # 移除 www
            if subdomain == 'www':
                subdomain = ''
            
            path = parsed.path
            path_segments = [s for s in path.split('/') if s]
            
            # 解析查询参数
            query_params = {}
            if parsed.query:
                query_params = {k: v[0] if len(v) == 1 else v 
                               for k, v in parse_qs(parsed.query).items()}
            
            # 识别站点类型和内容类型
            site_type, content_type = self._identify_site_type(
                domain, subdomain, path, path_segments
            )
            
            # 创建分析结果
            analysis = URLAnalysis(
                domain=domain,
                subdomain=subdomain,
                path=path,
                path_segments=path_segments,
                query_params=query_params,
                site_type=site_type,
                content_type=content_type,
            )
            
            # 提取额外信息
            self._extract_repo_info(analysis, domain, path)
            self._detect_language(analysis, path, path_segments)
            self._generate_category_hints(analysis)
            
            return analysis
            
        except Exception as e:
            return URLAnalysis(
                domain='',
                subdomain='',
                path='',
                path_segments=[],
                query_params={},
                site_type='unknown',
                content_type='unknown',
            )
    
    def _identify_site_type(self, domain: str, subdomain: str, 
                           path: str, path_segments: List[str]) -> Tuple[str, str]:
        """识别站点类型"""
        full_domain = f"{subdomain}.{domain}" if subdomain else domain
        
        # GitHub
        if domain in ('github.com', 'github.io'):
            return self._identify_github_content(path)
        
        # GitLab
        if domain == 'gitlab.com' or 'gitlab' in subdomain:
            return self._identify_gitlab_content(path)
        
        # 视频平台
        if domain in self.VIDEO_PLATFORMS:
            return 'video', self._identify_video_content(domain, path, path_segments)
        
        # 文档站点
        for pattern in self.DOCS_PATTERNS:
            if pattern.search(full_domain) or pattern.search(path):
                return 'docs', 'documentation'
        
        # 博客/文章
        for pattern in self.BLOG_PATTERNS:
            if pattern.search(path):
                return 'blog', 'article'
        
        # API 文档
        if any(seg in path_segments for seg in ['api', 'swagger', 'openapi']):
            return 'api', 'api_docs'
        
        # 默认
        return 'website', 'webpage'
    
    def _identify_github_content(self, path: str) -> Tuple[str, str]:
        """识别 GitHub 内容类型"""
        for content_type, pattern in self.GITHUB_PATTERNS.items():
            if pattern.match(path):
                return 'github', content_type
        
        # 检查是否是用户/组织页面
        if re.match(r'^/[^/]+/?$', path):
            return 'github', 'profile'
        
        return 'github', 'other'
    
    def _identify_gitlab_content(self, path: str) -> Tuple[str, str]:
        """识别 GitLab 内容类型"""
        if '/-/issues' in path:
            return 'gitlab', 'issues'
        if '/-/merge_requests' in path:
            return 'gitlab', 'merge_request'
        if '/-/pipelines' in path:
            return 'gitlab', 'ci'
        if '/-/blob/' in path or '/-/tree/' in path:
            return 'gitlab', 'code'
        
        return 'gitlab', 'repo'
    
    def _identify_video_content(self, domain: str, path: str, 
                                path_segments: List[str]) -> str:
        """识别视频内容类型"""
        if domain in ('youtube.com', 'youtu.be'):
            if '/watch' in path or domain == 'youtu.be':
                return 'video'
            if '/playlist' in path:
                return 'playlist'
            if '/channel' in path or '/c/' in path or '/@' in path:
                return 'channel'
        
        if domain == 'bilibili.com':
            if '/video/' in path:
                return 'video'
            if '/bangumi/' in path:
                return 'anime'
            if '/read/' in path:
                return 'article'
        
        return 'video'
    
    def _extract_repo_info(self, analysis: URLAnalysis, domain: str, path: str):
        """提取仓库信息"""
        if analysis.site_type in ('github', 'gitlab'):
            match = re.match(r'^/([^/]+)/([^/]+)', path)
            if match:
                analysis.repo_owner = match.group(1)
                analysis.repo_name = match.group(2)
    
    def _detect_language(self, analysis: URLAnalysis, path: str, 
                        path_segments: List[str]):
        """检测编程语言"""
        # 从文件扩展名检测
        if path_segments:
            last_segment = path_segments[-1]
            if '.' in last_segment:
                ext = last_segment.rsplit('.', 1)[-1].lower()
                if ext in self.LANG_EXTENSIONS:
                    analysis.language_hint = self.LANG_EXTENSIONS[ext]
                    return
        
        # 从路径关键词检测
        path_lower = path.lower()
        lang_keywords = {
            'python': 'Python', 'py': 'Python',
            'javascript': 'JavaScript', 'js': 'JavaScript',
            'typescript': 'TypeScript', 'ts': 'TypeScript',
            'golang': 'Go', 'go': 'Go',
            'rust': 'Rust', 'rs': 'Rust',
            'java': 'Java',
            'kotlin': 'Kotlin',
            'swift': 'Swift',
            'cpp': 'C++', 'c++': 'C++',
        }
        
        for keyword, lang in lang_keywords.items():
            if f'/{keyword}/' in path_lower or f'-{keyword}' in path_lower:
                analysis.language_hint = lang
                return
    
    def _generate_category_hints(self, analysis: URLAnalysis):
        """生成分类提示"""
        hints = []
        
        # 基于站点类型
        site_type_hints = {
            'github': [('编程/代码仓库', 0.9)],
            'gitlab': [('编程/代码仓库', 0.9)],
            'docs': [('学习/技术文档', 0.8)],
            'blog': [('社区', 0.6)],
            'video': [('娱乐/影音', 0.5)],
            'api': [('学习/技术文档', 0.7)],
        }
        
        if analysis.site_type in site_type_hints:
            hints.extend(site_type_hints[analysis.site_type])
        
        # 基于内容类型
        content_type_hints = {
            'issues': [('编程/代码仓库', 0.7)],
            'pull': [('编程/代码仓库', 0.7)],
            'wiki': [('学习/技术文档', 0.8)],
            'releases': [('编程/代码仓库', 0.7)],
            'documentation': [('学习/技术文档', 0.8)],
        }
        
        if analysis.content_type in content_type_hints:
            hints.extend(content_type_hints[analysis.content_type])
        
        # 基于语言提示
        if analysis.language_hint:
            hints.append((f'编程/编程语言', 0.5))
        
        analysis.category_hints = hints


# 便捷函数
def analyze_url(url: str) -> URLAnalysis:
    """分析 URL"""
    analyzer = URLAnalyzer()
    return analyzer.analyze(url)
