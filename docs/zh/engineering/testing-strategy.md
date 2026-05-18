# 测试策略

本页说明项目的测试架构、覆盖目标和执行方式，帮助贡献者理解质量保障的边界和期望。

## 测试金字塔

项目采用经典测试金字塔结构：

```
        ┌──────────────┐
        │    E2E 测试   │  CLI 端到端
        │    (少量)     │
        └──────────────┘
      ┌────────────────────┐
      │     集成测试       │  Pipeline 阶段交互
      │    (适量)          │
      └────────────────────┘
    ┌──────────────────────────┐
    │        单元测试           │  分类器、工具函数
    │       (大量)             │
    └──────────────────────────┘
```

| 层级 | 覆盖目标 | 运行时机 | 典型场景 |
|------|----------|----------|----------|
| 单元测试 | 单个函数/类方法 | 每次提交 | 规则匹配、置信度计算 |
| 集成测试 | 多模块交互 | PR 合并前 | Pipeline 阶段间数据契约 |
| E2E 测试 | CLI 入口到输出 | 发布前 | 完整处理流程验证 |

## 运行测试

```bash
# 运行全部测试
pytest -q

# 运行特定模块
pytest tests/test_fusion_engine.py -v

# 带覆盖率报告
pytest --cov=src --cov-report=html

# 只运行标记的快速测试
pytest -q -m "not slow"
```

## Mock 策略

项目对外部依赖采用明确的 Mock 边界：

| 依赖类型 | Mock 方式 | 工具 |
|----------|-----------|------|
| LLM API 调用 | 固定响应 | `unittest.mock` |
| 文件系统 | 临时目录 | `pytest.tmp_path` |
| 网络请求 | 录制回放 | `responses` 库 |
| ML 模型 | 轻量桩 | 预计算特征 |

### Mock 示例

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_llm_client():
    """Mock LLM API 调用，避免实际网络请求"""
    with patch('bookmarks_cleaner.services.llm.client.LLMClient') as mock:
        mock.return_value.classify.return_value = {
            'category': 'Development',
            'confidence': 0.92
        }
        yield mock

def test_llm_classifier_uses_mock(mock_llm_client):
    from bookmarks_cleaner.services.llm.classifier import LLMClassifier
    classifier = LLMClassifier()
    result = classifier.classify({'title': 'Python Tutorial', 'url': 'https://docs.python.org'})
    assert result['category'] == 'Development'
    assert mock_llm_client.return_value.classify.called
```

## 测试数据

项目维护两套测试数据：

1. **单元测试数据** (`tests/fixtures/`): 小型、确定性、版本控制
2. **集成测试数据** (`tests/data/`): 更大样本、模拟真实导出格式

```bash
tests/
├── fixtures/
│   ├── sample_bookmarks.html    # 10 条书签
│   └── sample_bookmarks.json    # JSON 格式对照
├── data/
│   └── large_export.html        # 1000+ 条书签
└── conftest.py                  # 共享 fixtures
```

## 故障注入测试

Pipeline 的容错能力通过故障注入测试验证：

```python
def test_malformed_html_recovery():
    """验证损坏 HTML 不应该崩溃整个处理"""
    loader = BookmarkLoader()
    with pytest.raises(PartialParseError) as exc_info:
        loader.load('tests/fixtures/corrupted.html')
    assert exc_info.value.recovered_count > 0  # 部分恢复

def test_ml_model_missing_fallback():
    """ML 模型缺失时应该降级到规则模式"""
    with patch.dict(os.environ, {'ML_MODEL_PATH': '/nonexistent'}):
        classifier = MLClassifier()
        result = classifier.classify({'title': 'Test', 'url': 'https://example.com'})
        assert result['source'] == 'rule'  # 降级到规则
        assert 'fallback' in result
```

## 覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|------------|----------|
| `src.pipelines` | ≥90% | ✅ 92% |
| `src.services.fusion` | ≥95% | ✅ 95% |
| `src.services.rules` | ≥90% | ✅ 91% |
| `src.services.ml` | ≥85% | ✅ 88% |
| `src.plugins` | ≥80% | ⚠️ 76% |

## 持续集成

每次 PR 都会触发完整的测试矩阵：

```yaml
# .github/workflows/ci.yml 片段
jobs:
  test:
    strategy:
      matrix:
        python: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest, macos-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -e ".[dev]"
      - run: pytest -q --cov
```

## 参考链接

- [Pipeline 架构](/zh/architecture/pipeline) — 理解测试边界的背景
- [ADR-005](/zh/adr#adr-005-测试边界与mock策略) — Mock 策略的决策记录
