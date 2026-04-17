# 快速配置指南

## 5 分钟完成所有配置

---

## 第一步：推送代码（1 分钟）

```bash
# 重新认证 GitHub（如果需要）
gh auth login

# 推送配置到 GitHub
git push origin master
```

---

## 第二步：一键打开所有配置页面（复制粘贴运行）

```bash
# 在终端中运行以下命令打开所有配置页面
echo "正在打开配置页面..."

# 1. 分支保护
x-www-browser "https://github.com/LessUp/bookmarks-cleaner/settings/rules" 2>/dev/null || \
open "https://github.com/LessUp/bookmarks-cleaner/settings/rules" 2>/dev/null || \
echo "请手动打开: https://github.com/LessUp/bookmarks-cleaner/settings/rules"

# 2. 添加 Topics
x-www-browser "https://github.com/LessUp/bookmarks-cleaner" 2>/dev/null || \
open "https://github.com/LessUp/bookmarks-cleaner" 2>/dev/null

# 3. 查看 CI 状态
x-www-browser "https://github.com/LessUp/bookmarks-cleaner/actions" 2>/dev/null || \
open "https://github.com/LessUp/bookmarks-cleaner/actions" 2>/dev/null
```

---

## 第三步：手动配置（3 分钟）

### A. 配置分支保护（最重要）

**访问：** https://github.com/LessUp/bookmarks-cleaner/settings/rules

1. 点击 **"New ruleset"** → **"New branch ruleset"**
2. 填写 **Ruleset Name**: `Main Branch Protection`
3. **Targets**: 点击 **Add target** → 选择 **Default branch**
4. **启用以下规则**（按顺序勾选）：
   - ☑️ Restrict deletions
   - ☑️ Require linear history
   - ☑️ Require a pull request before merging
     - Required approvals: **1**
     - ☑️ Dismiss stale PR approvals when new commits are pushed
     - ☑️ Require conversation resolution before merging
   - ☑️ Require status checks to pass before merging
     - ☑️ Require branches to be up to date
     - 搜索添加: `Lint & Format Check`, `Type Check`, `Test (Python 3.10)`, `Test (Python 3.11)`, `Test (Python 3.12)`
   - ☑️ Block force pushes
5. 点击 **Create**

### B. 添加 Topics 标签

**访问：** https://github.com/LessUp/bookmarks-cleaner

1. 在右侧找到 **Topics**
2. 点击齿轮图标
3. 添加以下标签（每个回车）：
   ```
   bookmark-manager
   ai-classification
   productivity
   knowledge-management
   python-cli
   nlp
   browser-tool
   bookmark-cleaner
   ```
4. 点击 **Save changes**

---

## 第四步：验证 CI（1 分钟）

**访问：** https://github.com/LessUp/bookmarks-cleaner/actions

等待几分钟，确认所有工作流显示绿色 ✅：
- Lint & Format Check
- Type Check
- Security Scan
- Test (Python 3.10/3.11/3.12)

---

## 可选配置

### 启用 Discussions

https://github.com/LessUp/bookmarks-cleaner/settings

- 找到 **Features** → 勾选 **Discussions** → Save

### 配置 PyPI 自动发布

**Step 1.** 获取 Token: https://pypi.org/manage/account/token/

**Step 2.** 添加到 GitHub: https://github.com/LessUp/bookmarks-cleaner/settings/secrets/actions
- Name: `PYPI_API_TOKEN`
- Secret: [粘贴 PyPI Token]

**Step 3.** 测试发布:
```bash
git tag -a v2.0.1 -m "Release v2.0.1"
git push origin v2.0.1
```

---

## 完成！✅

您的项目现在具备：
- ✅ 企业级 CI/CD 流程
- ✅ 分支保护（防止误操作）
- ✅ 自动化代码检查
- ✅ 社区治理文件
- ✅ 专业开源项目标准

**遇到问题？** 查看详细指南：[SETUP_GUIDE.md](./SETUP_GUIDE.md)
