#!/usr/bin/env python3
"""
第二轮智能分类 - 基于标题和URL的AI推理分类
生成可导入浏览器的HTML书签文件
"""
import json
import re
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

# 分类规则 - 基于域名和关键词的智能匹配
DOMAIN_RULES = {
    # 工作台
    'zego': '工作台',
    'bgi.com': '工作台', 
    'genomics.cn': '工作台',
    'dingtalk': '工作台',
    'tapd.cn': '工作台',
    
    # AI/人工智能
    'openai.com': 'AI/模型平台',
    'anthropic.com': 'AI/模型平台',
    'claude': 'AI/模型平台',
    'chatgpt': 'AI/模型平台',
    'deepseek': 'AI/模型平台',
    'huggingface': 'AI/模型平台',
    'hf-mirror': 'AI/模型平台',
    'qwen': 'AI/模型平台',
    'mistral': 'AI/模型平台',
    'gemini': 'AI/模型平台',
    'perplexity': 'AI/模型平台',
    'chatglm': 'AI/模型平台',
    'baichuan': 'AI/模型平台',
    'hunyuan': 'AI/模型平台',
    'metaso': 'AI/模型平台',
    'genspark': 'AI/模型平台',
    'reka.ai': 'AI/模型平台',
    'anakin.ai': 'AI/模型平台',
    'chat01.ai': 'AI/模型平台',
    'unlimitedai': 'AI/模型平台',
    'copilot': 'AI/AI编程',
    'cursor': 'AI/AI编程',
    'codeium': 'AI/AI编程',
    'qodo': 'AI/AI编程',
    'trae.ai': 'AI/AI编程',
    'marscode': 'AI/AI编程',
    'aider': 'AI/AI编程',
    'cto.new': 'AI/AI编程',
    'forgecode': 'AI/AI编程',
    'midjourney': 'AI/图像生成',
    'ghibli': 'AI/图像生成',
    'styleai': 'AI/图像生成',
    'comfy': 'AI/图像生成',
    'stable-diffusion': 'AI/图像生成',
    'image2video': 'AI/图像生成',
    'nvidia.cn/training': 'AI/机器学习',
    'kaggle': 'AI/机器学习',
    'deep-ml': 'AI/机器学习',
    '3blue1brown': 'AI/机器学习',
    
    # 编程
    'github.com': '编程/代码仓库',
    'gitlab': '编程/代码仓库',
    'gitee': '编程/代码仓库',
    'gitcode': '编程/代码仓库',
    'docker': '编程/DevOps',
    'kubernetes': '编程/DevOps',
    'k8s': '编程/DevOps',
    'jenkins': '编程/DevOps',
    'grafana': '编程/DevOps',
    'prometheus': '编程/DevOps',
    'elastic': '编程/DevOps',
    'kibana': '编程/DevOps',
    'rust': '编程/编程语言',
    'golang': '编程/编程语言',
    'python': '编程/编程语言',
    'javascript': '编程/编程语言',
    'typescript': '编程/编程语言',
    'vue': '编程/Web开发',
    'react': '编程/Web开发',
    'echarts': '编程/Web开发',
    'vscode': '编程/开发工具',
    'jetbrains': '编程/开发工具',
    'leetgpu': '编程/GPU编程',
    'leetcode': '编程/算法练习',
    'nowcoder': '编程/算法练习',
    
    # 生物信息
    'ncbi': '生物/生物信息',
    'bioconda': '生物/生物信息',
    'biocontainers': '生物/生物信息',
    'illumina': '生物/生物信息',
    'singlecell': '生物/生物信息',
    'gatk': '生物/生物信息',
    'huttenhower': '生物/生物信息',
    'rosalind': '生物/生物信息',
    'nature.com': '生物/论文',
    'biorxiv': '生物/论文',
    'researchhub': '生物/论文',
    
    # 学习
    'coursera': '学习/在线课程',
    'udemy': '学习/在线课程',
    'learn.microsoft': '学习/技术文档',
    'docs.': '学习/技术文档',
    'documentation': '学习/技术文档',
    'tutorial': '学习/教程',
    'runoob': '学习/教程',
    'hello-algo': '学习/教程',
    'mit.edu': '学习/在线课程',
    'datacastle': '学习/数据竞赛',
    
    # 社区
    'v2ex': '社区/技术论坛',
    'linux.do': '社区/技术论坛',
    'reddit': '社区/论坛',
    'stackoverflow': '社区/问答',
    'segmentfault': '社区/问答',
    'juejin': '社区/技术博客',
    'cnblogs': '社区/技术博客',
    'csdn': '社区/技术博客',
    'coolshell': '社区/技术博客',
    'appinn': '社区/软件论坛',
    '52pojie': '社区/技术论坛',
    'kafan': '社区/技术论坛',
    
    # 工具
    'notion': '工具/笔记',
    'obsidian': '工具/笔记',
    'remnote': '工具/笔记',
    'notepad': '工具/笔记',
    'mermaid': '工具/图表',
    'draw.io': '工具/图表',
    'excalidraw': '工具/图表',
    'diagrams': '工具/图表',
    'pairdrop': '工具/文件传输',
    'wormhole': '工具/文件传输',
    'dropmefiles': '工具/文件传输',
    'airportal': '工具/文件传输',
    'fanyi': '工具/翻译',
    'translate': '工具/翻译',
    'deepl': '工具/翻译',
    'iciba': '工具/翻译',
    'parsec': '工具/远程桌面',
    'cloud.tencent': '工具/云服务',
    'huaweicloud': '工具/云服务',
    'aliyun': '工具/云服务',
    
    # 娱乐
    'bilibili': '娱乐/视频',
    'youtube': '娱乐/视频',
    'iqiyi': '娱乐/视频',
    'youku': '娱乐/视频',
    'kuaishou': '娱乐/视频',
    'weibo': '娱乐/社交',
    'spotify': '娱乐/音乐',
    'music': '娱乐/音乐',
    
    # 资讯
    'news': '资讯/新闻',
    'landiannews': '资讯/科技资讯',
    'aiopenminds': '资讯/AI资讯',
    'aisourcehub': '资讯/AI资讯',
    
    # 其他常见
    'taobao': '购物/电商',
    'jd.com': '购物/电商',
    'mozilla': '浏览器/Firefox',
    'chrome': '浏览器/Chrome',
    'annas-archive': '资源/电子书',
    'z-library': '资源/电子书',
    'xmac': '资源/Mac软件',
    'macked': '资源/Mac软件',
    'portapps': '资源/便携软件',
    'norvig': '学习/编程思想',
    'geospy': 'AI/图像识别',
    'freedium': '工具/阅读工具',
    'youper': 'AI/AI应用',
    'coder.com': '编程/云开发环境',
    'jina.ai': 'AI/AI搜索',
    'greenteapress': '学习/免费书籍',
    'nvidia.com': 'AI/GPU计算',
    'solidot': '资讯/科技资讯',
    'thefarside': '娱乐/漫画',
    'go.dev': '编程/Go语言',
    'roocode': 'AI/AI编程',
    'ydma.com': '学习/职业发展',
    'felix.link': 'AI/AI工具',
    'falling42': '编程/教程',
    'hutusi': 'AI/机器学习',
    'naodai.org': '资源/网盘',
}

