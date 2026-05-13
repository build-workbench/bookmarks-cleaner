## Context

当前代码库存在明显的架构债务：
- `BookmarkProcessor` (1149行) 承担 8+ 种职责
- 融合逻辑在 3 处重复实现
- 配置加载存在两个入口
- Taxonomy 分为两个类但职责重叠

这些浅模块导致变更成本高、测试困难、AI 导航性差。本次重构通过提取接口、统一实现、解构上帝类来深化架构。

## Goals / Non-Goals

**Goals:**
- 提取 Protocol 接口层，支持依赖注入
- 消除融合逻辑重复实现
- 解构 BookmarkProcessor 为 ~200 行协调者
- 统一配置加载入口
- 合并 TaxonomyService 与 TaxonomyStandardizer
- 提升测试覆盖率（移除 skip 标记）

**Non-Goals:**
- 不改变外部 CLI 接口
- 不改变分类结果格式
- 不引入新的外部依赖
- 不改变插件系统核心设计

## Decisions

### Decision 1: 使用 Protocol 而非 ABC

**选择**: 使用 `typing.Protocol` 定义接口

**理由**:
- 结构化子类型：现有类无需修改即可满足接口
- 无继承开销：不占用单继承位置
- 类型检查友好：mypy/pyright 完整支持
- 渐进迁移：可以先定义接口，后逐步让现有类显式实现

**替代方案考虑**:
- ABC（抽象基类）：需要显式继承，破坏现有代码
- 无接口：无法实现依赖注入和独立测试

### Decision 2: FusionEngine 作为独立服务

**选择**: 提取 `FusionEngine` 类，三处调用者委托给它

**理由**:
- 单一职责：融合逻辑集中在一处
- 可测试：可以独立测试融合逻辑
- 可配置：权重、策略可统一配置

**架构位置**:
```
AIBookmarkClassifier ──┐
ClassifierOrchestrator ──┼──▶ FusionEngine
ClassifierPipeline ─────┘
```

### Decision 3: 解构顺序

**选择**: 阶段式解构，保持向后兼容

**阶段**:
1. 定义接口（Protocol）
2. 提取 FusionEngine
3. 创建新组件（BookmarkLoader、ClassificationCoordinator、FeedbackService）
4. 修改 BookmarkProcessor 使用新组件
5. 移除旧的内部实现

**理由**:
- 每阶段可验证：测试可在每阶段运行
- 渐进迁移：不一次性破坏所有依赖
- 回滚友好：任何阶段可独立回滚

### Decision 4: ConfigProvider 包装 EnhancedConfigManager

**选择**: ConfigProvider 作为接口，EnhancedConfigManager 作为实现

**理由**:
- 不破坏现有 EnhancedConfigManager 功能
- 新代码通过接口访问
- 渐进迁移：逐步替换 load_json_config 调用

### Decision 5: TaxonomyService 合并 TaxonomyStandardizer

**选择**: 将 TaxonomyStandardizer 方法合并到 TaxonomyService

**理由**:
- 两个类都加载 subjects.yaml
- 标准化是分类体系的一部分
- 消除重复的 YAML 加载

**迁移策略**:
- TaxonomyStandardizer 变成 TaxonomyService 的别名（废弃警告）
- 下一版本移除别名

## Risks / Trade-offs

### Risk 1: 破坏现有测试

**风险**: 重构可能破坏依赖内部实现的测试

**缓解**:
- 每阶段运行完整测试套件
- 新增接口 mock 测试
- 保持向后兼容层

### Risk 2: 性能回归

**风险**: 额外的抽象层可能影响性能

**缓解**:
- Protocol 无运行时开销
- 依赖注入在初始化时完成
- 保持缓存机制不变

### Risk 3: 迁移不完整

**风险**: 部分代码仍使用旧路径

**缓解**:
- 添加废弃警告
- 代码审查检查新调用
- 文档更新

## Migration Plan

### Phase 1: 接口层 (Day 1-2)

1. 创建 `src/interfaces/` 目录
2. 定义 `IClassifier`、`IDeduplicator`、`IExporter`、`IConfigProvider`、`IFusionEngine`
3. 添加类型检查通过

### Phase 2: FusionEngine (Day 2-3)

1. 创建 `src/services/fusion_engine.py`
2. 从三处提取融合逻辑
3. 修改调用者委托给 FusionEngine
4. 测试验证

### Phase 3: ConfigProvider (Day 3-4)

1. 定义 `ConfigProvider` 接口
2. `EnhancedConfigManager` 实现接口
3. 替换 `load_json_config` 调用
4. 测试验证

### Phase 4: 解构 BookmarkProcessor (Day 4-6)

1. 提取 `BookmarkLoader`
2. 提取 `ClassificationCoordinator`
3. 提取 `FeedbackService`
4. 修改 `BookmarkProcessor` 使用依赖注入
5. 测试验证

### Phase 5: Taxonomy 合并 (Day 6-7)

1. 合并方法到 TaxonomyService
2. TaxonomyStandardizer 变成别名
3. 添加废弃警告
4. 测试验证

## Open Questions

1. **接口命名**: 使用 `I` 前缀（如 `IClassifier`）还是无前缀（如 `Classifier`）？
   - 建议：使用 `I` 前缀，与 Python 社区惯例一致

2. **废弃周期**: TaxonomyStandardizer 别名保留多久？
   - 建议：保留一个 minor 版本，下个 major 版本移除

3. **测试策略**: 是否需要为每个接口创建单独的测试文件？
   - 建议：是的，每个接口一个 `test_<interface>_protocol.py`
