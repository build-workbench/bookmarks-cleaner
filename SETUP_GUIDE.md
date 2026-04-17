# CleanBook 项目配置实现指南

本文档帮助您完成项目的所有配置，包括 GitHub 仓库设置、CI/CD 流程和安全策略。

---

## 📋 快速清单

在推送代码到 GitHub 后，请按顺序完成以下配置：

- [ ] 1. 推送代码到 GitHub
- [ ] 2. 配置分支保护规则（最重要）
- [ ] 3. 添加项目 Topics
- [ ] 4. 测试 CI 工作流
- [ ] 5. 配置 PyPI 自动发布（可选）
- [ ] 6. 启用 Discussions（可选）

---

## 1. 推送代码到 GitHub

### 准备工作

```bash
# 检查所有更改是否已暂存
git status

# 如果有未暂存的文件，请暂存
git add .github/ .pre-commit-config.yaml pyproject.toml scripts/

# 提交更改
git commit -m "chore: 全面增强 GitHub 配置和 CI/CD 流程

- 添加安全策略、行为准则和社区文件
- 增强 CI 流程：格式化、类型检查、安全扫描
- 添加自动发布、过期 Issue 管理
- 添加 pre-commit 钩子和开发环境脚本
- 增强 pyproject.toml 元数据和工具配置"

# 推送到远程仓库
git push origin master
```

---

## 2. 配置分支保护规则 ⭐ 必须

### 步骤 1：访问设置页面

打开浏览器访问：
```
https://github.com/LessUp/bookmarks-cleaner/settings/rules
```

### 步骤 2：创建新的规则集

1. 点击绿色的 **"New ruleset"** 按钮
2. 选择 **"New branch ruleset"**

### 步骤 3：填写规则集信息

| 字段 | 值 |
|------|-----|
| Ruleset Name | `Main Branch Protection` |
| Enforcement | `Active` |

### 步骤 4：选择目标分支

在 "Targets" 部分：
1. 点击 **"Add target"**
2. 选择 **"Default branch"**

### 步骤 5：启用规则

按顺序勾选以下规则：

#### 基础保护
- ✅ **Restrict deletions**（禁止直接删除分支）
- ✅ **Require linear history**（要求线性历史，禁止使用 merge commits）
- ✅ **Block force pushes**（禁止强制推送）

#### 拉取请求要求
- ✅ **Require a pull request before merging**
  - Required approvals: `1`
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require conversation resolution before merging

#### 状态检查要求
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - **搜索并添加以下状态检查：**
    - `Lint & Format Check`
    - `Type Check`
    - `Test (Python 3.10)`
    - `Test (Python 3.11)`
    - `Test (Python 3.12)`

### 步骤 6：保存规则

点击页面底部的 **"Create"** 按钮。

---

## 3. 添加项目 Topics

### 步骤 1：访问仓库首页

```
https://github.com/LessUp/bookmarks-cleaner
```

### 步骤 2：编辑 Topics

1. 在页面右侧找到 Topics 区域
2. 点击齿轮图标（⚙️）或 "Topics" 文字
3. 添加以下 Topics：

```
bookmark-manager
ai-classification
productivity
knowledge-management
python-cli
nlp
browser-tool
bookmark-cleaner
machine-learning
open-source
```

4. 点击 "Save changes"

---

## 4. 验证 CI 工作流

推送代码后，CI 会自动运行。验证步骤：

### 查看运行状态

1. 访问：
```
https://github.com/LessUp/bookmarks-cleaner/actions
```

2. 点击最新的工作流运行

3. 确认所有任务通过：
   - Lint & Format Check ✅
   - Type Check ✅
   - Security Scan ✅
   - Test (Python 3.10) ✅
   - Test (Python 3.11) ✅
   - Test (Python 3.12) ✅

### 修复常见问题

如果 CI 失败，常见原因：

#### 问题 1：代码格式检查失败
```bash
# 本地修复
black src/ main.py tests/
isort src/ main.py tests/
git add .
git commit -m "style: fix code formatting"
git push
```

#### 问题 2：类型检查失败
```bash
# 本地修复（可选，可以暂时忽略）
mypy src/ main.py --ignore-missing-imports
```

#### 问题 3：安全扫描失败
```bash
# 检查安全问题
pip install bandit
bandit -r src/
```

---

## 5. 配置 PyPI 自动发布（可选）

### 前提条件

- 您已在 PyPI 注册了 `cleanbook` 包名
- 您是 PyPI 包的所有者

### 步骤 1：创建 PyPI API Token

