# The Plan — Daily Schedule + DSA Ladder (Sep → Nov 2026)

**Non-negotiable rule #1:** Fixed wake time every day, including weekends. Hours can shift ±30 min, the *sequence* never changes.
**Non-negotiable rule #2:** Phone charges overnight OUTSIDE the bedroom. First screen you touch is LeetCode.
**Non-negotiable rule #3:** One line per day in a notebook: date, problems attempted, solved-without-help Y/N, commit made, applications sent. No fancy tools.

**What you have:** 5,340 archived screenshots that ARE your curriculum — 25 OS lectures (paging, critical sections, page tables), 15 heap/tree resources (USFCA heap visualizer, VisuAlgo, tree-traversal notes), 77 SQL shots (incl. SQL Murder Mystery), the "15 Must-Know DSA Patterns" card. Stop collecting advice. Study your own archive.

---

## The Day (Mon–Sat)

| Time | Block | What happens |
|---|---|---|
| **7:00** | Wake | Water. No phone. Shoes on. |
| 7:00–7:40 | Body | 20 min walk/run/skip + shower. Movement before screens. |
| 7:40–8:10 | Breakfast | Same thing every day. Fewer decisions = less friction. |
| **8:10–9:40** | DSA Block 1 — LEARN | This week's pattern (see ladder). ONE explainer (NeetCode ≤20 min) + implement the template once by hand. |
| 9:40–9:55 | Break | Walk, water. Not Instagram. |
| **9:55–11:25** | DSA Block 2 — REDO | Re-solve yesterday's failed problems from scratch, blank editor. Failed redos count double. |
| 11:25–11:35 | Break | Move. |
| **11:35–13:05** | Project Block 1 | Deep work on this week's project task. Timer on. |
| **13:05–14:00** | Lunch + rest | Real rest. Food, chai, lie down. Screen-free. |
| **14:00–15:30** | Project Block 2 | Continue. Stop at a clean checkpoint, write a 1-line "next step". |
| 15:30–15:45 | Break | Walk. |
| **15:45–16:30** | Applications | 3 quality applications OR 5 referral messages OR a mix. Don't classify the JD upfront — the A/B/C/D type gets set only when an application converts to an OA/interview (that's when it tells you what to prep). Use your own ATS tooling. Log everything in the tracker. |
| **16:30–17:45** | Exercise | Gym / run / cricket — 60+ min elevated heart rate. This makes the other 9 hours possible. |
| 17:45–18:15 | Snack + shower | |
| **18:15–19:30** | Fundamentals rotation | Mon/Wed/Fri: OS, DBMS, Networks, OOP (interview theory). Tue/Thu/Sat: AI fundamentals (transformers, embeddings, RAG vs fine-tuning). **Study from your archive, not new PDFs** — it already has the good material. |
| **19:30–20:15** | Dinner | With family. |
| 20:15–21:00 | Review + plan | Update tracker. Write TOMORROW's 3 tasks on paper. 5-min flashcards: patterns, complexity, SQL joins, OS questions. |
| 21:00–22:30 | Free | Guilt-free. No LeetCode after 21:00 — sleep needs a runway. |
| **23:00** | Lights out | 8 hours. A tired brain solves zero graph problems. |

**Daily totals: DSA 3h · Projects 3h · Applications 45m · Fundamentals 1h15m**

## Sunday

| Time | What |
|---|---|
| Morning | Sleep in max 1 hr (protect the rhythm). |
| **10:30–12:15** | **LeetCode Weekly Contest** (live, timed). This IS mock-interview training. |
| 12:15–13:30 | Upsolve every missed problem, editorial allowed. |
| Afternoon | OFF. Recharge is part of the program. |
| 19:00–19:30 | Weekly review: problems vs target, applications sent, project milestone? Next week's 3 priorities. |

Saturday 20:30: **Biweekly Contest** when scheduled.

---

## The DSA ladder — patterns in dependency order

