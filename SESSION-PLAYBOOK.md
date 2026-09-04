# Session Playbook — Grey Matter / job-search

Read this first in any new session. It encodes every hard-won lesson from prior sessions so you repeat successes, not mistakes.

## 0. Ground truth

- **Local dir:** `C:/Users/rjaya/Desktop/job-search` (git repo, remote `origin → https://github.com/barryallen16/greymatter.git`, branch `main`)
- **Live Pages:** `https://barryallen16.github.io/greymatter/` — **project site = subpath `/greymatter/`**
- **VPS:** alias `partha` (`ssh partha`, user `ubuntu`, IP `140.245.196.45`, Oracle Cloud). Subdomains: `greymatter.isroot.in` (docs), `archive.isroot.in` (archive root, optional)
- **Stack:** static HTML + local `/static/css/tailwind.css` (44K, built) + Geist fonts + pixel icons. No backend. No emoji ever.

## 1. Iron rules (violations broke the site before)

1. **Relative asset paths, always.** Pages serves `/greymatter/` subpath — absolute `/static/*` 404s there. `index.html` (depth 0): `static/...`, `favicon/...`. `archive/`, `roadmaps/` (depth 1): `../static/...`, `../favicon/...`. `static/css/fonts.css`: `url('../fonts/...')` (relative to `/static/css/`).
2. **Never `cdn.tailwindcss.com`** (prod warning). Edit HTML, then `npm install && npm run build:css`. `node_modules/` + `package-lock.json` stay deleted; rebuild when needed.
3. **Never jsDelivr `geist-pixel/*.woff2`** (404). `font-family:"GeistPixel"` resolves via alias in `static/css/fonts.css` → local `GeistPixel-Square.ttf`.
4. **Only valid `data-lucide` names** (see `static/js/pixel-icons.js` `PIXEL_ICONS` keys). Invalid name → `el.style.display='none'` (invisible icon). There is NO `pixel` icon — use `cpu`/`zap`.
5. **No emoji in HTML.** Grep must return 0: `grep -rP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{1F600}-\x{1F64F}]' --include='*.html'`
6. **HTTP only.** `fetch()` (md files, jsonl) fails on `file://`. Always test with `python -m http.server`.
7. **No secrets in git.** Telegram token leak (`results.jsonl#L1516`) once triggered GitHub secret alert + full `filter-branch` purge. Redact as `REDACTED_*`, rotate via BotFather, never commit `.env`/keys.
8. **Keep dir lean (~22M).** Delete after use: `node_modules/`, `package-lock.json`, `*.zip`, `*.mhtml`, `scripts/.enrich_cache.json`, `*.log`, `.venv/`, nested `.git/`. `results*.jsonl` (4.8M each) ARE tracked (Pages needs them, token redacted). `youtube_urls.*`, `ats-resume-creation-skill/` stay ignored/deleted.

## 2. Other repos — DO NOT CLONE (policy)

Cloning was a one-time need to learn response shapes + endpoints. That knowledge is captured below — **never clone again**. If you must read a file, use GitHub API + raw (no clone):
- `https://api.github.com/repos/barryallen16/aman.ai-search/contents/`
- `https://raw.githubusercontent.com/barryallen16/aman.ai-search/main/<file>`

## 3. Meilisearch (same box, both indexes — everything a session needs)

