"""
Property Tests for Active Learning Engine
主动学习引擎属性测试

Tests Properties:
- Property 8: Low-Confidence Detection and Queuing
- Property 9: Uncertainty Sampling Priority
- Property 10: Session Request Limit
- Property 11: Feedback Persistence
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime

# 尝试导入依赖
try:
    from src.services.active_learning import ActiveLearningEngine, ReviewItem
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# 策略定义
confidence_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
category_strategy = st.sampled_from([
    '编程开发', '人工智能', '数据科学', '前端开发', '后端开发',
    '机器学习', '深度学习', '云计算', '网络安全', '未分类'
])
url_strategy = st.from_regex(r'https://[a-z]+\.[a-z]+/[a-z]+', fullmatch=True)
title_strategy = st.text(min_size=5, max_size=100)


def create_bookmark(url: str = "https://example.com/page", title: str = "Example") -> dict:
    """创建书签字典"""
    return {
        'id': str(hash(url)),
        'url': url,
        'title': title
    }


def create_alternatives(n: int = 3) -> list:
    """创建备选分类列表"""
    categories = ['编程开发', '人工智能', '数据科学', '前端开发', '后端开发']
    return [(categories[i % len(categories)], 0.1 * (n - i)) for i in range(n)]


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestLowConfidenceDetection:
    """低置信度检测测试 - Property 8"""
    
    @pytest.fixture
    def engine(self):
        """创建主动学习引擎"""
        config = {
            'confidence_threshold': 0.6,
            'max_requests_per_session': 10,
            'persist_path': '/tmp/test_active_learning'
        }
        return ActiveLearningEngine(config)
    
    @settings(max_examples=100)
    @given(
        confidence=st.floats(min_value=0.0, max_value=0.59, allow_nan=False),
        category=category_strategy
    )
    def test_low_confidence_detection_and_queuing(self, engine, confidence, category):
        """
        Property 8: Low-Confidence Detection and Queuing
        
        对于任何置信度低于配置阈值的已分类书签，
        应该被 Active_Learning_Engine 识别并出现在审核队列中。
        
        Validates: Requirements 3.1, 3.2
        """
        bookmark = create_bookmark()
        alternatives = create_alternatives()
        
        # 处理分类结果
        result = engine.process_classification(
            bookmark=bookmark,
            category=category,
            confidence=confidence,
            alternatives=alternatives
        )
        
        # 低置信度应该被检测到
        assert result is not None, \
            f"Low confidence {confidence} should be detected (threshold: 0.6)"
        
        # 应该出现在队列中
        assert engine.get_queue_size() > 0, \
            "Low confidence item should be in review queue"
        
        # 验证 ReviewItem 属性
        assert result.confidence == confidence
        assert result.predicted_category == category
        assert result.url == bookmark['url']
    
    @settings(max_examples=100)
    @given(
        confidence=st.floats(min_value=0.6, max_value=1.0, allow_nan=False),
        category=category_strategy
    )
    def test_high_confidence_not_queued(self, engine, confidence, category):
        """
        高置信度的分类不应该被加入审核队列。
        """
        bookmark = create_bookmark()
        
        result = engine.process_classification(
            bookmark=bookmark,
            category=category,
            confidence=confidence,
            alternatives=[]
        )
        
        # 高置信度不应该被检测为需要审核
        assert result is None, \
            f"High confidence {confidence} should not be queued (threshold: 0.6)"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestUncertaintySampling:
    """不确定性采样测试 - Property 9"""
    
    @pytest.fixture
    def engine(self):
        """创建主动学习引擎"""
        return ActiveLearningEngine({
            'confidence_threshold': 0.6,
            'max_requests_per_session': 100
        })
    
    @settings(max_examples=50)
    @given(
        confidences=st.lists(
            st.floats(min_value=0.1, max_value=0.5, allow_nan=False),
            min_size=3,
            max_size=10
        )
    )
    def test_uncertainty_sampling_priority(self, engine, confidences):
        """
        Property 9: Uncertainty Sampling Priority
        
        对于审核队列中的任何低置信度书签集合，
        项目应该按不确定性分数排序（不确定性越高越优先）以最大化信息增益。
        
        Validates: Requirements 3.5
        """
        # 添加多个低置信度项
        for i, conf in enumerate(confidences):
            bookmark = create_bookmark(
                url=f"https://example.com/page{i}",
                title=f"Title {i}"
            )
            # 创建不同的备选分类以产生不同的不确定性
            n_alternatives = (i % 3) + 1
            alternatives = create_alternatives(n_alternatives)
            
            engine.process_classification(
                bookmark=bookmark,
                category='测试分类',
                confidence=conf,
                alternatives=alternatives
            )
        
        # 获取队列中的项目
        items = []
        while True:
            item = engine.get_next_review_item()
            if item is None:
                break
            items.append(item)
        
        # 验证按不确定性排序（降序）
        for i in range(len(items) - 1):
            assert items[i].uncertainty_score >= items[i + 1].uncertainty_score, \
                f"Items should be ordered by uncertainty: {items[i].uncertainty_score} >= {items[i + 1].uncertainty_score}"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestSessionRequestLimit:
    """会话请求限制测试 - Property 10"""
    
    @settings(max_examples=50)
    @given(max_requests=st.integers(min_value=1, max_value=20))
    def test_session_request_limit(self, max_requests):
        """
        Property 10: Session Request Limit
        
        对于任何主动学习会话，反馈请求的数量不应超过
        配置的 max_requests_per_session 限制。
        
        Validates: Requirements 3.6
        """
        engine = ActiveLearningEngine({
            'confidence_threshold': 0.6,
            'max_requests_per_session': max_requests
        })
        
        # 添加比限制更多的项目
        for i in range(max_requests + 10):
            bookmark = create_bookmark(
                url=f"https://example.com/page{i}",
                title=f"Title {i}"
            )
            engine.process_classification(
                bookmark=bookmark,
                category='测试',
                confidence=0.3,
                alternatives=[]
            )
        
        # 尝试获取所有项目
        retrieved_count = 0
        while True:
            item = engine.get_next_review_item()
            if item is None:
                break
            retrieved_count += 1
        
        # 验证不超过限制
        assert retrieved_count <= max_requests, \
            f"Retrieved {retrieved_count} items, should not exceed limit {max_requests}"
        
        # 验证剩余请求数为 0
        assert engine.get_remaining_requests() == 0, \
            "Remaining requests should be 0 after reaching limit"
    
    def test_session_reset(self):
        """
        重置会话后应该可以继续获取项目。
        """
        engine = ActiveLearningEngine({
            'confidence_threshold': 0.6,
            'max_requests_per_session': 2
        })
        
        # 添加项目
        for i in range(5):
            bookmark = create_bookmark(url=f"https://example.com/page{i}")
            engine.process_classification(
                bookmark=bookmark,
                category='测试',
                confidence=0.3,
                alternatives=[]
            )
        
        # 获取到限制
        for _ in range(2):
            engine.get_next_review_item()
        
        # 验证达到限制
        assert engine.get_next_review_item() is None
        
        # 重置会话
        engine.reset_session()
        
        # 应该可以继续获取
        item = engine.get_next_review_item()
        assert item is not None, "Should be able to get items after session reset"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestFeedbackPersistence:
    """反馈持久化测试 - Property 11"""
    
    @pytest.fixture
    def engine(self):
        """创建主动学习引擎"""
        return ActiveLearningEngine({
            'confidence_threshold': 0.6,
            'persist_path': '/tmp/test_active_learning_feedback'
        })
    
    @settings(max_examples=100)
    @given(
        bookmark_id=st.text(min_size=1, max_size=50),
        correct_category=category_strategy
    )
    def test_feedback_persistence(self, engine, bookmark_id, correct_category):
        """
        Property 11: Feedback Persistence
        
        对于通过 Active_Learning_Engine 提交的任何用户反馈，
        已标注的样本应该被持久化并可检索用于模型重训练。
        
        Validates: Requirements 3.4
        """
        assume(len(bookmark_id.strip()) > 0)
        
        initial_count = len(engine.get_labeled_samples())
        
        # 提交反馈
        engine.submit_feedback(
            bookmark_id=bookmark_id,
            correct_category=correct_category,
            original_prediction='原始预测',
            original_confidence=0.4
        )
        
        # 验证样本已添加
        samples = engine.get_labeled_samples()
        assert len(samples) == initial_count + 1, \
            "Labeled sample should be added"
        
        # 验证样本内容
        latest_sample = samples[-1]
        assert latest_sample['bookmark_id'] == bookmark_id
        assert latest_sample['correct_category'] == correct_category
        assert 'timestamp' in latest_sample
    
    @settings(max_examples=20)
    @given(
        feedbacks=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),
                category_strategy
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_multiple_feedback_persistence(self, engine, feedbacks):
        """
        多个反馈应该都被持久化。
        """
        feedbacks = [(bid, cat) for bid, cat in feedbacks if len(bid.strip()) > 0]
        assume(len(feedbacks) > 0)
        
        for bookmark_id, category in feedbacks:
            engine.submit_feedback(
                bookmark_id=bookmark_id,
                correct_category=category
            )
        
        samples = engine.get_labeled_samples()
        assert len(samples) >= len(feedbacks), \
            f"Should have at least {len(feedbacks)} samples"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestUncertaintyCalculation:
    """不确定性计算测试"""
    
    @pytest.fixture
    def engine(self):
        """创建主动学习引擎"""
        return ActiveLearningEngine({'confidence_threshold': 0.6})
    
    @settings(max_examples=50)
    @given(
        confidence=st.floats(min_value=0.1, max_value=0.9, allow_nan=False),
        n_alternatives=st.integers(min_value=0, max_value=5)
    )
    def test_uncertainty_calculation(self, engine, confidence, n_alternatives):
        """
        不确定性分数应该是非负的。
        """
        alternatives = [(f'cat{i}', 0.1 * (i + 1)) for i in range(n_alternatives)]
        
        uncertainty = engine._calculate_uncertainty(confidence, alternatives)
        
        assert uncertainty >= 0, f"Uncertainty should be non-negative, got {uncertainty}"
    
    def test_high_confidence_low_uncertainty(self, engine):
        """
        高置信度应该对应低不确定性。
        """
        high_conf_uncertainty = engine._calculate_uncertainty(0.9, [])
        low_conf_uncertainty = engine._calculate_uncertainty(0.3, [('alt', 0.3)])
        
        assert high_conf_uncertainty <= low_conf_uncertainty, \
            "High confidence should have lower uncertainty"
