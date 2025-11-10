@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Literature Assistant Backend
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
if not exist "venv\.deps_installed" (
    echo 安装依赖包...
    pip install -r requirements.txt
    type nul > venv\.deps_installed
) else (
    echo 依赖包已安装
)

REM 创建必要的目录
if not exist "data\" mkdir data
if not exist "uploads\documents\" mkdir uploads\documents

REM 启动应用
echo.
echo 启动应用...
python run.py

pause

