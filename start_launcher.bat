@echo off
chcp 936 >nul
color 0A
echo ==============================
echo   BianjiangRVC Launcher
echo ==============================
echo.
set RVC=D:\Software\RVC20240604-AMD
echo starting launcher service...
start /MIN "BianjiangRVC-Launcher" cmd.exe /c "%RVC%\Runtime\python.exe" "D:\Study\Claude\BianjiangVOC\launcher_service.py"
echo.
timeout /t 3 /nobreak >nul
echo launcher running on :18765
echo.
pause >nul
