# FINDINGS — fresher job pipeline research

Persisted so this conversation survives context rot. **Last updated: 2026-09-25.**
Profile lives in `profile.json` (gitignored — contains phone/email).

---

## 1. Decision ledger

| # | Question | Decision | Status |
|---|---|---|---|
| Q1 | Location scope | **Chennai + Remote (India)**; "fully remote anywhere" = bonus tier only | locked |
| Q2 | Fresher definition | Pass if ANY: experience **0–2 yrs** / batch **2025–2026–2027** / intern. Exclude: `3+ years`, `4+ years`, `senior`, `staff`, `lead`, `5+ yrs`, `experienced only`. Interns get an `intern` tag, not dropped | locked |
| Q3 | Match tiers | **A** GenAI/ML/NLP/LLM-infra/data-eng (always shown) · **B** Python/backend/FastAPI/TS (shown, ranked below A) · **C** other fresher matches → **SQLite only, not in report** | locked |
| Q4 | LinkedIn path | **Option D only**: `linkedin-search` guest endpoints, ~2 queries/day. No MCP, no burner, no email alerts | locked |
| Q5 | freehire vs RSS | **freehire added, RSS dropped** (freehire is structured, ToS-clean, proven India coverage; Naukri/Indeed no longer offer open RSS) | locked |
| Q6 | Threads | **dropped** — cookieless search is dead (verified: query term absent from payload), no paid Apify; revisit only if user offers cookies | locked |
| Q7 | WhatsApp export drop folder | **`data/whatsapp_exports/*.txt`** (gitignored); "Chat export → Without media"; idempotent dedupe by `sha1(date\|author\|text)` | locked |
| Q8 | Schedule time + `schtasks` | **daily 08:30 local (=IST)** via `daily.bat`; sources fail independently → `run.log`, report still ships | locked |
| Q9 | Report format / retention | **top 20**: all Tier A (passes Q2/Q1) then Tier B with **≥3** profile keywords; **>14 days = stale** → excluded from report, kept in DB; **prune DB after 90 days**; output `report.md` + SQLite | locked |

**Matcher decision:** keyword scoring, **no LLM** (deterministic, ms-fast, pytest-able).

---

## 2. Goal

Daily pipeline that scrapes fresher job postings, stores them, scores against `profile.json`, writes `report.md`.

Sources decided for v1: **X (twitter-cli, burner cookies) · LinkedIn (guest endpoints) · freehire (public API) · WhatsApp (chat exports) · [Threads pending Q6]**.

---

## 3. Source survey (first search round)

**X/Twitter job scrapers**
- `kumardigamberjha/X_job_hunter_bot` — Playwright live-search poller, cookie auth (`x_cookies.json`), 15-min loop + jitter, Discord embeds, dedupe + noise filter. Closest match to "watch X for hiring posts".
- `ShreeshaBhat1004/Job-scout` — Tweepy (official API) + Hacker News, resume→TF-IDF ranking, ML-focused.
- `Harsh-C7/JobScraper` — 12 sources; X via **DuckDuckGo dorking**, SQLite dedupe, Excel output.
- `pranavsaji/Job-finder` — X + LinkedIn + Reddit + HN, FastAPI/Next.js, Claude outreach drafts.
- PyPI `prospect-jobs` — Playwright X search → LLM score → Streamlit dashboard.
- dev.to article "Find Jobs on Twitter" — Sorsa paid API ($49/mo), keyword cross-multiply, follower≥50 filter, SQLite dedupe. Key quote: headless X scrapers "get rate-limited or blocked within hours".

**Threads** — only generic scrapers exist: `data-scrape/threads-scraper`, `Chuanyin1202/threads-toolkit` (Apify), `vdite/threads-scraper` (Playwright BFS replies), `anatolykoptev/go-threads` (Go lib: public API claims no-auth profile/thread reads). No job-specific one.

**Instagram** — `vastavikadi/multimodal-job-extractor`: Playwright crawl + yt-dlp + EasyOCR + Faster-Whisper + Gemini → structured job records from job *Reels*. (Instagram only, not Threads.)

