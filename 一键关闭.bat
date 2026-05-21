@echo off
chcp 936 >nul
color 0C

echo ==============================
echo   BianjiangRVC - 一键关闭
echo ==============================
echo.
echo 正在关闭，请稍候...
echo.

:: 第1步：杀 Python 进程
echo [1/4] 停止 Python 后端...
powershell -NoProfile -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'app' } | ForEach-Object { $_.Kill() }"
echo.

:: 第2步：杀端口 8765
echo [2/4] 释放端口 8765...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8765"') do (
    taskkill /F /PID %%i >nul 2>&1
)
echo.

:: 第3步：杀 GPU 进程
echo [3/4] 释放 GPU 内存...
powershell -NoProfile -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'zluda|torch|rvc' } | ForEach-Object { $_.Kill() }"
echo.

:: 第4步：清理临时文件
echo [4/4] 清理临时文件...
if exist "D:\Software\RVC20240604-AMD\TEMP" del /Q "D:\Software\RVC20240604-AMD\TEMP\*" 2>nul

cls
echo ==============================
echo      全部关闭完成!
echo ==============================
echo.
echo   Python 后端已停止
echo   端口 8765 已释放
echo   GPU 内存已释放
echo.
echo ==============================

echo.
echo 按任意键退出...
pause >nul
