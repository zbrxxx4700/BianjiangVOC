@echo off
chcp 936 >nul
echo ==============================
echo   BianjiangRVC Native Host Setup
echo ==============================
echo.

set HOSTNAME=com.bianjiang.rvc
set SCRIPT_DIR=%~dp0

:: Try Edge first, then Chrome
set EDGE_DIR=%LOCALAPPDATA%\Microsoft\Edge\User Data\NativeMessagingHosts
set CHROME_DIR=%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts

if exist "%EDGE_DIR%" (
    copy /Y "%SCRIPT_DIR%%HOSTNAME%.json" "%EDGE_DIR%\" >nul
    echo [OK] Edge native host installed
) else (
    echo [SKIP] Edge not found
)

if exist "%CHROME_DIR%" (
    copy /Y "%SCRIPT_DIR%%HOSTNAME%.json" "%CHROME_DIR%\" >nul
    echo [OK] Chrome native host installed
) else (
    echo [SKIP] Chrome not found
)

echo.
echo Setup complete. Restart browser to apply.
echo.
pause
