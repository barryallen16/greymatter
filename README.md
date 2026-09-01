# Grey Matter — phone + laptop, from anywhere (VPS)

Static site: **Docs** (`/`) + **Roadmaps** (`/roadmaps/`) + **Archive** (`/archive/` 5340 items). All tickboxes work on phone, persist in `localStorage`, no backend.

**Fonts:** Geist + Geist Mono + Geist Pixel (`pixel` headlines, `mono` code). Loaded via Google Fonts + local `/static/fonts/*.ttf` (`/static/css/fonts.css` `GeistPixel` alias, `font-display: swap`). **Tailwind:** local `/static/css/tailwind.css` (built via `npm run build:css`, no CDN).

## Quick start (local phone test)

```bash
# from job-search folder
python -m http.server 8000
# open http://localhost:8000   (or http://<your-laptop-ip>:8000 on phone same WiFi)
```

`index.html` fetches `*.md` via `fetch()` — it **must** be served over HTTP (fails on `file://`). The error card explains this.

## VPS deploy (1 command)

```bash
# on VPS (Ubuntu/Debian with Docker)
git clone <your repo> && cd job-search
docker compose up -d --build
# open http://YOUR_VPS_IP:8000
```

To serve on port 80:

```yaml
# docker-compose.yml
ports:
  - "80:80"   # change 8000:80 → 80:80
```

Then `docker compose up -d --build` and open `http://YOUR_VPS_IP/`.

### With domain + HTTPS (isroot.in subdomain)

You created `greymatter.isroot.in` + `archive.isroot.in` (A records → YOUR_VPS_IP).

**Option A — path based (no DNS):** `http://YOUR_VPS_IP:8000/archive/` already works.

**Option B — subdomain (pretty):**
- `https://greymatter.isroot.in` → `nginx` `server_name greymatter.isroot.in` serves `/` (docs)
- `https://archive.isroot.in` → `nginx` `server_name archive.isroot.in` serves `/archive/` as root (uses `archive/results.enriched.jsonl` + `yt_dlp_url` fallback)

```bash
# HTTPS for both
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d greymatter.isroot.in -d archive.isroot.in
# certbot auto-detects both server blocks in nginx.conf
```

**Test subdomain locally before DNS:**
```bash
curl -H "Host: greymatter.isroot.in" http://YOUR_VPS_IP/health
# → ok greymatter
curl -H "Host: archive.isroot.in" http://YOUR_VPS_IP/health
# → ok archive
```

## What's where

```
job-search/  (now Grey Matter, was job-search)
  index.html              → Docs viewer (Daily Plan, Ideas, Ranking, Repo Analysis...) — Geist Pixel headlines
  daily-plan.md, ideas.md, ideas_ranking.md, repo-analysis.md, roles-*.md, career_advice_insights.md, fresher-*.md
  roadmaps/
    index.html            → list of daily roadmaps
    2026-09-02.html       → Heap Day 1 (27 ticks, localStorage, Export .md)
  archive/
    index.html            → Searchable archive of 5340 screenshots — filter by category, search, drawer detail (Geist Pixel), buttons vimium-hintable, yt_dlp_url fallback
    results.enriched.jsonl → 4.8M source (copied for subdomain root)
    results.jsonl
  favicon/
    favicon.ico, favicon-32x32.png, favicon-16x16.png, apple-touch-icon.png, 192/512, site.webmanifest
  static/
    css/tailwind.css (44K, built, no CDN), css/fonts.css (GeistPixel alias → local Square.ttf), js/pixel-icons.js, fonts/*.ttf, icons/pixel/*.svg
  Dockerfile + nginx.conf (greymatter.isroot.in + archive.isroot.in) + docker-compose.yml  → host anywhere
  scripts/enrich_yt_urls_ytdlp.py  → rebuild youtube_urls.csv if needed
  results.jsonl / results.enriched.jsonl → data (5M, .gitignore)
```

## Mobile friendly — what was fixed

* `viewport` + `env(safe-area-inset-top)` for iPhone notch on all headers
* Tap targets ≥44px (menu, nav, roadmap ticks 20×20, Export/Reset 40px)
* `touch-action: manipulation`, `-webkit-tap-highlight-color: transparent`, no text-zoom
* `overflow-x: auto` + `-webkit-overflow-scrolling: touch` for tables/code, `word-break` for long links
* Sticky headers with `backdrop-blur`, no horizontal overflow
* Docs sidebar: hamburger now 44×44, quick links to Roadmaps/Archive (portfolio/grey-matter removed)

Test on phone: open Chrome DevTools → Toggle device toolbar (iPhone SE / Pixel 7) → check no horizontal scroll, ticks easy to tap, sidebar slides.

## Adding tomorrow's roadmap

```bash
# copy template
cp roadmaps/2026-09-02.html roadmaps/2026-09-03.html
# or ask: "generate roadmap for 2026-09-03" — it will be created nightly
```

Update `roadmaps/index.html` link list.

Add new `.md` to docs viewer: edit `index.html` → `const DOCS = [...]` array.

## Not missing

* ✅ All `*.md` with 8 docs (daily, ideas, ranking, repo, roles, research, must-have, career)
* ✅ Archive: 5340 items, Geist Pixel headlines, filters (All/Career/YouTube/Website/Visual/GitHub), search + pagination 24/page, drawer with core content + enrichment JSON, mobile drawer bottom-sheet
* ✅ Fonts: Geist Sans/Mono + Geist Pixel (Google Fonts + jsDelivr CDN, swap)
* ✅ Roadmaps persist via `localStorage` (key `roadmap-YYYY-MM-DD`)
* ✅ Vimium: archive cards now `<button>` hintable via `f`, `Escape` closes drawer, links `rel="noopener noreferrer"`
* ✅ Favicon at `favicon/` (no portfolio), GeistPixel alias → local `GeistPixel-Square.ttf` (no 404), Tailwind local (no CDN warning)
* ✅ `nginx.conf` gzip, cache (assets 1h, html no-cache), security headers, `/health` + `/archive/` + `greymatter.isroot.in` + `archive.isroot.in` blocks
* ✅ `Dockerfile` alpine <10MB + `HEALTHCHECK`
* ✅ `.dockerignore` + `.gitignore` keep image/repo small (`ats-resume-creation-skill/` now ignored)

## Troubleshooting

* **Phone shows “Can’t load markdown”** → you opened `file://`, need `http://VPS_IP:8000/`
* **Ticks reset** → different browser/device = different `localStorage`. Export .md daily as backup.
* **Port 8000 blocked on VPS** → `sudo ufw allow 8000` or switch to 80

## One-liner to update VPS

```bash
git pull && docker compose up -d --build && docker compose ps
```
