# 开发指南

本指南面向希望为 CleanBook 贡献代码或基于其进行二次开发的开发者。

## 环境搭建

### 系统要求

- **Python**: 3.10+
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 2GB 可用空间

### 推荐的开发工具

```bash
# IDE 推荐
- VS Code + Python Extension
- PyCharm Professional
- Vim/Neovim + LSP

# 版本控制
- Git 2.20+

# 虚拟环境
- venv (Python 内置)
- conda
- poetry
```

### 项目初始化

```bash
# 克隆项目
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行健康检查
python main.py --health-check
```

## 项目结构

```
bookmarks-cleaner/
├── main.py                     # 主入口
├── config.json                 # 配置文件
├── pyproject.toml              # 项目元数据
├── requirements.txt            # 生产依赖
├── requirements-dev.txt        # 开发依赖
├── src/                        # 源代码
│   ├── cleanbook/             # 核心包
│   │   ├── cli.py             # CLI 入口
│   │   └── ...
│   ├── plugins/               # 插件系统
│   │   ├── base.py            # 插件基类
│   │   └── classifiers/       # 分类器插件
│   ├── services/              # 服务层
│   ├── ai_classifier.py       # AI 分类器
│   ├── bookmark_processor.py  # 书签处理器
│   ├── rule_engine.py         # 规则引擎
│   └── ...
├── tests/                      # 测试代码
├── models/                     # 模型存储
├── taxonomy/                   # 词表配置
└── docs/                       # 文档
```

## 代码规范

### Python 代码风格

使用类型注解和 dataclass：

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class BookmarkFeatures:
    """书签特征数据类"""
    url: str
    title: str
    domain: str = ""
    confidence: float = 0.0

def classify_bookmark(url: str, title: str) -> ClassificationResult:
    """
    分类单个书签
    
    Args:
        url: 书签 URL
        title: 书签标题
        
    Returns:
        分类结果对象
        
    Raises:
        ClassificationError: 分类失败时抛出
    """
    pass
```

### 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# 使用方式
logger.debug("调试信息: 特征提取开始")
logger.info(f"处理完成: {count} 个书签")
logger.warning("配置文件缺少某些字段")
logger.error(f"处理失败: {error_msg}")
```

### 测试规范

```python
import pytest
from unittest.mock import Mock, patch

class TestAIClassifier:
    """AI 分类器测试类"""
    
    def setup_method(self):
        """每个测试方法的初始化"""
        self.classifier = AIClassifier("test_config.json")
    
    def test_classify_github_url(self):
        """测试 GitHub URL 分类"""
        url = "https://github.com/user/repo"
        title = "Test Repository"
        
        result = self.classifier.classify(url, title)
        
        assert result.category == "技术/代码仓库"
        assert result.confidence > 0.8
```

## 扩展开发

### 添加新的分类器插件

1. 在 `src/plugins/classifiers/` 创建新文件
2. 继承 `ClassifierPlugin` 基类
3. 实现必需方法
4. 在 `registry.py` 注册

```python
# src/plugins/classifiers/my_classifier.py
from ..base import ClassifierPlugin, PluginMetadata, ClassificationResult

class MyClassifier(ClassifierPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_classifier",
            version="1.0.0",
            capabilities=["custom"],
            priority=50
        )
    
    def classify(self, features):
        # 实现分类逻辑
        return ClassificationResult(
            category="分类结果",
            confidence=0.9,
            method="my_classifier"
        )
```

### 添加新的导出格式

1. 扩展 `DataExporter` 类
2. 在 `bookmark_processor.py` 注册

```python
class XMLExporter(DataExporter):
    """XML 格式导出器"""
    
    def export(self, organized_bookmarks, output_file, stats=None):
        """导出 XML 格式"""
        # 实现导出逻辑
        pass
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_rule_engine.py

# 运行带覆盖率的测试
pytest --cov=src --cov-report=html

# 运行属性测试
pytest tests/test_*_properties.py
```

### 性能测试

```python
import time
import pytest

class TestPerformance:
    @pytest.mark.performance
    def test_classification_speed(self):
        classifier = AIClassifier("config.json")
        test_bookmarks = [("https://example.com", "Test")] * 100
        
        start = time.time()
        for url, title in test_bookmarks:
            classifier.classify(url, title)
        elapsed = time.time() - start
        
        assert len(test_bookmarks) / elapsed > 20  # 至少 20 个/秒
```

## 调试技巧

### 启用调试模式

```bash
# 命令行
python main.py --log-level DEBUG

# 代码中
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 使用断点

```python
import pdb; pdb.set_trace()
# 或使用更友好的 ipdb
import ipdb; ipdb.set_trace()
```

### 性能分析

```bash
# 使用 cProfile
python -m cProfile -o profile.prof main.py -i input.html

# 分析结果
python -c "import pstats; pstats.Stats('profile.prof').sort_stats('cumulative').print_stats(20)"
```

## 提交 Pull Request

1. Fork 仓库并创建功能分支
2. 编写代码并添加测试
3. 确保所有测试通过
4. 更新文档（如需要）
5. 提交 PR，描述清楚改动内容

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 添加新的分类器插件
fix: 修复缓存失效问题
docs: 更新 README
test: 添加性能测试
refactor: 重构规则引擎
```

## 发布流程

```bash
# 1. 更新版本号
# 编辑 pyproject.toml 中的 version

# 2. 更新 CHANGELOG.md

# 3. 提交更改
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): prepare v2.0.1"

# 4. 打标签
git tag v2.0.1

# 5. 推送
git push origin main --tags

# 6. GitHub Actions 会自动发布到 PyPI
```
