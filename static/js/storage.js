// Grey Matter storage — server-side SQLite via /api/store (nginx same-origin proxy).
// Drop-in replacement for the localStorage calls that used to live in each page:
//   storeGet(key) / storeSet(key, value) / storeDel(key)
// Falls back to localStorage when the API is unreachable (e.g. plain `python -m http.server`).
// First successful GET migrates any legacy localStorage value into SQLite, then removes it.

async function storeGet(key) {
  try {
    const r = await fetch('/api/store/' + encodeURIComponent(key));
    if (r.ok) {
      const v = await r.json();
      if (v !== null) return v;
    }
  } catch {}
  // API empty or unreachable — migrate legacy localStorage value once
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) return null;
    const v = JSON.parse(raw);
    storeSet(key, v).then(ok => { if (ok) localStorage.removeItem(key); });
    return v;
  } catch { return null; }
}

async function storeSet(key, value) {
  try {
    const r = await fetch('/api/store/' + encodeURIComponent(key), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(value)
    });
    if (r.ok) return true;
  } catch {}
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
  return false;
}

async function storeDel(key) {
  try { await fetch('/api/store/' + encodeURIComponent(key), { method: 'DELETE' }); } catch {}
  try { localStorage.removeItem(key); } catch {}
}
