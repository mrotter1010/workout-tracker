#!/usr/bin/env python3
"""
Workout Tracker Local Server
Run once: python3 server.py
Then open workout-tracker.html in your browser.
Keep this terminal window open while using the app.
Data is saved to workout-data.json in the same folder as this script.
"""

import http.server
import json
import os
import sys
from pathlib import Path

PORT = int(os.environ.get("PORT", 8080))
DATA_FILE = Path(__file__).parent / "workout-data.json"

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress access logs

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
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
        if self.path == "/data":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                # Validate JSON before writing
                json.loads(body)
                DATA_FILE.write_bytes(body)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
                print(f"  Saved → {DATA_FILE}")
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_cors()
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"\n  Workout Tracker Server")
    print(f"  ─────────────────────────────")
    print(f"  Data file : {DATA_FILE}")
    print(f"  Port      : {PORT}")
    print(f"\n  Open workout-tracker.html in your browser.")
    print(f"  Press Ctrl+C to stop.\n")
    server = http.server.HTTPServer(("localhost", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        sys.exit(0)
