# 性能方法学

本页解释应该如何阅读站点中的性能主张。它刻意避免给出未经维护验证的"调优偏方"，而是聚焦当前运行时形态下真正成立的解释方式。

<PerformanceChart />

## 测量包络

站点里的性能数字至少要沿四个轴阅读：

| 轴 | 要回答的问题 |
|----|--------------|
| 冷启动 | 在重型智能层尚未加载之前，进入运行时的成本是多少？ |
| 稳态吞吐 | Pipeline 进入工作态之后，书签处理速度如何？ |
| 模式宽度 | 当前运行是仅规则、混合模式，还是带 LLM 协助？ |
| 资源压力 | 内存与并发限制如何决定实际可处理上限？ |

## 基准测试方法论

### 测试环境

站点中报告的性能数字基于以下测试配置：

| 配置项 | 规格 |
|--------|------|
| CPU | AMD Ryzen 5 5600X（6 核 12 线程，3.7 GHz base） |
| 内存 | 32 GB DDR4 3200 |
| 存储 | NVMe SSD（读取 ~3.5 GB/s） |
| Python | 3.12（CPython） |
| 操作系统 | Ubuntu 22.04 LTS |
| 书签集规模 | 1,000 条（基准）、5,000 条（扩展测试） |

**声明**：这些数字是在单台机器上的单次测试结果，不是对所有环境的保证。实际速度受以下因素影响：CPU 核心数、内存带宽、书签平均 URL 长度、规则命中率。

### 基准测试脚本

你可以在自己的环境中复现基准：

```bash
# 安装测试依赖
pip install cleanbook[dev]

# 生成 1000 条测试书签
python -m cleanbook.bench.generate --count 1000 --output test_bookmarks.html

# 规则模式基准
time cleanbook -i test_bookmarks.html -o /tmp/bench_out/ --no-ml

# 混合模式基准（含 ML 初始化）
time cleanbook -i test_bookmarks.html -o /tmp/bench_out/

# 使用 Python 分析器（更精确）
python -m cProfile -o bench.prof -m cleanbook.main -i test_bookmarks.html -o /tmp/bench_out/ --no-ml
python -m pstats bench.prof
```

## 这些数字到底意味着什么

### 三种路径的成本构成

**规则优先路径**（最快）

```
冷启动: ~30–60 ms
  ├── Python 解释器初始化: ~20 ms
  ├── 配置文件加载: ~5 ms
  └── 规则集编译（正则预编译）: ~10 ms

稳态吞吐: 500–650 书签/秒
  ├── HTML 解析: ~25%
  ├── 规则匹配: ~35%
  ├── 目录树构建: ~20%
  └── 序列化导出: ~20%
```

**混合路径**（ML 辅助）

```
冷启动: ~1.2–3.0 秒
  ├── 规则路径开销: ~60 ms
  ├── scikit-learn 导入: ~400 ms
  ├── TF-IDF 向量器加载: ~200 ms
  └── 模型反序列化（pickle）: ~500 ms–2 s

稳态吞吐: 300–420 书签/秒
  ├── 规则命中部分: ~600/s（跳过 ML）
  └── ML 推理部分: ~150/s（特征提取 + 推理）
```

**LLM 协助路径**（可选）

```
延迟主导因素: 网络往返 + 模型推理
  ├── 本地 Ollama: ~200–800 ms/书签
  └── 远程 API（OpenAI 等）: ~400–1500 ms/书签

适用场景: 规则 + ML 均置信度低的歧义样本（通常 < 5%）
```

## 当前真正成立的优化杠杆

维护中的性能故事依赖下面这些与架构一致的杠杆：

### 1. 让常见路径保持确定性

越多书签在规则层就被解决，单次运行的边际成本就越低。规则引擎使用了以下优化：