1. 访问：https://pypi.org/manage/account/token/
2. 点击 **"Add API token"**
3. 填写：
   - Token name: `cleanbook-github-release`
   - Scope: `Project: cleanbook`（如果包已存在）或 `Entire account`（如果是新包）
4. 点击 **"Create token"**
5. **复制 Token**（以 `pypi-` 开头）

### 步骤 2：添加到 GitHub Secrets

1. 访问：
```
https://github.com/LessUp/bookmarks-cleaner/settings/secrets/actions
```

2. 点击 **"New repository secret"**
3. 填写：
   - Name: `PYPI_API_TOKEN`
   - Secret: [粘贴您的 PyPI Token]
4. 点击 **"Add secret"**

### 步骤 3：测试发布

创建并推送一个测试标签：

```bash
# 创建标签（示例：v2.0.1）
git tag -a v2.0.1 -m "Release version 2.0.1"

# 推送标签（触发 release 工作流）
git push origin v2.0.1
```

### 预期结果

推送标签后：
1. GitHub Actions 会自动运行 release 工作流
2. 创建 GitHub Release 页面
3. 构建 wheel 并发布到 PyPI
4. 检查：
   - https://github.com/LessUp/bookmarks-cleaner/releases
   - https://pypi.org/project/cleanbook/

---

## 6. 启用 Discussions（可选）

### 启用步骤

1. 访问：
```
https://github.com/LessUp/bookmarks-cleaner/settings
```

2. 找到 "Features" 区域
3. 勾选 **"Discussions"**
4. 点击 **"Save"**

### 配置讨论分类

启用后，访问：
```
https://github.com/LessUp/bookmarks-cleaner/discussions
```

配置分类：
- Q&A（问答）
- Ideas（功能建议）
- Show and tell（使用案例分享）

---

## 7. 本地开发环境配置

### 一键配置

```bash
# 运行自动配置脚本
./scripts/setup-dev-env.sh
```

### 手动配置

```bash
# 1. 创建虚拟环境
python3 -m venv .venv

# 2. 激活环境
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 安装 pre-commit 钩子
pre-commit install

# 5. 验证安装
black --version
isort --version
flake8 --version
pytest --version
```

### 常用开发命令

```bash
# 格式化代码
black src/ main.py tests/

# 排序导入
isort src/ main.py tests/

# 代码检查
flake8 src/ main.py --max-line-length=120

# 类型检查（可选）
mypy src/ main.py --ignore-missing-imports

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 提交前检查（运行所有 pre-commit 钩子）
pre-commit run --all-files
```

---

## 8. 验证配置完整性

### 访问以下链接确认配置成功

| 检查项 | 链接 | 预期结果 |
|--------|------|----------|
| 工作流状态 | https://github.com/LessUp/bookmarks-cleaner/actions | 显示绿色勾选 |
| 分支保护 | https://github.com/LessUp/bookmarks-cleaner/settings/rules | 显示 "Main Branch Protection" |
| Security | https://github.com/LessUp/bookmarks-cleaner/security | 显示 "Security policy" |
| Issues | https://github.com/LessUp/bookmarks-cleaner/issues/new/choose | 显示表单模板 |
| Topics | https://github.com/LessUp/bookmarks-cleaner | 右侧显示 Topics |

---

## 9. 故障排除

### 问题 1：推送失败

```bash
# 检查网络连接
git config --global http.sslVerify true

# 或使用 SSH
git remote set-url origin git@github.com:LessUp/bookmarks-cleaner.git
```

### 问题 2：CI 持续失败

```bash
# 本地先运行检查
pre-commit run --all-files

# 然后提交修复
git add .
git commit -m "ci: fix formatting issues"
git push
```

### 问题 3：分支保护导致无法推送

这是正常的！启用分支保护后：
1. 不能直接推送到 master
2. 必须通过 Pull Request
3. PR 需要代码审查和 CI 通过

**正确的开发流程：**
```bash
# 1. 创建功能分支
git checkout -b feature/my-feature

# 2. 开发并提交
git add .
git commit -m "feat: add new feature"

# 3. 推送到远程分支
git push origin feature/my-feature

# 4. 在 GitHub 创建 Pull Request
# 5. 等待 CI 通过和代码审查
# 6. 合并到 master
```

---

## 10. 获取帮助

遇到问题？

1. 查看 GitHub Actions 日志：https://github.com/LessUp/bookmarks-cleaner/actions
2. 查看本文档的详细步骤
3. 创建 Issue 讨论：https://github.com/LessUp/bookmarks-cleaner/issues

---

**配置完成后，您的项目将具备完整的持续集成、自动化发布和社区治理！** 🎉