**WhatsApp job sources**
- `femakin/JobScraper` — **Baileys group listener + OpenAI parser** of job messages; 15 sources, Next.js, Twilio alerts. Only real job+WhatsApp project.
- `puneetdixit200/openwa` — read-only placement-group collector (OpenWA), hashes senders, daily archives, no classification.
- `ericporres/whatsapp-mcp-server` — Baileys MCP (7 tools: list/get/search/export groups), chat intelligence briefings.

---

## 4. Agent-Reach assessment (`Panniantong/Agent-Reach`)

~77k stars, MIT, created 2026-02-24. **Not a scraper** — a router/installer/health-checker that delegates to upstream CLIs; `agent-reach doctor` re-routes when a backend dies (it retired yt-dlp for Bilibili after 412s).

| Need | Answer | Cookie? |
|---|---|---|
| X search | `twitter search "..." -n 10` via `twitter-cli` | **Yes — `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`** (2 env vars). Single-tweet read = zero-config |
| LinkedIn jobs | `mcporter call linkedin.search_jobs keywords=... location=... max_pages=2` | Yes (rejected — see §6) |
| Free web search | Exa via mcporter, **free no key** | No |
| RSS | `feedparser` zero-config | No |
| Page → text | Jina Reader `curl https://r.jina.ai/URL` free no key | No |
| Threads | ❌ no channel | — |
| WhatsApp | ❌ no channel | — |

**Verdict: use it.** It deletes our entire X scraper and replaces Brave (Exa is free). Still ours: Threads, WhatsApp, storage, matcher, report, scheduler.
**Install gotcha:** `grill-me`-style alias problem does not apply here, but agent-reach installs external CLIs — needs `--system` approval.

---

## 5. Scrapling vs Crawl4AI (PyPI metadata pulled directly)

| | Scrapling 0.4.15 | Crawl4AI 0.9.4 |
|---|---|---|
| Core deps | `lxml, cssselect, orjson, tld, w3lib` — **lean** | `litellm, numpy, nltk, shapely, pillow, rank-bm25, lark, pydantic, httpx, playwright, patchright, playwright-stealth` — **heavy** |
| Browser | `scrapling[fetchers]` extra (playwright, patchright, curl_cffi) | always |
| Strength | adaptive element relocation (site change → re-find), blocked-detect, AutoThrottle, Cloudflare Turnstile solve, spider API | Markdown/BM25/Pruning output, LLM extraction, RAG-oriented |
| Fit for us | Fetch layer: cookie sessions, block detection, auto backoff | Markdown/LLM extraction we don't need (short social posts, keyword matcher) |

