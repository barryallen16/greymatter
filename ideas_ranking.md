# ideas.md — Brutally Honest Interview/Resume Ranking

**Read:** `ideas.md:1` (19 ideas, Sep 1) + `repo-analysis.md:1` (34 repos) + `career_advice_insights.md:1` (524 advices) + `roadmap.sh/backend` (fetched Sep 1) + `aman.ai/sitemap.xml` 600 URLs + `aryan1 DSA` + `techinterviewhandbook`.

**Your edge today:** Python + basic SQL + Heap start. 4 months graduated, 2 LeetCode solves logged. Need job in 90 days, not 2-year research.

**Scoring:** Uniqueness = few freshers have it / existing competition. Usefulness = real Indian user pain + hiring manager cares. Resume worth = can you build it in 30 days with Python/FastAPI/RAG/Docker, defend Type A/B/C/D, show quant metrics + live URL.

---

## Roadmap.sh Backend — What You Are Missing (add now, not later)

`roadmap.sh/backend` fetched Sep 1 was JS-heavy shell, but standard 2026 backend track is stable:

**You already cover:** Python, Git/GitHub, FastAPI (`kaggle-automation` 6 routers), basic SQL, Docker/CI (tomorrow's task).

**Missing — add as 15-min micro-ticks, not new projects:**

1. **Relational DB depth** — PostgreSQL not SQLite: `ACID, indexes (B-Tree), normalization 1NF/2NF, EXPLAIN` — needed for *any* RAG scheme/complaint DB (`ideas.md:30` gov schemes). Do in `kaggle-automation` by swapping SQLite → Postgres in `docker-compose`.
2. **Caching + Rate limiting** — Redis `cache-aside` + IP rate limiter. `roadmap.sh` lists it before queues. You have no Redis evidence. Add to `kaggle-automation` `/health` + `SlowAPI` like `GovAssist` does.
3. **Auth + API security** — JWT/OAuth2, `12 Tips for API Security` `career.txt:240` (HTTPS, OAuth2, leveled keys, rate limit). Your `new-prince-hackathon` shipped JWT but never validated `repo-analysis.md:14`.
4. **Testing + CI/CD beyond lint** — `fresher-must-have-skills-2026` 10-point checklist: pytest with fixtures, not just `hl` — `tamil-tokenizer` has 23 tests, `kaggle-automation` has 3. Need 10-20 unit tests + GH Actions.
5. **Web server / Deploy** — Nginx reverse proxy, `docker-compose` healthcheck (your `moviemod-scraper` has one but 1639-line monolith). Tomorrow's `docker build` must pass, then `Render/Railway` live URL.

*Don't touch yet:* GraphQL/gRPC, Kafka/RabbitMQ, Kubernetes — explicitly `Recruiter Bluff` for freshers `fresher-must-have-skills-2026.md:232`.

---

## Ranking — 19 Ideas from ideas.md

### Tier S — Build now, resume gold (do 1, not 3)

| Rank | Idea | Uniqueness | Usefulness | Why resume gold / brutal truth | Verdict |
|---|---|---|---|---|---|
| **1** | **Gov scheme recommender AI** `ideas.md:30` — RAG over myscheme.gov.in, eligibility | ★★★★☆ Medium: 5-6 exist (scheme-saathi, GovAssist, sahayak, VaaniSahayak) but none dominant, all 2024-25, no Tamil voice | ★★★★★ High: 3,000 schemes, scattered ministries, citizens can't parse | **Best fit.** Rules engine *is* source of truth, not LLM hallucination (scheme-saathi design). You can do it with `FastAPI + Chroma + Groq + Streamlit`, hybrid TF-IDF/BM25 + `needs_info` vs `eligible`. Tamil + offline = differentiator vs existing Hindi-only. Backend roadmap perfect: API → DB (schemes.json) → RAG → deterministic eval + tests. Interview: explain why `failed` wins over `unknown`. | **Build. Interview Q: “How do you handle a missing age field without guessing?”** |
| **2** | **Fresherr (AI lawyer offer letter)** `ideas.md:8` | ★★★★☆ Medium: TakeHomeCalc checker, pdfcraft, ContractSafe exist but are regex/pattern based, new labour codes Nov 21 2025 make old templates stale `websearch:Offer Letter 2025` | ★★★★★ High: Every fresher fears bonds, clawback, variable >30% trap — your own pain | **Second best.** Upload PDF → CTC breakdown vs in-hand + notice + non-compete Section 27 void + training bond Section 74 check → negotiation email. You already parse Indian labour law. Do PDF extract + structured 10-section report like ContractSafe. Resume: talk about Nov 2025 wage definition 50% rule. | **Build. Low infra, high story.** |
| **3** | **Automatic complaint filler + helpline** `ideas.md:18` | ★★★★☆ High: no one does gov complaint form filling (CPGRAMS, consumer forum) as SLM | ★★★★☆ High: people don't know where to complain — forms are tedious | **Strong RAG + form mapping.** Fine-tune small SLM to map user story → correct portal + prefill. Helpline retrieval is RAG. Lean: start with 5 portals (consumer, cybercrime, RTI). Testable, demoable. | **Build after #1.** |

### Tier A — Strong if executed, needs hardening

| 4 | **Tamil TTS (lightweight male/female)** `ideas.md:79` | ★★★★★ High: almost no lightweight Tamil TTS, underrepresented | ★★★☆☆ Medium: niche but aligns with `tamil-tokenizer` edge | Needs audio ML (Indic Parler-TTS). If you wrap `ai4bharat/indic-parler` + fine-tune on Tamil, it's defensible infra. Harder than RAG — 30 days is tight. | **Do only if you pick Tamil edge.** |
| 5 | **OCR for exam paper + evaluation pipeline** `ideas.md:66` | ★★★☆☆ Medium: many OCRs, but exam formatting preservation + auto-evaluation vote is niche | ★★★★☆ High: teachers can't read handwriting — real pain | Needs PaddleOCR + layout (preserve tables/diagrams) + LLM grader with teacher approve gate. Good CV + LLM combo. Risk: handwriting variance. | **Good backup, needs dataset.** |
| 6 | **ticket iruka? (Strava for theatres)** `ideas.md:72` | ★★★★★ High: nothing like this | ★★★☆☆ Medium: cinephiles only | **Best product thinking.** BMS import + QR exhaustion DB (only n seats can claim) solves cheating. No AI needed — pure backend (auth, DB, Redis). Shows `fresher-must-have-skills-2026` LLD + caching. Low AI, high craft. | **If you want non-AI backend showcase, do this.** |

### Tier B — Fun wrapper, hard to defend

| 7 | **AI image/audio/video detector + extension** `ideas.md:3` | ★☆☆☆☆ Low: Hive, Deepfake Detector, Trulith, Verigin already in Chrome Store, right-click 1.4MB, free forever | ★★★★☆ High demand but saturated | **Don't.** Interviewer: “Why not call Hive API?” You'll say “I trained a model” with no evaluation vs SoTA. Only defensible if on-device Tamil deepfake or C2PA provenance, not generic detector. | **Skip for job.** |
| 8 | **Didn't name — free-tier “without credit card” search** `ideas.md:14` | ★★☆☆☆ Low: AlternativeTo, free-for-dev, saasworthy exist | ★★☆☆☆ Medium dev pain, small market | Curation, not engineering. CRUD + scraping, no RAG depth. | **Toy, not lead.** |
| 9 | **synthetic clone (WhatsApp chat)** `ideas.md:40` | ★★☆☆☆ Low: many WhatsApp-clone finetune repos | ★★☆☆☆ Low-medium | Ethics gray even with PII scrub — looks like stalking. Not lead portfolio. | **Side demo only.** |
| 10 | **partha (Tamil meme Tanglish bot + meme retrieval)** `ideas.md:59` | ★★★★☆ High for Tamil meme culture | ★★☆☆☆ Low: memes not enterprise | Fun, ties to Tamil edge + tool calling (meme folder), but hiring manager won't pay for yellow/pink font sentiment. Keep as personality side. | **Fun, not hire.** |

### Tier C — Demo only, don't lead resume

| 11 | **wo--men (male/female frame filter)** `ideas.md:25` | ★★☆☆☆ Tutorials everywhere (OpenCV gender) | ★☆☆☆☆ None — novelty | Ethics/bias minefield, no usefulness. | **No.** |
| 12 | **Athu ethu yethu (Tamil game LLM realtime)** `ideas.md:35` | ★★★☆☆ Medium fun | ★☆☆☆☆ Game logic trivial | Needs realtime STT-LLM-TTS low latency — hard, low interview ROI (just loop). | **No.** |
| 13 | **Offtxt (SMS data)** `ideas.md:82` — already `off-txt` 3.5/10 broken `repo-analysis.md:23` | ★★★☆☆ Unique idea, but you tried and core flow sends to hardcoded number | ★★☆☆☆ Feasibility low: 48kb image = 300 SMS (100/day limit), grayscale 10% looks bad, QR rebuild brittle | Interviewers poke holes: cost, latency, 100 SMS waste claim weak (most have WiFi). | **Don't double down.** |
| 14 | **Deep fake handwriting (salim)** `ideas.md:45` | ★★★☆☆ Research niche | ★★☆☆☆ Medium | Needs handwriting GAN/diffusion (needs 200+ samples per user), not 30-day Python+SQL feasible. | **Research, not job.** |

### Tier F — Avoid (ethics / ToS / too heavy)

| 15 | **instagram story patch (merge tagged stories via ReVanced)** `ideas.md:52` | ★★★☆☆ Unique | ★★☆☆☆ Frustration real | Violates Instagram ToS, needs reverse engineering, patch distribution = ban risk. `platform to generate patches` = liability. | **No — unsafe.** |
| 16 | **AI person finder in CCTV** `ideas.md:97` | ★★☆☆☆ Exists (face search) | ★★☆☆☆ Surveillance | Privacy, heavy video infra, needs face recognition at scale — not fresher solo. | **No.** |
| 17 | **healthprix halo (ASR for doctors, The Pitt)** `ideas.md:100` | ★★☆☆☆ Many medical ASR | ★★☆☆☆ High liability | Medical accuracy, needs fine-tune, HIPAA-like. | **No.** |
| 18 | **movie title extractor (poster OCR)** `ideas.md:104` | ★☆☆☆☆ Low: OCR already does, plus you must ignore artist names | ★☆☆☆☆ Low | Too narrow, not defensible. | **No.** |
| 19 | **Annachi (impatient AI personality)** `ideas.md:110` | ★☆☆☆☆ Gimmick | ★☆☆☆☆ None | No engineering depth — prompt persona. | **No.** |

---

## What to do brutally

You have 19 ideas, 3 are gold, 3 are okay, 13 are job-market suicide. You don't need more ideas — you need one `Gov scheme` **or** `Fresherr` shipped with:

* `Postgres` not SQLite + `Redis` cache + `JWT` auth (`roadmap.sh/backend` missing)
* 15 tests (`tamil-tokenizer` pattern 23 tests) + `Dockerfile` + `GH Actions` + live URL `fresher-must-have-skills-2026 10-point checklist`
* `heap` done (Kth Largest, Top K) + `site:lever.co` 3 apps/day classified A/B/C/D

Pick **#1 Gov scheme** if you want RAG backend (my reco — Tamil voice = moat), or **#2 Fresherr** if you want fastest win (labour codes fresh, no one patched templates yet). Don't do detector (#7) — you'll be 5th clone on Chrome Store.

*Next: update `roadmaps/2026-09-02.html` with 15-min Redis/Postgres micro-task added to Project 2.*

