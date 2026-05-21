@echo off
chcp 936 >nul
title BJRVC-Manager
color 0A

:MENU
cls
echo ==========================================
echo      BianjiangRVC 服务管理
echo ==========================================
echo.
echo  1. 启动服务
echo  2. 关闭服务
echo  3. 查看状态
echo  4. 退出
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto STATUS
if "%choice%"=="4" exit /b 0
goto MENU

:START
cls
echo.
echo [启动] 正在启动 BianjiangRVC 后端...
echo.
cd /d "D:\Software\RVC20240604-AMD"
set PYTHONPATH=D:\Study\agent\BianjiangVOC\backend;%PYTHONPATH%
start /MIN "BianjiangRVC" "D:\Software\RVC20240604-AMD\runtime\python.exe" "D:\Study\agent\BianjiangVOC\backend\app.py"
echo [启动] 后端已启动，首次编译 ZLUDA 约 10-30 分钟
echo [提示] 使用"一键启动.bat"可查看编译进度
echo.
pause
goto MENU

:STOP
cls
echo.
echo [关闭] 正在关闭 BianjiangRVC 后端...
echo.
taskkill /F /FI "WINDOWTITLE eq BianjiangRVC" /T 2>nul
echo   [停止] BianjiangRVC 窗口
powershell -NoProfile -Command "$ps = Get-Process -Name 'python' -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'app\\.py' }; if ($ps) { $ps | ForEach-Object { try { $_.Kill() } catch {} }; Write-Host '  [停止] Python 后端 (' $ps.Count '个)' } else { Write-Host '  [跳过] 无 Python 后端运行' }" 2>nul
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8765" 2^>nul') do taskkill /F /PID %%i 2>nul
echo   [释放] 端口 8765
echo.
echo [完成] 服务已关闭，GPU 内存已释放
echo.
pause
goto MENU

:STATUS
cls
echo.
echo [状态] 正在检查 BianjiangRVC 状态...
echo.
netstat -ano | findstr ":8765" >nul 2>&1
if %errorlevel%==0 (
    echo   [端口] 端口 8765 正在监听
    powershell -NoProfile -Command "try { $r = Invoke-RestMethod 'http://localhost:8765/health' -ErrorAction Stop; if ($r.status -eq 'ok') { Write-Host '  [状态] 后端运行正常 - 模型已就绪' } else { Write-Host '  [状态] 后端运行中 - 模型加载中...' } } catch { Write-Host '  [状态] 端口已占用但服务未响应' }" 2>nul
) else (
    echo   [状态] 后端未运行
)
echo.
pause
goto MENU
