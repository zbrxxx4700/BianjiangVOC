@echo off
title 边江TTS-启动
echo 正在启动边江 TTS 后端服务...
cd /d "D:\Software\RVC20240604-AMD"
set PYTHONPATH=D:\Study\Claude\BianjiangVOC\backend;%PYTHONPATH%
start /MIN "BianjiangTTS_Backend" "D:\Software\RVC20240604-AMD\runtime\python.exe" "D:\Study\Claude\BianjiangVOC\backend\app.py"
echo 服务已启动!
pause
