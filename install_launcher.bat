@echo off
chcp 936 >nul
title BianjiangRVC - Install Launcher
color 0A
echo ==============================
echo   BianjiangRVC Launcher Setup
echo ==============================
echo.
echo [1/3] Checking for old launcher...
taskkill /F /FI "WINDOWTITLE eq BianjiangRVC-Launcher" /T >nul 2>&1
echo   OK
echo.
echo [2/3] Starting launcher service...
wscript.exe "D:\Study\Claude\BianjiangVOC\start_launcher.vbs"
echo   OK
echo.
echo [3/3] Waiting for launcher...
set wait=0
:CHECK
timeout /t 2 /nobreak >nul
set /a wait+=2
powershell -NoProfile -Command "try{$r=Invoke-RestMethod 'http://localhost:18765/status' -EA Stop; if($r -ne $null){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
if %errorlevel%==0 goto READY
if %wait% lss 30 goto CHECK
echo   Timeout!
pause
exit /b 1
:READY
cls
echo ==============================
echo   Launcher is running!
echo ==============================
echo.
echo   Now you can use the browser extension
echo   to start/stop the TTS backend.
echo.
echo   This launcher will auto-start when
echo   you turn on your computer.
echo.
echo ==============================
echo.
pause >nul
