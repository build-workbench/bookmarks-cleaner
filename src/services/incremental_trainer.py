"""
Incremental Trainer - 增量训练器
支持模型的增量更新、版本管理和回滚
"""

import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ModelVersion:
    """模型版本"""
    version_id: str
    created_at: datetime
    training_samples: int
    accuracy: float
    model_path: str
    is_active: bool = False


class IncrementalTrainer:
    """增量训练器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化增量训练器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.batch_size = self.config.get('batch_size', 100)
        self.model_dir = self.config.get('model_dir', 'models/incremental')
        self.max_versions = self.config.get('max_versions', 5)
        self.performance_threshold = self.config.get('performance_threshold', 0.8)
        
        # 待处理样本
        self.pending_samples: List[Dict] = []
        
        # 模型版本历史
        self.model_versions: List[ModelVersion] = []
        self.current_version: Optional[str] = None
        
        # 模型实例（由外部设置）
        self.model = None
        
        # 验证集（用于性能验证）
        self._validation_set: List[Dict] = []
        
        # 统计信息
        self._stats = {
            'total_samples_trained': 0,
            'incremental_updates': 0,
            'rollbacks': 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # 确保目录存在
        os.makedirs(self.model_dir, exist_ok=True)
        
        # 加载版本历史
        self._load_version_history()
    
    def set_model(self, model):
        """
        设置要训练的模型
        
        Args:
            model: 支持 partial_fit 的模型实例
        """
        self.model = model
    
    def set_validation_set(self, validation_data: List[Dict]):
        """
        设置验证集
        
        Args:
            validation_data: 验证数据列表，每项包含 'features' 和 'label'
        """
        self._validation_set = validation_data
    
    def add_sample(self, features: Dict, label: str):
        """
        添加训练样本
        
        Args:
            features: 特征字典
            label: 标签
        """
        self.pending_samples.append({
            'features': features,
            'label': label,
            'timestamp': datetime.now().isoformat()
        })
        
        # 检查是否需要触发增量更新
        if len(self.pending_samples) >= self.batch_size:
            self._trigger_incremental_update()
    
    def add_samples_batch(self, samples: List[Dict]):
        """
        批量添加训练样本
        
        Args:
            samples: 样本列表，每项包含 'features' 和 'label'
        """
        for sample in samples:
            self.pending_samples.append({
                'features': sample['features'],
                'label': sample['label'],
                'timestamp': datetime.now().isoformat()
            })
        
        # 检查是否需要触发增量更新
        if len(self.pending_samples) >= self.batch_size:
            self._trigger_incremental_update()
    
    def force_update(self) -> bool:
        """
        强制触发增量更新（即使样本数不足）
        
        Returns:
            更新是否成功
        """
        if not self.pending_samples:
            return False
        
        return self._trigger_incremental_update()
    
    def _trigger_incremental_update(self) -> bool:
        """
        触发增量更新
        
        Returns:
            更新是否成功
        """
        if not self.pending_samples:
            return False
        
        if self.model is None:
            self.logger.warning("No model set for incremental training")
            return False
        
        try:
            # 保存当前版本
            self._save_version()
            
            # 执行增量训练
            self._partial_fit(self.pending_samples)
            
            # 更新统计
            self._stats['total_samples_trained'] += len(self.pending_samples)
            self._stats['incremental_updates'] += 1
            
            # 清空待处理样本
            sample_count = len(self.pending_samples)
            self.pending_samples.clear()
            
            # 验证性能
            if self._validation_set and not self._validate_performance():
                self.logger.warning("Performance degradation detected, rolling back")
                self.rollback()
                return False
            
            self.logger.info(f"Incremental update completed with {sample_count} samples")
            return True
            
        except Exception as e:
            self.logger.error(f"Incremental update failed: {e}")
            self.rollback()
            return False
    
    def _partial_fit(self, samples: List[Dict]):
        """
        执行 partial_fit
        
        Args:
            samples: 训练样本列表
        """
        if self.model is None:
            return
        
        if not hasattr(self.model, 'partial_fit'):
            self.logger.warning("Model does not support partial_fit")
            return
        
        X = [s['features'] for s in samples]
        y = [s['label'] for s in samples]
        
        # 获取所有可能的类别
        classes = list(set(y))
        if hasattr(self.model, 'classes_'):
            classes = list(set(classes) | set(self.model.classes_))
        
        self.model.partial_fit(X, y, classes=classes)
    
    def _save_version(self) -> Optional[str]:
        """
        保存模型版本
        
        Returns:
            版本 ID
        """
        if self.model is None:
            return None
        
        version_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_path = os.path.join(self.model_dir, f'version_{version_id}')
        
        try:
            # 使用临时文件确保原子性
            temp_path = version_path + '.tmp'
            self._serialize_model(temp_path)
            
            # 原子性重命名
            shutil.move(temp_path, version_path)
            
            # 计算当前准确率
            accuracy = self._calculate_accuracy() if self._validation_set else 0.0
            
            # 创建版本记录
            version = ModelVersion(
                version_id=version_id,
                created_at=datetime.now(),
                training_samples=self._stats['total_samples_trained'],
                accuracy=accuracy,
                model_path=version_path,
                is_active=True
            )
            
            # 更新版本历史
            for v in self.model_versions:
                v.is_active = False
            
            self.model_versions.append(version)
            self.current_version = version_id
            
            # 清理旧版本
            self._cleanup_old_versions()
            
            # 保存版本历史
            self._save_version_history()
            
            self.logger.info(f"Model version {version_id} saved")
            return version_id
            
        except Exception as e:
            self.logger.error(f"Failed to save model version: {e}")
            # 清理临时文件
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path, ignore_errors=True)
            raise
    
    def _serialize_model(self, path: str):
        """
        序列化模型
        
        Args:
            path: 保存路径
        """
        import joblib
        
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model, os.path.join(path, 'model.pkl'))
    
    def _load_model(self, path: str):
        """
        加载模型
        
        Args:
            path: 模型路径
        """
        import joblib
        
        model_file = os.path.join(path, 'model.pkl')
        if os.path.exists(model_file):
            self.model = joblib.load(model_file)
    
    def _cleanup_old_versions(self):
        """清理旧版本"""
        while len(self.model_versions) > self.max_versions:
            old_version = self.model_versions.pop(0)
            old_path = os.path.join(self.model_dir, f'version_{old_version.version_id}')
            
            if os.path.exists(old_path):
                shutil.rmtree(old_path, ignore_errors=True)
                self.logger.info(f"Cleaned up old version: {old_version.version_id}")
    
    def _validate_performance(self) -> bool:
        """
        验证模型性能
        
        Returns:
            性能是否达标
        """
        if not self._validation_set:
            return True
        
        accuracy = self._calculate_accuracy()
        return accuracy >= self.performance_threshold
    
    def _calculate_accuracy(self) -> float:
        """
        计算验证集准确率
        
        Returns:
            准确率
        """
        if not self._validation_set or self.model is None:
            return 0.0
        
        if not hasattr(self.model, 'predict'):
            return 0.0
        
        try:
            X = [s['features'] for s in self._validation_set]
            y_true = [s['label'] for s in self._validation_set]
            
            y_pred = self.model.predict(X)
            
            correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
            return correct / len(y_true) if y_true else 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to calculate accuracy: {e}")
            return 0.0
    
    def rollback(self) -> bool:
        """
        回滚到上一版本
        
        Returns:
            回滚是否成功
        """
        if len(self.model_versions) < 2:
            self.logger.warning("No previous version to rollback to")
            return False
        
        try:
            # 移除当前版本
            current = self.model_versions.pop()
            current_path = os.path.join(self.model_dir, f'version_{current.version_id}')
            
            if os.path.exists(current_path):
                shutil.rmtree(current_path, ignore_errors=True)
            
            # 加载上一版本
            previous = self.model_versions[-1]
            previous.is_active = True
            
            self._load_model(previous.model_path)
            self.current_version = previous.version_id
            
            self._stats['rollbacks'] += 1
            
            # 保存版本历史
            self._save_version_history()
            
            self.logger.info(f"Rolled back to version {previous.version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def load_version(self, version_id: str) -> bool:
        """
        加载指定版本
        
        Args:
            version_id: 版本 ID
            
        Returns:
            加载是否成功
        """
        for version in self.model_versions:
            if version.version_id == version_id:
                try:
                    self._load_model(version.model_path)
                    
                    # 更新活动状态
                    for v in self.model_versions:
                        v.is_active = (v.version_id == version_id)
                    
                    self.current_version = version_id
                    self._save_version_history()
                    
                    self.logger.info(f"Loaded version {version_id}")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Failed to load version {version_id}: {e}")
                    return False
        
        self.logger.warning(f"Version {version_id} not found")
        return False
    
    def get_version_history(self) -> List[ModelVersion]:
        """获取版本历史"""
        return self.model_versions.copy()
    
    def get_pending_count(self) -> int:
        """获取待处理样本数"""
        return len(self.pending_samples)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self._stats,
            'pending_samples': len(self.pending_samples),
            'version_count': len(self.model_versions),
            'current_version': self.current_version,
            'batch_size': self.batch_size
        }
    
    def _save_version_history(self):
        """保存版本历史"""
        try:
            history = []
            for v in self.model_versions:
                history.append({
                    'version_id': v.version_id,
                    'created_at': v.created_at.isoformat(),
                    'training_samples': v.training_samples,
                    'accuracy': v.accuracy,
                    'model_path': v.model_path,
                    'is_active': v.is_active
                })
            
            filepath = os.path.join(self.model_dir, 'version_history.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save version history: {e}")
    
    def _load_version_history(self):
        """加载版本历史"""
        try:
            filepath = os.path.join(self.model_dir, 'version_history.json')
            
            if not os.path.exists(filepath):
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            self.model_versions = []
            for item in history:
                version = ModelVersion(
                    version_id=item['version_id'],
                    created_at=datetime.fromisoformat(item['created_at']),
                    training_samples=item['training_samples'],
                    accuracy=item['accuracy'],
                    model_path=item['model_path'],
                    is_active=item.get('is_active', False)
                )
                self.model_versions.append(version)
                
                if version.is_active:
                    self.current_version = version.version_id
                    
        except Exception as e:
            self.logger.error(f"Failed to load version history: {e}")
