# Branch Protection Setup

## 使用 GitHub CLI 配置分支保护

### 1. 创建分支保护规则集 (Ruleset)

```bash
# 创建 main/master 分支保护规则集
gh api repos/{owner}/{repo}/rulesets \
  --method POST \
  --input - <<EOF
{
  "name": "Main Branch Protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": [~DEFAULT_BRANCH]
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    },
    {
      "type": "required_linear_history"
    },
    {
      "type": "required_signatures"
    },
    {
      "type": "pull_request",
      "parameters": {
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_approving_review_count": 1,
        "required_review_thread_resolution": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          {
            "context": "Lint & Format Check (ci)",
            "integration_id": 15368
          },
          {
            "context": "Test (Python 3.10)",
            "integration_id": 15368
          },
          {
            "context": "Test (Python 3.11)",
            "integration_id": 15368
          },
          {
            "context": "Test (Python 3.12)",
            "integration_id": 15368
          }
        ],
        "strict_required_status_checks_policy": true
      }
    }
  ]
}
EOF
```

### 2. 手动配置步骤 (通过 GitHub Web 界面)

如果 CLI 命令不可用，请按以下步骤手动配置：

1. 进入仓库 Settings → Branches
2. 点击 "Add rule" 或 "Add ruleset"
3. 配置以下规则：

#### 规则名称: `main-protection`

**应用目标:**
- 默认分支 (Default branch)

**规则:**
- ✅ Restrict deletions
- ✅ Require linear history
- ✅ Require merge queue
- ✅ Require a pull request before merging
  - Require approvals: 1
  - Dismiss stale PR approvals when new commits are pushed
  - Require review from Code Owners: ❌
  - Require approval of the most recent reviewable push
  - Require conversation resolution before merging
- ✅ Require status checks to pass before merging
  - Require branches to be up to date before merging
  - Status checks that are required:
    - `Lint & Format Check`
    - `Test (Python 3.10)`
    - `Test (Python 3.11)`
    - `Test (Python 3.12)`
- ✅ Require signed commits (推荐)
- ✅ Block force pushes

### 3. 验证配置

```bash
# 查看当前规则集
gh api repos/{owner}/{repo}/rulesets

# 或查看分支保护
gh api repos/{owner}/{repo}/branches/main/protection
```

### 4. 可选：使用环境变量配置

创建 `.github/.env.branch-protection` 文件来存储配置：

```bash
# 保存此脚本为 scripts/setup-branch-protection.sh
#!/bin/bash
set -e

echo "Setting up branch protection..."

# 验证 gh CLI 登录
if ! gh auth status &>/dev/null; then
    echo "Error: Not authenticated with GitHub CLI. Run 'gh auth login' first."
    exit 1
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Configuring branch protection for: $REPO"

# 创建规则集
gh api repos/$REPO/rulesets --method POST \
  --field "name=Main Branch Protection" \
  --field "target=branch" \
  --field "enforcement=active" \
  --input .github/ruleset.json

echo "Branch protection configured successfully!"
```

## 注意事项

1. **首次配置**: 确保你有仓库管理权限
2. **CI 检查**: 配置前确保 CI 工作流已正常运行
3. **团队协作**: 通知团队成员关于新的合并要求
4. **逐步实施**: 可以先启用规则但不强制，观察一段时间后再强制实施
