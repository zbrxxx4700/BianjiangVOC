"""Generate batch files with proper GBK encoding"""
import os

S = r'D:\Study\Claude\BianjiangVOC'

# start_launcher.bat
close = """@echo off
chcp 936 >nul
color 0A
echo ==============================
echo   BianjiangRVC Launcher
echo ==============================
echo.
echo starting launcher service...
start /MIN "BianjiangRVC-Launcher" cmd.exe /c "D:\Software\RVC20240604-AMD\runtime\python.exe" "D:\Study\Claude\BianjiangVOC\launcher_service.py"
echo.
timeout /t 3 /nobreak >nul
echo launcher running on :18765
echo.
pause >nul
"""

path = os.path.join(S, 'start_launcher.bat')
with open(path, 'wb') as f:
    f.write(close.replace('\n', '\r\n').encode('gbk'))
print(f'Written: {path}')

# Verify no bad bytes
with open(path, 'rb') as f:
    data = f.read()
bad = 0
for b in [0x0b, 0x07]:
    if bytes([b]) in data:
        print(f'  BAD: byte {hex(b)}')
        bad += 1
# Check no \r without \\ before runtime
idx = data.find(b'runtime')
if idx > 0:
    before = data[idx-1]
    print(f'  Byte before runtime: {hex(before)}')
    if before != 0x5c:  # not backslash
        print(f'  WARNING: expected 0x5c (backslash), got {hex(before)}')
        bad += 1
if bad == 0:
    print(f'  CLEAN')
