@echo off

echo ==========================================
echo   LLM Safety Evaluation System - Start Script
echo ==========================================

rem Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

rem Stop previously running services
echo Stopping previous services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do taskkill /f /pid %%a 2>nul

rem Wait for services to stop
echo Waiting for services to stop...
timeout /t 2 >nul

rem Start backend service
echo [1/2] Starting backend service...
start "Backend Service" cmd /k "cd backend && python main.py"

rem Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 >nul

rem Start frontend service
echo [2/2] Starting frontend service...
start "Frontend Service" cmd /k "python -m http.server 8080 --directory frontend"

rem Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 2 >nul

echo 
echo ==========================================
echo   System started successfully!
echo ==========================================
echo   Frontend: http://localhost:8080
echo   Backend: http://localhost:8000
echo ==========================================
echo.
echo Press any key to exit (services will keep running)...
pause >nul
