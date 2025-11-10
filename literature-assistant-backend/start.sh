#!/bin/bash

# Literature Assistant Backend 启动脚本

echo "========================================"
echo "Literature Assistant Backend"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
if [ ! -f "venv/.deps_installed" ]; then
    echo "安装依赖包..."
    pip install -r requirements.txt
    touch venv/.deps_installed
else
    echo "依赖包已安装"
fi

# 创建必要的目录
mkdir -p data
mkdir -p uploads/documents

# 启动应用
echo ""
echo "启动应用..."
python run.py

