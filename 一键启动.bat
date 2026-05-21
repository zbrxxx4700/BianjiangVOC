@echo off
chcp 936 >nul
title BianjiangRVC - 一键启动
color 0A

echo ==============================
echo   BianjiangRVC - 一键启动
echo ==============================
echo.

set /a STEP=0
set /a TOTAL=5

:: ======== 第 1 步：检查端口 ========
set /a STEP+=1
echo [%STEP%/%TOTAL%] 检查端口 8765 状态...
echo.
netstat -ano | findstr ":8765" | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo   [提示] 端口 8765 已被占用，请先运行一键关闭
    echo.
    pause
    exit /b 1
)
echo   [确认] 端口 8765 可用
echo.

:: ======== 第 2 步：设置环境 ========
set /a STEP+=1
echo [%STEP%/%TOTAL%] 设置运行环境...
echo.
cd /d D:\Software\RVC20240604-AMD
set PYTHONPATH=D:\Study\Claude\BianjiangVOC\backend;%PYTHONPATH%
echo   [路径] RVC 根目录: D:\Software\RVC20240604-AMD
echo   [环境] PYTHONPATH 已设置
echo.

:: ======== 第 3 步：启动后端 ========
set /a STEP+=1
echo [%STEP%/%TOTAL%] 启动 Python 后端...
echo.
start /MIN "BianjiangRVC" "D:\Software\RVC20240604-AMD\runtime\python.exe" "D:\Study\Claude\BianjiangVOC\backend\app.py"
echo   [启动] 后端已启动，等待就绪...
echo.

:: ======== 第 4 步：等待 ZLUDA 编译 ========
set /a STEP+=1
echo [%STEP%/%TOTAL%] 等待 ZLUDA 内核编译...
echo.
echo   首次编译约 10-30 分钟，请耐心等待
echo.

set wait_sec=0

:CHECK_LOOP
timeout /t 5 /nobreak >nul
set /a wait_sec+=5

powershell -NoProfile -Command "try { $r = Invoke-RestMethod 'http://localhost:8765/health' -ErrorAction Stop; if ($r.status -eq 'ok') { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 goto SUCCESS

set /a min=%wait_sec%/60
set /a sec=%wait_sec%-%min%*60
if %wait_sec% lss 60 (
    echo   [等待] %wait_sec%秒 - 正在编译 ZLUDA 内核...
) else (
    echo   [等待] %min%分%sec%秒 - 正在编译 ZLUDA 内核...
)

if %wait_sec% geq 1800 goto TIMEOUT
goto CHECK_LOOP

:TIMEOUT
echo.
echo   [超时] 等待超过 30 分钟，启动失败
echo   [日志] 请查看: D:\Study\Claude\BianjiangVOC\backend\server.log
echo.
pause
exit /b 1

:: ======== 第 5 步：完成 ========
:SUCCESS
set /a STEP+=1
cls
echo ==============================
echo      启动成功!
echo ==============================
echo.
echo   BianjiangRVC 后端已经就绪
echo.
echo   > 端口: 8765
echo   > 模型: BianjiangRVC V2
echo   > 源声音: Yunxi / Hyunsu
echo   > 设备: AMD GPU (ZLUDA)
echo.
echo   ??? 现在可以加载浏览器扩展使用了
echo   选中文字 > 点击浮窗 > 边江朗读
echo.
echo ==============================
echo.
echo 按任意键关闭本窗口...
pause >nul
exit /b 0
