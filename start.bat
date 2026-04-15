@echo off

echo ==========================================
echo   LLM Safety Evaluation System - Start Script
echo ==========================================

rem Stop previously running services
echo Stopping previous services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /f /pid %%a 2>nul

rem Wait for services to stop
echo Waiting for services to stop...
timeout /t 2 >nul

rem Start backend service
echo [1/2] Starting backend service...
start "Backend Service" cmd /k "cd backend && python start_server.py"

rem Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 >nul

rem Start frontend service
echo [2/2] Starting frontend service...
start "Frontend Service" cmd /k "python -m http.server 8000 --directory frontend"

rem Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 2 >nul

echo 
echo ==========================================
echo   System started successfully!
echo ==========================================
echo   Backend: http://localhost:8001
echo   Frontend: http://localhost:8000
echo ==========================================
