"""
Property Tests for Incremental Trainer
增量训练器属性测试

Tests Properties:
- Property 12: Incremental Update Trigger
- Property 13: Model Version History
- Property 14: Atomic Model Serialization
"""

import os
import shutil
import tempfile
import pytest
from hypothesis import given, strategies as st, settings, assume

# 尝试导入依赖
try:
    from src.services.incremental_trainer import IncrementalTrainer, ModelVersion
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False

# 检查 joblib 是否可用
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


# 策略定义
feature_strategy = st.fixed_dictionaries({
    'text': st.text(min_size=5, max_size=100),
    'value': st.floats(min_value=0, max_value=1, allow_nan=False)
})

label_strategy = st.sampled_from([
    '编程开发', '人工智能', '数据科学', '前端开发', '后端开发'
])


class MockModel:
    """模拟支持 partial_fit 的模型"""
    
    def __init__(self):
        self.classes_ = []
        self.fitted_samples = 0
    
    def partial_fit(self, X, y, classes=None):
        if classes:
            self.classes_ = list(set(self.classes_) | set(classes))
        self.fitted_samples += len(X)
    
    def predict(self, X):
        if not self.classes_:
            return ['未分类'] * len(X)
        return [self.classes_[0]] * len(X)


def create_trainer(batch_size=5, max_versions=3):
    """创建增量训练器"""
    temp_dir = tempfile.mkdtemp()
    config = {
        'batch_size': batch_size,
        'model_dir': temp_dir,
        'max_versions': max_versions
    }
    trainer = IncrementalTrainer(config)
    trainer.set_model(MockModel())
    return trainer, temp_dir


@pytest.mark.skipif(not IMPORTS_AVAILABLE or not JOBLIB_AVAILABLE, reason="Required imports not available")
class TestIncrementalUpdateTrigger:
    """增量更新触发测试 - Property 12"""
    
    @settings(max_examples=50)
    @given(
        batch_size=st.integers(min_value=2, max_value=10),
        n_samples=st.integers(min_value=1, max_value=30)
    )
    def test_incremental_update_trigger(self, batch_size, n_samples):
        """
        Property 12: Incremental Update Trigger
        
        对于任何新训练样本的累积，当数量超过配置的 batch_size 时，
        Incremental_Trainer 应该触发增量模型更新。
        
        Validates: Requirements 4.1, 4.2
        """
        temp_dir = tempfile.mkdtemp()
        try:
            trainer = IncrementalTrainer({
                'batch_size': batch_size,
                'model_dir': temp_dir,
                'max_versions': 5
            })
            trainer.set_model(MockModel())
            
            initial_updates = trainer._stats['incremental_updates']
            
            # 添加样本
            for i in range(n_samples):
                trainer.add_sample(
                    features={'text': f'sample {i}', 'value': 0.5},
                    label='测试分类'
                )
            
            # 计算预期的更新次数
            expected_updates = n_samples // batch_size
            actual_updates = trainer._stats['incremental_updates'] - initial_updates
            
            assert actual_updates == expected_updates, \
                f"Expected {expected_updates} updates for {n_samples} samples with batch_size {batch_size}, got {actual_updates}"
            
            # 验证待处理样本数
            expected_pending = n_samples % batch_size
            assert trainer.get_pending_count() == expected_pending, \
                f"Expected {expected_pending} pending samples, got {trainer.get_pending_count()}"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_force_update(self):
        """
        强制更新应该处理所有待处理样本。
        """
        trainer, temp_dir = create_trainer()
        try:
            # 添加少于 batch_size 的样本
            for i in range(3):
                trainer.add_sample(
                    features={'text': f'sample {i}'},
                    label='测试'
                )
            
            assert trainer.get_pending_count() == 3
            
            # 强制更新
            result = trainer.force_update()
            
            assert result is True
            assert trainer.get_pending_count() == 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.skipif(not IMPORTS_AVAILABLE or not JOBLIB_AVAILABLE, reason="Required imports not available")
