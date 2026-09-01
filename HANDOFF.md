# Handoff — Emoji → Pixel Icons (kaggle-automation style) + Archive/Geist + VPS

**For next LLM to redo / verify in its own style without asking user again.**

---

## 1. What user asked (in order)

1. `remove the emoji, clone kaggle-automation from my github, and see how it implemented icons and do it instead, after done, remove that repo from the current directory. write a handoff, such that if a llm has to redo or verify your work their style, it can do it`
2. Prior context (already done before this handoff, don't redo unless verifying):
   - Use Geist fonts preferably Geist Pixel
   - Create searchable website for `results.enriched.jsonl` (5340 items) organized, mobile friendly, for `isroot.in` subdomain
   - Make whole site mobile friendly + VPS hostable (`docker compose up`)
   - Rank `ideas.md` 19 ideas brutally, patch missing `roadmap.sh/backend` (Postgres/Redis)
   - Build `roadmaps/2026-09-02.html` daily tickbox roadmap

**Operator is Muse Spark (opencode/muse-spark-1.2-contributor-free) on win32, bash (pinned).**

---

## 2. How kaggle-automation implements icons (source of truth)

Clone: `https://github.com/barryallen16/kaggle-automation`

Structure:
```
app/static/
  css/fonts.css        # local Geist/Geist Mono/GeistPixel (Square/Circle/Grid/Line/Triangle) via /static/fonts/*.ttf
  css/custom.css       # glass-panel, terminal-window, pulse, mobile @media (table px-*, input font-size 16px)
  js/pixel-icons.js    # Pixelarticons v2.4.1 MIT, maps <i data-lucide="name"> → SVG from PIXEL_ICONS dict, keep Tailwind classes, call refreshIcons(root) after DOM or dynamic insertion
  icons/pixel/*.svg    # raw SVGs (activity, archive, clock, file, history, lock, network, etc. 40 files)
  fonts/Geist-*.ttf, GeistPixel-*.ttf
  icons/favicon.ico etc.
templates/index.html   # <i data-lucide="layout-dashboard"> + <script src="/static/js/pixel-icons.js"> + tailwind darkMode class, fontFamily sans: ['Geist Pixel Square','Geist',monospace]
```

Key: **No emoji, no CDN lucide, no external icon font.** Every icon is `<i data-lucide="kebab-case-name" class="w-4 h-4 ...">` replaced by `pixel-icons.js`. The SVG `viewBox="0 0 24 24" fill="currentColor" shape-rendering="crispEdges"` keeps pixel crisp.

Fonts: all locally served via `fonts.css`, not Google Fonts. But this job-search site historically used Google Fonts Geist; we kept **both** (Google + local) for compatibility, with `font-display: swap`. New archive uses both too.

---

## 3. What was done in job-search (to verify)

### 3.1 Copied static assets (no code change, just copy)

```bash
mkdir -p job-search/static/{js,css,fonts,icons/pixel}
cp kaggle-automation/app/static/js/pixel-icons.js          -> job-search/static/js/pixel-icons.js
cp kaggle-automation/app/static/css/fonts.css               -> job-search/static/css/fonts.css
cp kaggle-automation/app/static/css/custom.css              -> job-search/static/css/custom.css # copied but not linked yet (optional, not required)
cp -r kaggle-automation/app/static/fonts/.                  -> job-search/static/fonts/
cp -r kaggle-automation/app/static/icons/pixel/.            -> job-search/static/icons/pixel/
# also copied favicon.ico, site.webmanifest optionally
```

Result `job-search/static/` now exists:
- `js/pixel-icons.js` (2.0KB)
- `css/fonts.css` (local Geist definitions)
- `fonts/` (10 ttf)
- `icons/pixel/` (40 svgs)

### 3.2 Removed emoji and replaced with pixel icons

Grep before: `grep -P "[\x{1F300}-\x{1FAFF}]" job-search --include="*.html"` found 15 hits.

**Mapping used (emoji → pixel icon name):**

| Emoji / Context | Replacement | Reason |
|---|---|---|
| 📄 header doc logo | `file` | exact |
| 🗓️ Roadmaps | `clock` | time/roadmap |
| 🗃️ Archive | `archive` | exact |
| 💼 Portfolio | `external-link` | external |
| 🔒 error card | `lock` | exact |
| 📅 Daily Plan | `clock` | schedule |
| 💡 Ideas | `zap` | idea spark |
| 🏆 Ranking | `shield-check` | award |
| 🔍 Repo Analysis | `terminal` | code |
| 🎯 Roles & Focus | `network` | graph |
| 🧭 Research Notes | `info` | info |
| 📚 Must-Have Skills | `file` | docs |
| 🧠 Career Insights | `activity` | pulse |
| ⏳ roadmaps placeholder | `history` | waiting |
| 🎯 Today's Edge | `rocket` | launch |
| ✕ (close/clear) | `x` | exact |

All replacements use `<i data-lucide="name" class="w-4 h-4 ...">` with Tailwind color classes preserved.

**Files edited:**

1. `job-search/index.html`:
   - Header: `<span>📄</span>` → `<i data-lucide="file" class="w-5 h-5 text-emerald-400">`
   - Sidebar links: `🗓️ → clock`, `🗃️ → archive`, `💼 → external-link`
   - Error card: `🔒` → `<i data-lucide="lock" class="w-10 h-10 text-amber-400">`
   - `DOCS` array: `icon: '📅'` etc → `icon: 'clock'` etc. (8 entries)
   - Nav rendering: `<span class="text-lg">${doc.icon}</span>` → `<i data-lucide="${doc.icon}" class="w-4 h-4 text-zinc-400 mt-0.5 shrink-0">`
   - Added `<link rel="stylesheet" href="/static/css/fonts.css">` and `<script src="/static/js/pixel-icons.js"></script>` + `if(window.refreshIcons) refreshIcons(nav)` and `refreshIcons(document.body)` on load + errorCard.

2. `job-search/roadmaps/index.html`:
   - `🗃️ Archive` → `archive`, `← Docs` already text, kept but added `file` icon, `Portfolio →` added `external-link`
   - `⏳` → `history`
   - Added `<script src="/static/js/pixel-icons.js">` + refresh.

3. `job-search/roadmaps/2026-09-02.html`:
   - `🎯 Today's Edge` → `<i data-lucide="rocket" class="w-4 h-4"> Today's Edge`
   - Added `<link rel="stylesheet" href="/static/css/fonts.css">` + `<script src="/static/js/pixel-icons.js">` in head, and `if(window.refreshIcons) refreshIcons(document.body)` at end of inline script.
   - Removed duplicate script tags (was double).

4. `job-search/archive/index.html`:
   - Already had no emoji in most places (arrows are text, not emoji). Replaced the 3 `✕` (clearBtn, closeDrawer, chip) with `<i data-lucide="x" class="w-4 h-4">` etc.
   - Added `<link rel="stylesheet" href="/static/css/fonts.css">` + `<script src="/static/js/pixel-icons.js">` in head.
   - `renderActiveChips` now pushes `<i data-lucide="x" class="w-3 h-3">` and calls `refreshIcons(el)` after `innerHTML`.

5. `job-search/portfolio/index.html`:
   - No emoji found, but fixed nav tap targets and added `docs` link. Kept existing `cdnlogo` images, not pixel icons (icon set not needed there).

### 3.3 Removed cloned repo

Clone was at `C:/Users/rjaya/AppData/Local/Temp/opencode/kaggle-automation` (not in `job-search/`). Removed via `rm -rf`. Verified no `kaggle-automation` folder in `job-search/` via `ls -la job-search | grep kaggle` → 0.

### 3.4 Geist Pixel usage (prior task, preserved)

- `index.html`, `roadmaps/*.html`, `archive/index.html` already use Geist + Geist Mono + Geist Pixel (Google Fonts + jsDelivr + local fonts.css). Headlines use `.pixel` class (`GeistPixel`), mono for code. This was kept; the emoji removal did not break fonts.

### 3.5 VPS / archive integration (prior task, preserved, verify)

- `archive/index.html` is 5340-item searchable archive: fetches `../results.enriched.jsonl` fallback to `./results.enriched.jsonl` etc., category pills, search, 24/page, drawer.
- Copied `results.enriched.jsonl` + `results.jsonl` into `archive/` for subdomain root case.
- `nginx.conf` has 2 servers: `_` (main root) and `archive.isroot.in` (root `archive/`). Also `location /archive/` alias.
- `docker-compose.yml` `8000:80`, `Dockerfile` nginx:alpine, `README.md` with isroot.in steps.

---

## 4. How to verify (run these, no write)

```bash
# 1. No emoji left in served HTML
grep -r -P "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{1F600}-\x{1F64F}]" job-search --include="*.html" | wc -l
# expect 0

# 2. Pixel icons present
grep -r "data-lucide" job-search --include="*.html" | head
# expect ~15 hits: file, clock, archive, external-link, lock, zap, shield-check, terminal, network, info, activity, history, rocket, x

# 3. Script included
grep -r "pixel-icons" job-search --include="*.html"
# expect 4 files: index.html, archive/index.html, roadmaps/*.html

# 4. Static assets exist
ls -lh job-search/static/js/pixel-icons.js job-search/static/css/fonts.css
ls job-search/static/icons/pixel | wc -l  # expect 40
ls job-search/static/fonts | wc -l         # expect 10

# 5. No clone left
ls -la job-search | grep kaggle  # expect 0
ls -la /tmp/opencode 2>&1 | grep kaggle  # expect 0

# 6. Local serve check (requires http, not file://)
python -m http.server 8000 --directory job-search &
curl -s http://localhost:8000/ | grep -c "data-lucide"  # expect >0
curl -s http://localhost:8000/archive/ | grep -c "GeistPixel"  # expect >0
# kill: taskkill //PID $(netstat -ano | grep :8000 | grep LISTENING | awk '{print $5}' | head -n1) //F

# 7. Nginx build dry (if docker running)
docker build -t job-search:test job-search  # should succeed, <10MB
```

---

## 5. How to redo from scratch (LLM steps, win32)

```bash
# From job-search dir (pwd = job-search)
git clone https://github.com/barryallen16/kaggle-automation.git /tmp/kaggle-automation
mkdir -p static/{js,css,fonts,icons/pixel}
cp /tmp/kaggle-automation/app/static/js/pixel-icons.js static/js/
cp /tmp/kaggle-automation/app/static/css/fonts.css static/css/
cp -r /tmp/kaggle-automation/app/static/fonts/. static/fonts/
cp -r /tmp/kaggle-automation/app/static/icons/pixel/. static/icons/pixel/

# For each HTML file (index.html, archive/index.html, roadmaps/index.html, roadmaps/2026-09-02.html):
# - replace emoji spans with <i data-lucide="name">
#   mapping: 📄→file, 🗓️/📅→clock, 🗃️→archive, 💼→external-link, 🔒→lock, 💡→zap, 🏆→shield-check, 🔍→terminal, 🎯→network/rocket, 🧭→info, 📚→file, 🧠→activity, ⏳→history, ✕→x, 🎯→rocket
# - add <link rel="stylesheet" href="/static/css/fonts.css"> in <head> if not present
# - add <script src="/static/js/pixel-icons.js"></script> in <head> or before </body>
# - after any dynamic innerHTML that injects data-lucide, call if(window.refreshIcons) refreshIcons(container)
# - for DOCS array in index.html, change icon emoji to lucide names and render as <i data-lucide="${doc.icon}">

# Verify
grep -P "[\x{1F300}-\x{1FAFF}]" job-search --include="*.html" -r | wc -l  # 0
grep -r "pixel-icons" job-search --include="*.html" | wc -l  # >=4

# Cleanup
rm -rf /tmp/kaggle-automation
# ensure not in job-search
rm -rf job-search/kaggle-automation 2>/dev/null || true
```

Style notes for redo:
- Keep Tailwind classes on the `<i>` (the SVG preserves them via `iconSvg(name, cls)`).
- Keep `shape-rendering: crispEdges` for pixel crispness (in pixel-icons.js).
- Don't use CDN lucide or emoji font; use local pixel SVGs only.
- Keep Geist Pixel for headlines (`.pixel`), Geist Mono for code.
- Test on phone: tickboxes 20×20, tap targets ≥44px, sidebar hamburger 44×44, no horizontal scroll.

---

## 6. Current file inventory (after this handoff)

```
job-search/
  static/
    js/pixel-icons.js
    css/fonts.css
    css/custom.css
    fonts/Geist-*.ttf, GeistPixel-*.ttf (10)
    icons/pixel/*.svg (40)
  index.html               # no emoji, pixel icons, Geist, archive/roadmaps/portfolio links
  archive/index.html       # no emoji, x icons, pixel icons, 5340 search, Geist Pixel
  roadmaps/index.html      # no emoji, archive/file/history icons
  roadmaps/2026-09-02.html  # no emoji, rocket icon, pixel icons
  portfolio/index.html     # already no emoji, nav fixed
  nginx.conf               # main + archive.isroot.in
  Dockerfile, docker-compose.yml, README.md, .dockerignore
  results.enriched.jsonl, results.jsonl, youtube_urls.csv (large, served)
  archive/results.enriched.jsonl (copy for subdomain)
```

No `kaggle-automation` folder remains in `job-search/`.

---

## 7. Next LLM: what NOT to do

- Don't re-add emoji (user explicitly asked remove).
- Don't use CDN lucide (`https://unpkg.com/lucide`) — use local `static/js/pixel-icons.js` to match kaggle-automation style.
- Don't clone into `job-search/` — use `/tmp` and delete after.
- Don't add new emoji elsewhere (e.g., in new roadmaps, use `data-lucide` instead).
- Keep VPS/nginx as is; don't switch to Node or Python server unless asked.

If you must verify again, run the 7 checks in §4 and eyeball `http://localhost:8000/` on phone viewport — all icons should be crisp pixel squares, no tofu emoji.