TITLE_KEYWORDS = {
    # AI相关
    ('llm', 'gpt', 'transformer', 'attention', 'neural', '大模型', '深度学习', 'machine learning', 'deep learning'): 'AI/机器学习',
    ('claude', 'chatgpt', 'gemini', 'qwen', '通义', '文心', '智谱', 'ai chat', 'ai助手'): 'AI/模型平台',
    ('copilot', 'cursor', 'ai编程', 'ai code', 'code assist', 'kiro', 'aider'): 'AI/AI编程',
    ('stable diffusion', 'midjourney', 'dall-e', '图像生成', 'ghibli', '吉卜力', 'image generator'): 'AI/图像生成',
    ('prompt', '提示词'): 'AI/提示工程',
    ('agent', 'langchain'): 'AI/AI Agent',
    
    # 编程相关
    ('github', 'gitlab', 'repository', '仓库'): '编程/代码仓库',
    ('docker', 'kubernetes', 'k8s', 'devops', 'ci/cd', 'jenkins', '容器', 'container'): '编程/DevOps',
    ('rust', 'golang', 'go语言', 'python', 'java', 'c++', 'javascript', 'typescript'): '编程/编程语言',
    ('vue', 'react', 'angular', 'frontend', '前端', 'css', 'html'): '编程/Web开发',
    ('api', 'sdk', '接口', 'swagger'): '编程/API',
    ('gpu', 'cuda', '并行计算', 'hpc'): '编程/GPU编程',
    ('tmux', 'vim', 'terminal', '终端'): '编程/开发工具',
    ('linux', 'ubuntu', 'shell', 'bash'): '编程/Linux',
    
    # 生物信息
    ('基因', 'genome', 'dna', 'rna', '测序', 'sequencing', 'bioinformatics', '生物信息'): '生物/生物信息',
    ('单细胞', 'single cell', 'scrna', 'single-cell'): '生物/单细胞',
    ('bwa', 'gatk', 'samtools', 'picard', 'kneaddata'): '生物/生物信息工具',
    ('protein', '蛋白质', 'alphafold'): '生物/蛋白质',
    
    # 学习
    ('教程', 'tutorial', '入门', '学习', 'learn', 'course', '指南', 'guide'): '学习/教程',
    ('文档', 'documentation', 'docs', '手册', 'manual', 'reference'): '学习/技术文档',
    ('算法', 'algorithm', '数据结构', 'leetcode'): '学习/算法',
    ('cheat sheet', '速查', '备忘'): '学习/速查表',
    
    # 工具
    ('翻译', 'translate', 'translator'): '工具/翻译',
    ('文件传输', 'file sharing', 'file transfer', 'share file'): '工具/文件传输',
    ('笔记', 'note', 'markdown'): '工具/笔记',
    ('图表', 'diagram', 'chart', 'mermaid', 'plantuml'): '工具/图表',
    ('下载', 'download', '破解', 'crack', '汉化'): '工具/软件下载',
    ('pdf', '文档处理'): '工具/文档处理',
    ('vpn', '代理', 'proxy'): '工具/网络工具',
    
    # 资讯
    ('新闻', 'news', '资讯', '快讯'): '资讯/新闻',
    ('周刊', 'weekly', '日报'): '资讯/周刊',
    
    # 其他
    ('视频', 'video', '影音'): '娱乐/视频',
    ('音乐', 'music'): '娱乐/音乐',
    ('游戏', 'game'): '娱乐/游戏',
    ('电子书', 'ebook', 'pdf书'): '资源/电子书',
    ('流量卡', '手机卡'): '生活/通讯',
    ('银行', 'bank', '开户'): '生活/金融',
}

