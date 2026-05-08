"""
Network Checker - 网络检查器抽象

定义网络健康检查的统一接口，支持多种实现。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class HealthStatus(Enum):
    """健康状态"""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""

    url: str
    status: HealthStatus
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    redirect_url: Optional[str] = None
    content_type: Optional[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class NetworkChecker(ABC):
    """网络检查器抽象接口

    深度: 高（统一接口，多种后端实现）
    接口: check_url(url) -> HealthCheckResult
    """

    @abstractmethod
    def check_url(self, url: str) -> HealthCheckResult:
        """检查单个URL的健康状态

        Args:
            url: 要检查的URL

        Returns:
            健康检查结果
        """
        pass

    @abstractmethod
    def check_batch(
        self, urls: list[str], max_workers: int = 10
    ) -> list[HealthCheckResult]:
        """批量检查URL

        Args:
            urls: URL列表
            max_workers: 最大并发数

        Returns:
            健康检查结果列表
        """
        pass


class SyncHTTPChecker(NetworkChecker):
    """同步HTTP检查器

    使用 requests 库进行同步HTTP检查。
    深度: 中（简单接口，处理重试、超时、重定向等）
    """

    def __init__(
        self,
        timeout: int = 10,
        user_agent: Optional[str] = None,
        max_retries: int = 2,
    ):
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        self.timeout = timeout
        self.max_retries = max_retries

        # 创建会话
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (compatible; CleanBook/2.0)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

        # 设置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def check_url(self, url: str) -> HealthCheckResult:
        import time

        start_time = time.time()

        try:
            response = self.session.head(
                url, timeout=self.timeout, allow_redirects=True
            )

            # 如果 HEAD 不支持，尝试 GET
            if response.status_code == 405:
                response = self.session.get(
                    url, timeout=self.timeout, allow_redirects=True, stream=True
                )

            response_time = (time.time() - start_time) * 1000

            # 判断状态
            if 200 <= response.status_code < 300:
                status = HealthStatus.HEALTHY
            elif 300 <= response.status_code < 400:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.ERROR

            return HealthCheckResult(
                url=url,
                status=status,
                status_code=response.status_code,
                response_time_ms=response_time,
                redirect_url=str(response.url) if response.url != url else None,
                content_type=response.headers.get("Content-Type"),
            )

        except Exception as e:
            return HealthCheckResult(
                url=url,
                status=HealthStatus.ERROR,
                error_message=str(e),
            )

    def check_batch(
        self, urls: list[str], max_workers: int = 10
    ) -> list[HealthCheckResult]:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.check_url, url): url for url in urls}

            for future in as_completed(future_to_url):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    url = future_to_url[future]
                    results.append(
                        HealthCheckResult(
                            url=url,
                            status=HealthStatus.ERROR,
                            error_message=str(e),
                        )
                    )

        return results
