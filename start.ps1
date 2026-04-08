# 启动智能大模型安全评估系统

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  智能大模型安全评估系统 - 启动脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 启动后端服务
Write-Host "[1/2] 启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py" -WindowStyle Normal

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "[2/2] 启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 8080 --directory frontend" -WindowStyle Normal

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  系统启动完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  后端: http://localhost:8000" -ForegroundColor White
Write-Host "  前端: http://localhost:8080" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
