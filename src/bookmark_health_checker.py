"""
Bookmark Health Checker - 书签健康检查器
网络连接检测和书签状态验证
"""

import requests
import socket
import ssl
import re
import time
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from enum import Enum
from collections import Counter


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


class HealthChecker:
    """健康检查器 - 网络连接检测和书签状态验证"""
    
    def __init__(self, timeout: int = 10, max_workers: int = 20, user_agent: str = None):
        self.timeout = timeout
        self.max_workers = max_workers
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        # 创建HTTP会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # 设置重试策略
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def check_bookmarks(self, bookmarks: List[Dict], parallel: bool = True) -> List[Dict]:
        """检查书签健康状态"""
        if not bookmarks:
            return []
        
        if parallel:
            return self._check_bookmarks_parallel(bookmarks)
        else:
            return self._check_bookmarks_sequential(bookmarks)
    
    def _check_bookmarks_parallel(self, bookmarks: List[Dict]) -> List[Dict]:
        """并行检查书签"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_bookmark = {
                executor.submit(self._check_single_bookmark, bookmark): bookmark
                for bookmark in bookmarks
            }
            
            for future in as_completed(future_to_bookmark):
                bookmark = future_to_bookmark[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    error_result = self._create_error_result(bookmark, str(e))
                    results.append(error_result)
        
        return results
    
    def _check_bookmarks_sequential(self, bookmarks: List[Dict]) -> List[Dict]:
        """顺序检查书签"""
        results = []
        for bookmark in bookmarks:
            try:
                result = self._check_single_bookmark(bookmark)
                results.append(result)
            except Exception as e:
                error_result = self._create_error_result(bookmark, str(e))
                results.append(error_result)
        return results
    
    def _check_single_bookmark(self, bookmark: Dict) -> Dict:
        """检查单个书签"""
        url = bookmark.get('url', '')
        title = bookmark.get('title', '')
        
        check_result = {
            'url': url,
            'title': title,
            'original_bookmark': bookmark,
            'check_time': datetime.now().isoformat(),
            'status': HealthStatus.UNKNOWN.value,
            'status_code': None,
            'response_time': None,
            'final_url': url,
            'redirect_count': 0,
            'ssl_info': {},
            'content_info': {},
            'errors': [],
            'warnings': []
        }
        
        if not url or not self._is_valid_url(url):
            check_result['status'] = HealthStatus.ERROR.value
            check_result['errors'].append('无效或空URL')
            return check_result
        
        try:
            start_time = time.time()
            
            # 1. DNS解析检查
            dns_result = self._check_dns(url)
            if not dns_result['success']:
                check_result['status'] = HealthStatus.ERROR.value
                check_result['errors'].extend(dns_result['errors'])
                return check_result
            
            # 2. HTTP请求检查
            http_result = self._check_http(url)
            response_time = time.time() - start_time
            
            check_result['response_time'] = round(response_time * 1000, 2)
            check_result['status_code'] = http_result.get('status_code')
            check_result['final_url'] = http_result.get('final_url', url)
            check_result['redirect_count'] = http_result.get('redirect_count', 0)
            
            # 3. SSL信息检查（HTTPS）
            if url.startswith('https://'):
                ssl_info = self._check_ssl(url)
                check_result['ssl_info'] = ssl_info
            
            # 4. 内容信息检查
            if http_result.get('content'):
                content_info = self._analyze_content(http_result['content'])
                check_result['content_info'] = content_info
            
            # 5. 确定最终状态
            check_result['status'] = self._determine_health_status(
                http_result, check_result
            ).value
            
            # 6. 添加警告
            warnings = self._generate_warnings(http_result, check_result)
            check_result['warnings'] = warnings
            
        except Exception as e:
            check_result['status'] = HealthStatus.ERROR.value
            check_result['errors'].append(f'检查过程出错: {str(e)}')
        
        return check_result
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL有效性"""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except (ValueError, AttributeError) as e:
            self.logger.debug(f"URL验证失败: {url} - {e}")
            return False
    
    def _check_dns(self, url: str) -> Dict:
        """检查DNS解析"""
        result = {'success': False, 'errors': [], 'ip_addresses': []}
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]
            ip_addresses = socket.getaddrinfo(hostname, None)
            result['ip_addresses'] = list(set([ip[4][0] for ip in ip_addresses]))
            result['success'] = True
        except socket.gaierror as e:
            result['errors'].append(f'DNS解析失败: {str(e)}')
        except Exception as e:
            result['errors'].append(f'DNS检查出错: {str(e)}')
        return result
    
    def _check_http(self, url: str) -> Dict:
        """检查HTTP连接"""
        result = {
            'success': False, 'status_code': None, 'final_url': url,
            'redirect_count': 0, 'content': None, 'headers': {}, 'errors': []
        }
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True, stream=True)
            result['success'] = True
            result['status_code'] = response.status_code
            result['final_url'] = response.url
            result['redirect_count'] = len(response.history)
            result['headers'] = dict(response.headers)
            try:
                content = response.content[:10240]
                result['content'] = content
            except (requests.exceptions.RequestException, IOError) as e:
                self.logger.debug(f"读取响应内容失败: {e}")
        except requests.exceptions.Timeout:
            result['errors'].append(f'请求超时 (>{self.timeout}s)')
        except requests.exceptions.ConnectionError as e:
            result['errors'].append(f'连接错误: {str(e)}')
        except requests.exceptions.RequestException as e:
            result['errors'].append(f'请求异常: {str(e)}')
        except (ValueError, AttributeError) as e:
            result['errors'].append(f'HTTP检查出错: {str(e)}')
        return result
    
    def _check_ssl(self, url: str) -> Dict:
        """检查SSL证书信息"""
        ssl_info = {
            'valid': False, 'expires_at': None, 'days_until_expiry': None,
            'issuer': None, 'subject': None, 'errors': []
        }
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]
            port = parsed.port or 443
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    ssl_info['valid'] = True
                    ssl_info['subject'] = dict(x[0] for x in cert['subject'])
                    ssl_info['issuer'] = dict(x[0] for x in cert['issuer'])
                    expires_at = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    ssl_info['expires_at'] = expires_at.isoformat()
                    ssl_info['days_until_expiry'] = (expires_at - datetime.now()).days
        except ssl.SSLError as e:
            ssl_info['errors'].append(f'SSL握手失败: {str(e)}')
        except socket.timeout:
            ssl_info['errors'].append('SSL连接超时')
        except socket.gaierror as e:
            ssl_info['errors'].append(f'DNS解析失败: {str(e)}')
        except (ConnectionRefusedError, ConnectionResetError) as e:
            ssl_info['errors'].append(f'连接被拒绝: {str(e)}')
        except (ValueError, OSError) as e:
            ssl_info['errors'].append(f'SSL检查失败: {str(e)}')
        return ssl_info
    
    def _analyze_content(self, content: bytes) -> Dict:
        """分析网页内容"""
        content_info = {
            'size': len(content), 'content_type': None, 'title': None,
            'has_title_match': False, 'language': None, 'encoding': None
        }
        try:
            import chardet
            detected = chardet.detect(content)
            content_info['encoding'] = detected.get('encoding')
            text_content = content.decode(content_info['encoding'] or 'utf-8', errors='ignore')
            title_match = re.search(r'<title[^>]*>(.*?)</title>', text_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                content_info['title'] = title_match.group(1).strip()
            lang_match = re.search(r'<html[^>]*lang=["\']([^"\'>]+)["\']', text_content, re.IGNORECASE)
            if lang_match:
                content_info['language'] = lang_match.group(1)
        except (UnicodeDecodeError, LookupError) as e:
            self.logger.debug(f"内容解码失败: {e}")
        except re.error as e:
            self.logger.debug(f"正则匹配失败: {e}")
        return content_info
    
    def _determine_health_status(self, http_result: Dict, check_result: Dict) -> HealthStatus:
        """确定健康状态"""
        if not http_result.get('success'):
            return HealthStatus.ERROR
        status_code = http_result.get('status_code')
        if 200 <= status_code < 300:
            return HealthStatus.HEALTHY
        elif 300 <= status_code < 400:
            return HealthStatus.WARNING
        elif status_code in [404, 410]:
            return HealthStatus.ERROR
        elif 400 <= status_code < 500:
            return HealthStatus.WARNING
        else:
            return HealthStatus.ERROR
    
    def _generate_warnings(self, http_result: Dict, check_result: Dict) -> List[str]:
        """生成警告信息"""
        warnings = []
        response_time = check_result.get('response_time', 0)
        if response_time > 5000:
            warnings.append(f'响应时间过长: {response_time}ms')
        redirect_count = check_result.get('redirect_count', 0)
        if redirect_count > 3:
            warnings.append(f'重定向次数过多: {redirect_count}次')
        ssl_info = check_result.get('ssl_info', {})
        if ssl_info.get('days_until_expiry') is not None:
            days = ssl_info['days_until_expiry']
            if days < 30:
                warnings.append(f'SSL证书即将过期: {days}天后')
        status_code = check_result.get('status_code')
        if status_code and 300 <= status_code < 400:
            warnings.append(f'页面重定向: HTTP {status_code}')
        elif status_code and 400 <= status_code < 500:
            warnings.append(f'客户端错误: HTTP {status_code}')
        return warnings
    
    def _create_error_result(self, bookmark: Dict, error_message: str) -> Dict:
        """创建错误结果"""
        return {
            'url': bookmark.get('url', ''), 'title': bookmark.get('title', ''),
            'original_bookmark': bookmark, 'check_time': datetime.now().isoformat(),
            'status': HealthStatus.ERROR.value, 'status_code': None,
            'response_time': None, 'final_url': bookmark.get('url', ''),
            'redirect_count': 0, 'ssl_info': {}, 'content_info': {},
            'errors': [error_message], 'warnings': []
        }
    
    def get_summary(self, results: List[Dict]) -> Dict:
        """获取检查摘要"""
        if not results:
            return {
                'total_count': 0, 'accessible_count': 0, 'error_count': 0,
                'warning_count': 0, 'average_response_time': 0,
                'status_distribution': {}, 'common_errors': {},
                'slow_bookmarks': [], 'broken_bookmarks': [],
                'summary': '无书签需要检查'
            }
        
        total_count = len(results)
        status_counts = {}
        response_times = []
        errors = []
        slow_bookmarks = []
        broken_bookmarks = []
        
        for result in results:
            status = result.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            response_time = result.get('response_time')
            if response_time is not None:
                response_times.append(response_time)
                if response_time > 3000:
                    slow_bookmarks.append({
                        'url': result.get('url'), 'title': result.get('title'),
                        'response_time': response_time
                    })
            result_errors = result.get('errors', [])
            errors.extend(result_errors)
            if result.get('status') == HealthStatus.ERROR.value:
                broken_bookmarks.append({
                    'url': result.get('url'), 'title': result.get('title'),
                    'errors': result_errors
                })
        
        common_errors = dict(Counter(errors).most_common(10))
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        accessible_count = status_counts.get('healthy', 0) + status_counts.get('warning', 0)
        error_count = status_counts.get('error', 0)
        warning_count = status_counts.get('warning', 0)
        
        return {
            'total_count': total_count, 'accessible_count': accessible_count,
            'error_count': error_count, 'warning_count': warning_count,
            'average_response_time': round(average_response_time, 2),
            'status_distribution': status_counts, 'common_errors': common_errors,
            'slow_bookmarks': slow_bookmarks[:10], 'broken_bookmarks': broken_bookmarks[:10],
            'summary': f'检查完成: {accessible_count}/{total_count} 个链接可访问'
        }
