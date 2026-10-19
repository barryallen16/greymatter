"""Generate report.html — self-contained card-grid UI (no server, no deps).

Three views (Q10): Report (today's top matches), All jobs, By tier.
All data is embedded as JSON; filtering/tabs are instant client-side JS.
"""

from __future__ import annotations

import base64
import csv
import json
import sqlite3
import urllib.parse
from datetime import UTC, datetime
from pathlib import Path

# sibling repo of job-search, four levels up from job-search/scrape/jobpipe/page.py
IITM_DIR = Path(__file__).resolve().parents[3] / "iitm-startups"
ASSETS = Path(__file__).resolve().parent.parent / "assets"

# pixelarticons search icon (MIT), inlined into the static search inputs
ICO_SEARCH_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"'
    ' aria-hidden="true"><path d="M22 22h-2v-2h2v2Zm-2-2h-2v-2h2v2Zm-6-2H6v-2h8v2Zm4'
    " 0h-2v-2h2v2ZM6 16H4v-2h2v2Zm10 0h-2v-2h2v2ZM4 14H2V6h2v8Zm14 0h-2V6h2v8ZM6"
    ' 6H4V4h2v2Zm10 0h-2V4h2v2Zm-2-2H6V2h8v2Z"/></svg>'
)


def _fontface() -> str:
    """Geist Pixel body + Instrument Serif italic headers, offline file:// use."""
    faces = [
        ("Geist Pixel", 400, "normal", "geistpixel-400.woff2"),
        ("Instrument Serif", 400, "italic", "instrumentserif-400italic.woff2"),
    ]
    css = []
    for family, weight, style, name in faces:
        try:
            raw = (ASSETS / "fonts" / name).read_bytes()
        except OSError:
            continue
        b64 = base64.b64encode(raw).decode()
        css.append(
            f"@font-face{{font-family:'{family}';font-style:{style};"
            f"font-weight:{weight};"
            f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    return "".join(css)


def _load_startups() -> list[dict]:
    """IITM Research Park directory (sibling repo) + curated fresher roles."""
    try:
        with (IITM_DIR / "iitm-startups.csv").open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except OSError:
        return []
    try:
        roles = json.loads((IITM_DIR / "raw" / "fresher_roles.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        roles = {}
    by_name = {str(k).strip().lower(): v for k, v in roles.items()}
    return [
        {
            "name": (r.get("name") or "").strip(),
            "careers": (r.get("careers_page") or "").strip(),
            "linkedin": (r.get("linkedin") or "").strip(),
            "website": (r.get("company_page") or "").strip(),
            "roles": by_name.get((r.get("name") or "").strip().lower(), ""),
        }
        for r in rows
        if (r.get("name") or "").strip()
    ]


def _favicon_link() -> str:
    """IITM pixel-building favicon, transparent background as requested."""
    try:
        svg = (IITM_DIR / "favicon.svg").read_text(encoding="utf-8")
    except OSError:
        return ""
    return '<link rel="icon" href="data:image/svg+xml,' + urllib.parse.quote(svg) + '">'


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Daily fresher jobs: today's matches, search, startups.">
<meta name="theme-color" content="#4f46e5">
<meta property="og:title" content="Job pipeline">
<meta property="og:description" content="Today's fresher matches plus a searchable archive.">
<title>Job pipeline</title>
__FAVICON__
<style>
__FONTFACE__
:root{
  --bg:#f6f7f9;--card:#fff;--ink:#15181d;--muted:#667085;--line:#e4e7ec;
  --accent:#4f46e5;--a:#0e9f6e;--b:#4f46e5;--c:#98a2b3;color-scheme:light dark;
  --disp:'Geist Pixel','Courier New',monospace;
  --serif:'Instrument Serif',Georgia,serif;
  --ring:color-mix(in srgb,var(--accent) 55%,transparent);
  --success:#047857;--warn:#b45309;--danger:#dc2626;
  --shadow:0 1px 2px rgba(21,24,29,.06),0 12px 28px -18px rgba(79,70,229,.35);
  --shadow-hover:0 2px 4px rgba(21,24,29,.07),0 18px 36px -16px rgba(79,70,229,.42);
  --r-lg:12px;--r-md:8px;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#0f1115;--card:#171a21;--ink:#e8eaf0;--muted:#98a2b3;--line:#262a33;
        --accent:#818cf8;--a:#2dd4a0;--b:#818cf8;--c:#667085;
        --shadow:0 1px 2px rgba(0,0,0,.4),0 14px 30px -18px rgba(0,0,0,.7);
        --shadow-hover:0 2px 6px rgba(0,0,0,.45),0 20px 40px -16px rgba(0,0,0,.75);}
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--ink);
     font:15px/1.6 'Geist Pixel','Courier New',monospace}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:12px;top:-48px;z-index:50;background:var(--ink);color:var(--bg);
  font-family:var(--disp);font-size:12px;font-weight:700;text-decoration:none;
  padding:10px 14px;border-radius:8px;transition:top .18s ease}
