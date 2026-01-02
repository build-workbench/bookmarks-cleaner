# Implementation Plan: Architecture Algorithm Upgrade

## Overview

本实现计划将 CleanBook 系统从单体架构升级为插件式架构，并引入 Transformer 嵌入、主动学习、增量学习等先进算法。实现采用渐进式方式，确保每个阶段都可独立验证。

## Tasks

- [x] 1. 搭建插件架构基础设施
  - [x] 1.1 创建插件接口和元数据定义
    - 在 `src/plugins/` 目录下创建 `base.py`
    - 定义 `ClassifierPlugin` 抽象基类和 `PluginMetadata` 数据类
    - _Requirements: 1.1, 1.2_
  - [x] 1.2 实现 Plugin_Registry 核心功能
    - 创建 `src/plugins/registry.py`
    - 实现 register/unregister/enable/disable 方法
    - 实现插件验证逻辑
    - _Requirements: 1.1, 1.2, 1.6_
  - [x] 1.3 编写 Plugin_Registry 属性测试
    - **Property 1: Plugin Registration Consistency**
    - **Property 2: Plugin Invocation Order**
    - **Property 4: Runtime Plugin Toggle**
    - **Validates: Requirements 1.1, 1.2, 1.4, 1.6**
  - [x] 1.4 实现 Classifier_Pipeline 基础框架
    - 创建 `src/plugins/pipeline.py`
    - 实现插件调用和错误隔离
    - _Requirements: 1.4, 1.5_
  - [x] 1.5 编写 Classifier_Pipeline 属性测试
    - **Property 3: Plugin Failure Isolation**
    - **Validates: Requirements 1.5**

- [ ] 2. Checkpoint - 确保插件架构测试通过
  - 运行所有测试，确认插件架构基础设施正常工作
  - 如有问题请咨询用户

- [ ] 3. 实现特征存储和缓存系统
  - [x] 3.1 创建 Feature_Store 核心实现
    - 创建 `src/services/feature_store.py`
    - 实现 LRU 缓存和 TTL 过期机制
    - 实现持久化和加载功能
    - _Requirements: 6.1, 6.2, 6.4_
  - [x] 3.2 编写 Feature_Store 属性测试
    - **Property 17: Feature Store TTL Expiration**
    - **Property 18: LRU Eviction Policy**
    - **Validates: Requirements 6.1, 6.4**
  - [x] 3.3 实现近似最近邻搜索
    - 添加 brute-force 搜索作为基础实现
    - 预留 ANN 索引接口
    - _Requirements: 6.3_
  - [x] 3.4 实现缓存预热功能
    - 添加 warm_cache 方法
    - 添加命中率监控和告警
    - _Requirements: 6.5, 6.6_

- [ ] 4. 实现 Embedding 服务
  - [x] 4.1 创建 Embedding_Service 核心实现
    - 创建 `src/services/embedding_service.py`
    - 实现 Transformer 模型加载（sentence-transformers）
    - 实现 TF-IDF 降级方案
    - _Requirements: 2.1, 2.6_
  - [x] 4.2 实现嵌入生成和缓存集成
    - 实现 embed 和 embed_batch 方法
    - 集成 Feature_Store 缓存
    - _Requirements: 2.2, 2.3_
  - [ ] 4.3 编写 Embedding_Service 属性测试
    - **Property 5: Embedding Dimensionality Consistency**
    - **Property 6: Embedding Cache Round-Trip**
    - **Validates: Requirements 2.2, 2.3**
  - [x] 4.4 实现 Embedding_Classifier 插件
    - 创建 `src/plugins/classifiers/embedding_classifier.py`
    - 实现基于余弦相似度的分类
    - _Requirements: 2.4, 2.5_
  - [ ] 4.5 编写 Embedding_Classifier 属性测试
    - **Property 7: Cosine Similarity Classification**
    - **Validates: Requirements 2.4, 2.5**

