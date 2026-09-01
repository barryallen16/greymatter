# Full GitHub Repo Audit — barryallen16 (Jayadithya R)

*All 34 public repos cloned, read, and analyzed line-by-line. August 2026. Updated 2026-09-01 to include `tamil-tokenizer` (pushed 2026-08-28).*

---

## 🚨 Security incidents — fix before anything else

| # | Repo | Issue | Action |
|---|---|---|---|
| 1 | `moviemod-scraper` | **`.env` tracked in git** with live Telegram bot token (`8926550373:AAGoz…`) + private group chat ID | Revoke via @BotFather NOW; purge history with git-filter-repo |
| 2 | `bichecke/openrouter-stuff/save-raw.py:15`, `rjaya16.py:18` | **Two live OpenRouter API keys hardcoded** (`sk-or-v1-5a47d…`, `sk-or-v1-a35e5…`) | Revoke both keys |
| 3 | `middleman` | Real classmates' names, regnos, grades, GPAs committed in fixtures + static JSONL | Scrub PII |
| 4 | `new-prince-hackathon/backend/main1.py:12-13` | Supabase anon JWT hardcoded (decoded → `role: anon`, not service_role — bad but not catastrophic); ElevenLabs key shipped client-side via `EXPO_PUBLIC_*` (extractable from any APK) | Rotate key; proxy STT calls through backend |
| 5 | `movie-recommendations/main.py:47` | OMDB API key committed (`apikey=3a28395a`) | Revoke/regenerate |
| 6 | `off-txt` | Developer's own phone number hardcoded twice in source | Remove |

---

## Master ranking

