# Skill Gap Analysis — Fresher Tech Roles, India

**Date:** 2026-10-06
**Corpus:** 3,802 scraped postings -> 1,481 fresher software roles -> 1,056 with real descriptions
**Subject:** Jayadithya R (`profile.json`)
**Scope:** Geography filter deliberately disabled (per user request). Fresher + software roles only.

---

## 1. Scale

| Stage | Rows |
|---|---|
| DB when analysis started | 790 (only **18** reportable by the existing pipeline) |
| After wide harvest (freehire + X + LinkedIn) | **3,802** |
| Pass spam + software-domain filters | ~2,900 |
| **Fresher + software corpus (corrected gate)** | **1,481** |
| With descriptions >=250 chars | **1,056** |
| Distinct companies | **912** |
| AI/ML + GenAI subset | **356** |

Role family mix (descriptions only, n=1,010 dated 2026 or later):

| Family | Count |
|---|---|
| AI/ML & GenAI | 318 |
| Web / Support / Other | 275 |
| Python / Backend | 121 |
| DevOps / Cloud | 78 |
| Fullstack / JS-Web | 54 |
| QA / Test | 53 |
| Data Analyst / BI | 47 |
| Java / JVM | 19 |
| Data Engineering | 17 |
| Cyber / InfoSec | 16 |
| Mobile / Android | 12 |

---

## 2. Two real bugs in the existing fresher gate

`jobpipe/match.py` was undercounting fresher roles. Found by stress-testing the
regexes against phrasing I expected them to handle.

### Bug 1 — `BODY_EXCLUDE` rejects fresher-friendly experience ranges

`jobpipe/match.py:83`

```
0-2 years    -> kept
0-3 years    -> REJECTED   (wrong)
1-3 years    -> REJECTED   (wrong)
up to 3 years-> REJECTED   (wrong)
less than 3  -> REJECTED   (wrong)
under 3 years-> REJECTED   (wrong)
2-4 years    -> REJECTED   (borderline)
3+ years     -> REJECTED   (correct)
```

`BODY_EXCLUDE` matches any `[3-9]` followed by "year", with no notion of whether
the number is a floor or a ceiling. **46 real rows lost**, including:

- Praxair India (Linde) — "hiring FRESHER Data Scientists", `Exp: 0-3 Yrs`
- Siemens EDA — "Fresh graduates to early-career professionals (0 to 3 years)"
- HPE — "Software Systems Engineer (DevOps)", 1 to 3 years
- Cisco — Software Engineer, 1-3 Years
- JPMorgan — Data Analyst, 1 to 5 years
- Virtusa — "#Java Fresher Openings", 0-7 years

Corrected gate: parse the experience range into (lo, hi). Accept when `hi <= 3`.
When a range straddles the ceiling (`2-4`, `3-5`), decide by whether the **title**
carries a junior/fresher/graduate/intern signal, not the body.

Net effect of the corrected gate: **1,481 roles vs 1,447** under the old one.

### Bug 2 — `DOMAIN_EXCLUDE` is leaky

Only matches a fixed word list, so non-software roles survive as "tech":
`Buyer`, `Legal Counsel`, `Urban Planner`, `Account Manager`, `Network Project
Associate`, `Jr. Site Engineer`, `Supplier Quality Engineer`.

Conversely my own replacement over-rejected `AI Data Specialist` (lost on
"specialist"), `Security Engineering Intern` (lost on "security"), and
`QA Test Engineering` (lost on `qa\b`). Final filter keeps software terms
explicit and excludes only unambiguously non-software titles.

---

## 3. Method

Four passes. Three of them failed first and had to be redesigned — recorded here
because the failures are the reason to trust the result.

**Pass 1 — curated lexicon.** ~120 hand-written skill regexes, matched against
requirement sections only. Interpretable, but only finds skills I anticipated.

**Pass 2 — n-gram frequency. FAILED.** Top terms were `software` (569),
`solutions` (388), `performance` (356), `related` (366). Frequency in technical
prose is dominated by ordinary English.

**Pass 3 — co-occurrence with technical vocabulary. ALSO FAILED.** Scored each
term by the share of its postings that contained >=3 core tech words. This
returned `the` at 90% technicality, `and` at 89%, `with` at 88%. Generic words
sit inside technical postings just as often as technical words do. The filter
was measuring the wrong thing.

**Pass 4 — structural position. WORKED.** Restrict candidates to **titles and
bullet lines** (positions where JDs list tools, not prose), require the term to be
unexplained by any lexicon regex, then rank by posting prevalence. Output became
clean: remaining terms were recruiter names (`kumar`, `akshay`, `vazima`),
company suffixes (`ltd`, `pvt`, `inc`), and aggregator tags (`allweb3jobs`,
`duniyaas`, `work4freshers`).

