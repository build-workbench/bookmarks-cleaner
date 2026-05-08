# 最终收尾重构 - 技术设计文档

## Context

CleanBook项目经过多轮迭代开发，已完成核心功能实现和架构优化。当前项目状态：
- **代码库健康度**: 高（265个测试用例全部通过）
- **架构状态**: 已完成模块化重构，进入stable maintenance阶段
- **Git状态**: 存在分支混乱、未推送提交、运行时数据污染等问题
- **文档状态**: 存在过时报告、冗余文档

本次重构旨在解决收尾过程中的技术债务，使项目达到归档就绪状态。

## Goals / Non-Goals

**Goals:**
1. 净化Git仓库结构，确保仅保留master单一主线分支
2. 清理所有运行时数据和临时文件，防止版本控制污染
3. 删除过时文档和冗余内容，降低维护负担
4. 更新GitHub元数据，提升项目可发现性
5. 优化Git Pages营销内容，提升转化价值

**Non-Goals:**
- 不修改任何核心代码逻辑
- 不添加新功能或测试
- 不更新依赖版本
- 不修改CI/CD配置
- 不进行架构调整

## Decisions

### 1. Git分支清理策略

**决策**: 采用"本地删除 → 远程清理 → 推送同步"的三步策略

**替代方案考虑**:
- ❌ 保留feature分支标记为archived - 增加噪音，不符合单主线维护原则
- ✅ 直接删除所有已合并分支 - 干净彻底，符合极简主义

**执行顺序**:
```mermaid
graph LR
    A[检查已合并分支] --> B[删除本地分支]
    B --> C[清理远程分支]
    C --> D[推送本地提交]
    D --> E[验证单一master分支]
```

### 2. 运行时数据处理策略

**决策**: 完全清理并强化.gitignore规则

**理由**:
- `logs/` - 用户运行时生成，不应纳入版本控制
- `models/` (11MB) - 训练产物，用户可自行训练或下载预训练模型
- `.hypothesis/`, `.pytest_cache/` - 测试缓存，应被忽略

**替代方案考虑**:
- ❌ 保留模型文件方便用户 - 文件过大，违反版本控制最佳实践
- ✅ 用户需要时自行生成 - 符合"源代码即真相"原则

### 3. 文档处理策略

**决策**: 激进删除过时报告，精简维护负担重的文档

**删除清单**:
- `ARCHITECTURE_IMPROVEMENT_REPORT.md` - 重构已完成，历史价值低
- `docs/REFACTORING_SUMMARY.md` - 重构已完成，历史价值低
- `docs/code_quality_notes.md` - 临时笔记，应删除
- `docs/package-lock.json` - 前端依赖锁文件，应在.gitignore

**精简原则**:
- Git历史已记录所有变更细节
- 保留文档应有长期维护价值
- "If it's not maintained, delete it"

### 4. Git Pages优化策略

**决策**: 保持现有VitePress架构，优化内容营销价值

**优化方向**:
- 增加实际使用案例和效果展示
- 强化"为什么选择CleanBook"的价值主张
- 保持技术文档的中英双语支持

**不改变**:
- VitePress配置和主题
- 现有文档结构
- CI/CD构建流程

## Risks / Trade-offs

### Risk 1: 误删有价值的文档
- **风险**: 删除过时报告可能丢失历史决策信息
- **缓解**: Git历史已完整记录所有变更，可通过git log追溯
- **影响**: 低 - 重构决策已在CLAUDE.md和openspec中沉淀

### Risk 2: 模型文件缺失影响用户体验
- **风险**: 删除models/目录后用户需自行训练模型
- **缓解**: README中说明模型训练流程，提供预训练模型下载链接（未来）
- **影响**: 中 - 可通过文档说明解决

### Risk 3: Git分支清理导致协作者同步问题
- **风险**: 删除远程分支后协作者需要重新克隆或同步
- **缓解**: 项目为单维护者模式，无协作者冲突风险
- **影响**: 低 - 符合单维护者直接推送原则

### Trade-off 1: 文档删除 vs 历史保留
- **权衡**: 删除过时报告降低维护负担，但损失部分历史信息
- **选择**: 优先降低维护负担，历史信息由Git保留

### Trade-off 2: 模型删除 vs 用户便利
- **权衡**: 删除大型模型文件保持仓库轻量，但增加用户使用成本
- **选择**: 优先仓库轻量，通过文档补充使用指南

## Migration Plan

### Phase 1: Git分支净化 (预计10分钟)

```bash
# 1. 检查当前状态
git status
git branch -a

# 2. 删除已合并的本地分支
git branch -d refactor/eliminate-magic-numbers
git branch -d refactor/phase-1-eliminate-duplicates

# 3. 清理远程dependabot分支
git push origin --delete dependabot/github_actions/actions/configure-pages-6
git push origin --delete dependabot/pip/lxml-gte-5.2.2-and-lt-6.2.0
git push origin --delete dependabot/pip/rich-gte-13.7.1-and-lt-15.1.0

# 4. 推送本地提交
git push origin master

# 5. 验证
git branch -a
```

### Phase 2: 文件系统清洗 (预计10分钟)

```bash
# 1. 删除备份文件
rm src/ai_classifier.py.backup

# 2. 清理运行时数据
rm -rf logs/ models/ .hypothesis/ .pytest_cache/

# 3. 删除过时文档
rm ARCHITECTURE_IMPROVEMENT_REPORT.md
rm docs/REFACTORING_SUMMARY.md
rm docs/code_quality_notes.md
rm docs/package-lock.json

# 4. 清理临时文件
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +

# 5. 更新.gitignore
# 添加运行时数据忽略规则
```

### Phase 3: 文档精简 (预计15分钟)

```bash
# 1. 精简CONTEXT.md
# 保留核心领域概念，删除详细架构描述

# 2. 优化Git Pages
# 增加营销内容和使用案例

# 3. 更新CHANGELOG.md
# 记录本次收尾重构
```

### Phase 4: GitHub元数据更新 (预计5分钟)

```bash
# 使用gh CLI更新仓库信息
gh repo edit --description "智能书签清理与分类：规则+ML+LLM（可选）"
gh repo edit --add-topic bookmark-manager
gh repo edit --add-topic classification
gh repo edit --add-topic offline-first
```

### Phase 5: 最终验证 (预计10分钟)

```bash
# 1. 运行完整测试套件
python -m pytest -q

# 2. 验证CI配置
# 检查.github/workflows/配置正确性

# 3. 创建最终提交
git add .
git commit -m "chore: final repository closeout - cleanup and optimization"

# 4. 推送并验证
git push origin master

# 5. 检查Git Pages构建
# 访问 https://lessup.github.io/bookmarks-cleaner/ 验证
```

## Open Questions

无待解决的技术问题。所有决策均已明确。

## Correctness Properties

本次重构需维护以下正确性属性：

1. **代码完整性**: 所有测试用例必须继续通过
2. **Git历史完整性**: 不使用force push，保留完整提交历史
3. **文档一致性**: README、CHANGELOG与实际状态保持同步
4. **CI/CD正确性**: GitHub Actions配置不受影响
5. **Git Pages可用性**: 文档站点继续正常构建和访问
