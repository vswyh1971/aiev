@echo off

echo ==========================================
echo   智能大模型安全评估系统 - 启动脚本
echo ==========================================

rem 停止之前可能运行的服务
echo 停止之前可能运行的服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /f /pid %%a 2>nul

rem 等待服务停止
timeout /t 2 >nul

rem 启动后端服务
echo [1/2] 启动后端服务...
start "后端服务" cmd /k "cd backend && python start_server.py"

rem 等待后端启动
timeout /t 5 >nul

rem 启动前端服务
echo [2/2] 启动前端服务...
start "前端服务" cmd /k "python -m http.server 8000 --directory frontend"

rem 等待前端启动
timeout /t 2 >nul

echo 
echo ==========================================
echo   系统启动完成！
echo ==========================================
echo   后端: http://localhost:8001
echo   前端: http://localhost:8000
echo ==========================================
