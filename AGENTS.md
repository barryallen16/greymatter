# AGENTS.md — Grey Matter / job-search

Static site + tiny stdlib Python API + resume skill. Read this before doing anything.

## Layout

- `tracker/` — job application tracker (the interactive app).
- `api/main.py` — stdlib-only HTTP API: SQLite KV + PDF/DOCX file store. Runtime data in `api/data/` (gitignored, VPS volume — never commit).
- `docs/` — markdown notes + viewer (`docs/index.html` fetches `./<file>`).
- `roadmaps/`, `archive/` — roadmap pages; archive is a 5340-item viewer over root `results.enriched.jsonl` (keep both `results*.jsonl` at root — viewer and enrich script expect them there).
- `static/` (css/js/fonts/icons), `scripts/` (VPS/archive tooling), `favicon/`.
- `ats-resume-creation-skill/` — resume-builder skill (gitignored): builds tailored resumes, pushes results to the tracker. Workflow lives in its `SKILL.md`.

## Iron rules

- Relative asset paths from subdirs (`../static/...`); absolute `/static/*` 404s on Pages.
- No `cdn.tailwindcss.com` (edit HTML → `npm run build:css` → delete `node_modules/` + lockfile). No emoji — pixel icons via `<i data-lucide="name">` (valid keys in `static/js/pixel-icons.js`) + `refreshIcons()` after dynamic DOM.
- `fetch()` needs HTTP — test with `uv run python -m http.server`, never `file://`.
- No secrets in git. Keep the dir lean (no `node_modules/`, `*.zip`, `*.log`, nested `.git/`).

## Tracker API

Base: local `http://127.0.0.1:8080` (`PORT=8080 uv run python api/main.py`), prod `https://greymatter.isroot.in` (nginx proxies `/api/` → api, max body 12m).

- `GET /health` → `{"ok":true}`
- KV store — tracker state is key `tracker-apps-v1`, a JSON array of:
  `{id, company, role, link, type, status, followup, notes, created, files?}`
  (`type` ∈ A|B|C|D; `status` ∈ saved|applied|oa|interview|offer|rejected)
  - `GET /api/store/<key>` → JSON value or `null`; `PUT` JSON (≤5MB); `DELETE`.
  - Merge, never overwrite: GET array → upsert by `id` → PUT back.
- Files (resumes live here, served alongside the instance):
  - `GET /api/files` → `[{name, size}]`
  - `PUT /api/files/<name>` with raw file bytes (no multipart) — `.pdf`/`.docx` only, ≤10MB.
  - `GET /api/files/<name>` views inline (PDF in an iframe; DOCX rendered in-page via vendored mammoth, `static/js/mammoth.min.js`, loaded lazily); append `?download=1` to force download.
  - `DELETE /api/files/<name>`.
  - Name rules: no leading dot, ≤120 chars, no `'"<>`, extension must be `.pdf`/`.docx` (else 404).

## Resume skill → tracker (Hermes or any agent)

Follow `ats-resume-creation-skill/SKILL.md`. After `resume_store.py app add` / `update-status`, run as the last step:

```bash
uv run python ats-resume-creation-skill/scripts/tracker_push.py            # local API
uv run python ats-resume-creation-skill/scripts/tracker_push.py --url https://greymatter.isroot.in  # VPS
```

It merges `applications_index.json` into the tracker by app id (idempotent, updates in place) and uploads each resume as `<id>.pdf` / `<id>.docx` (+ `-cover` letter), linking them onto the tracker row. Re-run after every status change.

## Verify before push

```bash
uv run python -c "import py_compile; py_compile.compile('api/main.py', doraise=True)"
grep -rn "cdn.tailwindcss.com" --include="*.html" . | wc -l   # 0
uv run python -m http.server 8770 &  # then curl: / /tracker/ /docs/ /docs/daily-plan.md /archive/results.enriched.jsonl → all 200; kill server after
git add -A && git commit -m "<scope>: <what>" && git push origin main
```

## Don't

- No new dependencies for `api/` (stdlib only: `http.server` + `sqlite3`). If the file limit rises, raise nginx `client_max_body_size` to match.
- Don't move `results*.jsonl`, docs `.md` files, or `api/data/` — viewers, scripts, and the docs UI resolve them by path.
- Don't add abstractions (single-purpose helpers, speculative options) — shortest diff that works.
