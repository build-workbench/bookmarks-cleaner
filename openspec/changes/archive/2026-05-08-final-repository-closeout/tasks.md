# 最终收尾重构 - 实施任务清单

## 1. Git分支净化

- [ ] 1.1 检查当前Git状态和分支结构
- [ ] 1.2 删除本地已合并的feature分支（refactor/eliminate-magic-numbers, refactor/phase-1-eliminate-duplicates）
- [ ] 1.3 清理远程dependabot分支（3个过期分支）
- [ ] 1.4 推送本地领先提交到远程master分支
- [ ] 1.5 验证仅保留master单一主线分支

## 2. 文件系统清洗

- [ ] 2.1 删除备份文件（src/ai_classifier.py.backup）
- [ ] 2.2 清理运行时数据目录（logs/, models/, .hypothesis/, .pytest_cache/）
- [ ] 2.3 删除过时报告文档（ARCHITECTURE_IMPROVEMENT_REPORT.md, docs/REFACTORING_SUMMARY.md, docs/code_quality_notes.md）
- [ ] 2.4 删除docs/package-lock.json文件
- [ ] 2.5 清理所有.pyc和__pycache__临时文件
- [ ] 2.6 更新.gitignore文件添加运行时数据忽略规则
- [ ] 2.7 验证git status显示干净状态（无未跟踪的运行时数据）

## 3. 文档精简与优化

- [ ] 3.1 精简CONTEXT.md内容（保留核心领域概念，删除详细架构描述）
- [ ] 3.2 优化Git Pages中英文index.md内容（增加营销价值和使用案例）
- [ ] 3.3 更新CHANGELOG.md记录本次收尾重构
- [ ] 3.4 检查并删除其他冗余文档文件

## 4. GitHub元数据更新

- [ ] 4.1 使用gh CLI更新仓库description
- [ ] 4.2 使用gh CLI添加topics标签（bookmark-manager, classification, offline-first等）
- [ ] 4.3 配置Git Pages URL和about页面信息
- [ ] 4.4 验证GitHub仓库元数据与本地文档一致

## 5. 最终验证与归档

- [ ] 5.1 运行完整测试套件验证功能完整性（pytest -q）
- [ ] 5.2 验证CI/CD配置正确性（检查.github/workflows/）
- [ ] 5.3 创建最终收尾提交（包含所有变更）
- [ ] 5.4 推送到远程master分支并验证
- [ ] 5.5 检查Git Pages构建状态（访问文档站点验证）
- [ ] 5.6 归档本次OpenSpec change（使用opsx:archive）

## 验收标准

### Git仓库状态
- ✅ 仅存在master/main分支（本地和远程）
- ✅ 无未推送的本地提交
- ✅ git status显示干净状态

### 文件系统状态
- ✅ 无备份文件（.backup, .bak）
- ✅ 无运行时数据（logs/, models/, .hypothesis/, .pytest_cache/）
- ✅ 无过时报告文档
- ✅ .gitignore包含完整运行时数据忽略规则

### 文档状态
- ✅ CONTEXT.md内容精简
- ✅ Git Pages包含营销内容和使用案例
- ✅ CHANGELOG.md记录本次收尾

### GitHub状态
- ✅ description准确描述项目
- ✅ topics包含核心标签
- ✅ Git Pages可访问且内容正确

### 功能验证
- ✅ 所有测试通过（265个测试）
- ✅ CI配置正确
- ✅ Git Pages构建成功