# 安装

<CbBadge text="稳定版 v2.0.0" type="tip" />

## 系统要求

- **Python**: 3.10 或更高版本
- **操作系统**: Linux, macOS, Windows
- **内存**: 最低 512MB，推荐 2GB+（启用 ML 时）
- **磁盘**: 约 200MB（包含 ML 模型缓存）

## 安装方式

### 方式一：pipx（推荐）

[pipx](https://pipx.pypa.io/) 会在隔离的虚拟环境中安装 CleanBook，避免依赖冲突。

```bash
# 安装 pipx
pip install pipx
pipx ensurepath

# 安装 CleanBook
pipx install cleanbook

# 验证
which cleanbook
cleanbook --version
```

**升级**: `pipx upgrade cleanbook`
**卸载**: `pipx uninstall cleanbook`

### 方式二：pip

```bash
# 安装到当前 Python 环境
pip install cleanbook

# 验证
cleanbook --version
```

::: warning 注意
pip 安装可能会与系统其他 Python 包产生冲突，特别是在使用系统 Python 时。
:::

### 方式三：uv

使用 [uv](https://github.com/astral-sh/uv) 可获得更快的安装速度：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 CleanBook
uv tool install cleanbook

# 验证
cleanbook --version
```

### 方式四：源码安装

适用于想要修改代码或参与开发：

```bash
# 克隆仓库
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# 安装依赖
pip install -e ".[dev]"

# 验证
cleanbook --version
```

## 验证安装

运行以下命令验证安装成功：

```bash
# 查看版本
cleanbook --version

# 查看帮助
cleanbook --help

# 运行健康检查
cleanbook --health-check
```

## 可选依赖

### 启用机器学习（推荐）

```bash
# 安装 scikit-learn 以获得最佳分类效果
pip install scikit-learn numpy

# 或使用 pipx 注入依赖
pipx inject cleanbook scikit-learn numpy
```

### 启用 LLM（可选）

```bash
# 如果需要 LLM 增强分类
pip install openai

# pipx 注入
pipx inject cleanbook openai
```

## 配置环境

### 使用自定义配置

CleanBook 默认使用内置配置；如果你要覆盖它，请显式传入配置文件：

```bash
cleanbook -i bookmarks.html -o output/ -c ./config.json
```

## 常见问题

### Q: 安装失败，提示 "No module named 'sklearn'"?

```bash
# 安装 scikit-learn
pip install scikit-learn

# 或在使用时禁用 ML
cleanbook -i bookmarks.html --no-ml
```

### Q: Windows 上无法执行 cleanbook 命令?

```bash
# 检查 Scripts 目录是否在 PATH 中
pip show cleanbook

# 或直接使用 Python 模块
python -m cleanbook --help
```

### Q: macOS 上提示 "无法验证开发者"?

前往 **系统设置 → 隐私与安全性**，点击 "仍要打开"。

### Q: 如何完全卸载？

```bash
# pipx 安装
pipx uninstall cleanbook

# pip 安装
pip uninstall cleanbook

# 清理配置
rm -rf ~/.config/cleanbook
rm -rf ~/.cache/cleanbook
```

## 下一步

- [快速开始](../quickstart) — 5 分钟上手
- [配置详解](/zh/reference/config) — 了解 config.json 配置
- [配置指南](/zh/guide/configuration) — 理解配置文件覆盖方式