- Host `https://adhi.isroot.in`, key `barryallen@16` (public master key — usable for reads; recommend minting search-only keys via `aman.ai-search/index_meilisearch.py` and rotating master).
- Health: `curl https://adhi.isroot.in/health` → `{"status":"available"}`
- Demos: `https://barryallen16.github.io/yt-ssf/`, `https://barryallen16.github.io/aman.ai-search/`
- Query (both indexes, same shape):
```bash
curl -s -H "Authorization: Bearer barryallen@16" -H "Content-Type: application/json" \
  --data-binary '{"q":"<query>","limit":3}' \
  "https://adhi.isroot.in/indexes/<yt-ssf|aman-ai>/search"
```
- **yt-ssf hit shape** (`index yt-ssf`, subscription-feed videos): `{id, title, description, thumbnail_url, channel_name}` → watch link = `https://youtube.com/watch?v=<id>`. Known counts: `heap` 28 · `docker` 200 · `rest api` 112 · `sql join group by` 226 (weak top-3, wrappers only).
- **aman-ai hit shape** (`index aman-ai`, 20,595 sections / 485 pages): `{url (deep anchor link — use directly), page_url, title, section_title, level, section_path[], content}`. Known: strong on `docker` ([Step 3: Run the Container](https://aman.ai/infra/docker/#step-3-run-the-docker-container)) and `bias variance`; **no dedicated heap page**.
- Frontend pattern both use: `POST /indexes/<name>/search` with `Bearer`, `Ctrl+K` focuses search, render `title/url/snippet`.

## 4. Archive sweep (5340 docs, local)

- Script: `C:\Users\rjaya\AppData\Local\Temp\opencode\search_archive.py` (may not survive reboot — recreate from pattern: handle `result` as list-or-dict, `url = ed.url or enrichment.yt_dlp_url`, run with `PYTHONIOENCODING=utf-8` to avoid cp1252 emoji crash).
- Known strengths: SQL roadmaps (117), comms/resume X-Y-Z (122), AWS/IAM roadmaps (226), Linux Bandit/nohup (43). Weakness: most `youtube_video` rows have `url=null` + failed enrichment → use `enrichment.yt_dlp_url` fallback (already in `archive/index.html`).
- `archive/index.html` cards are `<button onclick="openDetail">` (vimium-`f` hintable), drawer links need `rel="noopener noreferrer"`, `Escape` closes drawer.

## 5. Verify before push (all must pass)

```bash
cd "C:/Users/rjaya/Desktop/job-search"
grep -r "cdn.tailwindcss.com" --include="*.html" . | wc -l          # 0
grep -r "cdn.jsdelivr.net.*geist.*woff" --include="*.html" . | wc -l # 0
grep -r 'data-lucide="pixel"' --include="*.html" . | wc -l          # 0
python -m http.server 8770  # then:
for p in "/" "/archive/" "/roadmaps/" "/roadmaps/2026-09-02.html" "/static/css/tailwind.css" "/static/css/fonts.css" "/static/js/pixel-icons.js" "/favicon/favicon.ico" "/daily-plan.md" "/archive/results.enriched.jsonl"; do echo -n "$p -> "; curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8770$p; done  # all 200
```

Then: `git add -A && git commit -m "<scope>: <what>" && git push origin main`. Pages rebuilds in 1–2 min. If remote says moved (`salim → greymatter`), `git remote set-url origin https://github.com/barryallen16/greymatter.git`.

## 6. VPS hosting (partha, Oracle — the painful lessons)

- Oracle blocks 80/443 at **VCN Security List** (OCI Console → Networking → VCN → Security Lists → Add Ingress `0.0.0.0/0` TCP 80 + 443) AND host `iptables` (`-I INPUT ... --dport 80/443 -j ACCEPT`). `ufw` inactive = fine.
- Only ONE nginx may own port 80: host `nginx.service` was the conflict — `sudo systemctl stop/disable nginx`, docker `80:80` wins. `docker-compose.yml` must map `["80:80","443:443"]` + volumes `./:/usr/share/nginx/html:ro`, `/etc/letsencrypt:/etc/letsencrypt:ro`.
- Certbot: use `--webroot -w /home/ubuntu/grey-matter` (standalone fails behind docker). Test `curl http://greymatter.isroot.in/.well-known/acme-challenge/test → ok` BEFORE certbot. Rate limit: 5 failures/hour per domain — wait it out.
- Never paste YAML as shell commands (renders `-bash: Add: command not found`). Use `cat > file <<'YAML'`.
- isroot.in allows 1 subdomain/hour — `archive.isroot.in` is optional; `/archive/` path works without it.
- `scp` direction: laptop→VPS `scp file partha:/tmp/`, then `sudo mv` + `chown ubuntu` + `nginx -t && reload`.

## 7. Session-end checklist

- [ ] `git status` clean, pushed, Pages verified (curl the live URL, not just local)
- [ ] Temp clones noted (in `/tmp/clones`, ephemeral — re-clone next session if gone)
- [ ] No new files left in `job-search/` that weren't asked for (user deletes aggressively)
- [ ] Update this playbook if you learned anything new