- [ ] 5. Checkpoint - 确保嵌入服务测试通过
  - 运行所有测试，确认嵌入服务正常工作
  - 如有问题请咨询用户

- [ ] 6. 实现多方法融合优化
  - [ ] 6.1 实现 Confidence_Calibrator
    - 创建 `src/services/confidence_calibrator.py`
    - 实现 Platt scaling 置信度校准
    - _Requirements: 5.2_
  - [ ] 6.2 扩展 Classifier_Pipeline 融合策略
    - 实现 weighted_voting、stacking、bayesian 三种策略
    - 实现冲突解决规则
    - _Requirements: 5.1, 5.4_
  - [ ] 6.3 编写融合策略属性测试
    - **Property 15: Fusion Strategy Application**
    - **Validates: Requirements 5.1**
  - [ ] 6.4 实现动态权重调整
    - 添加方法准确率统计
    - 实现基于历史准确率的权重更新
    - _Requirements: 5.3, 5.5_
  - [ ] 6.5 编写动态权重属性测试
    - **Property 16: Dynamic Weight Adjustment**
    - **Validates: Requirements 5.3, 5.5**
  - [ ] 6.6 实现 A/B 测试支持
    - 添加流量分配逻辑
    - _Requirements: 5.6_

- [ ] 7. 实现主动学习引擎
  - [ ] 7.1 创建 Active_Learning_Engine 核心实现
    - 创建 `src/services/active_learning.py`
    - 实现低置信度检测和队列管理
    - 实现不确定性采样（熵计算）
    - _Requirements: 3.1, 3.2, 3.5_
  - [ ] 7.2 编写主动学习属性测试
    - **Property 8: Low-Confidence Detection and Queuing**
    - **Property 9: Uncertainty Sampling Priority**
    - **Validates: Requirements 3.1, 3.2, 3.5**
  - [ ] 7.3 实现用户反馈收集
    - 实现 submit_feedback 方法
    - 实现会话请求限制
    - _Requirements: 3.3, 3.4, 3.6_
  - [ ] 7.4 编写反馈收集属性测试
    - **Property 10: Session Request Limit**
    - **Property 11: Feedback Persistence**
    - **Validates: Requirements 3.4, 3.6**

- [ ] 8. Checkpoint - 确保主动学习测试通过
  - 运行所有测试，确认主动学习引擎正常工作
  - 如有问题请咨询用户

- [ ] 9. 实现增量训练器
  - [ ] 9.1 创建 Incremental_Trainer 核心实现
    - 创建 `src/services/incremental_trainer.py`
    - 实现 partial_fit 增量训练
    - 实现批量触发逻辑
    - _Requirements: 4.1, 4.2_
  - [ ] 9.2 编写增量训练属性测试
    - **Property 12: Incremental Update Trigger**
    - **Validates: Requirements 4.1, 4.2**
  - [ ] 9.3 实现模型版本管理
    - 实现版本保存和清理
    - 实现回滚功能
    - _Requirements: 4.3, 4.4_
  - [ ] 9.4 编写版本管理属性测试
    - **Property 13: Model Version History**
    - **Validates: Requirements 4.3**
  - [ ] 9.5 实现原子性序列化
    - 使用临时文件和 rename 确保原子性
    - _Requirements: 4.6_
  - [ ] 9.6 编写原子性序列化属性测试
    - **Property 14: Atomic Model Serialization**
    - **Validates: Requirements 4.6**
  - [ ] 9.7 实现定时全量重训练
    - 添加调度逻辑
    - _Requirements: 4.5_

