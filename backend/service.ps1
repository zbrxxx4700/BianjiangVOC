# 边江 TTS 服务管理脚本 (PowerShell)
param([ValidateSet("start","stop","restart","status")][string]$Action = "status")

$BackendDir = "D:\Study\agent\BianjiangVOC\backend"
$RvcRoot = "D:\Software\RVC20240604-AMD"
$Port = 8765
$LogFile = "$BackendDir\server.log"
$PidFile = "$BackendDir\server.pid"
$PythonExe = "$RvcRoot\runtime\python.exe"
$AppPy = "$BackendDir\app.py"

function Start-Svc {
    Write-Host ">> 启动边江 TTS 后端服务..." -ForegroundColor Cyan
    try {
        $r = Invoke-RestMethod "http://localhost:$Port/health" -ErrorAction Stop
        if ($r.status -eq "ok") { Write-Host "服务已在运行!" -ForegroundColor Yellow; return }
    } catch {}
    
    if (Test-Path $LogFile) { Remove-Item $LogFile }
    
    $env:PYTHONPATH = "$BackendDir;$env:PYTHONPATH"
    $p = Start-Process -FilePath $PythonExe -ArgumentList $AppPy -WorkingDirectory $RvcRoot -NoNewWindow -PassThru -RedirectStandardOutput $LogFile -RedirectStandardError "${LogFile}.err"
    $p.Id | Out-File $PidFile -Encoding ascii
    
    Write-Host "服务已启动 (PID: $($p.Id))" -ForegroundColor Green
    Write-Host "首次启动需编译 ZLUDA 内核，约 10-30 分钟" -ForegroundColor Yellow
}

function Stop-Svc {
    Write-Host ">> 关闭边江 TTS 服务..." -ForegroundColor Cyan
    if (Test-Path $PidFile) {
        $pid = (Get-Content $PidFile).Trim()
        try { (Get-Process -Id $pid -ErrorAction Stop).Kill(); Write-Host "已终止 PID: $pid" -ForegroundColor Green }
        catch { Write-Host "进程 $pid 已不存在" -ForegroundColor Yellow }
        Remove-Item $PidFile -ErrorAction SilentlyContinue
    }
    # 补杀
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "app.py" } | ForEach-Object { $_.Kill() }
    Start-Sleep 1
    Write-Host "服务已关闭，GPU 内存已释放" -ForegroundColor Green
}

function Get-Status {
    Write-Host ">> 服务状态" -ForegroundColor Cyan
    $portCheck = netstat -ano | Select-String ":$Port"
    if ($portCheck) {
        Write-Host "[在线] 端口 $Port 正在监听" -ForegroundColor Green
        try {
            $r = Invoke-RestMethod "http://localhost:$Port/health" -ErrorAction Stop
            Write-Host "[状态] 引擎就绪" -ForegroundColor Green
            Write-Host "  模型: $($r.model.model)" -ForegroundColor Gray
            Write-Host "  设备: $($r.model.device)" -ForegroundColor Gray
            $voices = $r.available_voices -join ", "
            Write-Host "  可用声源: $voices" -ForegroundColor Gray
        } catch {
            Write-Host "[状态] 引擎加载中 (ZLUDA 编译中...)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[离线] 服务未运行" -ForegroundColor Red
    }
}

switch ($Action) {
    "start"   { Start-Svc }
    "stop"    { Stop-Svc }
    "restart" { Stop-Svc; Start-Sleep 2; Start-Svc }
    "status"  { Get-Status }
}