| Rank | Repo | Score | LOC (first-party) | Tests | Verdict in one line |
|---|---|---|---|---|---|
| 1 | tamil-tokenizer | **8.5/10** | ~1,810 (Rust) | ✅ 23 tests | Best differentiator — Rust BPE with Aho-Corasick, rayon + heap-optimized trainer, HF-published 32K tokenizer (11–16× faster than HF/SentencePiece on Tamil) |
| 2 | kaggle-automation | **8/10** | ~4,300 | ✅ real | Best backend engineering — layered FastAPI, shard distribution, session monitors, secrets hygiene |
| 3 | VulnChecker-Java | **8/10** | ~1,200 + 1GB pipeline | ✅ 102-case eval | Real LoRA SFT: 7-stage data pipeline (synthetic + dedup) → Unsloth r=64/α16 → 7B beats 14B (80.39% on 102 cases) |
| 4 | ats-resume-creation-skill | **7.5/10** | ~680 py | ❌ | Best code-per-line judgment calls; small scope |
| 5 | sivabharani-comments | **7/10** | ~900 | ❌ | Best scale story (1.18M chunks); product never shipped, 1 sloppy commit |
| 6 | Memory | **6.5/10** | ~800 | ❌ | Best vanilla-JS craft; React value-setter insight is genuinely non-obvious |
| 7 | fitcheck-website | **6.5/10** | ~2,400 | ❌ | Flagship: in-browser FashionCLIP, degradation chain, key rotation — oversells unfinished features |
| 8 | fitcheck-app | **6/10** | ~5,300 | ⚠️ 1 stale suite | CLIP+rules recommender with real tests; runs on 42 items; no fine-tuning despite claims |
| 9 | ats-resume-builder | **6/10** | ~1,470 | ❌ | Client-side Typst→WASM→PDF is neat; two near-identical 700-line HTML files |
| 10 | fitcheck-human-eval | **6/10** | ~215 | ❌ | Human eval harness puts you ahead of 95% of freshers; boilerplate README hides the results |
| 11 | portfolio | **6/10** | ~1,000 | n/a | Personality-driven brochure, not engineering evidence |
| 12 | hr-rag-agent | **5/10** | ~255 | ❌ | Clean tutorial-tier tool-calling RAG demo |
| 13 | yt-ssf | **5/10** | ~220 | ❌ | Practical personal search engine; excellent README, live demo |
| 14 | new-prince-hackathon | **5/10** | ~1,200 | ❌ | Demoable voice→STT→ML→UI pipeline; fake auth, hackathon duplication |
| 15 | quiz-wand | **4/10 code / 7 credential** | ~280 | ❌ | Published on Firefox AMO (real achievement); corrupted popup.js; ethics gray |
| 16 | fitcheck | **4/10** | ~1,100 | ❌ | Synthetic-data factory + preference microsites; good story, weak artifact |
| 17 | fitcheck-mini | **4/10** | ~410 | ❌ | Classical-CV prototype; keep as learning-arc story only |
| 18 | aman.ai-search | **4/10** | ~375 | ❌ | Small scrapy→meilisearch utility |
| 19 | unshortenBuddy | **4/10** | ~455 | ❌ | Deployed Telegram bot, decent structure; ad-bypass ethics |
| 20 | bichecke | **4/10** | ~3,500 | ❌ | Interesting VLM concept wrecked by leaked keys + five duplicate 579-line scripts |
| 21 | new-ncicit | **4/10** | ~970 | n/a | Real delivered client work for a university conference |
| 22 | moviemod-scraper | **3.5/10** | ~1,700 | ❌ | 16 stars & battle-tested, but 1,639-line monolith, live token leak, piracy ethics |
| 23 | off-txt | **3.5/10** | ~420 | ❌ | Best idea in the automation batch; core flow broken (hardcoded phone number) |
| 24 | llm-training-dataset-scraping | **3/10** | ~100 | ❌ | Tiny CPT-dataset learning exercise |
| 25 | middleman | **3/10** | ~650+frontend | ❌ | Primary API path crashes; classmate PII committed; great OCR prompt doc though |
| 26 | russian-hackatom-proj | **3/10** | ~265 real | ❌ | Restaurant-template fossils everywhere ("restaura", food constants); no ML training code |
| 27 | movie-recommendations | **3/10** | 61 | ❌ | Tutorial tier: wrong ML terminology in README, no requirements.txt, refits every click |
| 28 | white-ticket | **2/10** | ~460 unique | ❌ | Dead booking bot with honest confessional README |
| 29 | neetcode-submissions | **2/10** | 17 lines | n/a | **TWO problems solved.** Auto-synced proof of prep level. Biggest liability on the account |
| 30 | barryallen16 (profile) | **2/10** | 19 lines | n/a | Stock generator output |
| 31 | project01 | **2/10** | 245 | n/a | Lorem ipsum ToS, alert() forms — delete |
| 32 | TensorTonic-Solutions | **1/10** | 11 | n/a | Empty repo advertising solutions that don't exist — delete or fill |
| 33 | Vadachennai | **1/10** | 0 real | n/a | Untouched Expo template; package name doesn't match repo name — delete |
| 34 | salim | **0/10** | 0 | n/a | Zero files, zero commits — delete |

----

## Tier S — Lead with these

### 1. tamil-tokenizer — 8.5/10 *(pushed Aug 28, 2026 — your single strongest differentiator)*

A high-performance **BPE tokenizer for Tamil** in Rust — the one project on your account that is *not* another LLM wrapper and that 95% of Indian freshers cannot show. 1,814 LOC + 23 tests + HF-published 32K vocab (`barryallen16/tamil-tokenizer-wiki`, trained on 128K lines of Tamil Wikipedia).

