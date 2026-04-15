# 智能大模型安全评估系统 - 启动脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  智能大模型安全评估系统 - 启动脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 停止之前可能运行的服务
Write-Host "停止之前可能运行的服务..." -ForegroundColor Yellow
try {
    # 停止端口8001上的进程（后端）
    $backendProcesses = netstat -ano | findstr :8001
    if ($backendProcesses) {
        $pid = $backendProcesses -split '\s+' | Select-Object -Last 1
        Write-Host "停止后端进程 PID: $pid" -ForegroundColor Yellow
        taskkill /F /PID $pid -ErrorAction SilentlyContinue
    }
    
    # 停止端口8000上的进程（前端）
    $frontendProcesses = netstat -ano | findstr :8000
    if ($frontendProcesses) {
        $pids = $frontendProcesses -split '\n' | ForEach-Object { $_ -split '\s+' | Select-Object -Last 1 }
        $uniquePids = $pids | Select-Object -Unique
        foreach ($pid in $uniquePids) {
            if ($pid -match '^\d+$') {
                Write-Host "停止前端进程 PID: $pid" -ForegroundColor Yellow
                taskkill /F /PID $pid -ErrorAction SilentlyContinue
            }
        }
    }
} catch {
    Write-Host "停止服务时出错: $($_.Exception.Message)" -ForegroundColor Red
}

# 等待服务停止
Start-Sleep -Seconds 2

# 启动后端服务
Write-Host "[1/2] 启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python start_server.py" -WindowStyle Normal

# 等待后端启动
Start-Sleep -Seconds 5

# 启动前端服务
Write-Host "[2/2] 启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 8000 --directory frontend" -WindowStyle Normal

# 等待前端启动
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  系统启动完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  后端: http://localhost:8001" -ForegroundColor White
Write-Host "  前端: http://localhost:8000" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