**Verdict: Scrapling over Crawl4AI if a fetch framework is needed at all** — Crawl4AI drags an LLM stack for a feature we deliberately skipped. Caveat: neither solves X anti-bot (Scrapling's Turnstile bypass targets Cloudflare, X is not Cloudflare). Decision deferred in favour of agent-reach's `twitter-cli`.

---

## 6. LinkedIn policy verification (primary sources)

1. **User Agreement §8.2** (eff. 2024-11-20, linkedin.com/legal/user-agreement) bans:
   - *"Develop, support or use software, devices, scripts, robots or any other means or processes ... to **scrape or copy the Services**"*
   - *"Use **bots or other unauthorized automated methods to access the Services**"*
   - *"**bypassing or circumventing any access controls or use limits** (such as search results, profiles, or videos)"*
2. **§2.1** — *"you will only have **one LinkedIn account, which must be in your real name**"*; §8.2 bans *"Creating a false identity ... or using another's account (**such as sharing log-in credentials or copying cookies**)"* → **burner account = independent violation.**
3. **LinkedIn Help a1341387 "Prohibited software and extensions"** — no crawlers/bots/extensions that scrape or automate; violators *"risk having their accounts **restricted or shut down**"*.
4. **`LinkedIn v. ProAPIs`** (filed Oct 2025) — LinkedIn litigates scraper-API operators running fake-account mills. Same pattern as burner + MCP.
5. **No sanctioned API for individuals.** Job Posting API is employer-side and *"currently not accepting new partnerships"*; all other APIs are OAuth + partner-gated.
6. **hiQ v. LinkedIn (9th Cir. 2022)** — scraping *public logged-out* profiles isn't a CFAA crime. Criminal-law limit only; does **not** license breach of contract, and does not cover logged-in member access.

**Options table (final):**

| Option | Account risk | Policy |
|---|---|---|
| **D — `linkedin-search` guest endpoints** | **None** (no account attached) | ToS-gray, keep volume low |
| A — job-alert emails via IMAP | None | Fully compliant (chosen *against* in Q4) |
| B — MCP `search_jobs` + real account | Real | Explicit §8.2 violation |
| C — burner account + cookies | n/a | §2.1 + §8.2 double violation — **dead** |

---

## 7. Live experiment log (run from this machine, 2026-09-25)

| Target | Result | Conclusion |
|---|---|---|
| `x.com/search?q=fresher+hiring` | **HTTP 307, 0 bytes** | Logged-out X search = login wall. Dead. |
| `api.x.com/2/search/tweets` | **403** | Guest token search unavailable. |
| `html.duckduckgo.com/html/?q=site:x.com...` | **HTTP 202**, 0 parsed results | DDG bot challenge from this IP. |
| `lite.duckduckgo.com/lite/` | **HTTP 202** | Same. |
| `bing.com/search?q=site:x.com+hiring` | 200 but **0 x.com hits**, junk results | Bing ignores/degrades `site:` here. |
| `nitter.net/search` | **000 connection refused** | Nitter dead. |
| `syndication.twitter.com/srv/timeline-profile/...` | **HTTP 429** | Endpoint alive, rate-limited. Cookieless per-profile timeline = possible with backoff. |
| `cdn.syndication.twimg.com/timeline/profile` | 200, **0 bytes** | Deprecated. |
| **freehire** `GET /api/v1/agent/jobs/search?q=python+developer&countries=in&posted_within_days=14` | **200, 8 real hits** | ✅ Turing/Bengaluru, iCapital/Jaipur, Capco/Mumbai, Luxoft, Zensar. **No key, no auth.** |
| freehire `countries=India` | **0 hits** | ⚠️ Facet takes ISO codes — `in`, not `India` (silent empty result). |
| **Threads** `threads.com/search?q=hiring+fresher` | 200, **0 post codes, query term absent** | Empty shell; search auth-gated. |
| **Threads** `threads.com/@nasa` (after `-L`) | 200, **identical 283,710 bytes**, `nasa` absent | Logged-out profile reads also return a shell. **Correction:** earlier claim that cookieless Threads search yields ~20 results came from Apify READMEs and is **not reproducible here**. |
| Google Custom Search JSON API | — | **Closed to new customers**, discontinues 2027-01-01. Not an option. |
| Brave Search API | — | $5 free credits/mo (≈1,000 queries) with $0 prepay + card on file. Viable fallback, currently unused. |

---

## 8. X ban-risk ladder

1. **DuckDuckGo dorking** — no login → zero account risk (but DDG blocked here).
2. **Logged-out guest endpoints** — low risk, mostly dead (see log).
3. **Your cookies in Playwright, low volume** — moderate; symptoms: "Something went wrong", 429, soft restriction. Recoverable by dormancy.
4. **Your cookies + aggressive pagination / any write automation** — real suspension risk.

**Chosen:** `twitter-cli` with **2 env vars from a burner account** (never the personal account), read-only, no Playwright fingerprint games. Fallback if blocked: syndication timeline endpoint with 429 backoff.

---

## 9. Reference projects (application side, downstream)

`MadsLorentzen/ai-job-search` — 43.9k stars, MIT, Claude Code framework: `/setup /scrape /rank /apply /interview /outcome`. Needs paid Claude + LaTeX. Stealable:

1. **`.agents/skills/linkedin-search/`** — bun CLI over LinkedIn's public `jobs-guest` endpoints, zero runtime deps:
   ```bash
   bun run .agents/skills/linkedin-search/cli/src/cli.ts \
     search -l "Chennai, Tamil Nadu, India" -q "fresher python" --jobage 7 --format json
   ```
   Flags: `--jobage 1|7|14|30`, `--jobage-minutes`, `--remote remote|hybrid|onsite`, `--page`, `--limit`, `detail <id|url>`. Its own SKILL.md: *"automated access is against LinkedIn's ToS — keep volume low, personal use only."*
2. **`.agents/skills/freehire-search/`** — bun CLI over `https://freehire.me/api/v1/agent/jobs/search`; params `q`, `limit`, `offset`, `posted_within_days`, `work_mode`, facets `regions|countries|cities|seniority|category|skills` (ISO country codes). Self-hostable via `FREEHIRE_API_URL`.
3. **Portal-skill contract** — each source = folder with `search`/`detail` CLI, `--format json|table|plain`, `enabled:` flag in `SKILL.md`, own tests. `/scrape` auto-discovers. **Adopt this as our source interface** instead of inventing one.

Also available there if wanted later: `/rank` fit framework, drafter-reviewer `/apply`, `/gmail-sync` status detection.

---

## 10. Architecture (as built, 2026-09-25)

```
run.py            daily entrypoint (schtasks → daily.bat, 08:30 IST)
jobpipe/sources.py freehire (urllib JSON), linkedin guest (urllib HTML),
                  x (twitter-cli subprocess --json), whatsapp (.txt exports),
                  jobportal (urllib JSON: /api/v1/jobs + pagination),
                  fresherflow (urllib JSON: github raw feed),
                  threads (threads-scraper subprocess → CSV → post rows)
                  → Posting(source, ext_id, url, title, company, location, text, posted_at)
jobpipe/store.py  SQLite data/jobs.db — dedupe by (source, ext_id), tier/score/in_report
jobpipe/match.py  Q1 location gate, Q2 fresher filter, Q3 tiers, profile.json scoring
jobpipe/report.py report.md — A first, then B (≥3 keywords), C stays DB-only
jobpipe/page.py   report.html — single-page UI (no tabs): Today's matches first,
                  then filterable Browse all (search, tier chips, source dropdown,
                  newest/score sort, urgent/featured toggles, reset, live counts),
                  cards with tier pill, New badge, skill chips, Apply link; no server
tests/            13 pytest cases (filters, gates, dedupe, report, whatsapp parse, jobportal parse)
```

Runtime deps: **none** (stdlib urllib/sqllib/re only). Dev: ruff + pytest via uv.
Toolchain per global rules: **uv**, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`; commit every small verified change, never push.

---

## 11. Open questions

None — Q1–Q9 all locked in the decision ledger (§1).

---

## 12. Build log (2026-09-25)

- Implemented per §10; all checks green (ruff, format, 9 tests); live run: freehire 98 + LinkedIn 16 stored, report renders, X fails gracefully without cookies, WhatsApp waits for exports.
- **freehire**: `countries=` takes ISO codes (`in`, not `India` — silent 0 hits); `description_format=text`.
- **LinkedIn**: called the guest endpoint directly with urllib — no bun, no vendored `linkedin-search` CLI (that repo's skill shells out to bun; ours needs none). 10 cards/page, id in `urn:li:jobPosting:`, date in `<time datetime=…>`.
- **twitter-cli 0.8.5** installed via `uv tool install twitter-cli`. Needs `TWITTER_AUTH_TOKEN` + `TWITTER_CT0` (burner account, Q4 ladder L1). **agent-reach NOT installed** — we call `twitter` directly, so its router adds nothing (supersedes §4 verdict for this project).
- **Location gate bug fixed**: dropped `india` from the regex — every freehire row ends ", India", so it passed all of India. Gate is now `chennai|remote|wfh` only; empty location (X/WhatsApp) falls back to the message text.
- **Tier A bug fixed**: removed bare `transformers?` (matched "MSC Transformers", an electrical-transformer maker).
- **Report bug fixed**: selection now enforces Q9 itself (A always, B needs ≥3, C never) — classify alone wasn't enough because report re-selected rows from the DB.
- Classify runs over the **whole DB** each run, not just new rows, so rule changes retro-fix old rows.
- `run.py` creates `data/whatsapp_exports/` automatically; drop exports there.
- **UI**: `report.html` generated on every run (`uv run run.py --open` to launch it). Three tabbed card grids — Report (today's matches), All jobs (full DB), By tier (A/B/C sections) — plus instant search and tier chips; all client-side, works offline from file://.
- **X live (all 4 sources green)**: `twitter-cli 0.8.5` search was broken upstream (SearchTimeline 404 — logged-out x.com no longer serves `ondemand.s`, so no transaction header; upstream issues #69/#78, unfixed on PyPI). **Local patch applied** to `%APPDATA%\uv\tools\twitter-cli\Lib\site-packages\twitter_cli\client.py` `_ensure_client_transaction()`: fetch authenticated `https://x.com/home` with session cookies instead of logged-out `x.com`. ⚠️ `uv tool upgrade twitter-cli` will revert this — re-apply until upstream merges (PRs #71/#79/#86).
- **X field mapping**: tweet JSON uses camelCase — `createdAtISO`/`createdAt` (not `created_at`), `author.screenName` (not `screen_name`), `author` is a dict; `url` built as `https://x.com/{screenName}/status/{id}`.
- **WhatsApp**: "Without media" exports are always `.zip` — parser reads `.txt` entries inside the zip (ignores media/macOS junk) and accepts both styles: iOS `[25/09/2026, 9:15:30 AM] A: m` and Android `18/08/26, 15:51 - A: m` (24h, 2-digit year, no brackets).
- **Registry env extraction gotcha**: when reading `setx` values via bash `reg query`, use `awk '/REG_SZ/{print $NF}'` — a plain `$NF` picks up blank/key-path lines, and the embedded newline makes curl fail with `curl: (43)` (header injection). The scheduled task reads the registry natively, so it was never affected.
- **jobportal (CareerDiscover, job-portal-zeta-two-46.vercel.app)**: Next.js App Router; `/` is a 404 shell, real listing at `/jobs`. Only 4 client API routes exist in the JS bundles (`/api/v1/jobs`, `/api/v1/categories`, `/api/admin/me`, `/api/settings`) — no detail API; detail is SSR at `/jobs/detail/{slug}` (apply URL lives there as `applicationUrl` in the RSC payload and description in `<meta name=description>` — not fetched; the detail URL itself is the posting link). `GET /api/v1/jobs?page=&limit=&keyword=&sector=&workMode=&employmentType=&experienceLevel=&categoryId=&minSalary=&sort=&city=&isFeatured=&isUrgent=` → `{success, data[10/page], pagination{total,page,limit,totalPages}}`, no auth (33 jobs total at build time). List items carry no description/apply URL — `text` is built from title+company+type+level+mode+sector+category+requiredSkills; location is deduped city/state/country (Remote jobs arrive as Remote/Remote/IN); `publishedAt || createdAt` → posted_at; `ext_id=jp-{id}`. Added to default `--sources`; runs inside the existing 08:30 task with no schedule change.
- **Scoring overhaul (precision, Q1/Q2/Q9 gates untouched)**: the keyword list was polluted — `engineer` hit 169/262 rows, `yt` (a yt-dlp split fragment) matched "everything"/"analytics" 106×, `plus`/`clip`/`dlp`/`face` were noise, `rust` matched "trust". Now: whole skill items + solid tokens (len≥4 + stoplist), headline tokens (len≥3), project tech harvested (rayon, qwen2/3, flask, supabase, scikit...); single-token matching is word-prefix (`rust`≠`trust` but `infra`=`infrastructure`); subsumed hits collapse (`sql`+`sqlite`=1); score = distinct skills. The old test fixture itself passed only via the `yt`-inside-"Python" junk point — fixed to use real skills.
- **Fresher gate**: dropped vacuous `\bget\b` (matched the verb "get"; measured zero rows relied on it); added trainee/apprentice/walk-in/off-campus, year ranges without leading zero (`1-2 years`, `2+ years`), `class of`; exclude adds architect/founder/cto/ceo. Deliberately still strict on no-signal titles (31 LinkedIn/jobportal rows like bare "AI Engineer" stay out — with no description they'd flood Tier A at score ~0).
- **Tiers**: A += tokenizer/embeddings/inference/LoRA/HuggingFace/diffusion/GPT/BERT/RLHF/annotation terms + plurals (`llms?`, `language models?`); B += rust/flask/react/devops/docker/k8s/graphql/node/next/mongo/redis/aws/azure/gcp/kafka/spark/airflow/terraform/supabase/ci-cd/rest-api + `APIs` plural (while `rapid` still correctly excluded); location guards `remote sensing`.
- **Measured on all 262 rows** (dumped classifications to temp JSON before editing, diffed after): 18 score changes — all junk-point removals; 1 tier fix (Azure DevOps C→B); report 5→4 (dropped a software-testing role that only passed on junk points; verified it isn't the user's stack). Spot-check of the odd Tier A ("Junior Security Analyst") confirmed legit: description is AI/LLM penetration testing (prompt injection).
- **UI transparency**: cards show matched-skill chips (computed client-side from embedded keywords under the same rules — no schema change), header shows A/B/C counts, search covers source, Urgent badge pulses (disabled under prefers-reduced-motion). report.md lines now show `skills: …`.
- **fresherflow (FresherFlow India-Jobs-Internships, fresherflow.github.io)**: static site, jobs baked into inline JS as `window.__FEED__ = {lastUpdated, count, jobs[]}` — but the same data lives as raw JSON in the repo, so the source reads `https://raw.githubusercontent.com/FresherFlow/India-Jobs-Internships/main/data/jobs.json` directly (no HTML scraping, no auth). Schema: `{id, title, company, type JOB|INTERNSHIP, status PUBLISHED|EXPIRED, locations[], workMode ONSITE|HYBRID|REMOTE|'', applyLink (direct!), dateAdded YYYY-MM-DD, addedAt ISO, tags[], notesHighlights}`. 127 rows, 81 PUBLISHED at build time — EXPIRED skipped, `ext_id=id`. Location = locations + workMode title-cased when not duplicated (REMOTE rows in city lists still pass the gate via the appended `, Remote`). 6 Chennai + 8 Remote rows pass gates; first fetch added 0 to report (fresh A-row was stale-dated) — feed is mostly north-India onsite, so expect low yield.
- **UI redesign (taste skill + ux-design)**: design read = personal data-tool dashboard for solo scanning; dials 5/3/6 (familiar tool patterns, static + hover only, dense but readable). One accent (indigo) locked; status colors (tier/urgent/featured) unchanged. New filter row: text search + tier chips (kept) + source dropdown (built from DATA, survives new sources) + sort (Newest/Top score) + Urgent/Featured toggle chips + Reset. Report tab keeps curated order; other views respect sort. Live "Showing N of M" count after every interaction; empty states point at Reset. Verified headless in node with stubbed DOM against real 343-row DATA: report 4, fresherflow 81, urgent 27, featured 28, tier A 6.
- **UI rewrite (tabs deleted)**: the 3-tab IA confused the reader (tabs + tier chips were two navigations doing one job), cards led with insider `score N`, and a daily pipeline never showed what's new. Now one page: **Today's matches** (curated, rank-ordered) on top, **Browse all** below with the filter bar directly above the grid it affects. Deleted: tabs + dead CSS. Cards now lead with Tier pill + blue **New** badge (fetched ≤36h and posted ≤7d) + relative time top-right; score moved into the tier pill's tooltip; stats line reads "4 matches today · 123 new · 343 tracked". Verified headless against live DATA (matches 4, browse 343, all filters narrow correctly).
- **IITM Startups tab**: that repo is a startup *directory* (212 IITM Research Park ventures: name/company_page/linkedin/careers_page, sourced from respark.iitm.ac.in), not a job board — so it merged as a second **IITM Startups** tab (Jobs vs Startups = two datasets, no clash with the deleted 3-view confusion), not as pipeline rows. `write_html` reads `../iitm-startups/iitm-startups.csv` + `raw/fresher_roles.json` (company → curated fresher roles, 34 mapped) at generation and embeds both; graceful empty fallback if the sibling repo is absent. Tab has its own search (name + roles), All/Fresher-tech-roles/Has-careers/Has-LinkedIn/Has-website chips, Careers(primary)/LinkedIn/Website buttons, dense rows collapsing to column <640px. The white pixel-building `favicon.svg` ships via data-URI `<link rel=icon>` with a transparent background (user override — nearly invisible on light browser chrome by design). Verified headless: 212 rows, search narrows to 1, careers filter 192.
- Note: the live `index.html` over there has a Fresher-tech-roles chip + `FRESHER` const that `build_index.py` cannot reproduce (zero mentions — page was hand-edited or built by an uncommitted script). Our tab mirrors the *live page*, not the stale generator. No iitm data is copied into this repo — `write_html` reads the sibling CSV/JSON live each run (`data/` holds only `jobs.db` + `whatsapp_exports`).
- **Threads tool fixed (but still not wired).** Root cause found in `cli.py`: `parse_replies` always puts the root post itself at `rows[0]`, so a zero-reply post yields exactly 1 valid row — and the `len(valid_rows) < 2 → failed` gate silently discarded every post without replies (the `remote hiring` 5-post case). **Local patch applied** to `%APPDATA%\uv\tools\threads-comment-scraper\Lib\site-packages\threads_scraper\cli.py`: `not valid_rows → failed`, single root row relabeled `type: post`. Verified two ways: (1) deterministic stub through the real `cli.main()` (monkeypatched search+fetch, zero network) → 1 saved row, `type=post`; (2) live `remote hiring` → 20 rows saved (was 0). ⚠️ `uv tool upgrade threads-comment-scraper` reverts this — re-apply. Verdict unchanged: live yield is ~1 noisy location-less post per query (USA retyping gig), so supply still fails Q1 — tool stays fixed-but-unwired for manual play.
- **Threads location-shaping follow-up: still dead.** Retried with location-bearing queries (`chennai hiring`, `freshers chennai` → 0 results each; `remote hiring` → 5 posts found, 0 comments on all, repeated 403 token-refresh loop, rc=1). Threads simply has no Chennai/fresher job conversation with engagement for this tool to collect — shaping can't fix absent supply. Verdict stands: DROP.
- Tried user-suggested `JobOpportunity` (22 comments) and `Job Hunting` (37 comments): high engagement but 1 unique post each, both global noise (VA-team post, Indonesian sidejob) gated out on location — **not wired** (would add minutes per run for zero report rows).
- **Threads wired (user override of the DROP verdict).** `threads()` shells the patched CLI (2 queries: `chennai jobs`, `remote hiring` — rephrased after `chennai hiring`/`freshers chennai`/`jobs in chennai` returned 0; bare `chennai` returns photo spam so it stays out; limit 15, delays 2–4s, `--no-checkpoint`, CSV to temp dir — never the repo; missing binary fails the source cleanly like X). `_parse_threads_csv` dedupes to one Posting per post (prefers `type: post`): `ext_id=post_id||post_code`, `url=https://www.threads.net/@{user}/post/{code}`, `company=@user`, `title/text` = cleaned `post_text` (≥10 chars), `posted_at` from unix ts. First live run: fetched=2, new=2 in ~3.5 min, both Tier C noise (Indonesian remote-job account) — pipe proven, yield as predicted (~0–2 noisy rows/run). Cost note: adds minutes to the 08:30 run for near-zero yield; drop back out if it ever slows the schedule. Added to default `--sources` (now 7).
- **CareerValore (careervalore.com/job/)**: WordPress; `job_listings` post type is stale Oct-2025 SEO spam (251 dup rows — skipped); the live board is the `job` category (id 1362, 219 posts, fresh daily). Source: `GET /wp-json/wp/v2/posts?categories=1362&per_page=100&page=&orderby=date&order=desc` (3 pages cap), full `content.rendered` as match text, `ext_id=id`. Title convention `Company – Hiring for Role @ Place` parsed best-effort (`_cv_company_location`, empty when unsure). First fetch: 219 rows, all Tier C (204 pan-India location fails, 13 not-fresher) — correct, feed is mostly mechanical/electrical/pan-India. Also fixed `html.unescape` in `_clean` (titles like `&#8211;` now decode across all sources).
- **JobsAlertX (jobsalertx.vercel.app)**: Next.js static export, category routes SSR'd client-side — but `feed.xml` carries 20 fresh jobs/day with perfect schema: `title="{Role} at {Company}"`, detail link (uuid), `description="{Role} at {Company} — {Location} | TYPE | level | salary ### body"`, pubDate, category; blog guides filtered by `/jobs/` link check. Location = dash-segment after company (falls back to raw head). First fetch: 20 rows, A1/B1, **GenAI Developer Intern @ RecruitBots AI (Remote, India) in report**.
- **techihire.com: DROP.** Freelancer marketplace, not a browsable board: `/find-a-job` is a JS shell (1.9KB text, no SSR data), all 64 JS chunks combed — only `/api/auth*` endpoints; job browsing runs on Next.js Server Actions behind Sign In. Homepage "Experience/Salary" texts are sample content, `"title"` strings are a skills cloud. No public listing endpoint exists — revisit only with an account.
- **Pixel-art redesign**: Geist Pixel (400 latin woff2, 17KB, committed under `assets/fonts/`, base64 `@font-face` at generation — offline file:// safe) for headers/labels/buttons/badges, Geist Sans (400/600 latin) for everything else, system-ui only as fallback; pixelarticons (MIT, npm `pixelarticons`) search + external-link SVGs inlined (Apply button, search fields); hard 4px surfaces + pills-only tags + line-tinted card shadows + press states; spacing fixes — skill-chips div now conditional (killed phantom flex gap), `h2.head` margin normalized (was `-4px` bottom), card gap 8→10px. Verified: 351KB page, ruff + 14 tests, node headless jobs+tabs green.
- **Scheduled run made observable (Q8)**: `daily.bat` now redirects to `daily.log` and exits with run.py's code. ⚠️ First attempt redirected to `run.log` itself — cmd holds the file open for the whole redirect, so run.py's own `log()` hit `PermissionError` on its first line and the run died. Two files, not one. Proof: `schtasks /run` fired 21:29 (Last Result 1, the PermissionError), then 21:31 (Last Result 0). Task is logon-only + AC-power by user decision; first automatic fire 2026-09-26 08:30. **Threads dropped from the default `--sources`** (user override of the wire-up) — 3 rows, all Tier C, ~3.5 min per run; the parser stays for manual runs. Full 9-source run now ~60s.
- **Fresher gate reads the head, not the body** (Q2 unchanged): `FRESHER_EXCLUDE` now scans title+location+company; the body is scanned by `BODY_EXCLUDE` (numeric years bar only). JDs say "work with senior engineers", "escalate to senior stakeholders" and "*Principal Duties*" in roles explicitly for freshers — 50 of 585 rows were rejected on a word that appeared anywhere in 3-10k chars of prose. Measured: **82 rows recovered, 0 lost**, report 6 → 14 rows. Also fixed `_cv_company_location`: it matched the first `–` instead of the `@`, so "Citi – Hiring for Technology – Full Time Analyst @Chennai" parsed location as `Full Time Analyst` (8 Chennai/Remote rows lost).
- **LinkedIn descriptions fetched** (`jobs-guest/jobs/api/jobPosting/{id}`, 1.2s pacing): search cards carry no description, so every guest posting stored 0 chars, scored 0 and failed the fresher gate on absence of evidence. All 16 stored rows gained 1.4k–10k chars; **+5 report rows**. This exposed a store bug — `INSERT OR IGNORE` can never fill a field that arrives later, so `insert_new` now also refreshes url/title/company/location/text/posted_at/flags for known rows (fetched_at stays first-seen so `prune` still means 90 days of discovery). Also fixed a latent crash: `_parse_when` built `timedelta(day=1)` for "1 day ago" → `TypeError` that would have killed the whole LinkedIn source.
- **Keyword fragments dropped**: tokenizing "LoRA fine-tuning (Unsloth)" and "CLIP/transformers.js" invented `fine`, `tuning`, `clip` plus the unmatchable literal `lora fine-tuning (unsloth`. 39 → 35 keywords, report row set unchanged (only reordering). Q1/Q2/Q3/Q9 all still locked and unchanged — only the mechanics moved.
- **Moved into the Grey Matter hub (2026-10-19)**: the pipeline now lives at `job-search/scrape/` and publishes its top matches to KV key `jobscrape-jobs-v1` (`publish.py`, the same Q9 selection as report.md; rows shaped for `jobs/index.html` with `source_type: "scrape"` + `tier`). The hub's `/jobs/` page merges that key with job-filter's `jobfilter-jobs-v1` and writes tracker rows with a `js-` prefix — a separate key on purpose, because job-filter republishes its key wholesale and would delete these rows. `daily.bat` now also runs the publisher against `https://greymatter.isroot.in`. `jobpipe/page.py`'s IITM sibling path went from 3 to 4 parents (`parents[3]`).
