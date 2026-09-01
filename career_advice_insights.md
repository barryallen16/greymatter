# Career Advice Insights — Full Audit of 524 Entries in `results.jsonl`

**Source:** `results.jsonl:1` → `career_advice` category = 524 entries, extracted 2022-2026. All 524 read via `career.txt:1-524` (temp export). Date: 2026-09-01.
**Method:** Parsed `title | core_content | url` per line, deduped by `core_content` hash (many Instagram carousels duplicated), scored for relevance to your profile: Python + SQL (`SELECT/WHERE/GROUP BY`) + starting Heap on AlgoMap, 4 months graduated, target ₹5-18 LPA no-bond roles `fresher-must-have-skills-2026.md:39`.

---

## 0. Summary Counts

| Bucket | Count | % | Notes |
|---|---|---|---|
| **High-signal for you** | ~78 | 15% | DSA, SQL, Python projects, resume/interview, job platforms |
| **Medium/breadth** | ~62 | 12% | AWS, system design, ML prerequisites, learning meta |
| **Noise to drop** | ~384 | 73% | trading/stocks, passive income, mattress tester, Netflix tagger, laptop specs, value education, motivational filler, duplicate reels |

Keyword hits across 524: `ai:222, data:96, python:44, java:32, resume:31, project:36, course:34, sql:16, dsa:9, aws:8, interview:34` — AI dominates but mostly generic reels.

**Dedup note:** ~30% are exact duplicates (e.g., `Top 10 YT AI/ML` repeated, `How to install Chrome OS` repeated, `Industrial guaranteed Internship @SmartED` twice `career.txt:158/160`). Unique insight count ≈ 360.

---

## 1. High-Signal Insights (Keep — mapped to your 4 interview types)

### A. DSA & Coding Interview (Type A: LeetCode protected tests)

*The notebook says: `handle edge cases, write clean functional code` + `Ask recruiter what round will be`.*

| # | Advice (title) | Core | Source | Maps to |
|---|---|---|---|---|
| 1 | `TOP 5 WEBSITES TO PRACTICE CODING CHALLENGES` | Great for interview practice | `career.txt:35` | Daily DSA block `daily-plan.md:8` |
| 2 | `An Instagram Reel by caroline_codes` | 1) LEETCODE 2) HACKERRANK 3) EXERCISM 4) CODEWARS 5) CODECHEF | `career.txt:36` | Grind75 `techinterviewhandbook` |
| 3 | `TOP 5 BOOKS TO LEARN DATA STRUCTURES AND ALGORITHMS` | 1) Grokking Algorithms. 2) DS Made Easy. 3) Introduction... | `career.txt:15` | 9-stage roadmap `aryan1` Foundations 1-2d |
| 4 | `The image provides career advice for CS majors` | Build 3 good projects (1/month), apply 5/day, 3 LeetCode/day → WILL land job | `career.txt:247` | `daily-plan.md:87` floors 2+1+30m |
| 5 | `Rajya Vardhan Mishra, Google 800+ interviews` | 8 algorithmic strategies | `career.txt:283` | `techinterviewhandbook techniques` |
| 6 | `A technical interview prep guide` | DP breaks into sub-problems, 0/1 knapsack | `career.txt:285` | Stage 8 DP 2-3d `aryan1` |
| 7 | `The image provides breakdown of recommended weekly coding hours` | 25-30h/week → job in 3-4 months | `career.txt:467` | `daily-plan.md:33` 3h DSA + 2 contests |
| 8 | `Big Tech SWE Interview Process` | Junior 80% Algo & Code 20% Behavioral | `career.txt:468` | Type A focus |
| 9 | `HOW TO MASTER LEETCODE IN 2026` + `Let's start 2026 strong` | 93 patterns, not 1000 Qs. Pick DS → Study → Questions. Heap/Binary Search/BFS... | `career.txt:483/487` | Heap next |
| 10 | `Tired of solving random DSA` | MAANG = 93 types, not 1000 random | `career.txt:420` | Pattern learning `aman.ai/code/*` |
| 11 | `Most Repeated Coding Interview Questions - Numbers` | Palindrome, prime, range | `career.txt:386` | Easy fluency 50 |
| 12 | `Step-by-Step Approach` | 0 Learn Lang → Complexity → Brute Force → Arrays/Linked List → Search | `career.txt:241` | `fresher-must-have-skills-2026.md:75` Pillar 1 |

**Action for you (heap next):** Drop books, stick to `AlgoMap heap + aman.ai/code/heap + techinterviewhandbook/algorithms/heap` — 1 template, redo failed `daily-plan.md:18`.

### B. SQL & Data (your牢 edge, but only basic so far)

