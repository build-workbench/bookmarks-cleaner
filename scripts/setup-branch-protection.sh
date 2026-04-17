#!/bin/bash
set -e

# Branch Protection Setup Script
# Usage: ./scripts/setup-branch-protection.sh

echo "🔒 Setting up branch protection..."

# 验证 gh CLI 登录
if ! gh auth status &>/dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI. Run 'gh auth login' first."
    exit 1
fi

# 获取仓库信息
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q '.defaultBranchRef.name')

echo "📦 Repository: $REPO"
echo "🌿 Default Branch: $DEFAULT_BRANCH"

# 检查规则集是否已存在
EXISTING_RULESET=$(gh api repos/$REPO/rulesets --paginate 2>/dev/null | jq -r '.[] | select(.name == "Main Branch Protection") | .id')

if [ -n "$EXISTING_RULESET" ]; then
    echo "⚠️  Ruleset 'Main Branch Protection' already exists (ID: $EXISTING_RULESET)"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh api repos/$REPO/rulesets/$EXISTING_RULESET --method DELETE
        echo "🗑️  Deleted existing ruleset"
    else
        echo "⏹️  Skipping setup"
        exit 0
    fi
fi

# 提供手动配置指南
cat << GUIDE

📋 Please configure branch protection manually:

1. Go to: https://github.com/$REPO/settings/rules
2. Click "New ruleset"
3. Name: "Main Branch Protection"
4. Target branches: Select "Default branch"
5. Enable these rules:
   - ☑️ Restrict deletions
   - ☑️ Require linear history
   - ☑️ Require a pull request before merging
     - Required approvals: 1
     - ☑️ Dismiss stale PR approvals when new commits are pushed
     - ☑️ Require conversation resolution
   - ☑️ Require status checks to pass
     - ☑️ Require branches to be up to date
     - Add checks: "Lint & Format Check", "Type Check", "Test (Python 3.10-3.12)"
   - ☑️ Block force pushes
6. Click "Create"

Alternatively, run this command with admin permissions:
  gh api repos/$REPO/rulesets --method POST --input .github/ruleset.json

GUIDE

echo "✅ Setup guide complete!"