**Pass 5 — targeted probe.** Frequency can only find frequent skills. Probed ~60
skills deliberately excluded from the lexicon, including post-cutoff ones
(agentic AI, MCP, LangGraph, vector DBs). Only one regex found zero hits
(`feature stores / pipelines`).

**Profile evidence.** `profile.json` scanned in full — skills array, project
tech, descriptions, bullets — not just the skills block.

---

## 4. Findings

Ranked by demand in AI/ML + GenAI postings. A skill counts as a gap only if the
profile cannot back it **by substance**.

### Tier 1 — real gaps with high demand

| # | Skill | All roles | AI/ML roles | Verdict |
|---|---|---|---|---|
| 1 | **Agentic AI / multi-agent systems** | 7.0% | **16.7%** | No agent loop, orchestration, or tool-calling anywhere in the profile |
| 2 | **DSA / algorithms** | 17.0% | **23.0%** | Engineering ability is proven; DSA practice is not evidenced |
| 3 | **Azure** | 16.3% | **16.7%** | AWS EC2 only |
| 4 | **Kubernetes** | 9.6% | 7.9% | Docker only; Compose is not orchestration |
| 5 | **LangChain / LangGraph** | 2.8% | **8.5%** | RAG skills exist, no framework ever used |
| 6 | **GCP** | 11.1% | 11.9% | — |

**DSA is the one that actually gates you.** Every proctored fresher round in the
external research (TCS NQT Prime, Infosys SP, HackWithInfy, Accenture,
Cognizant GenC Next, Fractal) screens on live DSA and SQL before anyone reads a
portfolio. No premium GenAI knowledge compensates for failing that gate.

### Tier 2 — genuine gaps, narrower demand

| Skill | All roles | AI/ML roles | Note |
|---|---|---|---|
| Model serving / deployment | 0.9% | — | GGUF quantization proves packaging, not serving |
| MLOps | 2.6% | 6.3% | CI + Docker + 12 test suites prove discipline; no registry/serving/monitoring |
| Redis / caching | 5.3% | 5.3% | Meilisearch is search, not a cache |
| pandas / numpy | 4.2% | 9.7% | Data pipelines described in prose; libraries unnamed |
| Terraform / IaC | 7.4% | 3.8% | Only worth it for DevOps/SRE, not AI |
| Browser automation (Playwright/Selenium) | 3.2% | 2.5% | scrapy/yt-dlp prove scraping only |
| Power BI / Tableau | 4.8% | 4.7% | — |
| Postman | 3.0% | 3.5% | — |
| Time-series / forecasting | 2.3% | 4.1% | — |
| GraphQL | 2.3% | 1.9% | — |
| Observability / monitoring | 9.5% | 8.2% | Session monitor is a cron script, not observability |
| MCP | 0.8% | 1.9% | Barely on the market yet |

### Tier 3 — already yours, but the profile never says so

These are resume omissions, not skill gaps. Each one is currently costing
screening matches.

| Skill | All roles | AI/ML roles | Substantive evidence |
|---|---|---|---|
| **Communication** | 41.0% | 32.7% | First-author IEEE paper — the strongest soft-skill artifact available |
| **PyTorch** | 5.3% | 15.1% | Unsloth LoRA fine-tuning runs on PyTorch; the word never appears |
| **RAG** | 5.9% | 17.0% | ChromaDB + Meilisearch embeddings + 4-phase distillation |
| **Vector DB** | 3.9% | 10.7% | ChromaDB is a vector store |
| **Computer vision** | 3.0% | 7.5% | FashionCLIP, Qwen3-VL auto-annotation across 106K images |
| **Recommender systems** | 14.1% | 11.6% | FitCheck is a published recommender paper |
| **React** | 16.2% | 15.4% | Next.js and React Native are React |
| **System design** | 17.0% | 23.0% | 19-account credential pool, 223 GPU runs, hash-checkpointed resume |
| **Statistics** | 11.5% | 18.6% | p<0.05, r=0.303, N=849 |
| **English proficiency** | 16.0% | 10.7% | IEEE publication |
| **Git** | 28.9% | 28.9% | — |
| **REST API** | 21.4% | 22.3% | — |
| **SQL / PostgreSQL** | 25.6% | 28.0% | — |
| **CI/CD** | 21.3% | 14.8% | uv sync + ruff + pytest in Actions |
| **Docker** | 14.5% | 16.4% | — |
| **Python** | 41.1% | 56.9% | — |
| **Testing** | 11.0% | 8.5% | 12 suites, 23 tokenizer tests, 40+ lit tests |
| **FastAPI** | 4.3% | 8.5% | — |
| **TypeScript** | 11.3% | 12.9% | — |
| **Java** | 17.6% | 12.3% | VulnChecker-Java |

