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

// Merge rows edited in the browser onto a freshly re-read server array.
// `base` = what this page loaded, `local` = what the user changed since,
// `fresh` = what the server holds now. A full-array PUT from a stale page would
// silently delete rows added by a push (tracker_push.py / job-filter publish.py)
// and revert any field edited elsewhere, so only fields this page actually touched
// are applied — plus rows added or deleted here.
const EDIT_KEYS = ['status', 'link', 'type', 'followup', 'notes', 'created', 'jd', 'files'];

function mergeRows(base, local, fresh) {
  const out = Array.isArray(fresh) ? fresh.slice() : [];
  const was = new Map((base || []).map(a => [a.id, a]));
  const now = new Map((local || []).map(a => [a.id, a]));
  for (const [id, a] of now) {
    const server = out.find(x => x.id === id);
    if (!server) { out.push({ ...a }); continue; }            // added on this device
    const old = was.get(id);
    for (const k of EDIT_KEYS)
      if (!old || JSON.stringify(a[k]) !== JSON.stringify(old[k])) server[k] = a[k];
  }
  for (const [id] of was)                                     // deleted here
    if (!now.has(id)) {
      const i = out.findIndex(x => x.id === id);
      if (i > -1) out.splice(i, 1);
    }
  return out;
}

async function storeDel(key) {
  try { await fetch('/api/store/' + encodeURIComponent(key), { method: 'DELETE' }); } catch {}
  try { localStorage.removeItem(key); } catch {}
}