.skip:focus{top:12px;color:var(--bg)}
.wrap{max-width:1180px;margin:0 auto;padding:20px 16px 60px}
header.top{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;align-items:baseline;
  gap:6px 14px;margin:0 -16px;padding:14px 16px;
  background:color-mix(in srgb,var(--bg) 86%,transparent);
  backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
h1{font-size:22px;margin:0;font-family:var(--disp);font-weight:700;letter-spacing:-.02em;
  text-wrap:balance}
.stats{color:var(--muted);font-size:13px;font-variant-numeric:tabular-nums}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:16px;
  background:var(--card);border:1px solid var(--line);border-radius:var(--r-lg);
  padding:12px;box-shadow:var(--shadow)}
.vtabs{display:flex;gap:4px;margin:16px 0 4px;border-bottom:1px solid var(--line)}
.vtabs button{appearance:none;background:none;border:0;border-bottom:2px solid transparent;
  padding:10px 14px;font-family:var(--disp);font-size:12px;color:var(--muted);
  cursor:pointer;min-height:44px;border-radius:8px 8px 0 0}
.vtabs button:hover{color:var(--ink);background:color-mix(in srgb,var(--ink) 5%,transparent)}
.vtabs button.active{color:var(--ink);border-bottom-color:var(--accent);font-weight:600}
#q{flex:1;min-width:0;padding:10px 14px 10px 40px;font:inherit;color:var(--ink);
   background:color-mix(in srgb,var(--ink) 4%,var(--card));border:1px solid var(--line);
   border-radius:var(--r-md);min-height:44px}
#sq{flex:1;min-width:0;padding:10px 14px 10px 40px;font:inherit;color:var(--ink);
   background:color-mix(in srgb,var(--ink) 4%,var(--card));border:1px solid var(--line);
   border-radius:var(--r-md);min-height:44px}
#q:focus,#sq:focus{outline:2px solid var(--accent);outline-offset:1px}
.searchwrap{position:relative;flex:1;min-width:220px;display:flex}
.searchwrap svg{position:absolute;left:13px;top:50%;transform:translateY(-50%);
  width:16px;height:16px;color:var(--muted);pointer-events:none}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chips button{appearance:none;padding:8px 14px;font-family:var(--disp);font-size:11px;
  cursor:pointer;background:var(--card);color:var(--muted);
  border:1px solid var(--line);border-radius:999px;min-height:40px;
  transition:background .16s ease,color .16s ease,border-color .16s ease,transform .08s ease}
.chips button:hover{color:var(--ink);border-color:var(--muted)}
.chips button:active{transform:translateY(1px)}
.chips button.active{background:var(--ink);color:var(--card);
  border-color:var(--ink);font-weight:600}
select{font-family:var(--disp);font-size:11px;color:var(--ink);background:var(--card);
  border:1px solid var(--line);border-radius:var(--r-md);padding:10px 12px;
  min-height:44px;cursor:pointer}
#count{font-size:13px;color:var(--muted);margin:0 0 12px;font-variant-numeric:tabular-nums}
#scount{font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
#reset{appearance:none;background:none;border:0;color:var(--muted);
  font-family:var(--disp);font-size:11px;cursor:pointer;text-decoration:underline;
  padding:8px;min-height:40px;border-radius:6px}
#reset:hover{color:var(--ink)}
#grid,#matches{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.sec{margin-top:28px}
h2.head{grid-column:1/-1;font-family:var(--serif);font-style:italic;font-weight:400;
  font-size:27px;line-height:1.2;letter-spacing:0;color:var(--ink);
  margin:16px 0 6px;text-wrap:balance}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r-lg);
      padding:18px 16px 16px;display:flex;flex-direction:column;gap:10px;
      box-shadow:var(--shadow);
      transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
.card:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover);
  border-color:color-mix(in srgb,var(--accent) 28%,var(--line))}
