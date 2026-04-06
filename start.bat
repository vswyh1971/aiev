@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   智能大模型安全评估系统 - 启动脚本
echo ========================================
echo.

cd /d %~dp0

set VENV_PATH=%~dp0venv_eval
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe
set PIP_EXE=%VENV_PATH%\Scripts\pip.exe

echo [1/4] 检查虚拟环境...
if not exist "%PYTHON_EXE%" (
    echo 正在创建虚拟环境...
    python -m venv venv_eval
    if errorlevel 1 (
        echo 错误: 虚拟环境创建失败
        pause
        exit /b 1
    )
)

echo [2/4] 激活虚拟环境并安装依赖包...
call %VENV_PATH%\Scripts\activate.bat
%PIP_EXE% install -r backend\requirements.txt -q

echo [3/4] 启动后端服务...
echo.
echo 系统正在启动，请稍候...
echo ========================================
echo 后端服务地址: http://localhost:8000
echo 前端界面地址: 请在浏览器中打开 frontend\index.html
echo 虚拟环境路径: %VENV_PATH%
echo ========================================
echo.
echo 默认账号信息:
echo   管理员: admin / admin123
echo   审计员: auditor / auditor123
echo   普通用户: testuser / user123
echo.
echo 按 Ctrl+C 停止服务
echo.

cd backend
%PYTHON_EXE% main.py

pause