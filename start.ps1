# 启动智能大模型安全评估系统

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  智能大模型安全评估系统 - 启动脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查并创建虚拟环境
Write-Host "检查虚拟环境..." -ForegroundColor Yellow
$venvPython = ".\venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "虚拟环境未找到，正在创建..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "安装依赖..." -ForegroundColor Yellow
    & .\venv\Scripts\pip.exe install -r backend\requirements.txt
}

# 停止现有服务
Write-Host "停止现有服务..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8000,8080 -ErrorAction SilentlyContinue | ForEach-Object { 
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue 
}
Start-Sleep -Seconds 2

# 启动后端服务（使用虚拟环境的Python）
Write-Host "[1/2] 启动后端服务..." -ForegroundColor Yellow
$backendCmd = "cd backend; ..\venv\Scripts\python.exe main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 等待后端启动
Start-Sleep -Seconds 5

# 启动前端服务
Write-Host "[2/2] 启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 8080 --directory frontend" -WindowStyle Normal

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  系统启动完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  前端: http://localhost:8080" -ForegroundColor White
Write-Host "  后端: http://localhost:8000" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