#matches .card{border-color:color-mix(in srgb,var(--accent) 26%,var(--line))}
.card .row{display:flex;justify-content:space-between;align-items:center;gap:8px}
.tier{font-family:var(--disp);font-size:11px;font-weight:700;padding:4px 10px;border-radius:6px;
  font-variant-numeric:tabular-nums;white-space:nowrap}
.tier.A{background:color-mix(in srgb,var(--a) 16%,transparent);color:var(--a)}
.tier.B{background:color-mix(in srgb,var(--b) 14%,transparent);color:var(--b)}
.tier.C{background:color-mix(in srgb,var(--c) 16%,transparent);color:var(--c)}
.score{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.card h3{margin:0;font-size:17px;line-height:1.35;font-weight:600;overflow-wrap:anywhere;
  text-wrap:pretty;letter-spacing:-.005em}
.card h3 a{color:inherit;text-decoration:none}
.card h3 a:hover{color:var(--accent);text-decoration:underline}
.meta{margin:0;color:var(--muted);font-size:13px}
.foot{display:flex;align-items:center;gap:8px;margin-top:auto;padding-top:4px}
.badge{font-family:var(--disp);font-size:10px;color:var(--muted);background:var(--bg);
       border:1px solid var(--line);padding:4px 8px;border-radius:999px;white-space:nowrap}
.badge.urgent{color:#dc2626;border-color:#f87171;background:#fef2f2;font-weight:700;
  animation:pulse 1.8s ease-in-out infinite}
@keyframes pulse{50%{opacity:.5}}
@media (prefers-reduced-motion:reduce){.badge.urgent{animation:none}}
.skills{display:flex;flex-wrap:wrap;gap:6px}
.skills:empty{display:none}
.kw{font-family:var(--disp);font-size:10px;color:var(--accent);
    background:color-mix(in srgb,var(--accent) 10%,transparent);
    padding:3px 9px;border-radius:999px;white-space:nowrap}
.badge.feat{color:#b45309;border-color:#fbbf24;background:#fffbeb;font-weight:700}
.badge.new{background:var(--accent);color:#fff;border-color:transparent;font-weight:700}
.badge.saved{background:color-mix(in srgb,var(--warn) 12%,var(--card));color:var(--warn);
  border-color:color-mix(in srgb,var(--warn) 40%,var(--line));font-weight:700}
.badge.applied{color:var(--success);border-color:color-mix(in srgb,var(--success) 45%,var(--line));
  background:color-mix(in srgb,var(--success) 10%,var(--card));font-weight:700}
.apply{margin-left:auto;background:var(--accent);color:#fff;text-decoration:none;
       font-family:var(--disp);font-weight:700;font-size:13px;padding:10px 16px;
       border-radius:var(--r-md);min-height:44px;display:inline-flex;align-items:center;gap:6px;
       box-shadow:0 6px 16px -8px color-mix(in srgb,var(--accent) 70%,transparent);
       transition:filter .16s ease,transform .08s ease,box-shadow .16s ease}
.apply:hover{filter:brightness(1.08);box-shadow:var(--shadow-hover)}
.apply:active{transform:translateY(1px)}
.apply svg{width:14px;height:14px;flex:none}
.card-actions{display:flex;align-items:center;gap:8px;margin-top:auto;padding-top:10px;
  border-top:1px solid var(--line);flex-wrap:wrap}
.act-btn{appearance:none;background:var(--card);border:1px solid var(--line);
  border-radius:var(--r-md);
  color:var(--muted);font-family:var(--disp);font-size:11px;font-weight:600;padding:8px 12px;
  cursor:pointer;min-height:40px;display:inline-flex;align-items:center;gap:4px;
  transition:all .15s ease}
.act-btn:hover{color:var(--ink);border-color:var(--ink)}
.act-btn.active{background:color-mix(in srgb,var(--accent) 15%,transparent);
  color:var(--accent);border-color:var(--accent)}
.act-btn.star-btn.active{color:#b45309;border-color:#fbbf24;background:#fffbeb}
.act-btn.app-btn.active{color:#047857;border-color:#34d399;background:#ecfdf5}
.act-btn.dismiss-btn:hover{color:#dc2626;border-color:#f87171;background:#fef2f2}
.act-btn.pitch-btn{color:var(--ink);font-weight:700}
.act-btn.pitch-btn:hover{background:color-mix(in srgb,var(--accent) 10%,transparent);
  color:var(--accent)}
.card.is-applied{opacity:0.62}
.card.is-applied:hover{opacity:1}
.empty{grid-column:1/-1;color:var(--muted);text-align:center;padding:48px 16px;
       border:1px dashed var(--line);border-radius:var(--r-lg);background:var(--card)}
.empty code{background:var(--bg);padding:2px 6px;border-radius:6px}
ul.srows{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:4px}
.srow{display:flex;align-items:center;gap:4px 12px;padding:12px;border-radius:var(--r-md);
  border-bottom:1px solid var(--line)}
.srow:hover{background:color-mix(in srgb,var(--ink) 3%,transparent)}
.sname{font-weight:600}
.sname a{color:inherit;text-decoration:none}
.sname a:hover{color:var(--accent);text-decoration:underline}
.sroles{color:var(--muted);font-size:13px;margin:2px 0 0}
.slinks{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap;flex:none}
.sbtn{display:inline-flex;align-items:center;gap:8px;font-family:var(--disp);
  font-size:11px;font-weight:700;padding:9px 14px;min-height:44px;border-radius:var(--r-md);
  text-decoration:none;white-space:nowrap;border:1px solid var(--line);
  color:var(--muted);background:var(--card)}
.sbtn:hover{color:var(--ink);border-color:var(--muted)}
.sbtn:active{transform:translateY(1px)}
.sbtn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
@media (max-width:640px){.srow{flex-direction:column;align-items:flex-start}.slinks{margin-left:0}
  header.top{margin:0 -16px}.toolbar{position:static}}
</style>
</head>
<body>
<a class="skip" href="#matches">Skip to matches</a>
<div class="wrap">
  <header class="top"><h1>Job pipeline</h1>
    <span class="stats" id="stats" aria-live="polite"></span></header>
  <nav class="vtabs" id="vtabs" role="tablist" aria-label="Sections">
    <button data-vtab="jobs" class="active" role="tab"
      aria-selected="true" aria-controls="vjobs">Jobs</button>
    <button data-vtab="startups" role="tab" aria-selected="false"
      aria-controls="vstartups">IITM Startups</button>
  </nav>
  <div id="vjobs" role="tabpanel">
  <section aria-labelledby="mhead">
    <h2 class="head" id="mhead">Today's matches</h2>
    <main id="matches"></main>
  </section>
  <section class="sec">
    <h2 class="head">Browse all</h2>
  <div class="toolbar">
    <div class="searchwrap">__ICO_SEARCH__<input id="q" type="search"
      placeholder="Search title, company, skills…" autocomplete="off"
      aria-label="Search jobs"></div>
    <div class="chips" id="status-chips" role="group" aria-label="Status">
      <button data-st="active" class="active" aria-pressed="true">Active</button>
      <button data-st="saved" aria-pressed="false">Saved ★</button>
      <button data-st="applied" aria-pressed="false">Applied ✓</button>
      <button data-st="all" aria-pressed="false">All</button>
    </div>
    <div class="chips" id="chips" role="group" aria-label="Tier">
      <button data-tier="all" class="active" aria-pressed="true">All Tiers</button>
      <button data-tier="A" aria-pressed="false">A</button>
      <button data-tier="B" aria-pressed="false">B</button>
      <button data-tier="C" aria-pressed="false">C</button>
    </div>
    <select id="src" aria-label="Filter by source">
      <option value="all">All sources</option>
    </select>
    <select id="sort" aria-label="Sort jobs">
      <option value="newest">Newest first</option>
      <option value="score">Top score first</option>
    </select>
    <div class="chips" id="flags" role="group" aria-label="Flags">
      <button data-flag="urgent" aria-pressed="false">Urgent</button>
      <button data-flag="featured" aria-pressed="false">Featured</button>
    </div>
    <button id="reset">Reset</button>
  </div>
  <div id="count" aria-live="polite"></div>
  <main id="grid" aria-live="polite"></main>
  </section>
  </div>
  <div id="vstartups" hidden role="tabpanel">
    <h2 class="head" id="shead">Startups</h2>
    <div class="toolbar">
      <div class="searchwrap">__ICO_SEARCH__<input id="sq" type="search"
        placeholder="Search startups…" autocomplete="off" aria-label="Search startups"></div>
      <div class="chips" id="schips" role="group" aria-label="Startup filters">
        <button data-sf="all" class="active" aria-pressed="true">All</button>
        <button data-sf="fresher" aria-pressed="false">Fresher tech roles</button>
        <button data-sf="careers" aria-pressed="false">Has careers</button>
        <button data-sf="linkedin" aria-pressed="false">Has LinkedIn</button>
        <button data-sf="website" aria-pressed="false">Has website</button>
      </div>
    </div>
    <div id="scount" aria-live="polite"></div>
    <ul class="srows" id="slist"></ul>
  </div>
</div>
<script>
const DATA = __DATA__;
const KEYWORDS = __KEYWORDS__;
const STARTUPS = __STARTUPS__;
const $ = s => document.querySelector(s);
// icons: pixelarticons (MIT, npm pixelarticons) — search + external-link
const ICO_SEARCH = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"'
  + ' aria-hidden="true"><path d="M22 22h-2v-2h2v2Zm-2-2h-2v-2h2v2Zm-6-2H6v-2h8v2Zm4'
  + ' 0h-2v-2h2v2ZM6 16H4v-2h2v2Zm10 0h-2v-2h2v2ZM4 14H2V6h2v8Zm14 0h-2V6h2v8ZM6'
  + ' 6H4V4h2v2Zm10 0h-2V4h2v2Zm-2-2H6V2h8v2Z"/></svg>';
const ICO_EXT = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"'
  + ' aria-hidden="true"><path d="M11 5H5v2h6V5ZM5 7H3v12h2V7Zm12 12H5v2h12v-2Zm2-6h-2v6h2v-6Zm-8'
  + ' 0H9v2h2v-2Zm2-2h-2v2h2v-2Zm2-2h-2v2h2V9Zm2-2h-2v2h2V7Zm2-2h-2v2h2V5Zm2-2h-2v8h2V3Z"/>'
  + '<path d="M21 3h-8v2h8V3Z"/></svg>';
const esc = s => (s ?? '').replace(/[&<>"']/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const rel = iso => {
  if (!iso) return 'unknown';
  const d = Math.floor((Date.now() - new Date(iso)) / 864e5);
  if (d <= 0) return 'today';
  if (d === 1) return '1 day ago';
  if (d < 7) return d + ' days ago';
  if (d < 30) { const w = Math.floor(d / 7); return w + (w === 1 ? ' week ago' : ' weeks ago'); }
  if (d < 365) { const m = Math.floor(d / 30);
    return m + (m === 1 ? ' month ago' : ' months ago'); }
  const y = Math.floor(d / 365);
  return y + (y === 1 ? ' year ago' : ' years ago');
};
let tier = 'all', source = 'all', sort = 'newest', status = 'active';
let urgentOnly = false, featOnly = false;
const isNew = j => j.fetched && j.posted_at
  && (Date.now() - new Date(j.fetched)) < 36e5 * 36
  && (Date.now() - new Date(j.posted_at)) < 864e5 * 7;
const SOURCES = [...new Set(DATA.map(j => j.source))].sort();
SOURCES.forEach(s => {
  const o = document.createElement('option');
  o.value = s; o.textContent = s; $('#src').appendChild(o);
});
const bySort = (a, b) => sort === 'score'
  ? (b.score - a.score || (b.posted_at || '').localeCompare(a.posted_at || ''))
  : (b.posted_at || '').localeCompare(a.posted_at || '');
const RES = KEYWORDS.map(k => /^[a-z0-9]+$/.test(k) ? new RegExp('\\b' + k + '\\w*') : null);
function hits(j){
  const t = (j.title + ' ' + j.company + ' ' + j.location + ' ' + (j.text||'')).toLowerCase();
  const m = KEYWORDS.filter((k, i) => RES[i] ? RES[i].test(t) : t.includes(k));
  return m.filter(k => !m.some(o => o !== k && o.includes(k))).slice(0, 8);
}

function stats(){
  const rep = DATA.filter(j => j.in_report).length;
  const fresh = DATA.filter(isNew).length;
  $('#stats').textContent = rep + ' matches today · ' + fresh + ' new · '
    + DATA.length + ' tracked · updated __STAMP__';
}

function match(j){
  const key = j.source + ':' + j.id;
  const isSaved = localStorage.getItem('star_' + key) === '1';
  const isApplied = localStorage.getItem('app_' + key) === '1';
  const isDismissed = localStorage.getItem('dis_' + key) === '1';

  if (status === 'active' && (isDismissed || isApplied)) return false;
  if (status === 'saved' && !isSaved) return false;
  if (status === 'applied' && !isApplied) return false;
  if (status !== 'all' && isDismissed && status !== 'active') return false;

  if (tier !== 'all' && j.tier !== tier) return false;
  if (source !== 'all' && j.source !== source) return false;
  if (urgentOnly && !j.urgent) return false;
  if (featOnly && !j.featured) return false;
  const q = $('#q').value.trim().toLowerCase();
  if (!q) return true;
  return (j.title + ' ' + j.company + ' ' + j.location + ' ' + j.source + ' ' + (j.text||''))
    .toLowerCase().includes(q);
}

function copyPitch(btn, id, source){
  const j = DATA.find(x => x.id === id && x.source === source);
  if (!j) return;
  const sk = hits(j);
  const blob = (j.title + ' ' + (j.text||'')).toLowerCase();
  let text = '';
  if (sk.some(k => ['mlir', 'llvm', 'compiler', 'kernel'].includes(k)) || blob.includes('mlir')) {
    text = "Hi! I noticed your opening for " + j.title + " at " + (j.company || 'your team')
      + ". At Blubridge Technologies, I built MLIR operator-fusion passes and custom tensor"
      + " dialect lowerings cutting kernel launch overhead by ~20%. I'd love to bring this"
      + " systems expertise to your team: https://github.com/barryallen16";
  } else if (sk.some(k => ['tokenizer', 'bpe', 'tamil'].includes(k))
             || blob.includes('tokenizer')) {
    text = "Hi! I saw the " + j.title + " opening at " + (j.company || 'your team')
      + ". I developed an open-source BPE tokenizer for Tamil in Rust that's 11-16x faster than"
      + " SentencePiece (published on Hugging Face: https://github.com/barryallen16/tamil-tokenizer)."
      + " I'd love to chat about how my NLP infra background aligns with the role!";
  } else if (sk.some(k => ['lora', 'unsloth', 'vlm', 'qwen', 'distillation'].includes(k))
             || blob.includes('lora') || blob.includes('fine-tun')) {
    text = "Hi! I saw you're hiring for " + j.title
      + ". I'm the first author of an IEEE 2026 paper on VLM distillation using Qwen3-VL and LoRA"
      + " (FitCheck, 3.14x less VRAM, model and datasets on Hugging Face). I'd love to bring"
      + " my fine-tuning and evaluation experience to " + (j.company || 'your team') + "!";
  } else if (sk.some(k => ['fastapi', 'docker', 'backend'].includes(k))) {
    text = "Hi! I'm reaching out for " + j.title + " at " + (j.company || 'your team')
      + ". I build end-to-end backend & ML systems, including a Dockerized FastAPI control plane"
      + " sharding GPU workloads across multi-account pools with CI/CD and Telegram alerting"
      + " (https://github.com/barryallen16/kaggle-automation). Would love to connect!";
  } else {
    text = "Hi! I'm reaching out about the " + j.title + " role at " + (j.company || 'your team')
      + ". I'm a 2026 AI graduate building AI systems bottom-up: open-model inference, Rust infra,"
      + " and human evaluation harnesses (work at https://github.com/barryallen16)."
      + " Would love to discuss how I can contribute!";
  }
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = 'Copied ✓';
    btn.classList.add('active');
    setTimeout(() => { btn.innerHTML = orig; btn.classList.remove('active'); }, 1800);
  });
}

function toggleStar(key){
  const cur = localStorage.getItem('star_' + key) === '1';
  if (cur) localStorage.removeItem('star_' + key);
  else localStorage.setItem('star_' + key, '1');
  render();
}
function toggleApp(key){
  const cur = localStorage.getItem('app_' + key) === '1';
  if (cur) localStorage.removeItem('app_' + key);
  else localStorage.setItem('app_' + key, '1');
  render();
}
function toggleDismiss(key){
  const cur = localStorage.getItem('dis_' + key) === '1';
  if (cur) localStorage.removeItem('dis_' + key);
  else localStorage.setItem('dis_' + key, '1');
  render();
}

function card(j){
  const key = j.source + ':' + j.id;
  const isSaved = localStorage.getItem('star_' + key) === '1';
  const isApplied = localStorage.getItem('app_' + key) === '1';

  const apply = j.url
    ? '<a class="apply" href="' + esc(j.url)
      + '" target="_blank" rel="noopener">Apply ' + ICO_EXT + '</a>'
    : '';
  const sk = hits(j);
  return '<article class="card' + (isApplied ? ' is-applied' : '') + '">'
    + '<div class="row"><span><span class="tier ' + j.tier + '" title="score '
    + j.score + '">Tier ' + j.tier + '</span>'
    + (isNew(j) ? ' <span class="badge new">New</span>' : '')
    + (isSaved ? ' <span class="badge saved">★ Saved</span>' : '')
    + (isApplied ? ' <span class="badge applied">'
      + '✓ Applied</span>' : '')
    + '</span>'
    + '<span class="score" title="' + esc(j.posted_at || '') + '">'
    + rel(j.posted_at) + '</span></div>'
    + '<h3>' + (j.url
        ? '<a href="' + esc(j.url) + '" target="_blank" rel="noopener">' + esc(j.title) + '</a>'
        : esc(j.title)) + '</h3>'
    + '<p class="meta">' + esc(j.company || '—')
    + (j.location ? ' · ' + esc(j.location) : '') + '</p>'
    + (sk.length ? '<div class="skills">'
      + sk.map(h => '<span class="kw">' + esc(h) + '</span>').join('') + '</div>' : '')
    + '<div class="foot"><span class="badge">' + esc(j.source) + '</span>'
    + (j.urgent ? '<span class="badge urgent">Urgent</span>' : '')
    + (j.featured ? '<span class="badge feat">Featured</span>' : '')
    + '</div>'
    + '<div class="card-actions">'
    + '<button class="act-btn pitch-btn" onclick="copyPitch(this,\\'' + esc(j.id)
    + '\\',\\'' + esc(j.source) + '\\')" title="Copy personalized pitch message">Pitch</button>'
    + '<button class="act-btn star-btn' + (isSaved ? ' active' : '')
    + '" onclick="toggleStar(\\'' + esc(key) + '\\')" title="Bookmark this role">★'
    + (isSaved ? ' Saved' : '') + '</button>'
    + '<button class="act-btn app-btn' + (isApplied ? ' active' : '')
    + '" onclick="toggleApp(\\'' + esc(key) + '\\')" title="Mark as applied">✓'
    + (isApplied ? ' Applied' : '') + '</button>'
    + '<button class="act-btn dismiss-btn" onclick="toggleDismiss(\\''
    + esc(key) + '\\')" title="Hide this role">✕</button>'
    + apply
    + '</div>'
    + '</article>';
}
function render(){
  const mrows = DATA.filter(j => j.in_report && match(j))
    .sort((a,b) => a.tier.localeCompare(b.tier) || b.score - a.score);
  const brows = DATA.filter(match).sort(bySort);
  $('#mhead').textContent = "Today's matches · " + mrows.length;
  $('#matches').innerHTML = mrows.length
    ? mrows.map(card).join('')
    : '<div class="empty">No matches today. Browse everything below.</div>';
  $('#grid').innerHTML = brows.length
    ? brows.map(card).join('')
    : '<div class="empty">No jobs match these filters. '
      + 'Try widening the search or press Reset.</div>';
  $('#count').textContent = 'Showing ' + brows.length + ' of ' + DATA.length + ' jobs';
}
$('#chips').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  tier = b.dataset.tier;
  $('#chips').querySelectorAll('button').forEach(x => {
    const on = x === b; x.classList.toggle('active', on); x.setAttribute('aria-pressed', on);
  });
  render();
});
$('#status-chips').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  status = b.dataset.st;
  $('#status-chips').querySelectorAll('button').forEach(x => {
    const on = x === b; x.classList.toggle('active', on); x.setAttribute('aria-pressed', on);
  });
  render();
});
$('#q').addEventListener('input', render);
$('#src').addEventListener('change', e => { source = e.target.value; render(); });
$('#sort').addEventListener('change', e => { sort = e.target.value; render(); });
$('#flags').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  const on = b.dataset.flag === 'urgent'
    ? (urgentOnly = !urgentOnly) : (featOnly = !featOnly);
  b.classList.toggle('active', on);
  b.setAttribute('aria-pressed', on);
  render();
});
$('#reset').addEventListener('click', () => {
  $('#q').value = '';
  tier = 'all'; source = 'all'; sort = 'newest'; status = 'active';
  urgentOnly = featOnly = false;
  $('#src').value = 'all'; $('#sort').value = 'newest';
  $('#chips').querySelectorAll('button')
    .forEach(x => {
      const on = x.dataset.tier === 'all';
      x.classList.toggle('active', on); x.setAttribute('aria-pressed', on);
    });
  $('#status-chips').querySelectorAll('button')
    .forEach(x => {
      const on = x.dataset.st === 'active';
      x.classList.toggle('active', on); x.setAttribute('aria-pressed', on);
    });
  $('#flags').querySelectorAll('button').forEach(x => {
    x.classList.remove('active'); x.setAttribute('aria-pressed', 'false');
  });
  render();
});
function showTab(v){
  $('#vtabs').querySelectorAll('button')
    .forEach(x => {
      const on = x.dataset.vtab === v;
      x.classList.toggle('active', on); x.setAttribute('aria-selected', on);
    });
  $('#vjobs').hidden = v !== 'jobs';
  $('#vstartups').hidden = v !== 'startups';
}
$('#vtabs').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  showTab(b.dataset.vtab);
});
let sq = '', sfilter = 'all';
function smatch(r){
  if (sfilter === 'fresher' && !r.roles) return false;
  if (sfilter === 'careers' && !r.careers) return false;
  if (sfilter === 'linkedin' && !r.linkedin) return false;
  if (sfilter === 'website' && !r.website) return false;
  if (sq && !(r.name + ' ' + (r.roles || '')).toLowerCase().includes(sq)) return false;
  return true;
}
function sbtn(href, label, primary){
  if (!href) return '';
  return '<a class="sbtn' + (primary ? ' primary' : '') + '" href="' + esc(href)
    + '" target="_blank" rel="noopener">' + label + '</a>';
}
function srender(){
  const rows = STARTUPS.filter(smatch);
  $('#shead').textContent = 'Startups · ' + rows.length;
  $('#scount').textContent = rows.length === STARTUPS.length
    ? 'Showing all ' + rows.length
    : 'Showing ' + rows.length + ' of ' + STARTUPS.length;
  $('#slist').innerHTML = rows.length ? rows.map(r => {
    const home = r.website || r.linkedin || r.careers || '#';
    return '<li class="srow"><div><div class="sname"><a href="' + esc(home)
      + '" target="_blank" rel="noopener">' + esc(r.name) + '</a></div>'
      + (r.roles ? '<p class="sroles">' + esc(r.roles) + '</p>' : '') + '</div>'
      + '<div class="slinks">' + sbtn(r.careers, 'Careers', true)
      + sbtn(r.linkedin, 'LinkedIn', false) + sbtn(r.website, 'Website', false)
      + '</div></li>';
  }).join('')
    : '<div class="empty">No startups match. Clear the search or pick All.</div>';
}
$('#sq').addEventListener('input', e => { sq = e.target.value.trim().toLowerCase(); srender(); });
$('#schips').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  sfilter = b.dataset.sf;
  $('#schips').querySelectorAll('button').forEach(x => {
    const on = x === b; x.classList.toggle('active', on); x.setAttribute('aria-pressed', on);
  });
  srender();
});
stats(); render(); srender();
</script>
</body>
</html>
"""


def write_html(conn: sqlite3.Connection, path: Path, keywords=None) -> int:
    """Write the self-contained UI. Returns number of jobs embedded."""
    rows = conn.execute(
        "SELECT source, ext_id, url, title, company, location, text, posted_at, fetched_at,"
        " tier, score, in_report, is_urgent, is_featured FROM jobs"
    ).fetchall()
    data = [
        {
            "source": r["source"],
            "id": r["ext_id"],
            "url": r["url"],
            "title": r["title"],
            "company": r["company"],
            "location": r["location"],
            "text": (r["text"] or "")[:500],
            "posted_at": r["posted_at"],
            "fetched": r["fetched_at"],
            "tier": r["tier"],
            "score": r["score"],
            "in_report": bool(r["in_report"]),
            "urgent": bool(r["is_urgent"]),
            "featured": bool(r["is_featured"]),
        }
        for r in rows
    ]
    blob = json.dumps(data).replace("<", "\\u003c")
    kwblob = json.dumps(sorted(set(keywords or []))).replace("<", "\\u003c")
    stblob = json.dumps(_load_startups(), ensure_ascii=False).replace("<", "\\u003c")
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    html = PAGE.replace("__DATA__", blob).replace("__KEYWORDS__", kwblob)
    html = html.replace("__STARTUPS__", stblob).replace("__FAVICON__", _favicon_link())
    html = html.replace("__FONTFACE__", _fontface())
    html = html.replace("__ICO_SEARCH__", ICO_SEARCH_SVG)
    path.write_text(html.replace("__STAMP__", stamp), encoding="utf-8")
    return len(data)
