# Role Targets & Job Search Focus — Jayadithya R (Aug 2026)

Based on a full read of all 34 repos. Fit scores reflect **evidence in your code today**, not potential. Updated 2026-09-01 — `tamil-tokenizer` (Rust BPE, 32K HF-published, 23 tests) is now your strongest differentiator; `VulnChecker-Java` (real LoRA SFT) closes the prior honesty gap.

---

## 1. Roles you can credibly apply to, ranked by fit

### 🎯 Tier 1 — Apply aggressively (portfolio already supports it)

| Role | Fit | Why your portfolio wins | Lead with |
|---|---|---|---|
| **NLP / Tokenizer Infra Engineer** | ★★★★★ | `tamil-tokenizer` alone: Rust BPE (rayon + heap + Aho-Corasick), 247 Tamil cluster base vocab, 32K HF-published model, 23 tests, 11–16× faster than HF/SentencePiece on Tamil. No fresher in your pool has this. | `tamil-tokenizer` + HF card |
| **GenAI / LLM Application Engineer** | ★★★★★ | RAG agent, tool-calling loop, VLM auto-annotation, human eval harness, *plus* `VulnChecker-Java` as real LoRA SFT proof and `tamil-tokenizer` as infra depth. Most freshers have 1 ChatGPT-wrapper; you have an *inference + infra spectrum* (local LM Studio → cloud Groq → in-browser transformers.js → Rust tokenizer). | `tamil-tokenizer` + `VulnChecker-Java` + fitcheck family |
| **Python Backend Engineer (FastAPI/API-heavy)** | ★★★★☆ | `kaggle-automation` is properly layered (routers/services/db), has tests, session monitors, background workers. `middleman`, `hr-rag-agent`, `ats-resume-builder` add breadth | `kaggle-automation` |
| **Data / ML Pipeline Engineer (entry)** | ★★★★☆ | 1.18M-chunk transcript pipeline w/ proxy rotation + checkpoint resume, dataset cleaning/validation code, scrapy/yt-dlp extraction, MySQL persistence, incremental dedup logic | `sivabharani-comments`, `llm-training-dataset-scraping` |
| **Applied AI Engineer @ AI-first startups** | ★★★★☆ | End-to-end ownership story: synthetic data → labeling UI → CLIP recommender → full-stack app → human eval. Startups hire for exactly this "ship the whole loop" profile | fitcheck narrative |

### 🥈 Tier 2 — Apply selectively (needs 1–2 weeks of gap-filling first)

| Role | Gap to close before applying |
|---|---|
| **ML Systems / Infra (junior)** | `tamil-tokenizer` already proves systems depth (Rust, Aho-Corasick, rayon, heap, `lto=true`); add CI + crates.io publish + `pyo3` Python binding and you can credibly chase this. |
| **MLOps / ML Platform (junior)** | You have the orchestration instincts (`kaggle-automation`) but no Docker-in-a-clean-repo, no CI, no model registry/serving story. Add Dockerfile + GitHub Actions + a one-paragraph deploy doc to kaggle-automation → then apply |
| **Computer Vision Engineer (entry)** | Real but dated evidence: DeepLabV3/YOLOv8 prototype, counterfeit-detection concept (`bichecke`). Needs the leaked keys fixed + one clean writeup of the training notebook |
| **Full-Stack (React/TS, startup tier)** | fitcheck-website + hackathon apps are real, but thin vs dedicated web devs. Only target startups that value the AI layer on top |
| **SDE at product companies (Zoho-tier & above)** | Pure OA gate: your 2-problem NeetCode repo is disqualifying today. Nothing else matters until DSA volume is fixed |

### ❌ Don't waste cycles on (yet)

- **DevOps/SRE-only roles** — no infra-as-code, no K8s, no observability evidence.
- **Java/Spring enterprise backend** — zero evidence, and it would bury your differentiators.
- **Pure frontend roles** — you'd compete against stronger, focused portfolios with your weakest asset.
- **Data Analyst/BI** — under-sells you; your pandas/matplotlib work is incidental, not central.

---

## 2. Where your focus should go (the honest math)

**Priority order, by expected return on effort:**

