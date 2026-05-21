"""BianjiangRVC Launcher - silent backend control"""
import json, os, shutil, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = 18765
RVC_PY = r'D:\Software\RVC20240604-AMD\runtime\python.exe'
BACKEND_PY = os.path.join(BASE, 'backend', 'app.py')
RVC_DIR = r'D:\Software\RVC20240604-AMD'
BACKEND_URL = 'http://localhost:8765/health'

def backend_running():
    try:
        import urllib.request
        return urllib.request.urlopen(BACKEND_URL, timeout=2).status == 200
    except:
        return False

class Handler(BaseHTTPRequestHandler):
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        if self.path == '/status':
            self._json({'running': backend_running()})
        else:
            self._json({'error': 'not found'}, 404)

    def do_POST(self):
        if self.path == '/start':
            # Kill any process on port 8765 first
            import subprocess as _sp
            _sp.run('for /f "tokens=5" %i in ('netstat -ano ^| findstr ":8765"') do taskkill /F /PID %i 2>nul', shell=True)
            import time as _t; _t.sleep(1)
            if backend_running():
                self._json({'status': 'ok', 'message': 'already running'})
                return
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.join(BASE, 'backend') + ';' + env.get('PYTHONPATH', '')
            subprocess.Popen(
                [RVC_PY, BACKEND_PY],
                cwd=RVC_DIR,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self._json({'status': 'ok'})
        elif self.path == '/stop':
            try:
                import urllib.request
                req = urllib.request.Request('http://localhost:8765/shutdown', method='POST')
                urllib.request.urlopen(req, timeout=3)
            except:
                pass
            self._json({'status': 'ok'})
        else:
            self._json({'error': 'not found'}, 404)

    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    # Register startup
    startup = os.path.join(os.environ['APPDATA'],
        'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
        'BianjiangRVC_Launcher.vbs')
    vbs = os.path.join(BASE, 'start_launcher.vbs')
    if os.path.exists(vbs) and not os.path.exists(startup):
        try:
            shutil.copy2(vbs, startup)
        except:
            pass
    HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
