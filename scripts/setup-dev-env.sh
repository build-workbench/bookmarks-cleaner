#!/bin/bash
set -e

# CleanBook 开发环境配置脚本
# 一键配置本地开发环境

echo "🚀 CleanBook 开发环境配置"
echo "============================"
echo ""

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📦 Python 版本: $PYTHON_VERSION"

# 检查是否在虚拟环境中
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ 已在虚拟环境中: $VIRTUAL_ENV"
else
    echo "📝 创建虚拟环境..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo "✅ 虚拟环境创建完成"
    else
        echo "✅ 虚拟环境已存在"
    fi

    echo "📝 激活虚拟环境..."
    source .venv/bin/activate
fi

echo ""
echo "🔧 安装开发依赖..."
pip install --upgrade pip
pip install -e ".[dev]"

echo ""
echo "🔧 安装 pre-commit 钩子..."
pre-commit install

echo ""
echo "🔧 验证安装..."
echo "----------------------------"
for tool in black isort flake8 pytest; do
    if command -v $tool &> /dev/null; then
        version=$($tool --version 2>&1 | head -1)
        echo "✅ $tool: $version"
    else
        echo "⚠️  $tool: 未找到"
    fi
done

echo ""
echo "🚀 运行代码质量检查..."
echo "----------------------------"

# 运行格式检查 (不修改文件)
echo ""
echo "📋 检查代码格式 (black --check)..."
black --check --diff src/ main.py tests/ 2>/dev/null || {
    echo "💡 发现格式问题，运行 'black src/ main.py tests/' 修复"
}

# 运行导入排序检查
echo ""
echo "📋 检查导入排序 (isort --check)..."
isort --check-only --diff src/ main.py tests/ 2>/dev/null || {
    echo "💡 发现导入排序问题，运行 'isort src/ main.py tests/' 修复"
}

# 运行 flake8
echo ""
echo "📋 运行代码检查 (flake8)..."
if ! flake8 src/ main.py --max-line-length=120 --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo "💡 发现 flake8 问题，请修复后重新运行验证"
fi

echo ""
echo "📋 运行运行时路径测试..."
if ! python3 -m pytest -q tests/test_runtime_paths.py; then
    echo "💡 运行时路径测试失败，请先修复 packaging / resource path 问题"
fi

echo ""
echo "✅ 开发环境配置完成！"
echo ""
echo "📖 常用命令:"
echo "  source .venv/bin/activate      # 激活虚拟环境"
echo "  black src/ main.py tests/      # 格式化代码"
echo "  isort src/ main.py tests/      # 排序导入"
echo "  flake8 src/ main.py            # 代码检查"
echo "  python3 -m pytest -q tests/test_runtime_paths.py  # 运行时路径基线"
echo "  python3 -m pytest -q           # 运行完整测试"
echo "  pre-commit run --all-files     # 运行所有预提交检查"
echo "  pre-commit run black           # 只运行 black"
echo ""
