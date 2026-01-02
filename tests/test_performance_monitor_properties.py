"""
Property Tests for Performance Monitor
性能监控服务属性测试

Tests Properties:
- Property 23: Latency Percentile Accuracy
- Property 24: Latency Alert Emission
- Property 25: Prometheus Format Validity
"""

import re
import pytest
from hypothesis import given, strategies as st, settings, assume

# 尝试导入依赖
try:
    from src.services.performance_monitor import PerformanceMonitor
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# 策略定义
latency_strategy = st.floats(min_value=0.1, max_value=1000.0, allow_nan=False)
confidence_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
method_strategy = st.sampled_from([
    'rule_engine', 'ml_classifier', 'embedding_classifier', 'llm_classifier'
])


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestLatencyPercentileAccuracy:
    """延迟百分位数准确性测试 - Property 23"""
    
    @pytest.fixture
    def monitor(self):
        """创建性能监控器"""
        return PerformanceMonitor({
            'latency_threshold_ms': 100,
            'window_size': 10000
        })
    
    @settings(max_examples=50)
    @given(
        latencies=st.lists(
            st.floats(min_value=0.1, max_value=500.0, allow_nan=False),
            min_size=20,
            max_size=200
        )
    )
    def test_latency_percentile_accuracy(self, monitor, latencies):
        """
        Property 23: Latency Percentile Accuracy
        
        对于任何记录的分类延迟集合，计算的百分位数（p50, p95, p99）
        应该根据百分位数定义在数学上正确。
        
        Validates: Requirements 8.1, 8.2
        """
        # 记录延迟
        for latency in latencies:
            monitor.record_classification(
                method='test_method',
                latency_ms=latency,
                confidence=0.8
            )
        
        # 获取百分位数
        percentiles = monitor.get_latency_percentiles()
        
        # 排序延迟用于验证
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)
        
        # 计算预期百分位数
        def expected_percentile(p):
            idx = int(n * p)
            idx = min(idx, n - 1)
            return sorted_latencies[idx]
        
        expected_p50 = expected_percentile(0.5)
        expected_p95 = expected_percentile(0.95)
        expected_p99 = expected_percentile(0.99)
        
        # 验证百分位数（允许小误差）
        assert abs(percentiles['p50'] - expected_p50) < 0.01, \
            f"p50 should be {expected_p50}, got {percentiles['p50']}"
        assert abs(percentiles['p95'] - expected_p95) < 0.01, \
            f"p95 should be {expected_p95}, got {percentiles['p95']}"
        assert abs(percentiles['p99'] - expected_p99) < 0.01, \
            f"p99 should be {expected_p99}, got {percentiles['p99']}"
    
    @settings(max_examples=30)
    @given(
        latencies=st.lists(
            st.floats(min_value=0.1, max_value=500.0, allow_nan=False),
            min_size=5,
            max_size=100
        )
    )
    def test_percentile_ordering(self, monitor, latencies):
        """
        百分位数应该满足 p50 <= p95 <= p99。
        """
        for latency in latencies:
            monitor.record_classification(
                method='test',
                latency_ms=latency,
                confidence=0.8
            )
        
        percentiles = monitor.get_latency_percentiles()
        
        assert percentiles['p50'] <= percentiles['p95'], \
            f"p50 ({percentiles['p50']}) should be <= p95 ({percentiles['p95']})"
        assert percentiles['p95'] <= percentiles['p99'], \
            f"p95 ({percentiles['p95']}) should be <= p99 ({percentiles['p99']})"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestLatencyAlertEmission:
    """延迟告警发送测试 - Property 24"""
    
    @settings(max_examples=50)
    @given(
        threshold=st.floats(min_value=10.0, max_value=200.0, allow_nan=False),
        latency=st.floats(min_value=1.0, max_value=500.0, allow_nan=False)
    )
    def test_latency_alert_emission(self, threshold, latency):
        """
        Property 24: Latency Alert Emission
        
        对于任何延迟超过配置阈值的分类，
        Performance_Monitor 应该发出警告告警。
        
        Validates: Requirements 8.3
        """
        monitor = PerformanceMonitor({
            'latency_threshold_ms': threshold,
            'window_size': 1000
        })
        
        # 记录分类
        monitor.record_classification(
            method='test_method',
            latency_ms=latency,
            confidence=0.8
        )
        
        # 获取告警
        alerts = monitor.get_alerts()
        
        if latency > threshold:
            # 应该有告警
            assert len(alerts) > 0, \
                f"Should emit alert when latency {latency} > threshold {threshold}"
            
            # 验证告警类型
            latency_alerts = [a for a in alerts if a['type'] == 'latency']
            assert len(latency_alerts) > 0, "Should have latency alert"
        else:
            # 不应该有延迟告警
            latency_alerts = [a for a in alerts if a['type'] == 'latency']
            assert len(latency_alerts) == 0, \
                f"Should not emit alert when latency {latency} <= threshold {threshold}"
    
    def test_alert_callback(self):
        """
        告警回调应该被调用。
        """
        monitor = PerformanceMonitor({'latency_threshold_ms': 50})
        
        alerts_received = []
        
        def callback(alert):
            alerts_received.append(alert)
        
        monitor.add_alert_callback(callback)
        
        # 触发告警
        monitor.record_classification(
            method='test',
            latency_ms=100,  # 超过阈值
            confidence=0.8
        )
        
        assert len(alerts_received) > 0, "Callback should be called"
        assert alerts_received[0]['type'] == 'latency'


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestPrometheusFormatValidity:
    """Prometheus 格式有效性测试 - Property 25"""
    
    @pytest.fixture
    def monitor(self):
        """创建性能监控器"""
        return PerformanceMonitor({
            'latency_threshold_ms': 100,
            'window_size': 1000
        })
    
    # Prometheus 指标格式正则
    PROMETHEUS_LINE_PATTERN = re.compile(
        r'^[a-zA-Z_][a-zA-Z0-9_]*(\{[^}]*\})?\s+-?[0-9]+\.?[0-9]*([eE][+-]?[0-9]+)?$'
    )
    
    @settings(max_examples=30)
    @given(
        methods=st.lists(method_strategy, min_size=1, max_size=5),
        n_records=st.integers(min_value=1, max_value=20)
    )
    def test_prometheus_format_validity(self, monitor, methods, n_records):
        """
        Property 25: Prometheus Format Validity
        
        对于任何指标导出，输出应该符合有效的 Prometheus 文本格式规范。
        
        Validates: Requirements 8.4
        """
        # 记录一些数据
        for method in methods:
            for _ in range(n_records):
                monitor.record_classification(
                    method=method,
                    latency_ms=50.0,
                    confidence=0.8
                )
        
        # 记录缓存访问
        monitor.record_cache_access(hit=True)
        monitor.record_cache_access(hit=False)
        
        # 导出 Prometheus 格式
        output = monitor.export_prometheus_metrics()
        
        # 验证格式
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 验证行格式
            assert self.PROMETHEUS_LINE_PATTERN.match(line), \
                f"Invalid Prometheus format: '{line}'"
    
    def test_prometheus_contains_required_metrics(self, monitor):
        """
        Prometheus 输出应该包含必需的指标。
        """
        # 记录一些数据
        monitor.record_classification(
            method='test_method',
            latency_ms=50.0,
            confidence=0.8
        )
        monitor.record_cache_access(hit=True)
        
        output = monitor.export_prometheus_metrics()
        
        # 验证必需的指标存在
        required_metrics = [
            'classification_latency_p50',
            'classification_latency_p95',
            'classification_latency_p99',
            'cache_hit_rate',
            'cache_hits_total',
            'cache_misses_total'
        ]
        
        for metric in required_metrics:
            assert metric in output, f"Missing required metric: {metric}"
    
    def test_prometheus_method_labels(self, monitor):
        """
        方法指标应该包含正确的标签。
        """
        methods = ['rule_engine', 'ml_classifier']
        
        for method in methods:
            monitor.record_classification(
                method=method,
                latency_ms=50.0,
                confidence=0.8
            )
        
        output = monitor.export_prometheus_metrics()
        
        # 验证方法标签
        for method in methods:
            assert f'method="{method}"' in output, \
                f"Should have label for method {method}"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestMethodAccuracyTracking:
    """方法准确率追踪测试"""
    
    @pytest.fixture
    def monitor(self):
        """创建性能监控器"""
        return PerformanceMonitor({'latency_threshold_ms': 100})
    
    @settings(max_examples=50)
    @given(
        correct_count=st.integers(min_value=0, max_value=100),
        incorrect_count=st.integers(min_value=0, max_value=100)
    )
    def test_method_accuracy_calculation(self, monitor, correct_count, incorrect_count):
        """
        方法准确率应该正确计算。
        """
        total = correct_count + incorrect_count
        assume(total > 0)
        
        # 记录正确的分类
        for _ in range(correct_count):
            monitor.record_classification(
                method='test_method',
                latency_ms=50.0,
                confidence=0.8,
                correct=True
            )
        
        # 记录错误的分类
        for _ in range(incorrect_count):
            monitor.record_classification(
                method='test_method',
                latency_ms=50.0,
                confidence=0.8,
                correct=False
            )
        
        # 验证准确率
        accuracy = monitor.get_method_accuracy('test_method')
        expected_accuracy = correct_count / total
        
        assert abs(accuracy - expected_accuracy) < 0.001, \
            f"Accuracy should be {expected_accuracy}, got {accuracy}"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestConfidenceDistribution:
    """置信度分布测试"""
    
    @pytest.fixture
    def monitor(self):
        """创建性能监控器"""
        return PerformanceMonitor({'latency_threshold_ms': 100})
    
    @settings(max_examples=30)
    @given(
        confidences=st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            min_size=10,
            max_size=100
        )
    )
    def test_confidence_distribution(self, monitor, confidences):
        """
        置信度分布应该正确统计。
        """
        for conf in confidences:
            monitor.record_classification(
                method='test_method',
                latency_ms=50.0,
                confidence=conf
            )
        
        distribution = monitor.get_confidence_distribution('test_method')
        
        # 验证总数
        total_in_distribution = sum(distribution.values())
        assert total_in_distribution == len(confidences), \
            f"Distribution total {total_in_distribution} should equal input count {len(confidences)}"
        
        # 验证桶范围
        for bucket in distribution.keys():
            bucket_value = float(bucket)
            assert 0.0 <= bucket_value <= 0.9, \
                f"Bucket {bucket} should be in [0.0, 0.9]"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestDailyReport:
    """每日报告测试"""
    
    def test_daily_report_structure(self):
        """
        每日报告应该包含必需的字段。
        """
        monitor = PerformanceMonitor({'latency_threshold_ms': 100})
        
        # 记录一些数据
        monitor.record_classification(
            method='test_method',
            latency_ms=50.0,
            confidence=0.8
        )
        
        report = monitor.generate_daily_report()
        
        # 验证必需字段
        required_fields = [
            'date',
            'generated_at',
            'latency_percentiles',
            'method_stats',
            'cache_hit_rate',
            'alerts_count'
        ]
        
        for field in required_fields:
            assert field in report, f"Report should contain {field}"