class TestModelVersionHistory:
    """模型版本历史测试 - Property 13"""
    
    @settings(max_examples=30)
    @given(n_updates=st.integers(min_value=1, max_value=8))
    def test_model_version_history(self, n_updates):
        """
        Property 13: Model Version History
        
        对于任何增量更新序列，所有之前的模型版本（最多 max_versions 个）
        应该被维护并可用于回滚。
        
        Validates: Requirements 4.3
        """
        temp_dir = tempfile.mkdtemp()
        max_versions = 3
        
        try:
            trainer = IncrementalTrainer({
                'batch_size': 2,
                'model_dir': temp_dir,
                'max_versions': max_versions
            })
            trainer.set_model(MockModel())
            
            # 执行多次更新
            for update_idx in range(n_updates):
                for i in range(2):  # batch_size = 2
                    trainer.add_sample(
                        features={'text': f'update{update_idx}_sample{i}'},
                        label=f'类别{update_idx}'
                    )
            
            # 验证版本数量不超过 max_versions
            versions = trainer.get_version_history()
            assert len(versions) <= max_versions, \
                f"Version count {len(versions)} should not exceed max_versions {max_versions}"
            
            # 验证版本可以被检索
            for version in versions:
                assert version.version_id is not None
                assert version.model_path is not None
                assert os.path.exists(version.model_path), \
                    f"Version path {version.model_path} should exist"
                    
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_rollback_functionality(self):
        """
        回滚应该恢复到上一个版本。
        """
        trainer, temp_dir = create_trainer(batch_size=2, max_versions=3)
        try:
            # 创建多个版本
            for update_idx in range(3):
                for i in range(2):
                    trainer.add_sample(
                        features={'text': f'sample{update_idx}_{i}'},
                        label=f'类别{update_idx}'
                    )
            
            versions_before = len(trainer.get_version_history())
            current_version = trainer.current_version
            
            # 回滚
            result = trainer.rollback()
            
            assert result is True
            assert len(trainer.get_version_history()) == versions_before - 1
            assert trainer.current_version != current_version
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_load_specific_version(self):
        """
        应该能够加载特定版本。
        """
        trainer, temp_dir = create_trainer(batch_size=2, max_versions=3)
        try:
            # 创建多个版本
            for update_idx in range(3):
                for i in range(2):
                    trainer.add_sample(
                        features={'text': f'sample{update_idx}_{i}'},
                        label=f'类别{update_idx}'
                    )
            
            versions = trainer.get_version_history()
            assume(len(versions) >= 2)
            
            # 加载第一个版本
            first_version = versions[0]
            result = trainer.load_version(first_version.version_id)
            
            assert result is True
            assert trainer.current_version == first_version.version_id
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.skipif(not IMPORTS_AVAILABLE or not JOBLIB_AVAILABLE, reason="Required imports not available")
class TestAtomicSerialization:
    """原子性序列化测试 - Property 14"""
    
    @settings(max_examples=30)
    @given(n_samples=st.integers(min_value=2, max_value=10))
    def test_atomic_model_serialization(self, n_samples):
        """
        Property 14: Atomic Model Serialization
        
        对于任何模型更新，序列化应该是原子的——
        要么完整的模型被成功保存，要么不保存任何部分/损坏的状态。
        
        Validates: Requirements 4.6
        """
        trainer, temp_dir = create_trainer(batch_size=2, max_versions=5)
        try:
            # 添加样本触发更新
            for i in range(n_samples):
                trainer.add_sample(
                    features={'text': f'sample {i}'},
                    label='测试'
                )
            
            # 验证所有版本都是完整的
            for version in trainer.get_version_history():
                model_path = version.model_path
                
                # 验证目录存在
                assert os.path.exists(model_path), \
                    f"Version directory {model_path} should exist"
                
                # 验证模型文件存在
                model_file = os.path.join(model_path, 'model.pkl')
                assert os.path.exists(model_file), \
                    f"Model file {model_file} should exist"
                
                # 验证没有临时文件残留
                temp_path = model_path + '.tmp'
                assert not os.path.exists(temp_path), \
                    f"Temporary file {temp_path} should not exist"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_no_partial_state_on_failure(self):
        """
        失败时不应该留下部分状态。
        """
        trainer, temp_dir = create_trainer()
        try:
            model_dir = trainer.model_dir
            
            # 记录初始状态
            initial_versions = len(trainer.get_version_history())
            
            # 模拟正常更新
            for i in range(2):
                trainer.add_sample(
                    features={'text': f'sample {i}'},
                    label='测试'
                )
            
            # 验证更新成功
            assert len(trainer.get_version_history()) == initial_versions + 1
            
            # 检查没有临时文件
            for item in os.listdir(model_dir):
                assert not item.endswith('.tmp'), \
                    f"Temporary file {item} should not exist"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.skipif(not IMPORTS_AVAILABLE or not JOBLIB_AVAILABLE, reason="Required imports not available")
class TestVersionCleanup:
    """版本清理测试"""
    
    @settings(max_examples=20)
    @given(
        max_versions=st.integers(min_value=2, max_value=5),
        n_updates=st.integers(min_value=1, max_value=10)
    )
    def test_old_versions_cleaned_up(self, max_versions, n_updates):
        """
        旧版本应该被正确清理。
        """
        temp_dir = tempfile.mkdtemp()
        
        try:
            trainer = IncrementalTrainer({
                'batch_size': 1,
                'model_dir': temp_dir,
                'max_versions': max_versions
            })
            trainer.set_model(MockModel())
            
            # 执行多次更新
            for i in range(n_updates):
                trainer.add_sample(
                    features={'text': f'sample {i}'},
                    label='测试'
                )
            
            # 验证版本数量
            versions = trainer.get_version_history()
            assert len(versions) <= max_versions, \
                f"Should have at most {max_versions} versions, got {len(versions)}"
            
            # 验证磁盘上的版本目录数量
            version_dirs = [
                d for d in os.listdir(temp_dir)
                if d.startswith('version_') and os.path.isdir(os.path.join(temp_dir, d))
            ]
            assert len(version_dirs) <= max_versions, \
                f"Should have at most {max_versions} version directories"
                
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
