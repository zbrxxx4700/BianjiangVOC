"""Native messaging host for BianjiangRVC"""
import sys, json, struct, os, subprocess, time

BASE = r"D:\Study\Claude\BianjiangVOC"
BAT_START = os.path.join(BASE, "一键启动.bat")
BAT_STOP = os.path.join(BASE, "一键关闭.bat")
HEALTH_URL = "http://localhost:8765/health"

def send_message(msg):
    data = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("I", len(data)))
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

def read_message():
    raw = sys.stdin.buffer.read(4)
    if not raw or len(raw) < 4:
        return None
    length = struct.unpack("I", raw)[0]
    return json.loads(sys.stdin.buffer.read(length).decode("utf-8"))

def check_backend():
    try:
        import urllib.request
        r = urllib.request.urlopen(HEALTH_URL, timeout=3)
        return r.status == 200
    except:
        return False

def cmd_start():
    if check_backend():
        return {"status": "ok", "message": "already running"}
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", "", BAT_START], shell=True)
        return {"status": "ok", "message": "starting..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_stop():
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", "", BAT_STOP], shell=True)
        return {"status": "ok", "message": "stopping..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cmd_status():
    running = check_backend()
    return {"status": "ok", "running": running}

if __name__ == "__main__":
    while True:
        msg = read_message()
        if msg is None:
            break
        cmd = msg.get("command", "")
        if cmd == "start":
            resp = cmd_start()
        elif cmd == "stop":
            resp = cmd_stop()
        elif cmd == "status":
            resp = cmd_status()
        else:
            resp = {"status": "error", "message": f"unknown: {cmd}"}
        send_message(resp)
        if cmd == "stop":
            break
