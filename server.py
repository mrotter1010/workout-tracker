#!/usr/bin/env python3
#!/usr/bin/env python3
import http.server
import json
import os
import sys
from pathlib import Path

PORT = int(os.environ.get("PORT", 10000))
DATA_FILE = Path(__file__).parent / "workout-data.json"
APP_KEY = os.environ.get("APP_KEY", "")

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  {self.address_string()} {args[0]}", flush=True)

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-App-Key")

    def check_auth(self):
        if not APP_KEY:
            return True
        return self.headers.get("X-App-Key", "") == APP_KEY

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/" or path == "/app":
            if not DATA_FILE.parent.joinpath("workout-tracker.html").exists():
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"workout-tracker.html not found")
                return
            content = DATA_FILE.parent.joinpath("workout-tracker.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.send_cors()
            self.end_headers()
            self.wfile.write(content)
        elif path == "/data":
            if not self.check_auth():
                self.send_response(401)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors()
            self.end_headers()
            if DATA_FILE.exists():
                self.wfile.write(DATA_FILE.read_bytes())
            else:
                self.wfile.write(b"{}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/data":
            if not self.check_auth():
                self.send_response(401)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                json.loads(body)
                DATA_FILE.write_bytes(body)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
                print(f"  Saved → {DATA_FILE} ({len(body)} bytes)", flush=True)
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_cors()
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Bind first, print after — ensures port is open before any output
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Workout Tracker running on 0.0.0.0:{PORT}", flush=True)
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
