"""
Performance Monitor - 性能监控服务
记录延迟、准确率、置信度分布等指标
"""

import logging
import statistics
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional


class PerformanceMonitor:
    """性能监控服务"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化性能监控服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.latency_threshold = self.config.get('latency_threshold_ms', 100)
        self.window_size = self.config.get('window_size', 10000)
        
        # 延迟记录
        self._latencies: deque = deque(maxlen=self.window_size)
        
        # 方法统计
        self._method_stats: Dict[str, Dict] = defaultdict(lambda: {
            'calls': 0,
            'correct': 0,
            'confidences': deque(maxlen=1000),
            'latencies': deque(maxlen=1000)
        })
        
        # 缓存统计
        self._cache_stats = {'hits': 0, 'misses': 0}
        
        # 内存使用样本
        self._memory_samples: deque = deque(maxlen=100)
        
        # 告警列表
        self._alerts: List[Dict] = []
        
        # 告警回调
        self._alert_callbacks: List[Callable] = []
        
        # 线程锁
        self._lock = threading.RLock()
        
        self.logger = logging.getLogger(__name__)
    
    def record_classification(
        self,
        method: str,
        latency_ms: float,
        confidence: float,
        correct: Optional[bool] = None
    ):
        """
        记录分类指标
        
        Args:
            method: 分类方法名称
            latency_ms: 延迟（毫秒）
            confidence: 置信度
            correct: 预测是否正确（可选）
        """
        with self._lock:
            # 记录全局延迟
            self._latencies.append(latency_ms)
            
            # 记录方法统计
            stats = self._method_stats[method]
            stats['calls'] += 1
            stats['confidences'].append(confidence)
            stats['latencies'].append(latency_ms)
            
            if correct is not None and correct:
                stats['correct'] += 1
            
            # 检查延迟阈值
            if latency_ms > self.latency_threshold:
                self._emit_alert(
                    'latency',
                    f"Classification latency {latency_ms:.2f}ms exceeds threshold {self.latency_threshold}ms",
                    {'method': method, 'latency_ms': latency_ms}
                )
    
    def record_cache_access(self, hit: bool):
        """
        记录缓存访问
        
        Args:
            hit: 是否命中
        """
        with self._lock:
            if hit:
                self._cache_stats['hits'] += 1
            else:
                self._cache_stats['misses'] += 1
    
    def record_memory_usage(self, bytes_used: int):
        """
        记录内存使用
        
        Args:
            bytes_used: 使用的字节数
        """
        with self._lock:
            self._memory_samples.append({
                'timestamp': datetime.now(),
                'bytes': bytes_used
            })
    
    def record_feedback(self, method: str, was_correct: bool):
        """
        记录用户反馈（用于计算准确率）
        
        Args:
            method: 分类方法名称
            was_correct: 预测是否正确
        """
        with self._lock:
            stats = self._method_stats[method]
            if was_correct:
                stats['correct'] += 1
    
    def get_latency_percentiles(self) -> Dict[str, float]:
        """
        获取延迟百分位数
        
        Returns:
            包含 p50, p95, p99 的字典
        """
        with self._lock:
            if not self._latencies:
                return {'p50': 0.0, 'p95': 0.0, 'p99': 0.0}
            
            sorted_latencies = sorted(self._latencies)
            n = len(sorted_latencies)
            
            def percentile(p: float) -> float:
                idx = int(n * p)
                idx = min(idx, n - 1)
                return sorted_latencies[idx]
            
            return {
                'p50': percentile(0.5),
                'p95': percentile(0.95),
                'p99': percentile(0.99)
            }
    
    def get_method_accuracy(self, method: str) -> float:
        """
        获取方法准确率
        
        Args:
            method: 方法名称
            
        Returns:
            准确率（0-1）
        """
        with self._lock:
            stats = self._method_stats.get(method, {})
            calls = stats.get('calls', 0)
            correct = stats.get('correct', 0)
            return correct / calls if calls > 0 else 0.0
    
    def get_method_latency_percentiles(self, method: str) -> Dict[str, float]:
        """
        获取特定方法的延迟百分位数
        
        Args:
            method: 方法名称
            
        Returns:
            包含 p50, p95, p99 的字典
        """
        with self._lock:
            stats = self._method_stats.get(method, {})
            latencies = list(stats.get('latencies', []))
            
            if not latencies:
                return {'p50': 0.0, 'p95': 0.0, 'p99': 0.0}
            
            sorted_latencies = sorted(latencies)
            n = len(sorted_latencies)
            
            def percentile(p: float) -> float:
                idx = int(n * p)
                idx = min(idx, n - 1)
                return sorted_latencies[idx]
            
            return {
                'p50': percentile(0.5),
                'p95': percentile(0.95),
                'p99': percentile(0.99)
            }
    
    def get_confidence_distribution(self, method: str) -> Dict[str, int]:
        """
        获取置信度分布
        
        Args:
            method: 方法名称
            
        Returns:
            置信度分布字典（按 0.1 分桶）
        """
        with self._lock:
            stats = self._method_stats.get(method, {})
            confidences = stats.get('confidences', [])
            
            distribution = defaultdict(int)
            for conf in confidences:
                bucket = int(conf * 10) / 10  # 0.0, 0.1, ..., 0.9
                distribution[f"{bucket:.1f}"] += 1
            
            return dict(distribution)
    
    def get_cache_hit_rate(self) -> float:
        """
        获取缓存命中率
        
        Returns:
            命中率（0-1）
        """
        with self._lock:
            total = self._cache_stats['hits'] + self._cache_stats['misses']
            return self._cache_stats['hits'] / total if total > 0 else 0.0
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        with self._lock:
            return self._cache_stats.copy()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        获取内存使用统计
        
        Returns:
            内存使用统计字典
        """
        with self._lock:
            if not self._memory_samples:
                return {'current': 0, 'avg': 0, 'max': 0}
            
            bytes_list = [s['bytes'] for s in self._memory_samples]
            return {
                'current': bytes_list[-1] if bytes_list else 0,
                'avg': statistics.mean(bytes_list),
                'max': max(bytes_list)
            }
    
    def _emit_alert(self, alert_type: str, message: str, details: Dict = None):
        """
        发出告警
        
        Args:
            alert_type: 告警类型
            message: 告警消息
            details: 详细信息
        """
        alert = {
            'type': alert_type,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self._alerts.append(alert)
        
        # 调用告警回调
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """
        添加告警回调
        
        Args:
            callback: 回调函数，接收 alert 字典作为参数
        """
        self._alert_callbacks.append(callback)
    
    def get_alerts(self, since: datetime = None) -> List[Dict]:
        """
        获取告警列表
        
        Args:
            since: 可选的时间过滤器
            
        Returns:
            告警列表
        """
        with self._lock:
            if since is None:
                return self._alerts.copy()
            
            return [
                a for a in self._alerts
                if datetime.fromisoformat(a['timestamp']) >= since
            ]
    
    def clear_alerts(self):
        """清空告警列表"""
        with self._lock:
            self._alerts.clear()
    
    def export_prometheus_metrics(self) -> str:
        """
        导出 Prometheus 格式指标
        
        Returns:
            Prometheus 格式的指标字符串
        """
        lines = []
        
        # 延迟指标
        percentiles = self.get_latency_percentiles()
        lines.append(f'classification_latency_p50 {percentiles["p50"]}')
        lines.append(f'classification_latency_p95 {percentiles["p95"]}')
        lines.append(f'classification_latency_p99 {percentiles["p99"]}')
        
        # 方法准确率和调用次数
        with self._lock:
            for method, stats in self._method_stats.items():
                accuracy = self.get_method_accuracy(method)
                # 转义方法名中的特殊字符
                safe_method = method.replace('"', '\\"')
                lines.append(f'classification_accuracy{{method="{safe_method}"}} {accuracy}')
                lines.append(f'classification_calls{{method="{safe_method}"}} {stats["calls"]}')
        
        # 缓存指标
        lines.append(f'cache_hit_rate {self.get_cache_hit_rate()}')
        lines.append(f'cache_hits_total {self._cache_stats["hits"]}')
        lines.append(f'cache_misses_total {self._cache_stats["misses"]}')
        
        # 内存指标
        memory = self.get_memory_usage()
        lines.append(f'memory_usage_bytes {memory["current"]}')
        
        return '\n'.join(lines)
    
    def generate_daily_report(self) -> Dict:
        """
        生成每日报告
        
        Returns:
            报告字典
        """
        with self._lock:
            method_reports = {}
            for method, stats in self._method_stats.items():
                method_reports[method] = {
                    'calls': stats['calls'],
                    'accuracy': self.get_method_accuracy(method),
                    'confidence_distribution': self.get_confidence_distribution(method),
                    'latency_percentiles': self.get_method_latency_percentiles(method)
                }
            
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'generated_at': datetime.now().isoformat(),
                'latency_percentiles': self.get_latency_percentiles(),
                'method_stats': method_reports,
                'cache_hit_rate': self.get_cache_hit_rate(),
                'cache_stats': self._cache_stats.copy(),
                'memory_usage': self.get_memory_usage(),
                'alerts_count': len(self._alerts),
                'total_classifications': sum(s['calls'] for s in self._method_stats.values())
            }
    
    def reset_stats(self):
        """重置所有统计数据"""
        with self._lock:
            self._latencies.clear()
            self._method_stats.clear()
            self._cache_stats = {'hits': 0, 'misses': 0}
            self._memory_samples.clear()
            self._alerts.clear()
