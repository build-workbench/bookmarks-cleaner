# 优化技巧

本文档汇总 Bookmarks Cleaner 的性能优化技巧，帮助您获得最佳处理速度。

## 快速优化清单

| 优化项 | 预期提升 | 难度 |
|--------|----------|------|
| 增加并发线程数 | 2-4x | 低 |
| 启用缓存 | 20-50% | 低 |
| 禁用 ML/LLM | 10x+ | 低 |
| 批量处理 | 30% | 低 |
| 调整批大小 | 10-20% | 中 |

## 并发优化

### 调整线程数

```bash
# 根据CPU核心数调整
cleanbook -i bookmarks.html --workers 8
```

**推荐值**：
- 2核：2-4 线程
- 4核：4-8 线程
- 8核+：8-16 线程

### 批量处理

```python
# ❌ 逐个处理
for file in files:
    processor.process_files([file])

# ✅ 批量处理
processor.process_files(files)
```

## 缓存优化

### 启用持久化缓存

```json
{
  "cache": {
    "enabled": true,
    "embedding_persistent": true,
    "cache_dir": ".cache/bookmarks"
  }
}
```

### 预热缓存

```python
# 首次运行预热缓存
cleanbook -i bookmarks.html --warm-cache

# 后续运行利用缓存
cleanbook -i new_bookmarks.html  # 快得多
```

## 内存优化

### 流式处理

对于超大书签文件（>50,000 条）：

```python
from src.bookmark_processor import BookmarkProcessor

processor = BookmarkProcessor(
    config_path="config.json",
    max_workers=4,
)

# 流式处理，避免内存溢出
for chunk in processor.process_streaming("huge_bookmarks.html", chunk_size=1000):
    print(f"处理进度: {chunk.progress}%")
```

### 延迟初始化

```python
# 延迟加载重量级组件
class LazyLoader:
    def __init__(self):
        self._model = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = load_heavy_model()
        return self._model
```

## I/O 优化

### 并行文件读取

```python
import aiofiles
import asyncio

async def read_files_async(files: List[str]) -> List[str]:
    """异步并行读取文件"""
    tasks = [read_file_async(f) for f in files]
    return await asyncio.gather(*tasks)

async def read_file_async(path: str) -> str:
    async with aiofiles.open(path, 'r') as f:
        return await f.read()
```

### 输出缓冲

```python
# 使用缓冲写入
BUFFER_SIZE = 1000
buffer = []

for result in results:
    buffer.append(result)
    if len(buffer) >= BUFFER_SIZE:
        write_batch(buffer)
        buffer.clear()

# 写入剩余
if buffer:
    write_batch(buffer)
```

## 算法优化

### 规则引擎优先

```python
# 配置权重，让规则引擎处理更多书签
{
  "fusion_weights": {
    "rule": 0.5,     # 提高规则权重
    "ml": 0.3,
    "semantic": 0.1,
    "llm": 0.1
  }
}
```

### 减少冗余计算

```python
# ❌ 重复计算
for bookmark in bookmarks:
    domain = extract_domain(bookmark.url)  # 每次都计算
    category = classify_by_domain(domain)

# ✅ 缓存计算结果
domain_cache = {}
for bookmark in bookmarks:
    domain = domain_cache.get(bookmark.url) or extract_domain(bookmark.url)
    domain_cache[bookmark.url] = domain
    category = classify_by_domain(domain)
```

## 配置调优

### 最佳实践配置

```json
{
  "max_workers": 4,
  "batch_size": 100,
  
  "ai_settings": {
    "enable_learning": true,
    "confidence_threshold": 0.7,
    "use_ml": true,
    "use_llm": false
  },
  
  "cache": {
    "enabled": true,
    "feature_ttl": 7200,
    "classification_ttl_hours": 48
  },
  
  "performance": {
    "task_timeout": 30,
    "retry_count": 2,
    "streaming_threshold": 50000
  }
}
```

### 禁用重量级特性

```json
{
  "ai_settings": {
    "use_ml": false,
    "use_llm": false
  }
}
```

**速度对比**：
| 配置 | 1000 书签处理时间 |
|------|-------------------|
| 全功能 | 45s |
| 无 ML | 8s |
| 仅规则 | 2s |

## 性能分析

### 使用内置分析

```bash
# 启用性能分析
cleanbook -i bookmarks.html --profile

# 输出分析报告
Performance Report:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stage              Time     %      
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loading            0.3s     2%
Deduplication      0.2s     1%
Classification     12.5s    76%
Organization       1.8s     11%
Export             1.5s     10%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 16.3s
```

### 使用 cProfile

```bash
python -m cProfile -s cumtime main.py -i bookmarks.html
```

## 相关文档

- [并发处理](/zh/performance/concurrency) - 并发模型详解
- [缓存策略](/zh/performance/caching) - 缓存系统