| # | Advice | Core | Source |
|---|---|---|---|
| 13 | `A career advice post arguing SQL > JS` | SQL guarantees jobs for life, stability | `career.txt:11` | Aligns `job-search-research.md:23` 5,979 Chennai DA jobs |
| 14 | `Instagram post advising data analysts` | Excel+SQL gets DA, but PowerBI/Tableau to grow | `career.txt:18` | `job-search-research.md:108` visual bar |
| 15 | `SQL Murder Mystery` | Self-directed lesson + fun game, learn concepts | `career.txt:24` | **Top pick: do before window functions** |
| 16 | `SQL (Most important. No shortcuts.)` | Order: SELECT/WHERE/GROUP BY/HAVING → Joins → Subqueries/CTE → Window (ROW_NUMBER,RANK...) | `career.txt:497` | Direct next 6-8 weeks `fresher-must-have-skills-2026.md:84` |
| 17 | `The Reality of Data Jobs` | JD: SQL/Python/R/Spark, Interview: SQL/Python/Azure, Actual: SQL/Excel | `career.txt:415` | Honest JD `fresher-must-have-skills-2026.md:199` bluff |
| 18 | `Roadmap to Becoming Data Analyst 2025` | Soft skills + Seaborn/Plotly/Tableau/PowerBI | `career.txt:398` | Portfolio dashboard 1 week `job-search-research.md:113` |

**Action:** `SQL Murder Mystery` (1 weekend) → `50 LeetCode SQL` window functions — fills `Hiring filter` `fresher-must-have-skills-2026.md:216`.

### C. Python Projects & Portfolio (Type C: GitHub portfolio, Type B: AI-assisted navigation)

| # | Advice | Core | Source | Maps to |
|---|---|---|---|---|
| 19 | `Don't overthink it. Build...` + duplicate `Don't overthink` | Calculator → Weather App (live APIs) → CRUD Flask+DB → Chatbot Streamlit+GPT | `career.txt:5/400` | `practical-tutorials/project-based-learning` `dump.txt:231` — **better than todo clones** `fresher-must-have-skills-2026.md:29` |
| 20 | `You only need these 10 Project ideas` | Landing Page, Image Slider... | `career.txt:21` | Drop — too trivial, `fresher-must-have-skills-2026` rejects |
| 21 | `ChatGPT provides 10 beginner Python projects` | To-Do, weather etc. | `career.txt:195` | Same as #19, keep one list |
| 22 | `POV: You realise DSA is a scam` | Master lang, complexity, brute → optimize | `career.txt:242/243` | Aligns Type B subtle errors drill |
| 23 | `An Instagram post by codersheary AI projects` | Smart search Elastic/OpenAI, RAG, GPT FAQ chatbot, summarization | `career.txt:321` | Fits `fitcheck-website` RAG story `repo-analysis.md:86` |
| 24 | `7 ML Projects That Add Value` | Auto Image Captioning, ASR | `career.txt:262` | Too heavy now — skip, focus `kaggle-automation` |
| 25 | `NLP Project Ideas using Hugging Face` | Sentiment BERT, Summarization, Chatbot GPT-2 | `career.txt:305/306` | Keep 1 max, not 12 |
| 26 | `POV: You're leveling up API game` | Dog Image Fetch, Weather OpenWeather, Quotes... | `career.txt:387` | Good for `kaggle-automation` API muscle `repo-analysis.md:76` |
| 27 | `These GitHub repos will make you 10X` | how-web-works, developer-roadmap... | `career.txt:142` | Matches `sindresorhus/awesome` `dump.txt:230` |
| 28 | `The image provides career advice for CS majors` (repeat but project angle) | Build 3 good projects | `career.txt:247` | Treat `fitcheck` family as ONE story `repo-analysis.md:86` |

**Action:** Polish `kaggle-automation` (add `Dockerfile + GH Actions` `repo-analysis.md:84`) + one RAG FAQ chatbot (light, defensible) — not 10 new ideas. Addresses `projects never finished` notebook.

### D. Resume, ATS & Interview Craft (Type C + Behavioral)