Learn patterns in the order each one NEEDS the previous. **Starting point: Trees (Ladder 5) — that's where algomap has you.** Trees pull stacks (iterative traversals) and hash maps (seen-sets, level tracking) in through redos, so backfill Ladders 1–4 one redo at a time alongside — don't pause trees for them. (Cross-check: the "15 Must-Know DSA Patterns" card in your archive — Sliding Window, Two Pointers, Prefix Sum, Tree Traversal, DFS, BFS, Matrix, Backtracking, DP, Fast & Slow, In-Place Reversal, Monotonic Stack, Binary Search, Intervals, Top K — same spine, reordered so nothing is used before it's taught.)

### Ladder 1 — Arrays & Hashing (3 wks · ~30 problems, backfill alongside trees)
Everything else uses a hash map.
1. Hash map + set basics → Two Sum, Contains Duplicate, Valid Anagram
2. Prefix counting → Group Anagrams, Top K Frequent (bucket count version)
3. Prefix sum → Range Sum Query, Subarray Sum Equals K
4. Closed by [Two Pointers + Sliding Window](../archive/?q=two%20pointers%20sliding%20window) week: Valid Palindrome, 3Sum, Longest Substring Without Repeating, Best Time to Buy/Sell

### Ladder 2 — Stacks (1 wk · ~8 problems)
Monotonic stack is just "hash map of next-greater" with a stack. Valid Parentheses → Min Stack → Daily Temperatures → Evaluate Reverse Polish.

### Ladder 3 — Linked Lists (1 wk · ~8 problems)
Your archive has 24 linked-list notes (doubly circular, pseudo-code) from ChatGPT sessions — redo them properly. Fast & Slow pointers (cycle detection) → Reverse a Linked List → Merge Two Sorted Lists → Reorder List. The pointer gymnastics here is exactly what makes tree recursions survivable.

### Ladder 4 — Binary Search (1 wk · ~6 problems)
Binary search = sliding window on a sorted answer space. Classic → Search in Rotated Sorted Array → Find Minimum in Rotated → Koko Eating Bananas.

### Ladder 5 — Trees (2 wks · ~15 problems) ← START HERE (current algomap section)
A tree is a linked list that forks; BFS here is queue = sliding window on levels. Videos come straight from your own subscription index (yt-ssf @ adhi.isroot.in — search it before hunting YouTube).
1. **Traversal week:** recursive preorder/inorder/postorder → iterative with an explicit stack → level order with a queue. Watch: mycodeschool "Binary tree traversal: Preorder, Inorder, Postorder" (`gm8DUJJhmY4`) + "breadth-first and depth-first strategies" (`9RHO6jU--GU`); Alvin's LeetCode 94/144/145 tutorials for the iterative variants. Reading: aman.ai/code/data-structures/#binary-tree + aman.ai DFS pages (via your aman-ai index).
2. **BST week:** code io - Tamil Ep-26 insert/search (`qZkQ6CZm2Tw`) + Ep-27 delete (`ZZp5EaXJXlo`) and mycodeschool's BST implementation (`COZK7NATh4k`) — all already in your feed. Problems: Validate BST → Search in BST → LCA → Max Depth/Diameter.
Visuals: [VisuAlgo](https://visualgo.net/en) + [USFCA tree/heap visualizer](https://www.cs.usfca.edu/~galles/visualization/MinHeap.html) cards already saved in your archive.

### Ladder 6 — Heaps (1 wk · ~6 problems, after trees — where it always belonged)
A heap is just a tree with a shape rule + "keep the top-k while scanning" (a prefix-count problem). The old plan started restarts HERE — learning a new structure on day one of a broken streak — which is why it produced zero twice. Trees first, then heaps is one new thing on an existing foundation.
1. **Day 1:** Write a bucket-count + heapq solution for Top K Frequent. It is Arrays-&-Hashing knowledge plus `heapq`, nothing new — that's why it works on day one.
2. Day 2: Kth Largest Element (same pattern, one line different). Then Last Stone Weight, K Closest Points.
3. Merge K Sorted Lists — the one real heap algorithm. Redo without help next day.

### Ladder 7 — Backtracking (1 wk · ~6 problems)
DFS on a tree you build while you walk it. Subsets → Permutations → Combination Sum → Word Search. Needs Ladder 5's DFS only.

### Ladder 8 — Graphs (2 wks · ~12 problems)
BFS/DFS you already know from trees, on an adjacency list. Number of Islands → Clone Graph → Course Schedule (topo sort) → Union-Find: Number of Connected Components.

### Ladder 9 — 1-D DP (2 wks · ~10 problems)
DP = backtracking + a hash map of solved states (Ladders 1 + 7). Climbing Stairs → House Robber → Coin Change → Longest Increasing Subsequence → Word Break.

### Ladder 10 — 2-D DP + Greedy + Intervals (2 wks · ~10 problems)
Unique Paths → Edit Distance (cross-check OS paging theory from your archive's 25 OS notes — same state-table thinking). Greedy: Jump Game. Intervals: Merge Intervals, Non-overlapping Intervals.

**Total: ~16 weeks ≈ Nov 20, ~110–120 problems at the NeetCode-150 spine.** Track weekly on the [NeetCode roadmap](https://neetcode.io/roadmap).

---

## Projects (parallel, one track only)

| Phase | Weeks | Task |
|---|---|---|
| Cleanup | 1 | Revoke Telegram token + 2 OpenRouter keys, purge `.env` history, scrub `middleman` PII, delete Vadachennai/project01/salim/TensorTonic-Solutions |
| kaggle-automation hardening | 2–5 | Dockerfile that passes `docker build .` → GitHub Actions CI (pytest + lint) → SQLite → Postgres in compose (one index + `EXPLAIN ANALYZE`) → Redis cache-aside + rate limit |
| Ship one flagship | 6–9 | Pick **Gov scheme recommender** (RAG, your #1 ranked idea) **or** **Fresherr** (offer-letter checker). FastAPI + Postgres + tests + live URL |
| Interview prep | 10–16 | 1 mock/week. 6 STAR stories mapped to your repos. Interview debrief doc within 24h of every round |

---

## Targets (put on your wall)

| Metric | Now | Sep 30 | Oct 31 | Nov 30 |
|---|---|---|---|---|
| Problems | 72 | 130 | 200 | 280 |
| Contest rating | unrated | 1500+ | 1600+ | 1650+ |
| Applications sent | ? | 40 | 90 | 150 |
| Referral conversations | 0 | 10 | 25 | 40 |

(Previous plan said 180 problems by Sep 30 — that was 108 problems in 5 weeks alongside 3h/day of projects. Not happening. These targets are: ~2 problems/day, every day, no hero weeks.)

**Minimum viable day** (when life happens): 2 problems + 1 application + 30 min project. Never zero. Streak > perfection.