def classify_bookmark(title, url):
    """基于标题和URL智能分类"""
    title_lower = title.lower()
    url_lower = url.lower()
    domain = urlparse(url).netloc.lower()
    
    # 1. 先检查域名规则
    for pattern, category in DOMAIN_RULES.items():
        if pattern in domain or pattern in url_lower:
            return category
    
    # 2. 检查标题关键词
    for keywords, category in TITLE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return category
    
    # 3. 特殊处理 github.io 页面
    if 'github.io' in domain:
        if any(kw in title_lower for kw in ['blog', '博客']):
            return '社区/技术博客'
        return '编程/开源项目'
    
    # 4. 根据URL路径推断
    path = urlparse(url).path.lower()
    if '/docs' in path or '/documentation' in path:
        return '学习/技术文档'
    if '/blog' in path:
        return '社区/技术博客'
    if '/tutorial' in path or '/guide' in path:
        return '学习/教程'
    
    # 5. 根据域名后缀和特征推断
    if '.edu' in domain or 'university' in domain or 'mit.edu' in domain:
        return '学习/学术资源'
    if 'cloud' in domain:
        return '工具/云服务'
    if 'app.' in domain or '.app' in domain:
        return '工具/在线工具'
    if 'api' in domain or 'api' in path:
        return '编程/API'
    
    # 6. 根据标题特征推断
    if any(kw in title_lower for kw in ['工具', 'tool', 'generator', '生成器']):
        return '工具/在线工具'
    if any(kw in title_lower for kw in ['dashboard', '仪表盘', '控制台', 'console']):
        return '工具/在线服务'
    if any(kw in title_lower for kw in ['pricing', '价格', '定价', 'plan']):
        return '工具/在线服务'
    
    return None  # 无法分类

def generate_html(categorized_bookmarks):
    """生成浏览器书签HTML"""
    html = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
'''
    
    # 按主分类排序
    main_categories = defaultdict(lambda: defaultdict(list))
    for cat, bookmarks in categorized_bookmarks.items():
        if '/' in cat:
            main, sub = cat.split('/', 1)
        else:
            main, sub = cat, ''
        main_categories[main][sub].extend(bookmarks)
    
    # 分类排序优先级
    category_order = ['工作台', 'AI', '编程', '生物', '学习', '社区', '工具', '资讯', '娱乐', '其他']
    
    for main in category_order:
        if main not in main_categories:
            continue
        subcats = main_categories[main]
        
        html += f'    <DT><H3>{main}</H3>\n'
        html += '    <DL><p>\n'
        
        for sub, bookmarks in sorted(subcats.items()):
            if sub:
                html += f'        <DT><H3>{sub}</H3>\n'
                html += '        <DL><p>\n'
                for bm in bookmarks:
                    title = bm['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                    html += f'            <DT><A HREF="{bm["url"]}">{title}</A>\n'
                html += '        </DL><p>\n'
            else:
                for bm in bookmarks:
                    title = bm['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                    html += f'        <DT><A HREF="{bm["url"]}">{title}</A>\n'
        
        html += '    </DL><p>\n'
    
    html += '</DL><p>\n'
    return html

def main():
    # 读取第一轮结果
    with open('../output-round-1/all_bookmarks.json', 'r', encoding='utf-8') as f:
        bookmarks = json.load(f)
    
    print(f'读取 {len(bookmarks)} 个书签')
    
    # 分类
    categorized = defaultdict(list)
    reclassified = 0
    
    for bm in bookmarks:
        title = bm['title']
        url = bm['url']
        original_cat = bm['category']
        confidence = bm['confidence']
        
        # 如果原分类置信度低或未分类，尝试重新分类
        if confidence < 0.75 or '未分类' in original_cat:
            new_cat = classify_bookmark(title, url)
            if new_cat:
                categorized[new_cat].append({'title': title, 'url': url})
                reclassified += 1
                continue
        
        # 保持原分类
        categorized[original_cat].append({'title': title, 'url': url})
    
    print(f'重新分类: {reclassified} 个')
    print(f'分类数: {len(categorized)}')
    
    # 生成HTML
    html = generate_html(categorized)
    
    output_file = 'bookmarks_final.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'已生成: {output_file}')
    
    # 打印分类统计
    print('\n分类统计:')
    for cat, items in sorted(categorized.items(), key=lambda x: -len(x[1])):
        print(f'  {cat}: {len(items)} 个')

if __name__ == '__main__':
    main()