- [ ] 10. 实现分类体系动态管理
  - [ ] 10.1 创建 Taxonomy_Service 核心实现
    - 创建 `src/services/taxonomy_service.py`
    - 实现 YAML 加载和保存
    - _Requirements: 7.1_
  - [ ] 10.2 编写 Taxonomy YAML 属性测试
    - **Property 19: Taxonomy YAML Round-Trip**
    - **Validates: Requirements 7.1**
  - [ ] 10.3 实现分类名称验证
    - 实现命名规范校验
    - _Requirements: 7.3_
  - [ ] 10.4 编写分类名称验证属性测试
    - **Property 20: Category Name Validation**
    - **Validates: Requirements 7.3**
  - [ ] 10.5 实现分类重命名和合并
    - 实现 rename_category 和 merge_categories 方法
    - _Requirements: 7.4, 7.5_
  - [ ] 10.6 编写重命名和合并属性测试
    - **Property 21: Category Rename Propagation**
    - **Property 22: Category Merge Completeness**
    - **Validates: Requirements 7.4, 7.5**
  - [ ] 10.7 实现迁移脚本导出
    - 实现 export_migrations 方法
    - _Requirements: 7.6_

- [ ] 11. Checkpoint - 确保分类体系管理测试通过
  - 运行所有测试，确认分类体系服务正常工作
  - 如有问题请咨询用户

- [ ] 12. 实现性能监控服务
  - [ ] 12.1 创建 Performance_Monitor 核心实现
    - 创建 `src/services/performance_monitor.py`
    - 实现延迟记录和百分位数计算
    - 实现方法准确率和置信度分布统计
    - _Requirements: 8.1, 8.2_
  - [ ] 12.2 编写性能监控属性测试
    - **Property 23: Latency Percentile Accuracy**
    - **Validates: Requirements 8.1, 8.2**
  - [ ] 12.3 实现延迟告警
    - 实现阈值检测和告警发送
    - _Requirements: 8.3_
  - [ ] 12.4 编写延迟告警属性测试
    - **Property 24: Latency Alert Emission**
    - **Validates: Requirements 8.3**
  - [ ] 12.5 实现 Prometheus 格式导出
    - 实现 export_prometheus_metrics 方法
    - _Requirements: 8.4_
  - [ ] 12.6 编写 Prometheus 格式属性测试
    - **Property 25: Prometheus Format Validity**
    - **Validates: Requirements 8.4**
  - [ ] 12.7 实现每日报告生成
    - 实现 generate_daily_report 方法
    - _Requirements: 8.5_
  - [ ] 12.8 实现缓存和内存使用追踪
    - 添加缓存命中率和内存使用记录
    - _Requirements: 8.6_

- [ ] 13. 迁移现有分类器为插件
  - [ ] 13.1 将 RuleEngine 封装为插件
    - 创建 `src/plugins/classifiers/rule_classifier.py`
    - 实现 ClassifierPlugin 接口
    - _Requirements: 1.3_
  - [ ] 13.2 将 MLClassifier 封装为插件
    - 创建 `src/plugins/classifiers/ml_classifier.py`
    - 实现 ClassifierPlugin 接口
    - _Requirements: 1.3_
  - [ ] 13.3 将 LLMClassifier 封装为插件
    - 创建 `src/plugins/classifiers/llm_classifier.py`
    - 实现 ClassifierPlugin 接口
    - _Requirements: 1.3_

- [ ] 14. 集成和端到端测试
  - [ ] 14.1 更新 EnhancedClassifier 使用新架构
    - 集成 Plugin_Registry 和 Classifier_Pipeline
    - 集成 Active_Learning_Engine
    - 集成 Performance_Monitor
  - [ ] 14.2 更新配置文件支持新功能
    - 添加插件配置项
    - 添加融合策略配置
    - 添加主动学习配置
  - [ ] 14.3 编写集成测试
    - 测试完整分类流程
    - 测试插件热插拔
    - 测试主动学习流程

- [ ] 15. Final Checkpoint - 确保所有测试通过
  - 运行完整测试套件
  - 验证所有需求已实现
  - 如有问题请咨询用户

## Notes

- 所有任务均为必需，包括属性测试任务
- 每个任务都引用了具体的需求以确保可追溯性
- Checkpoint 任务用于阶段性验证
- 属性测试验证通用正确性属性
- 单元测试验证特定示例和边界条件