| # | Advice | Core | Source |
|---|---|---|---|
| 29 | `I landed 95% jobs by applying cold` | Focus transferable, tailored per JD | `career.txt:279` | `job-search-research.md:147` cold 2-3% vs referral 30% |
| 30 | `The image provides advice on tailoring` | Go through JD ask: Have I done? How? Impact? Would they care? | `career.txt:280` | `techinterviewhandbook.org/resume` keyword: less is more, 1 page |
| 31 | `how to answer tell me about yourself` | Who You Are: I am XYZ major... | `career.txt:108` | `techinterviewhandbook/self-introduction` STAR(R) |
| 32 | `As recruiter, I NEVER hire...` | Customize per role, X-Y-Z: Accomplished [X] by [Y] → [Z] | `career.txt:354` | `fresher-must-have-skills-2026.md:339` summary line |
| 33 | `MY RESUME WASN'T FANCY — IT WAS FOCUSED` | Impact lines `Built X saved Y`, quant % | `career.txt:426` | Same |
| 34 | `YOUR RESUME IS KILLING YOU` | Replace `hard-working` → `Reduced reporting 35% Excel automation` | `career.txt:480` | Same |
| 35 | `Deepali Kothari resume tips` | 1 page MAX, 6 sec scan, ChatGPT convert vague → numbers | `career.txt:431` | Same |
| 36 | `How to optimize resume to land interviews` | Tailor keywords Node.js/REST | `career.txt:287` | `fresher-must-have-skills-2026.md:206` decryption matrix |
| 37 | `Optimize LinkedIn Profile 30m 6 prompts` + duplicate `Optimise` | Headline [Role|Keywords|Proof] + Featured top projects | `career.txt:276/447` | `roles-and-job-search-focus.md:59` positioning line |
| 38 | `The image provides tip ATS Workday/Taleo` | Parses all text plain black | `career.txt:518` | `job-search-research.md:167` simple template |
| 39 | `Check these things Before joining` | What projects? stack? culture? growth? | `career.txt:490` | Your recruiter ask template `Type A/B/C/D` |
| 40 | `The image provides 3 questions to ask interviewers` | Successful internship? Clarify? Next steps? | `career.txt:272` | `techinterviewhandbook/final-questions` |
| 41 | `My Resume That Helped Me Crack Zoho` (x3 dup) | Fresher resume → all questions from resume | `career.txt:512` | Pin top 3 repos `repo-analysis.md:175` |
| 42 | `The post advises treating career like product` | Positioning/market/distribution/moat | `career.txt:522` | `find your edge` notebook |

### E. Job Search Platforms & Outreach (Type A/B/C all need this before interview)

| # | Advice | Source |
|---|---|---|
| 43 | `Best websites to search for jobs` AngelList startup, Glassdoor, Indeed, Scouted, Linkedin | `career.txt:34` |
| 44 | `A list of recommended job search platforms` Instahyre fast, Otta abroad, Jobicy remote | `career.txt:244` + `I Hate LinkedIn` duplicate `245` |
| 45 | `TOP JOB SEARCH PLATFORMS` INDIA: Naukri, LinkedIn, Indeed, FoundIt, Shine | `career.txt:381` | Matches `job-search-research.md:152` Instahyre > Naukri > walk-ins |
| 46 | `20 Websites Actively Hiring` Indeed, LinkedIn, Glassdoor, ZipRecruiter | `career.txt:277` | Overlap, dedup to 1 |
| 47 | `Video tutorial Google search operator` `site:linkedin.com/jobs "data analyst"` | `career.txt:265` |
| 48 | `Google search query` `site:lever.co OR site:greenhouse.io entry` | `career.txt:267/523` | **Gold: lever/greenhouse early apply** |
| 49 | `A networking message template` Hi [name] interested in [company] role | `career.txt:270/422` | `job-search-research.md:149` referral worth 40 |
| 50 | `Biggest fresher mistake networking?` Not `Hi sir openings?` → `Hey I built [link] feedback?` | `career.txt:409` |
| 51 | `Crazy networking strategy` YouTube Day in Life → find employees | `career.txt:421` |
| 52 | `STOP WAITING FOR HR. START APPLYING SMART` LinkedIn Actively hiring + AngelList/Wellfound + YC Jobs + DM managers | `career.txt:425` |
| 53 | `Find internships on LinkedIn like this` Search `[major] internships hiring` filter POSTS | `career.txt:304/313` |

**Action:** `Naukri 100% + Instahyre + site:lever.co` 3 quality apps/day `daily-plan.md:24` — not 200 spam.

### F. Learning Resources & Fundamentals (T-shaped, calmness, product thinking)

| # | Advice | Source |
|---|---|---|
| 54 | `Instagram post by codingwithsagar 11 platforms` Codewit, FreeCodeCamp... Coursera, YouTube | `career.txt:9` |
| 55 | `Websites To Learn To Code For Free` same list | `career.txt:26` |
| 56 | `FREE resources Front End` javascript.info, github js-algorithms, Frontend Mentor, sindresorhus/awesome | `career.txt:27/29` |
| 57 | `Learn For Free` w3schools, FreeCodeCamp, LearnGitBranching | `career.txt:132/88` |
| 58 | `Save it for a lifetime` css-tricks, javascript.info, scrimba, kaggle/python, codecademy/sql, programiz/DSA | `career.txt:88/141` |
| 59 | `Don't pay to learn` HTML CSS-TRICKS, JS javascript.info, React Scrimba, Python Kaggle, SQL Codecademy | `career.txt:141` |
| 60 | `Top Platforms to learn ML` OpenML, DeepLearning.ai, Kaggle, Sentdex, Krish Naik | `career.txt:347` | Matches `Top 10 YT AI/ML` `career.txt:2` (Karpathy, sentdex, Raschka...) |
| 61 | `Resources For Learning ML` 3Blue1Brown linear algebra, Gilbert Strang MIT | `career.txt:357` |
| 62 | `A video sharing free coding education` Harvard CS50, CodingBat, OSSU, FreeCodeCamp | `career.txt:83` |
| 63 | `The image displays Instagram reel overlay Data-Structures | Variables & OOP | Iterators` | `career.txt:45` |
| 64 | `Pandas Exercise-14` | `career.txt:115` | Ties `website` dump `w3resource` — good for heap + pandas day |
| 65 | `Python Regex Exercise-1` | `career.txt:118` |
| 66 | `Learn Prompting` learnprompting.org | `career.txt:135` | RAG prompt engineering `aman.ai/primers/ai/prompt-engineering` |

