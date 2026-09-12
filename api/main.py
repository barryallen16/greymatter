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
from urllib.parse import parse_qs, unquote

DB = Path(__file__).parent / "data" / "store.db"
DB.parent.mkdir(exist_ok=True)
FILES = Path(__file__).parent / "data" / "files"
FILES.mkdir(parents=True, exist_ok=True)
FILE_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE = 10 * 1024 * 1024  # resumes are <1MB; 10MB headroom, nginx client_max_body_size must exceed this
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

    def _fname(self):
        p = self.path.split("?", 1)[0]
        if not p.startswith("/api/files/"):
            return None
        name = Path(unquote(p.removeprefix("/api/files/"))).name.strip()
        if not name or len(name) > 120 or name.startswith("."):
            return None
        if any(c in name for c in "'\"<>"):  # keep names onclick-safe for the tracker UI
            return None
        if Path(name).suffix.lower() not in FILE_TYPES:
            return None
        return name

    def _dl_name(self, name):
        """Friendly download filename from ?as= (falls back to the stored name).

        Same safety rules as stored names, plus the extension must match the
        file's own type — an invalid alias is ignored, never an error, so
        downloads keep working on browsers that ignore the `download` attr.
        """
        q = self.path.split("?", 1)[1] if "?" in self.path else ""
        try:
            alias = (parse_qs(q).get("as", [""])[0] or "").strip()
        except ValueError:
            return name
        if not alias or len(alias) > 120 or alias.startswith("."):
            return name
        # ponytail: ASCII whitelist — blocks CR/LF header injection; non-Latin
        # names fall back to the slug, add RFC 5987 encoding if that matters
        if any(not (c.isascii() and (c.isalnum() or c in "._-")) for c in alias):
            return name
        suf = Path(alias).suffix.lower()
        if suf not in FILE_TYPES or suf != Path(name).suffix.lower():
            return name
        return alias

    def _send_file(self, name, download=False, as_name=None):
        f = FILES / name
        if not f.is_file():
            return self._send(404, b'{"error":"not found"}')
        data = f.read_bytes()
        ctype = FILE_TYPES[Path(name).suffix.lower()]
        disp = ("attachment" if download else "inline") + f'; filename="{as_name or name}"'
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Disposition", disp)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, b'{"ok":true}')
        if self.path.split("?", 1)[0] in ("/api/files", "/api/files/"):
            items = sorted(
                ({"name": p.name, "size": p.stat().st_size} for p in FILES.iterdir()
                 if p.is_file() and p.suffix.lower() in FILE_TYPES),
                key=lambda d: d["name"].lower(),
            )
            return self._send(200, json.dumps(items).encode())
        name = self._fname()
        if name is not None:
            return self._send_file(name, download="download" in (self.path.split("?", 1)[1] if "?" in self.path else ""), as_name=self._dl_name(name))
        key = self._key()
        if not key:
            return self._send(404, b'{"error":"not found"}')
        row = conn.execute("SELECT v FROM kv WHERE k=?", (key,)).fetchone()
        self._send(200, (row[0] if row else "null").encode())

    def do_PUT(self):
        name = self._fname()
        if name is not None:  # raw file bytes — no multipart lib needed
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_FILE or n <= 0:
                self.close_connection = True
                return self._send(413 if n > MAX_FILE else 400, b'{"error":"empty or too large (max 10MB)"}')
            (FILES / name).write_bytes(self.rfile.read(n))
            return self._send(200)
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
        name = self._fname()
        if name is not None:
            try:
                (FILES / name).unlink()
            except FileNotFoundError:
                pass
            return self._send(200)
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
