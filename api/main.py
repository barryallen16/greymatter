"""Grey Matter storage API — key-value store over SQLite + roadmap CRUD.

Replaces browser localStorage so ticks/tracker sync across devices.
stdlib only (no deps): http.server + sqlite3. Run: python main.py
"""
import json
import os
import sqlite3
import threading
import uuid
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
MAX_FILE = 10 * 1024 * 1024
conn = sqlite3.connect(DB, check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
conn.execute("CREATE TABLE IF NOT EXISTS roadmaps (id TEXT PRIMARY KEY, content TEXT NOT NULL)")
conn.commit()
lock = threading.Lock()

MAX_BODY = 5 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, payload=b'{"ok":true}', ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def _read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            self.rfile.read(min(n, 64 * 1024 * 1024))
            self.close_connection = True
            return None, 413
        raw = self.rfile.read(n) if n > 0 else b""
        if not raw:
            return {}, 200
        try:
            return json.loads(raw.decode("utf-8", "replace")), 200
        except ValueError:
            return None, 400

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
        if any(c in name for c in "'\"<>"):
            return None
        if Path(name).suffix.lower() not in FILE_TYPES:
            return None
        return name

    def _dl_name(self, name):
        q = self.path.split("?", 1)[1] if "?" in self.path else ""
        try:
            alias = (parse_qs(q).get("as", [""])[0] or "").strip()
        except ValueError:
            return name
        if not alias or len(alias) > 120 or alias.startswith("."):
            return name
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

    def _rm_parts(self):
        p = self.path.split("?", 1)[0]
        if not p.startswith("/api/roadmaps"):
            return None
        rest = p[len("/api/roadmaps"):].strip("/")
        return rest.split("/") if rest else []

    def _slug(self, s):
        out = "".join(c.lower() if c.isalnum() else "-" for c in (s or ""))
        while "--" in out:
            out = out.replace("--", "-")
        return out.strip("-") or "roadmap"

    def _normalize_roadmap(self, body, rid):
        content = dict(body or {})
        content.setdefault("id", rid)
        # accept flat tasks -> single phase
        if "phases" not in content and "tasks" in content:
            tasks = []
            for t in content.get("tasks", []):
                if isinstance(t, str):
                    tasks.append({"id": uuid.uuid4().hex[:8], "html": t})
                else:
                    tasks.append({"id": t.get("id") or uuid.uuid4().hex[:8],
                                  "html": t.get("html") or t.get("text") or ""})
            content["phases"] = [{"name": content.get("title", "Tasks"), "badge": "",
                                  "color": "emerald", "count": len(tasks), "tasks": tasks}]
            del content["tasks"]
        # ensure phases exist
        content.setdefault("phases", [])
        for ph in content["phases"]:
            ph.setdefault("tasks", [])
            for t in ph["tasks"]:
                t.setdefault("id", uuid.uuid4().hex[:8])
                t.setdefault("html", t.get("text", ""))
        if content.get("mvp") and isinstance(content["mvp"], dict):
            content["mvp"].setdefault("id", uuid.uuid4().hex[:8])
            content["mvp"].setdefault("html", content["mvp"].get("text", ""))
        return content

    def _task_count(self, content):
        n = sum(len(ph.get("tasks", [])) for ph in content.get("phases", []))
        if content.get("mvp"):
            n += 1
        return n

    def do_GET(self):
        parts = self._rm_parts()
        if parts is not None:
            if parts == []:
                rows = conn.execute("SELECT id, content FROM roadmaps").fetchall()
                items = []
                for rid, content in rows:
                    try:
                        c = json.loads(content)
                    except ValueError:
                        c = {}
                    items.append({"id": rid, "title": c.get("title", ""),
                                  "date": c.get("date", ""), "task_count": self._task_count(c)})
                return self._send(200, json.dumps(items).encode())
            rid = parts[0]
            row = conn.execute("SELECT content FROM roadmaps WHERE id=?", (rid,)).fetchone()
            if not row:
                return self._send(404, b'{"error":"not found"}')
            try:
                content = json.loads(row[0])
            except ValueError:
                content = {}
            trow = conn.execute("SELECT v FROM kv WHERE k=?", (f"roadmap:{rid}:ticks",)).fetchone()
            ticks = {}
            if trow:
                try:
                    ticks = json.loads(trow[0])
                except ValueError:
                    ticks = {}
            return self._send(200, json.dumps({"id": rid, "ticks": ticks, **content}).encode())

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

    def do_POST(self):
        parts = self._rm_parts()
        if parts is not None:
            if parts == []:
                body, code = self._read_body()
                if code != 200 or body is None:
                    return self._send(code, b'{"error":"invalid json"}')
                title = body.get("title") or "Roadmap"
                rid = body.get("id") or (body.get("date", "") + "-" + self._slug(title)).strip("-")
                if not rid:
                    rid = uuid.uuid4().hex[:8]
                # uniqueness
                base = rid
                i = 2
                while conn.execute("SELECT 1 FROM roadmaps WHERE id=?", (rid,)).fetchone():
                    rid = f"{base}-{i}"
                    i += 1
                content = self._normalize_roadmap(body, rid)
                with lock:
                    conn.execute("INSERT INTO roadmaps(id,content) VALUES(?,?)", (rid, json.dumps(content)))
                    conn.commit()
                return self._send(200, json.dumps({"id": rid, "url": f"/roadmaps/roadmap.html?id={rid}"}).encode())

            rid = parts[0]
            if len(parts) >= 2 and parts[1] == "phases":
                body, code = self._read_body()
                if code != 200 or body is None:
                    return self._send(code, b'{"error":"invalid json"}')
                row = conn.execute("SELECT content FROM roadmaps WHERE id=?", (rid,)).fetchone()
                if not row:
                    return self._send(404, b'{"error":"not found"}')
                content = json.loads(row[0])
                name = (body.get("name") or "").strip()
                if not name:
                    return self._send(400, b'{"error":"name required"}')
                if any(ph.get("name") == name for ph in content.get("phases", [])):
                    return self._send(409, b'{"error":"phase exists"}')
                phase = {"name": name, "badge": body.get("badge", ""),
                         "color": body.get("color", "emerald"), "tasks": []}
                content.setdefault("phases", []).append(phase)
                with lock:
                    conn.execute("UPDATE roadmaps SET content=? WHERE id=?", (json.dumps(content), rid))
                    conn.commit()
                return self._send(200, json.dumps({"name": name}).encode())

            if len(parts) >= 2 and parts[1] == "tasks":
                body, code = self._read_body()
                if code != 200 or body is None:
                    return self._send(code, b'{"error":"invalid json"}')
                row = conn.execute("SELECT content FROM roadmaps WHERE id=?", (rid,)).fetchone()
                if not row:
                    return self._send(404, b'{"error":"not found"}')
                content = json.loads(row[0])
                phase_name = body.get("phase")
                phase = None
                for ph in content.get("phases", []):
                    if phase_name and ph.get("name") == phase_name:
                        phase = ph
                        break
                if phase is None:
                    if content.get("phases"):
                        phase = content["phases"][0]
                    else:
                        phase = {"name": phase_name or "Tasks", "badge": "", "color": "emerald", "tasks": []}
                        content.setdefault("phases", []).append(phase)
                tid = body.get("id") or uuid.uuid4().hex[:8]
                html = body.get("html")
                if html is None:
                    html = body.get("text", "")
                phase["tasks"].append({"id": tid, "html": html})
                phase["count"] = len(phase["tasks"])
                with lock:
                    conn.execute("UPDATE roadmaps SET content=? WHERE id=?", (json.dumps(content), rid))
                    conn.commit()
                return self._send(200, json.dumps({"id": tid}).encode())

            if len(parts) >= 2 and parts[1] == "ticks":
                body, code = self._read_body()
                if code != 200 or body is None:
                    return self._send(code, b'{"error":"invalid json"}')
                ticks = body.get("ticks", body)
                if not isinstance(ticks, dict):
                    return self._send(400, b'{"error":"ticks must be object"}')
                with lock:
                    conn.execute("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                                 (f"roadmap:{rid}:ticks", json.dumps(ticks)))
                    conn.commit()
                return self._send(200)

            return self._send(404, b'{"error":"not found"}')

        # files upload via PUT only; POST not used
        return self._send(404, b'{"error":"not found"}')

    def do_PUT(self):
        parts = self._rm_parts()
        if parts is not None:
            if len(parts) == 1:
                rid = parts[0]
                body, code = self._read_body()
                if code != 200 or body is None:
                    return self._send(code, b'{"error":"invalid json"}')
                if not conn.execute("SELECT 1 FROM roadmaps WHERE id=?", (rid,)).fetchone():
                    return self._send(404, b'{"error":"not found"}')
                content = self._normalize_roadmap(body, rid)
                with lock:
                    conn.execute("UPDATE roadmaps SET content=? WHERE id=?", (json.dumps(content), rid))
                    conn.commit()
                return self._send(200)
            if len(parts) == 2 and parts[1] == "ticks":
                body, code = self._read_body()
                if code != 200 or body is None:
                    return self._send(code, b'{"error":"invalid json"}')
                ticks = body.get("ticks", body)
                if not isinstance(ticks, dict):
                    return self._send(400, b'{"error":"ticks must be object"}')
                rid = parts[0]
                with lock:
                    conn.execute("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                                 (f"roadmap:{rid}:ticks", json.dumps(ticks)))
                    conn.commit()
                return self._send(200)
            return self._send(404, b'{"error":"not found"}')

        name = self._fname()
        if name is not None:
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
        parts = self._rm_parts()
        if parts is not None:
            if len(parts) == 1:
                rid = parts[0]
                with lock:
                    conn.execute("DELETE FROM roadmaps WHERE id=?", (rid,))
                    conn.execute("DELETE FROM kv WHERE k=?", (f"roadmap:{rid}:ticks",))
                    conn.commit()
                return self._send(200)
            if len(parts) == 3 and parts[1] == "phases":
                rid = parts[0]
                pname = unquote(parts[2])
                row = conn.execute("SELECT content FROM roadmaps WHERE id=?", (rid,)).fetchone()
                if not row:
                    return self._send(404, b'{"error":"not found"}')
                content = json.loads(row[0])
                before = len(content.get("phases", []))
                content["phases"] = [ph for ph in content.get("phases", []) if ph.get("name") != pname]
                found = len(content["phases"]) != before
                with lock:
                    conn.execute("UPDATE roadmaps SET content=? WHERE id=?", (json.dumps(content), rid))
                    conn.commit()
                return self._send(200, json.dumps({"deleted": found}).encode())

            if len(parts) == 3 and parts[1] == "tasks":
                rid = parts[0]
                tid = parts[2]
                row = conn.execute("SELECT content FROM roadmaps WHERE id=?", (rid,)).fetchone()
                if not row:
                    return self._send(404, b'{"error":"not found"}')
                content = json.loads(row[0])
                found = False
                for ph in content.get("phases", []):
                    before = len(ph.get("tasks", []))
                    ph["tasks"] = [t for t in ph.get("tasks", []) if t.get("id") != tid]
                    if len(ph["tasks"]) != before:
                        found = True
                    ph["count"] = len(ph["tasks"])
                if content.get("mvp") and content["mvp"].get("id") == tid:
                    del content["mvp"]
                    found = True
                with lock:
                    conn.execute("UPDATE roadmaps SET content=? WHERE id=?", (json.dumps(content), rid))
                    conn.commit()
                return self._send(200, json.dumps({"deleted": found}).encode())
            return self._send(404, b'{"error":"not found"}')

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

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
