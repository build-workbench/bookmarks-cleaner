# CleanBook 快速上手

CleanBook 是一个用于清理与分类浏览器书签的命令行工具，支持规则 + 机器学习 + 可选 LLM 分类，默认离线可用。

## 安装

### 推荐方式：pipx（隔离环境）

```powershell
# 安装 pipx（如未安装）
python -m pip install --user pipx
python -m pipx ensurepath

# 安装 CleanBook
pipx install .
```

### 从源码运行

```powershell
# 克隆仓库后直接运行
python main.py --help
```

## 命令入口

| 命令 | 说明 |
|------|------|
| `cleanbook` | 命令式处理（等价于 `python main.py`） |
| `cleanbook-wizard` | 向导式体验（基于 Rich 的交互式菜单） |

## 最小示例

```powershell
# 处理单个书签 HTML 文件
cleanbook -i examples/demo_bookmarks.html -o output

# 处理并训练 ML 模型
cleanbook -i examples/demo_bookmarks.html --train

# 交互向导模式
cleanbook-wizard

# 健康检查
cleanbook --health-check
```

## 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --input` | 输入文件或通配符 | 必需 |
| `-o, --output` | 输出目录 | `output` |
| `--workers` | 并行线程数 | 4 |
| `--threshold` | 分类置信度阈值 | 0.7 |
| `--train` | 启用 ML 训练 | 关闭 |
| `--no-ml` | 关闭 ML 分类 | 关闭 |
| `--limit N` | 限制处理数量（调试用） | 无限制 |
| `--health-check` | 系统健康检查 | - |
| `--log-level` | 日志级别 | INFO |

## 输出格式

| 格式 | 文件名 | 用途 |
|------|--------|------|
| HTML | `bookmarks_*.html` | 导入浏览器（Netscape 格式） |
| JSON | `bookmarks_*.json` | 二次处理、数据分析 |
| Markdown | `report_*.md` | 知识库归档、文档 |

## LLM 分类（可选）

默认关闭，遵循”可用即用、不可用自动降级”原则。

### 配置步骤

1. 编辑 `config.json`：

```json
“llm”: {
  “enable”: true,
  “provider”: “openai”,
  “base_url”: “https://api.openai.com”,
  “model”: “gpt-4o-mini”,
  “api_key_env”: “OPENAI_API_KEY”,
  “temperature”: 0.0,
  “timeout_seconds”: 25
}
```

2. 设置环境变量：

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = “你的_API_Key”

# Linux/macOS
export OPENAI_API_KEY=”你的_API_Key”
```

> 未设置 Key 或调用失败时，系统自动回退到离线分类路径。

## 分类策略

CleanBook 采用多层次分类策略：

```
┌─────────────────────────────────────────┐
│  1. 规则引擎 (优先级最高，亚毫秒响应)       │
│     - 域名匹配、关键词匹配、路径模式        │
├─────────────────────────────────────────┤
│  2. 机器学习 (中等优先级)                  │
│     - Random Forest、SVM、Naive Bayes   │
├─────────────────────────────────────────┤
│  3. 语义分析 (辅助)                       │
│     - 词向量相似度、TF-IDF               │
├─────────────────────────────────────────┤
│  4. LLM 分类 (可选，最低优先级)            │
│     - OpenAI 兼容接口                    │
└─────────────────────────────────────────┘
```

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 输出标题 emoji 叠加 | 使用最新版，确认 `show_confidence_indicator` 配置 |
| LLM 调用无效 | 检查 `llm.enable` 与环境变量，失败会自动回退 |
| 打包安装异常 | 使用 `pipx install .` 或 `python -m pip install .` |
| 内存不足 | 使用 `--no-ml` 禁用 ML，或减少 `--workers` |

## 下一步

- [书签管理最佳实践](/design/bookmark_best_practices_zh)
- [系统架构](/design/system_architecture)
- [开发指南](/guides/development_guide)
