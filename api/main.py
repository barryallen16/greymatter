"""Grey Matter storage API — key-value store over SQLite.

Replaces browser localStorage so ticks/tracker sync across devices.
stdlib only (no deps): http.server + sqlite3. Run: python main.py
"""
import json
import os
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

DB = Path(__file__).parent / "data" / "store.db"
DB.parent.mkdir(exist_ok=True)
conn = sqlite3.connect(DB, check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
conn.commit()
lock = threading.Lock()  # ponytail: single global lock — fine for 1 user, shard if traffic appears

MAX_BODY = 5 * 1024 * 1024  # tracker JSON is <100KB


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, payload=b'{"ok":true}', ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def _key(self):
        key = unquote(self.path.removeprefix("/api/store/"))
        return key if key and "/" not in key else None

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, b'{"ok":true}')
        key = self._key()
        if not key:
            return self._send(404, b'{"error":"not found"}')
        row = conn.execute("SELECT v FROM kv WHERE k=?", (key,)).fetchone()
        self._send(200, (row[0] if row else "null").encode())

    def do_PUT(self):
        key = self._key()
        if not key:
            return self._send(404, b'{"error":"not found"}')
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            # drain (bounded) so the client can finish sending, else it sees an aborted connection
            self.rfile.read(min(n, 64 * 1024 * 1024))
            self.close_connection = True
            return self._send(413, b'{"error":"too large"}')
        body = self.rfile.read(n)
        try:
            json.loads(body or b"null")
        except ValueError:
            return self._send(400, b'{"error":"invalid json"}')
        with lock:
            conn.execute(
                "INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (key, body.decode("utf-8", "replace")),
            )
            conn.commit()
        self._send(200)

    def do_DELETE(self):
        key = self._key()
        if not key:
            return self._send(404, b'{"error":"not found"}')
        with lock:
            conn.execute("DELETE FROM kv WHERE k=?", (key,))
            conn.commit()
        self._send(200)

    def log_message(self, *a):  # keep container logs quiet
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