- **Architecture:** `vocab.rs` (TamilTokenizer — 247 Tamil char-cluster base tokens, GPT-2 byte mappings, o200k-style special-token layout), `pretokenizer.rs` (Tamil-aware regex splitter), `trainer.rs` (558 ln — parallel corpus load via rayon, packed `u64` pair keys, `BinaryHeap<u32>` max-heap for merges), `encoder.rs` (Aho-Corasick `O(n)` multi-pattern matcher, `FxHashMap` + `AHashMap`, `Arc` sharing), `main/train/encode/decode/benchmark` CLIs.
- **Genuinely good engineering:** `pack_pair(a,b) = (a<<32)|b` for cache-friendly heap keys; rayon parallelism only where it helps (corpus ingest); `FxHashMap`/`AHashMap` for hot paths; `profile.release lto=true` + `opt-level=3`; `__meta__` dropped in subset (honest TODO). Special tokens BOS/EOS/pad/unk/mask/question/answer/code + 100 reserved — mirrors production tokenizer layouts, not toy code.
- **Tests & benchmarks:** 23 tests in `tests/lib.rs` (vocab size range, no-dup, contiguous IDs, round-trip encode/decode), `benchmark.rs` + `bench_encode/speed` + `benchmark_tiktoken.py` head-to-head vs tiktoken (OpenAI), SentencePiece, HF Tokenizers. README claims **11× SentencePiece, 16× HF on Tamil @ 52.9 MB/s** — reproducible via `cargo bench`. Fertility metrics reported (Tamil 4.22 tok/word vs English 1.03).
- **Interview angle:** "I built infra for an underrepresented language — why Tamil needs cluster-aware base vocab, why Aho-Corasick beats trie for encode, why a heap beats sorting each merge." No other fresher at the table has answered that.
- **To reach 9.5/10:** add `.github/workflows/ci.yml` (`cargo test` + `cargo bench`), publish to crates.io + `cargo install tamil_tokenizer`, add a Python binding via `pyo3` (so a Python-first interviewer can `pip install` it), tighten README fertility discussion (explain why Tamil 4.22 is *good* vs tiktoken's 2.06 at 100K vocab — tradeoff of vocab size).

### 2. VulnChecker-Java — 8/10 *(freelance, Aug 2026 — your proof of real fine-tuning)*

Fine-tuned Qwen2.5-Coder for Java vulnerability detection end-to-end (pushed to `barryallen16/VulnChecker-Java`, datasets on HF). Cures the audit's biggest gap: fitcheck's "LLM fine-tuning" was inference-only; *this* repo is actual `SFTTrainer` + `get_peft_model` with LoRA r=64/α=16 and a 102-case eval harness where the 7B beats the 14B (80.39%). Own this story and the earlier honesty gap disappears.

### 3. kaggle-automation — 8/10 *(pushed Aug 24, 2026)*
Pools multiple Kaggle API keys to run parallel GPU workloads; auto-shards datasets across accounts; central FastAPI dashboard monitors 12-hour sessions.

- **Architecture:** proper FastAPI layering — 6 routers (`accounts/runs/distributed/logs/files/settings`), service layer (`WorkloadDistributor`, `AccountManager`, `SessionMonitor`, `KaggleService`, `TelegramService`), SQLite persistence, Jinja UI. ~4,300 LOC.
- **Genuinely good engineering:** notebook-shard-config injection (handles `.ipynb` JSON correctly), background 12h-session monitor via lifespan hooks, auth token gating with loud warning when unset, CORS locked to localhost, correct `.gitignore` (`.env`, `kaggle.json`, `*.db`) — verified nothing sensitive is tracked.
- **Tests:** `test_inference_script.py` (383 ln), `test_distributor.py` (246), `test_automation.py` (123) — the only repo besides fitcheck-app with real tests.
- **Interview angle:** "distributed compute orchestration over constrained free-tier GPU quotas" — scheduling, sharding, failure monitoring, alerting.
- **To reach 9/10:** Dockerfile, GitHub Actions CI, README architecture diagram.

### 2. fitcheck family — treat as ONE project story (7/10 combined)
The narrative arc most freshers can't tell: synthetic data generation → crowdsourced preference labeling → classical CV prototype → CLIP+rules hybrid recommender → full-stack app → human eval harness. Published HF dataset (`barryallen16/fitcheck-annotate-dataset`) is externally verifiable.

**fitcheck-website (6.5)** — React 19 + TS + Vite + Tailwind/shadcn.
- **Standouts:** Marqo-FashionCLIP running fully **in-browser** via transformers.js (singleton lazy loader, hand-rolled cosine similarity); garment upload → Qwen3-VL-4B via local LM Studio with strict raw-JSON prompting; IndexedDB (correct choice for base64 images); recommendation chain Groq(JSON mode) → retry-with-rejected-pair-memory-fed-back-into-prompt → deterministic JS fallback; multi-key rate-limit rotation for Groq/Gemini; OpenWeatherMap→fabric rules engine; SFT dataset generator with negative-pair curriculum.
- **Red flags:** README oversells (persona/virtual try-on not actually mounted); `groqService.ts` artificially sleeps 12–18s after response for fake "thinking" suspense; AI-tool fingerprints (`/mnt/okcomputer/output` in info.md, kimi plugin dep); zero tests.

**fitcheck-app (6)** — the ML core, ~5,300 LOC.
- `generate_embeddings.py` (344 ln): crash-safe incremental writes, MD5 change detection, checkpoint/resume — legitimately well-engineered batch job.
- `outfit_generator.py` (591 ln): weighted scoring — 35% visual coherence (pairwise cosine) / 30% color harmony (hand-built theory rules) / 20% style matrix / 15% occasion fit.
- `test_system.py`: real unittest classes with tempdir fixtures — but embeds a 360-line DEPLOYMENT.md as a Python string, and sibling `test_workflow.py` asserts against an outdated API shape (would crash if run).
- **Fatal weakness:** entire system operates on **42 garments**. Prepare a scaling answer or extend the dataset.
- **Honesty gap:** `llm-classification/` notebooks are named like LoRA fine-tunes but are **inference-only annotation jobs** — zero `.train()`, zero trainer code anywhere. The README's teacher→student distillation claim is unsupported by any repo.

**fitcheck-human-eval (6)** — Next.js 15 + Neon serverless Postgres; rates 100 teacher-model outputs on Relevance&Culture/Overall; injection-safe parameterized SQL. Fix the create-next-app boilerplate README to report actual eval results.

**fitcheck-mini (4 as artifact / 7 as story)** — DeepLabV3(person-class bug on garment shots) + GrabCut + KMeans colors + YOLOv8(Fashion-MNIST labels mismatched to ethnic wear) + Gemini pairing. Keep for the "I started here, hit these walls, migrated to VLM annotation + CLIP" narrative.

### 3. ats-resume-creation-skill — 7.5/10
Agent Skill (SKILL.md format): persistent candidate-profile JSON that merges without losing history, generates .docx via python-docx → PDF via headless LibreOffice, plus application-tracking CLI (`add/list/check-duplicate/update-status`).
- Atomic writes (`os.replace`), keyed dedupe on (company,title,start), correct exit codes for agent consumption.
- Domain-informed decisions documented in comments: literal `- ` bullets because ATS parsers drop Word numbering-field text, east-asian font-slot XML fix, fresh LO user-profile per conversion, right-tab date alignment instead of tables.
- Gaps: zero tests, exact-string dedupe only, single squash commit. Pair with `ats-resume-builder` (client-side Typst→WASM→PDF compilation; duplicated Gemini/OpenRouter variants; dead Gradio stub) into one "I automated my own job hunt" narrative.

### 4. sivabharani-comments — 7/10 story, weak artifact
Data-engineering + LLM pipeline over a Tamil tech YouTuber's 2,755 videos: scrapes auto-generated Tamil transcripts, runs local Gemma (Unsloth, 4-bit, Kaggle GPUs) over **1,185,665 chunks** to detect moments he reads viewer names.
- Real engineering: multiprocess free-proxy validation with live dead-proxy removal, hash-based resume-from-checkpoint dedup, incremental JSONL appends, HF datasets upload, honest write-ups ("English transcripts are worthless").
- Weaknesses: single commit whose message pastes a Windows venv path; the promised searchable lookup was never built (pipeline ends at JSONL); broad exception swallowing; no tests.

---

## Tier A — Supporting cast

### 5. Memory — 6.5/10
Website generating personalized Google Forms autofill bookmarklets (fuzzy question matching, localStorage persistence).
- **Star insight:** bypasses React's controlled-input value tracker via `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set.call(...)` then dispatches synthetic events — without this Google Forms ignores programmatic fills. Non-obvious DOM/framework knowledge.
- Synonym-pattern matching with positive/negative patterns; handles ARIA radios, listbox dropdowns, native inputs; demo mode with fake persona data. Finished + demo video.
- Weaknesses: duplicate iteration folders committed, magic strings, degree hardcoded 'btech'.

### 6. fitcheck-human-eval — see Tier S family above.

### 7. quiz-wand — 4/10 code, 7/10 credential
Chrome MV3 + Firefox browser extension: scrapes MCQs from Google Forms, sends to Gemini, auto-clicks answers. **Listed on Firefox Add-ons (AMO) = passed Mozilla review** — legitimate distribution achievement.
- Critical defect: `popup.js` corrupted by copy-paste (entire file nested inside itself → every listener registered 2–3×).
- Answer matching relies on exact `aria-label === model reply` (breaks on paraphrase); deprecated gemini-1.5-flash.
- Ethics: it's a quiz-cheating tool — frame carefully or don't lead with it.

### 8. hr-rag-agent — 5/10
Agentic RAG: LM Studio local inference + ChromaDB vector search + SQLite writes via OpenAI-compatible tool calling. Clean, readable, ~255 lines — and exactly one round of tool calls (no multi-step loop), committed `.db` binary, no tests. Tutorial-plus tier; fine as breadth evidence.

### 9. yt-ssf — 5/10
Personal search engine over YouTube subscription feed: yt-dlp (cookie-gated feed extraction) → scrapy metadata crawl → Meilisearch index → hosted search UI. Excellent step-by-step README with screenshots + live demo on GitHub Pages. Small but real and shipped.

### 10. new-prince-hackathon — 5/10
"All Is Well" mental-health app (Expo RN + Supabase + Flask/sklearn + ElevenLabs STT): voice→transcription→risk-classification→color-morphing UI, realtime chat via Supabase postgres_changes, streak logic across UTC boundaries.
- Real feature work, demoable pipeline; auth-gated routing done correctly.
- But: JWT attached to `/predict_text` never validated server-side (auth theater), Activity.tsx is a 311-line copy-paste of index.tsx with dead imports, `text_model.joblib` ships with no training script/dataset/metrics (unverifiable claim).

### 11. portfolio — 6/10
Hand-written vanilla HTML/Tailwind CDN/GSAP; Tanglish copy, pixel-reveal hero animation, filterable project grid, 2 blog posts (FitCheck breakdown, Qwen Java-vuln fine-tune). Works as a business card; contains ~90 lines of dead modal code. It's evidence of taste, not engineering.

---

## Tier B — Talking points only

| Repo | Notes |
|---|---|
| **new-ncicit (4)** | Real delivered website for NCICT'25 university conference (969 lines hand-authored HTML). Evidence you can ship for real stakeholders on deadline. Committed Vite build bundle whose source isn't in the repo. |
| **aman.ai-search (4)** | Scrapy spider + Meilisearch indexing of aman.ai content. Small utility, works. |
| **unshortenBuddy (4)** | Telegram bot resolving ad-walled shorteners via headless Chrome + Postgres cache + admin approval workflow. Deployed with changelog. Bugs: SQL built from tuple repr, filter-precedence error, Selenium blocks asyncio event loop. Ad-bypass ethics. |
| **moviemod-scraper (3.5)** | 16 stars, working, survives piracy-domain rotations via redirect-tracker resolution; Docker compose w/ MySQL healthcheck. BUT: 1,639-line monolith, same ad-wall block pasted 6×, 34-entry season dict ×2, bare excepts everywhere, cosmetic multiprocessing (pool.starmap with exactly ONE task tuple), module-level DB connection, **live token leak**, piracy ethics. Frame as "browser automation against adversarial targets" if at all. |
| **off-txt (3.5)** | Expo RN app: payments-over-SMS exploiting free SMS quotas on Indian voice-only plans — best *idea* in the batch. Core flow broken: multi-select contacts ignored, sends to developer's own hardcoded number. Modern expo-router structure otherwise. |
| **bichecke (4)** | VLM warranty/counterfeit assessment for bike parts (helmet/spark plug/air filter) on edge devices. Interesting concept + 750-line training notebook. Wrecked by: two live OpenRouter keys, five near-identical 579-line scripts differing only by account name, dataset images bloating repo to 84MB. |
| **llm-training-dataset-scraping (3)** | Tamil lyrics corpus scraping/cleaning for continued pre-training experiments. ~100 lines. Learning exercise; readme shows genuine curiosity about CPT. |
| **middleman (3)** | GPA calculator from result screenshots: FastAPI + Gemini Vision OCR. **Broken primary path**: `os.path.jsoin` typo swallowed by broad except, NameErrors, endpoint calls nonexistent function. Real classmates' PII committed. The OCR prompt engineering doc (O-vs-0 rules, index-6 correction rule learned from failures, IMAGE_UNCLEAR sentinel) is the gem here. |
| **white-ticket (2)** | TicketNew booking bot (Leo/Chithha era). Zero functions, seat geometry as raw nth-child selectors, dead since 2023. Confessional README ("the code is amateur... everything is hardcoded") is a small maturity signal. Queue-jumping ethics. |
| **russian-hackatom-proj (3)** | HackAtom energy-prediction demo: React+Flask+CatBoost. Built on a restaurant landing template — folder literally named `cooking/`, commented-out dish constants, "restaura" alt-texts, verbatim YouTube-tutorial maps file not even imported. Real authored code ≈265 lines; ML training absent (serialized model only). |

## Delete immediately

- **Vadachennai (1)** — untouched Expo template, zero beyond scaffold, package name mismatch (`middleman`). Abandoned at minute zero.
- **project01 (2)** — Quiz World landing page with Lorem ipsum legal dialogs and alert()-only forms. Week-3-of-learning-Tailwind energy.
- **salim (0)** — zero files, zero commits.
- **TensorTonic-Solutions (1)** — README advertises auto-synced solutions; repo contains none.
- **movie-recommendations (3)** — fix before deciding: rename README technique (it's collaborative filtering, not content), add requirements.txt, cache the model, remove the key. Or fold into portfolio as a learning artifact.

---

## Cross-cutting findings (what an interviewer will pattern-match)

1. **DSA evidence: 2 problems / 17 lines** (neetcode-submissions, auto-synced). This outweighs every project on the account during screening. Aug-2026 fresher bar: 150–300+.
2. **Every repo is a single squashed commit** — no visible process, nothing for git archaeology to validate.
3. **Almost zero CI (now 1 bright spot), tests in exactly 3 repos, Docker only inside the messiest repo.** tamil-tokenizer's 23 tests are the counter-example — lean into it. Add CI there first; it becomes the template.
4. **AI-scaffold fingerprints**: `/mnt/okcomputer/output`, kimi-plugin devDependency, CLAUDE.md/AGENTS.md files, emoji-dense LLM-style docs, DEPLOYMENT.md embedded in a test string. Assume interviewers know the tells; your defense is explaining every architectural decision unprompted.
5. **README honesty gaps — now partially cured:** fitcheck's "LLM fine-tuning" was inference-only, but **VulnChecker-Java proves you *have* done real LoRA SFT** — cite it explicitly to close the gap. Remaining gaps: movie-recommendations technique mislabel, Vadachennai name/package mismatch, oversold persona/try-on features, tamil-tokenizer speed claim (defensible but benchmark hardware must be stated — run `cargo bench` on the reviewer's machine).
6. **What's genuinely differentiated:** tokenizer infra for an underrepresented language (Rust + Aho-Corasick + rayon + heap-optimized BPE), eval culture (human eval harness *and* tokenizer fertility/compression metrics), inference-strategy spectrum (local LM Studio → cloud → in-browser transformers.js → quantized Unsloth), scale instincts (1.18M chunks, proxy rotation, checkpoint resume), and compute-hacking creativity (kaggle-automation). Add `tamil-tokenizer` to every intro — it alone separates you from 100 LLM-wrapper portfolios.

## 30-day fix list (priority order)

1. Revoke Telegram token + both OpenRouter keys; purge `.env` from moviemod-scraper history; scrub middleman PII; delete the four junk repos.
2. DSA daily grind — decides whether anything else gets read.
3. FitCheck honesty pass: cite VulnChecker-Java as your real SFT proof (or delete the fitcheck distillation claim); remove okcomputer/kimi tells and the artificial sleep; fix stale tests.
4. Ship sivabharani-comments' missing search layer (Meilisearch + tiny frontend) — turns the best scale story into a product with a URL.
5. kaggle-automation **and** tamil-tokenizer: Dockerfile + GitHub Actions + architecture diagrams in READMEs. tamil-tokenizer's CI is the easiest win on the account — `cargo test && cargo bench` — do it first and reuse the workflow.