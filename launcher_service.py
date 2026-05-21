"""BianjiangRVC Launcher - HTTP service for extension start/stop control"""
import json, os, shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = 18765

def find_bat(keyword):
    for f in os.listdir(BASE):
        if keyword in f and f.endswith('.bat'):
            return os.path.join(BASE, f)
    return None

class Handler(BaseHTTPRequestHandler):
    def _json(self, data):
        self.send_response(200)
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
            try:
                import urllib.request
                urllib.request.urlopen('http://localhost:8765/health', timeout=2)
                self._json({'running': True})
            except:
                self._json({'running': False})
        else:
            self._json({'error': 'not found'})

    def do_POST(self):
        if self.path == '/start':
            bat = find_bat('启动')
            if bat:
                subprocess.Popen(['cmd.exe', '/c', 'start', '', bat], shell=True)
            self._json({'status': 'ok'})
        elif self.path == '/stop':
            try:
                import urllib.request
                urllib.request.urlopen('http://localhost:8765/shutdown', method='POST', timeout=3)
            except:
                bat = find_bat('关闭')
                if bat:
                    subprocess.Popen(['cmd.exe', '/c', 'start', '', bat], shell=True)
            self._json({'status': 'ok'})
        else:
            self._json({'error': 'not found'})

    def log_message(self, fmt, *args):
        pass

if __name__ == '__main__':
    # One-time startup registration
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