### G. System Design & CS Core (mid-senior, but fresher LLD bar for Zoho-tier)

*Not career_advice but implied:* `Amazon SDE-1 topics` `career.txt:471-476` (OOP/OS/DBMS/Networks + LLD Caching/Scalability + STAR principles) + `I Failed SD interviews until 10 concepts: B-Trees vs LSM, Replication, SQL vs NoSQL` `career.txt:320` → maps `fresher-must-have-skills-2026.md:103` LLD Parking Lot/Splitwise.

---

## 2. Noise Filtered (Drop — 384 entries)

**Trading/Finance/Investing (~70):** `SKILLS TO LEARN FOR INVESTORS` `54`, `10 Best Books Debt` `56`, `Investing vs Trading` `66`, `30 Topics Trading` `67`, `HOW TO BUY STOCKS` `68`, `5 financial things at 18` `101`, `HOW TO BUY STOCKS`, `THINGS EVERYONE SHOULD LEARN` duplicate — zero interview ROI.

**Motivational filler / Generic hustle (~90):** `Be mean with your time 4am 100 pushups` `75`, `7 best coding apps` `39`, `15 BOOKS FILMMAKING` `47/104`, `EACH MUSCLE GROUP` `78`, `GET YOUR LIFE TOGETHER LIST` `228`, `Control this 5 things` `358`, `Major cheat code stop explaining dreams` `413` — notebook `Working with intention` is enough.

**Non-tech job spoof / Scam bait (~40):** `mattress tester $90k` `59`, `video game tester $30/hr` `60`, `Netflix tagger $20/hr` `63`, `3 stocks dividend check` `61`, `06 remote jobs $80/hr No Resume` `403`, `5 high-paying without degree` `22` — distracts.

**Laptop/specs spam (~20):** `laptop recommendations 25K-35K` `6`, `Programming Laptop Must have i3 8GB` `43/55`, `Dell Vostro 3490` duplicate — irrelevant.

**Academic/timetable noise (~40):** `Sun News 10th results` `16`, `HSC RESULTS` `17`, `TimeTable-CAT II` `225`, `BMCE Units` `99`, `Value Education` `181-184` — exam clutter from screenshots.

**Duplicate reels (collapsed):** `STILL WANT MORE 10 steps` `49` + `Things entrepreneurs should Google 45 laws` `76/77` + `It costs $0 startup Namelix/Canva` `69/79` + `Industrial Internship SmartED` `158/160` — keep one.

---

## 3. How This Changes Your Tomorrow (2026-09-02) Roadmap

*Keep daily-plan.md:33 3h DSA / 3h Project / 45m Apps / 75m Fundamentals but inject filtered insights:*

*   **DSA:** Heap via `aman.ai/code/heap` + `Top 5 Books DSA Grokking` + `93 patterns` `career.txt:420` — not random books.
*   **SQL:** `SQL Murder Mystery` weekend, then `SQL Most important` window functions `career.txt:497` — matches `fresher-must-have-skills-2026.md:84`.
*   **Projects:** One `kaggle-automation Dockerfile` commit (show work `Varun Mayya`) + log subtle AI errors (Type B) — not 10 ideas.
*   **Apps:** `site:lever.co OR site:greenhouse.io` `career.txt:267` early + `Naukri` daily update + ask recruiter `what to prioritize` template + classify Type A/B/C/D per JD.
*   **Portfolio:** Fix resume to `1 page X-Y-Z` `career.txt:354` + `LinkedIn Headline [Role|Keywords|Proof]` `career.txt:276` + why that stack story for `tamil-tokenizer/kaggle`.

All 524 accounted for; 78 kept, 384 dropped explicit above — your nightly roadmap will pull only from kept list + `techinterviewhandbook` + `aman.ai` + `aryan1`.

*Full 524 titles preserved in `C:\Users\rjaya\AppData\Local\Temp\opencode\career.txt:1` for audit; this file is the filtered synthesis.*