---

## 5. Recommended order of action

1. **Rewrite the skills block in `profile.json`** to explicitly name PyTorch,
   RAG, vector database, computer vision, React, pandas/numpy, and MLOps. ~20
   minutes of work; closes six gaps that do not exist.
2. **Start DSA and SQL practice.** This is the actual filter.
3. **Build one agentic AI project** — an orchestrator plus two or three
   specialised agents with tool use and an evaluation step. Highest demand gap
   (16.7% of AI roles) and the fastest visible win.
4. Learn **LangGraph/LangChain** while building #3 — 8.5% of AI roles.
5. Add **Azure** alongside AWS if targeting product companies.

Deliberately skipped: Terraform, Redis, GraphQL, Postman, Power BI. Real gaps,
but low demand for the AI/ML track.

---

## 6. External cross-check

The corpus conclusions were checked against independent 2026 fresher postings:

- **Cognizant Ace Team** (Full-Stack AI Engineer, 2026 batch only) asks for
  RAG pipelines, LangChain/LangGraph/CrewAI/AutoGen, prompt engineering,
  embeddings, vector DB concepts, CI/CD, containers, Kubernetes.
- **Siemens Energy** (0-3 yrs) asks for Python, ML, RAG, NLP, FastAPI, cloud,
  embeddings, DSA.
- **Fujitsu Data & AI Apprentice** (0-1 yr) — Python and SQL mandatory, plus
  scikit-learn/TensorFlow/PyTorch, Hugging Face, LangChain, Azure Data Factory,
  Databricks, Power BI, REST APIs.
- **UnitedHealth/Optum** (2026 batch, NIT/IIT only) — Python FastAPI or Java
  Spring, React, GCP, RESTful APIs, Agile.
- **AI engineering placement market analysis, 2026** — describes a core layer
  (Python, SQL, DSA, Git, one web framework) that filters before any premium
  skill is evaluated, and a premium layer (agentic AI, LLM/RAG, MLOps) worth
  20-40% salary uplift. Agentic AI named as the slice most freshers have not
  touched.

Every Tier 1 gap above is corroborated by independent sources.

---

## 7. Limitations

Where this analysis could be wrong:

- **Source bias.** freehire is 49% of the corpus, linkedin 30%, X 27%. X postings
  report communication at 5% vs linkedin's 57% — social posts are keyword-stuffed
  and thin. Per-source cross-check of the two large independent sources agrees
  closely (python 42% vs 53%, azure 21% vs 27%), so the main signal is not an
  artifact of one source. X and whatsapp are **excluded from percentage
  reporting** where they distort it.
- **Two sources failed mid-harvest.** `jobsalertx` returns HTTP 404 (dead RSS
  feed). `careervalore` returns HTTP 400 beyond `pages=3`. Coverage of non-metro
  India is therefore likely underrepresented.
- **LinkedIn under-sampled.** ~7.6 minutes per 30 query/location pairs; stopped
  at 110 pairs instead of running another ~40 minutes.
- **Document frequency, not requirement rate.** A skill in a JD's
  responsibilities section counts the same as one under "required". Requirement
  sections were isolated heuristically; the parser misses JDs that do not use
  headings. Treat percentages as prevalence, not as must-have rates.
- **No geographic split**, per instruction. Geography changes which skills are
  actually asked for.
- **Corpus skew.** The fresher tech market in this data skews service/aggregator
  heavy (TCS/Infosys/Cognizant patterns). Product companies and AI labs are thin,
  so the DSA and system-design bar is probably **understated** for the roles most
  worth targeting.
- **Freshness.** 57 rows carry `posted_at` from 2016-2025; they are included in
  the corpus but the reported percentages use the 1,010 rows dated 2026 or later.

---

## Reproducing

Scripts live in `C:\Users\rjaya\AppData\Local\Temp\opencode\skillgap\` (temp dir,
not committed):

| File | Role |
|---|---|
| `corpus.py` | loads DB, original gate baseline |
| `gate_audit.py` | stress-tests the fresher gate regexes |
| `fixed_gate.py` | corrected early-career gate + domain filter |
| `final_corpus.py` | canonical 1,481-role corpus, dedupe |
| `mine.py` | role families, curated lexicon, n-grams |
| `analysis.py` | requirement sections, prevalence vs profile evidence |
| `discover3.py` | working n-gram discovery (titles + bullets) |
| `probe.py` | targeted probe for skills outside the lexicon |
| `verdict.py` | separates true gaps from resume omissions |

No repository files were modified and nothing was committed.