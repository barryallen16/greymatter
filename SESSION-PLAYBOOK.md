# Session Playbook — Grey Matter / job-search

Read first in any new session.

## 0. Ground truth

- Local: `C:/Users/rjaya/Desktop/job-search` (`origin → https://github.com/barryallen16/greymatter.git`, `main`)
- Pages: `https://barryallen16.github.io/greymatter/` = subpath `/greymatter/`
- VPS: `ssh partha` (`ubuntu`, `140.245.196.45`, Oracle). Subdomains: `greymatter.isroot.in`, `archive.isroot.in` (optional)
- Stack: static HTML + local `static/css/tailwind.css` + Geist + pixel icons. No backend. No emoji.

## 1. Iron rules

1. **Relative paths.** `index.html`: `static/...`, `favicon/...`. `archive/`, `roadmaps/`: `../static/...`. `static/css/fonts.css`: `url('../fonts/...')`. Absolute `/static/*` 404s on Pages.
2. **No `cdn.tailwindcss.com`.** Edit HTML → `npm install && npm run build:css` → delete `node_modules/`, `package-lock.json`.
3. **No jsDelivr geist-pixel woff2** (404). `GeistPixel` alias in `static/css/fonts.css` → local TTF.
4. **Valid `data-lucide` only** (keys in `static/js/pixel-icons.js`). Invalid = `display:none`. No `pixel` icon — use `cpu`/`zap`.
5. **No emoji.** `grep -rP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{1F600}-\x{1F64F}]' --include='*.html'` → 0.
6. **HTTP only** (`fetch()` dies on `file://`). Test with `python -m http.server`.
7. **No secrets.** Redact `REDACTED_*`, rotate via BotFather.
8. **Lean dir (~22M).** Delete after use: `node_modules/`, `package-lock.json`, `*.zip`, `*.mhtml`, `*.log`, `.venv/`, nested `.git/`. `results*.jsonl` ARE tracked (Pages needs them, token redacted).

## 2. Other repos — DO NOT CLONE

Shapes + endpoints below replace cloning. File read fallback (no clone):
`https://raw.githubusercontent.com/barryallen16/aman.ai-search/main/<file>`

## 3. Meilisearch (`https://adhi.isroot.in`, key `barryallen@16`)

```bash
curl -s -H "Authorization: Bearer barryallen@16" -H "Content-Type: application/json" \
  --data-binary '{"q":"<query>","limit":3}' \
  "https://adhi.isroot.in/indexes/<yt-ssf|aman-ai>/search"
```

- Health: `/health` → `{"status":"available"}`. Demos: `https://barryallen16.github.io/yt-ssf/`, `https://barryallen16.github.io/aman.ai-search/`
- **yt-ssf**: `{id, title, description, thumbnail_url, channel_name}` → `https://youtube.com/watch?v=<id>`. Counts: `heap` 28 · `docker` 200 · `rest api` 112 · `sql join group by` 226 (weak).
- **aman-ai** (20,595 sections / 485 pages): `{url (deep anchor, use directly), page_url, title, section_title, level, section_path[], content}`. Strong: `docker`, `bias variance`. Gap: no heap page.

## 4. Archive sweep (5340 docs)

- Script: `C:\Users\rjaya\AppData\Local\Temp\opencode\search_archive.py` (ephemeral — recreate if gone: `result` is list-or-dict, `url = ed.url or enrichment.yt_dlp_url`, run with `PYTHONIOENCODING=utf-8`).
- Strengths: SQL (117), comms/X-Y-Z (122), AWS/IAM (226), Linux Bandit/nohup (43). Weakness: `youtube_video` rows mostly `url=null` → `yt_dlp_url` fallback (already in `archive/index.html`).
- Cards are `<button>` (vimium-`f`), drawer links need `rel="noopener noreferrer"`, `Escape` closes.

## 5. Verify before push

```bash
cd "C:/Users/rjaya/Desktop/job-search"
grep -r "cdn.tailwindcss.com" --include="*.html" . | wc -l          # 0
grep -r "cdn.jsdelivr.net.*geist.*woff" --include="*.html" . | wc -l # 0
grep -r 'data-lucide="pixel"' --include="*.html" . | wc -l          # 0
python -m http.server 8770  # then:
for p in "/" "/archive/" "/roadmaps/" "/roadmaps/2026-09-02.html" "/static/css/tailwind.css" "/static/css/fonts.css" "/static/js/pixel-icons.js" "/favicon/favicon.ico" "/daily-plan.md" "/archive/results.enriched.jsonl"; do echo -n "$p -> "; curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8770$p; done  # all 200
```

`git add -A && git commit -m "<scope>: <what>" && git push origin main` (Pages: 1–2 min).

## 6. VPS (partha, Oracle)

- Open 80/443 at **VCN Security List** (Networking → VCN → Security Lists → Ingress `0.0.0.0/0` TCP 80+443) AND host `iptables -I INPUT ... --dport 80/443 -j ACCEPT`. `ufw` inactive = fine.
- One nginx on :80: `sudo systemctl stop/disable nginx`; docker `["80:80","443:443"]` + volumes `./:/usr/share/nginx/html:ro`, `/etc/letsencrypt:/etc/letsencrypt:ro`.
- Certbot `--webroot -w /home/ubuntu/grey-matter` (standalone fails behind docker). Verify `/.well-known/.../test → ok` first. Limit: 5 failures/hour/domain.
- YAML via `cat > file <<'YAML'`, never pasted as commands. `archive.isroot.in` optional (1 subdomain/hour). `scp file partha:/tmp/` → `sudo mv` + `chown` + `nginx -t && reload`.

## 7. Session end

- [ ] pushed, Pages curl-verified (live URL, not just local)
- [ ] no unasked files left in `job-search/`
- [ ] playbook updated with anything new