```python
# 域名索引：O(1) 查找而非 O(R) 遍历
self._domain_index: dict[str, str] = {
    domain: category
    for category, rules in self.rules.items()
    for domain in rules.get('domains', [])
}

def _match_domain(self, url: str) -> Optional[str]:
    hostname = urlparse(url).hostname or ''
    # 精确匹配
    if hostname in self._domain_index:
        return self._domain_index[hostname]
    # 后缀匹配（e.g., docs.github.com → github.com）
    parts = hostname.split('.')
    for i in range(len(parts) - 1):
        candidate = '.'.join(parts[i:])
        if candidate in self._domain_index:
            return self._domain_index[candidate]
    return None
```

典型大型书签库中，规则命中率约为 60–75%，这意味着大多数书签以接近 O(1) 的代价完成分类。

### 2. 延迟初始化重型依赖

ML 模型和语义向量器在第一次需要时才会初始化，而不是在进程启动时：

```python
class MLClassifier:
    def __init__(self):
        self._model = None      # 延迟加载
        self._vectorizer = None

    @property
    def model(self):
        if self._model is None:
            self._model = self._load_model()
        return self._model
```

这让规则模式的冷启动保持在 100ms 以下，即使用户已安装了 ML 依赖。

### 3. 并发分类

对于混合路径，`ThreadPoolExecutor` 允许多个书签并行分类（在 I/O 等待和 GIL 释放时有效）：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def classify_batch(
    self,
    bookmarks: list[Bookmark],
    max_workers: int = 4,
) -> list[ClassificationResult]:
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(self.classify, bm): bm for bm in bookmarks}
        return [f.result() for f in as_completed(futures)]
```

**实测加速比**：对于 5,000 条书签，4 线程带来约 1.8–2.3x 加速（受 GIL 限制，远低于理论 4x）。

### 4. 保持本地执行

除非用户显式选择，否则不要把性能问题变成网络往返问题。

## Profiling 工具链

### cProfile（标准库）

```bash
# 对完整运行进行性能分析
python -m cProfile -o output.prof cleanbook -i bookmarks.html

# 查看热点函数
python -c "
import pstats
p = pstats.Stats('output.prof')
p.sort_stats('cumulative')
p.print_stats(20)
"
```

### line_profiler（逐行分析）

```bash
pip install line_profiler

# 在热点函数上添加 @profile 装饰器后运行
kernprof -l -v cleanbook -i bookmarks.html
```

### memory_profiler（内存分析）

```bash
pip install memory_profiler

# 分析内存增长
mprof run cleanbook -i bookmarks.html
mprof plot
```

### 快速诊断流程

```
性能问题 → 确认模式（规则/混合/LLM）
    ↓
规则模式仍慢 → cProfile → 通常是 HTML 解析或正则编译
    ↓
混合模式慢 → 区分冷启动 vs 稳态
    ├── 冷启动慢 → 检查模型文件大小、磁盘速度
    └── 稳态慢 → line_profiler 定位 ML 推理热点
```

## 时间复杂度速查

| 操作 | 复杂度 | 实际说明 |
|------|--------|---------|
| 加载（N 条书签） | $O(N)$ | 文件大小线性 |
| URL 哈希去重 | $O(N)$ | 哈希表操作 |
| 标题近似去重 | $O(N^2)$ 最坏 | 使用 MinHash 可降至 $O(N)$ |
| 规则分类（域名索引） | $O(N)$ | 哈希查找 |
| TF-IDF 分类 | $O(N \cdot V)$ | V ≈ 5,000 特征维度 |
| 目录树构建 | $O(N \log N)$ | 排序 + 树插入 |
| HTML 序列化 | $O(N)$ | 线性写入 |

## 与其他性能页面的关系

- [并发处理](/zh/performance/concurrency) 讨论为何运行时采用当前并发模型（`ThreadPoolExecutor` vs `asyncio`）。
- [缓存策略](/zh/performance/caching) 讨论复用机制到底能带来什么收益（TF-IDF 矩阵缓存、规则集缓存）。
- [技术白皮书](/zh/whitepaper) 则把性能放回系统边界与失败模型中整体解释。
