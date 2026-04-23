# 自定义规则示例

通过 `config.json` 的 `category_rules` 定义自己的分类逻辑。

## 基本规则结构

```json
{
  "category_rules": {
    "分类名称": {
      "rules": [
        {
          "match": "匹配类型",
          "keywords": ["关键词1", "关键词2"],
          "weight": 权重值
        }
      ],
      "description": "分类说明"
    }
  }
}
```

## 示例一：开发文档分类

为常用技术文档建立分类：

```json
{
  "category_rules": {
    "📚 开发文档": {
      "rules": [
        {"match": "domain", "keywords": ["docs.python.org"], "weight": 20},
        {"match": "domain", "keywords": ["developer.mozilla.org"], "weight": 20},
        {"match": "domain", "keywords": ["docs.github.com", "docs.gitlab.com"], "weight": 18},
        {"match": "url_pattern", "pattern": "^https://.*\\.readthedocs\\.io", "weight": 15},
        {"match": "title", "keywords": ["documentation", "docs", "API reference"], "weight": 12}
      ]
    }
  }
}
```

## 示例二：技术栈分类

按技术栈组织书签：

```json
{
  "category_rules": {
    "⚛️ React": {
      "rules": [
        {"match": "domain", "keywords": ["react.dev", "reactjs.org"], "weight": 20},
        {"match": "title", "keywords": ["react", "redux", "next.js"], "weight": 15},
        {"match": "url_ends_with", "patterns": ["/react-", "/react_"], "weight": 12}
      ]
    },
    "🐹 Go": {
      "rules": [
        {"match": "domain", "keywords": ["go.dev", "golang.org"], "weight": 20},
        {"match": "title", "keywords": ["golang", "go module", "goroutine"], "weight": 15}
      ]
    }
  }
}
```

## 示例三：工作相关分类

区分工作和个人书签：

```json
{
  "category_rules": {
    "💼 工作工具": {
      "rules": [
        {"match": "domain", "keywords": ["jira.company.com", "confluence.company.com"], "weight": 20},
        {"match": "domain", "keywords": ["slack.com", "teams.microsoft.com"], "weight": 18},
        {"match": "title", "keywords": ["internal wiki", "engineering blog"], "weight": 15}
      ]
    }
  }
}
```

## 示例四：资源类型分类

按资源类型（视频、文档、代码）分类：

```json
{
  "category_rules": {
    "▶️ 视频教程": {
      "rules": [
        {"match": "domain", "keywords": ["youtube.com", "bilibili.com"], "weight": 10},
        {"match": "title", "keywords": ["tutorial", "course", "视频", "教程"], "weight": 8},
        {"match": "url_ends_with", "patterns": ["watch", "video"], "weight": 12}
      ]
    },
    "💾 GitHub 仓库": {
      "rules": [
        {"match": "url_pattern", "pattern": "^https://github\\.com/[^/]+/[^/]+$", "weight": 20},
        {"match": "domain", "keywords": ["github.com", "gitlab.com"], "weight": 8}
      ]
    }
  }
}
```

## 规则权重指南

| 权重 | 说明 | 使用场景 |
|------|------|----------|
| 20 | 绝对命中 | 特定域名，如 `github.com/[user]/[repo]` |
| 15 | 强匹配 | 官方文档站点 |
| 10 | 标准匹配 | 关键词匹配 |
| 5 | 弱匹配 | 辅助判断 |

## 测试规则

```bash
# 使用测试模式验证规则
cleanbook -i test-bookmarks.html -o output/ --dry-run --verbose

# 查看分类统计
cat output/bookmarks_summary.md | grep "分类分布"

# 查找特定分类的书签
grep -A 5 "分类名称" output/bookmarks_data.json
```

## 规则优化技巧

1. **避免过度宽泛**: 不要使用过于通用的关键词（如 "the", "article"）
2. **从少开始**: 先建立少数核心分类，逐步扩展
3. **定期审查**: 查看 "未分类" 书签，补充规则覆盖
4. **文档化**: 为复杂规则添加注释说明

## 下一步

- [配置详解](../reference/config) — 完整配置选项
- [基础用法示例](./basic) — 更多使用场景