1. **DSA volume — 50% of your study time.** Hard truth: it's the gate in front of everything. Service companies (TCS Digital, Infosys SP, Cognizant, Accenture), mid-tier product cos, and even many AI startups run OAs. Your auto-synced 2-problem repo actively hurts you. Target: 150+ problems before serious OA season, NeetCode 150 as the spine. Either grind it privately or let the sync make the repo look respectable again.
2. **One flagship polished to depth, not five new projects — 25%.** `tamil-tokenizer` + `VulnChecker-Java` + fitcheck family are now the trio — make them defensible: cite VulnChecker as your real SFT proof (or delete the fitcheck distillation claim), extend fitcheck past 42 garments, add `cargo test`/`cargo bench` CI + crates.io publish to `tamil-tokenizer` (easiest win on the account), and Dockerfile + CI to `kaggle-automation`. Depth in 3 projects beats breadth in 20.
3. **Ship the missing search layer on sivabharani-comments — 10%.** Turns your best scale story into a working product with a URL. One weekend of Meilisearch work.
4. **Hygiene/security pass — 10%.** Revoke leaked tokens (Telegram, 2× OpenRouter), scrub PII from `middleman`, delete `Vadachennai`/`project01`/`salim`/empty repos, pin down AI-scaffold tells. Recruiters do click through.
5. **Application infrastructure — 5%.** You already built ATS tools — actually use them. Track every application; you wrote the tracker.

---

## 3. Market targeting (India, from Chennai)

**Highest-probability segments for this profile:**

- **AI-first startups (seed–Series B)** hiring "AI engineer" without DSA-heavy loops — Bangalore/Chennai remote-friendly. Your portfolio reads exactly like what their job posts describe ("built RAG, evaluated outputs, worked with open models"). Channels: Wellfound, YC jobs board, peerlist, founder DMs with a 3-line pitch + demo links.
- **Chennai product companies:** Zoho (Zia team), Freshworks (Freddy AI), Chargebee, Kissflow, Mad Street Den/Vue.ai (Chennai's flagship AI company — strong fit), Ford GTBC, Athenahealth, PayPal Chennai. These value demonstrable shipping + will still OA you → back to priority #1.
- **GCCs building GenAI teams** (Standard Chartered GBS, Caterpillar, Ford, Cognizant AI hub): steady fresher intake, interview = aptitude + basics + projects. Good floor while startups process.
- **HuggingFace/open-source visibility:** your HF account already has a dataset + fine-tune. Blog posts linking repos ↔ HF artifacts give recruiters verifiable external proof — rare among freshers, cheap for you to produce since the blogs exist in draft form on your portfolio.

**Positioning line to standardize everywhere:**
> "I build AI systems from the bottom up: tokenizer infra for Tamil (Rust + Aho-Corasick) → data pipelines → open-model inference (local/edge/in-browser) → product → human eval."

Every resume bullet, LinkedIn headline, and cold DM should ladder up to that sentence. It is genuinely differentiated; most freshers can only claim the wrapper.

---

## 4. Sequencing (Aug–Nov 2026)

| Window | Action |
|---|---|
| **Now–Sep** | Security fixes + delete junk repos + README honesty pass (cite `VulnChecker-Java` to close gap). Add `tamil-tokenizer` CI + crates.io publish this week. Start DSA daily (non-negotiable). Apply to Tier-1 startup/NLP roles in parallel — early apps face less competition. |
| **Sep–Oct** | Flagship polish (SFT run or claim removal, CI/Docker/tests on kaggle-automation, ship sivabharani search layer). Campus/off-campus drives begin in earnest — don't skip service-company drives; offers in hand change your negotiating posture. |
| **Oct–Nov** | Volume phase: 15–20 targeted applications/week, referral mining (LinkedIn alumni from your college at target cos), Unstop/hackathons for extra signal if time permits. |

---

## 5. Single biggest risk

Not the projects — those clear the bar for the roles you want. The risk is **DSA**: every path above except seed-stage startup DMs runs a coding assessment. If August-you applies broadly with 2 problems of practice, the portfolio never gets seen. Flip the ratio: grind first, apply continuously, let the repos close the deals after the OA gets you in the room.
