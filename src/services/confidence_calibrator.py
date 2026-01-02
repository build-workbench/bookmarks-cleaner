"""
Confidence Calibrator - 置信度校准器
对多方法融合后的置信度进行校准
"""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np

class ConfidenceCalibrator:
    """置信度校准器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化置信度校准器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.method = self.config.get('method', 'platt')  # platt, isotonic, none
        
        # Platt scaling 参数
        self._platt_a = 1.0
        self._platt_b = 0.0
        
        # Isotonic regression 数据
        self._isotonic_x = []
        self._isotonic_y = []
        self._isotonic_fitted = False
        
        # 校准数据
        self._calibration_data: List[Tuple[float, bool]] = []
        self._min_samples = self.config.get('min_samples', 100)
        
        self.logger = logging.getLogger(__name__)
    
    def calibrate(self, confidence: float) -> float:
        """
        校准置信度
        
        Args:
            confidence: 原始置信度
            
        Returns:
            校准后的置信度
        """
        if self.method == 'none':
            return confidence
        
        if self.method == 'platt':
            return self._platt_calibrate(confidence)
        elif self.method == 'isotonic':
            return self._isotonic_calibrate(confidence)
        
        return confidence
    
    def _platt_calibrate(self, confidence: float) -> float:
        """
        Platt scaling 校准
        
        Args:
            confidence: 原始置信度
            
        Returns:
            校准后的置信度
        """
        # Sigmoid 变换: 1 / (1 + exp(a * x + b))
        z = self._platt_a * confidence + self._platt_b
        calibrated = 1.0 / (1.0 + np.exp(-z))
        return float(np.clip(calibrated, 0.0, 1.0))
    
    def _isotonic_calibrate(self, confidence: float) -> float:
        """
        Isotonic regression 校准
        
        Args:
            confidence: 原始置信度
            
        Returns:
            校准后的置信度
        """
        if not self._isotonic_fitted or not self._isotonic_x:
            return confidence
        
        # 简单的线性插值
        x_arr = np.array(self._isotonic_x)
        y_arr = np.array(self._isotonic_y)
        
        if confidence <= x_arr[0]:
            return float(y_arr[0])
        if confidence >= x_arr[-1]:
            return float(y_arr[-1])
        
        # 找到插值位置
        idx = np.searchsorted(x_arr, confidence)
        x0, x1 = x_arr[idx-1], x_arr[idx]
        y0, y1 = y_arr[idx-1], y_arr[idx]
        
        # 线性插值
        t = (confidence - x0) / (x1 - x0) if x1 != x0 else 0
        calibrated = y0 + t * (y1 - y0)
        
        return float(np.clip(calibrated, 0.0, 1.0))
    
    def add_calibration_sample(self, predicted_confidence: float, was_correct: bool):
        """
        添加校准样本
        
        Args:
            predicted_confidence: 预测的置信度
            was_correct: 预测是否正确
        """
        self._calibration_data.append((predicted_confidence, was_correct))
        
        # 当样本足够时，重新拟合
        if len(self._calibration_data) >= self._min_samples:
            self._fit_calibration()
    
    def _fit_calibration(self):
        """拟合校准模型"""
        if len(self._calibration_data) < self._min_samples:
            return
        
        confidences = np.array([x[0] for x in self._calibration_data])
        correct = np.array([1.0 if x[1] else 0.0 for x in self._calibration_data])
        
        if self.method == 'platt':
            self._fit_platt(confidences, correct)
        elif self.method == 'isotonic':
            self._fit_isotonic(confidences, correct)
    
    def _fit_platt(self, confidences: np.ndarray, correct: np.ndarray):
        """
        拟合 Platt scaling 参数
        
        Args:
            confidences: 置信度数组
            correct: 正确性数组
        """
        try:
            from scipy.optimize import minimize
            
            def neg_log_likelihood(params):
                a, b = params
                z = a * confidences + b
                p = 1.0 / (1.0 + np.exp(-z))
                p = np.clip(p, 1e-10, 1 - 1e-10)
                return -np.sum(correct * np.log(p) + (1 - correct) * np.log(1 - p))
            
            result = minimize(neg_log_likelihood, [1.0, 0.0], method='BFGS')
            self._platt_a, self._platt_b = result.x
            self.logger.info(f"Platt scaling fitted: a={self._platt_a:.3f}, b={self._platt_b:.3f}")
        except ImportError:
            self.logger.warning("scipy not available, using default Platt parameters")
        except Exception as e:
            self.logger.error(f"Platt fitting failed: {e}")
    
    def _fit_isotonic(self, confidences: np.ndarray, correct: np.ndarray):
        """
        拟合 Isotonic regression
        
        Args:
            confidences: 置信度数组
            correct: 正确性数组
        """
        # 按置信度排序
        sorted_idx = np.argsort(confidences)
        sorted_conf = confidences[sorted_idx]
        sorted_correct = correct[sorted_idx]
        
        # 分桶计算平均正确率
        n_bins = 10
        bin_edges = np.linspace(0, 1, n_bins + 1)
        
        self._isotonic_x = []
        self._isotonic_y = []
        
        for i in range(n_bins):
            mask = (sorted_conf >= bin_edges[i]) & (sorted_conf < bin_edges[i+1])
            if np.sum(mask) > 0:
                bin_center = (bin_edges[i] + bin_edges[i+1]) / 2
                bin_accuracy = np.mean(sorted_correct[mask])
                self._isotonic_x.append(bin_center)
                self._isotonic_y.append(bin_accuracy)
        
        self._isotonic_fitted = len(self._isotonic_x) > 0
        self.logger.info(f"Isotonic regression fitted with {len(self._isotonic_x)} bins")
    
    def get_calibration_stats(self) -> Dict:
        """
        获取校准统计信息
        
        Returns:
            统计信息字典
        """
        if not self._calibration_data:
            return {'samples': 0}
        
        confidences = [x[0] for x in self._calibration_data]
        correct = [x[1] for x in self._calibration_data]
        
        return {
            'samples': len(self._calibration_data),
            'method': self.method,
            'avg_confidence': np.mean(confidences),
            'accuracy': np.mean(correct),
            'platt_a': self._platt_a,
            'platt_b': self._platt_b
        }
