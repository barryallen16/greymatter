"""Match postings against profile.json: fresher filter, location, tier, keyword score.

Decisions locked in FINDINGS.md (Q1-Q3, Q9):
  Q1 location  : Chennai + Remote (India)
  Q2 fresher   : 0-2 yrs OR batch 2025-2027 OR intern; exclude senior/3+ yrs
  Q3 tiers     : A = GenAI/ML/NLP, B = Python/backend/TS, C = DB only
  Q9 report    : top 20; Tier B needs score >= 3; >14 days = stale, excluded
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .sources import Posting

MIN_TIER_B_SCORE = 3  # Q9: Tier B rows need at least this many distinct profile skills

LOCATION_OK = re.compile(
    r"\bchennai\b|\bremote\b(?!\s+(?:sensing|desktop|access|troubleshooting|server|wipe|support|management|host|console))|work[\s-]from[\s-]home|\bwfh\b",
    re.I,
)

# Stricter remote check when evaluating posting body prose (when location field is empty)
TEXT_LOCATION_OK = re.compile(
    r"\bchennai\b|work[\s-]from[\s-]home|\bwfh\b"
    r"|\b(?:fully\s+remote|100%\s+remote|remote\s+(?:in|across)\s+india|remote\s+(?:developer|engineer|intern|internship|role|position|job|work|opportunity))\b"
    r"|\b(?:location|mode|workplace)\s*[:–-]\s*remote\b",
    re.I,
)

FRESHER_INCLUDE = re.compile(
    r"fresher|fresh(?:er)? graduate|new grad|graduate engineer|graduate trainee"
    r"|\btrainees?\b|apprentice\w*|walk[\s-]?ins?|off[\s-]?campus|on[\s-]?campus"
    r"|entry[\s-]level|junior|\bintern(?:ship)?s?\b"
    r"|\b(?:0\s*[-–]?\s*)?[12]\s*(?:\+|-|to)?\s*(?:years?|yrs?)\b"
    r"|(?:batch|graduat\w+|pass(?:ed)? out|class of)\s*(?:of\s*)?202[5-7]"
    r"|202[5-7]\s*(?:batch|graduat\w+)",
    re.I,
)

FRESHER_EXCLUDE = re.compile(
    r"\b[3-9]\s*\+?\s*(?:-|to)?\s*\d*\s*(?:years?|yrs?)"
    r"|\b[3-9]\s*(?:-|to)\s*\d+\s*(?:years?|yrs?)"
    r"|\bsenior\b|\bstaff\b|\bprincipal\b|\blead\b|\bhead of\b"
    r"|experience(?:d)?\s+only|\bmanager\b|\bdirector\b"
    r"|\barchitect\b|\bco[\s-]?founders?\b|\bfounders?\b|\bcto\b|\bceo\b",
    re.I,
)

# Non-tech / non-software role titles that must not dilute the report
DOMAIN_EXCLUDE = re.compile(
    r"\b(?:mechanical|civil|electrical|electronics\s+hardware|hardware\s+design"
    r"|vlsi|embedded\s+hardware|biotech|biotechnology|bioinformatics"
    r"|medical\s+coding|clinical\s+research|nursing|pharmacy"
    r"|sales|business\s+development|bpo|telecaller|telemarketing|customer\s+support"
    r"|desktop\s+support|workstation\s+support|intune\s+support|helpdesk"
    r"|voice\s+process|non[\s-]voice|content\s+writer|copywriter|seo\s+executive"
    r"|accountant|accounts\s+executive|financial\s+analyst|audit\s+associate"
    r"|graphic\s+designer|motion\s+designer|video\s+editor)\b",
    re.I,
)

TECH_ROLE_OVERRIDE = re.compile(
    r"\b(?:software|developer|programmer|ai\s+engineer|ml\s+engineer|data\s+scientist|data\s+engineer|nlp\s+engineer|backend)\b",
    re.I,
)

# Aggregator roundup tweets / weekly digests that pack multiple unrelated roles into one post
SPAM_EXCLUDE = re.compile(
    r"\b\d+\s+(?:fresh|new)\s+\w*\s*(?:internships?|roles?|opportunities|jobs?)\s+found\b"
    r"|fresh\s+web3\s+internships"
    r"|\broundup\b|\bweekly\s+digest\b|\bdaily\s+digest\b",
    re.I,
)

# Body copy is scanned for the numeric experience bar only. Job descriptions say
# "work with senior engineers", "escalate to senior stakeholders" and "Principal
# Duties" in roles that are explicitly for freshers, so a word match anywhere in
# the body threw away 50 of 585 rows. Measured 2026-09-25: 82 rows recovered, 0 lost.
BODY_EXCLUDE = re.compile(
    r"\b[3-9]\s*\+?\s*(?:-|to)?\s*\d*\s*(?:years?|yrs?)"
    r"|\b[3-9]\s*(?:-|to)\s*\d+\s*(?:years?|yrs?)",
    re.I,
)

TIER_A = re.compile(
    r"gen[\s-]?ai|generative ai|machine learning|\bml\b|\bnlp\b|\bllms?\b|deep learning"
    r"|data scientist|data engineer|ai engineer|ai/ml|pytorch|tensorflow"
    r"|hugging[\s-]?face|prompt engineer|computer vision|mlops|\brag\b"
    r"|language models?|fine[\s-]?tun\w+|llm eval|tokeniz\w+|embeddings?|inference"
    r"|\blora\b|\bunsloth\b|diffusion|\bgpt\b|\bbert\b|\bwhisper\b|semantic search"
    r"|vector[\s-]?(?:db|database)s?|recommender|data\s+annotat\w+|data\s+label\w+|human eval"
    r"|\brlhf\b|\bdpo\b|reinforcement learning",
    re.I,
)
TIER_B = re.compile(
    r"\bpython\b|backend|back[\s-]end|fastapi|django|flask|typescript|javascript"
    r"|\bnode\b|node\.?js|next\.?js|full[\s-]stack|software engineer|web developer"
    r"|\bapis?\b|data pipeline|\betl\b|\bsql\b|postgres|developer|analyst"
    r"|\brust\b|react\b|devops|docker|kubernetes|graphql|mongodb|redis\b"
    r"|\baws\b|\bazure\b|\bgcp\b|kafka\b|spark\b|airflow|terraform|supabase"
    r"|ci/?cd|rest[\s-]?api",
    re.I,
)

# Tokens too generic to be useful as standalone skill keywords.
STOPWORDS = {
    "engineer",
    "plus",
    "face",
    "next",
    "learn",
    "native",
    "github",
    "actions",
    "coder",
    # halves of hyphen/slash compounds whose full form is already a keyword:
    # "LoRA fine-tuning (Unsloth)" and "CLIP/transformers.js" split into these.
    "fine",
    "tuning",
    "clip",
}


def _tokens(item: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", item.lower())


def load_keywords(profile_path: Path) -> list[str]:
    """Profile-driven keyword list: whole skill items, their solid tokens,
    headline tokens, and project tech tokens. Split fragments shorter than
    4 chars (yt, dlp) and generic words (engineer, plus, ...) are dropped —
    they matched everywhere (analytics, everything, ...)."""
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    words: set[str] = set()
    for group in profile.get("skills", []):
        if group.get("category") == "Spoken Languages":
            continue
        for item in group.get("items", []):
            if "(" not in item:  # "lora fine-tuning (unsloth" can never match a posting
                words.add(item.lower())
            for tok in _tokens(item):
                if len(tok) >= 4 and tok not in STOPWORDS:
                    words.add(tok)
    for extra in profile.get("headline", "").lower().split():
        token = extra.strip(" .,()")
        if len(token) >= 3 and token not in STOPWORDS:
            words.add(token)
    for proj in profile.get("projects", []):
        for tech in proj.get("tech", []):
            for tok in _tokens(tech):
                if len(tok) >= 5 and tok not in STOPWORDS:
                    words.add(tok)
                    if tok.endswith("s") and not tok.endswith("es") and len(tok) > 5:
                        words.add(tok[:-1])  # datasets -> dataset
    cleaned = sorted({w.strip(" .,()") for w in words if len(w.strip(" .,()")) > 1})
    return cleaned


def is_fresher(text: str) -> bool:
    if FRESHER_EXCLUDE.search(text):
        return False
    return bool(FRESHER_INCLUDE.search(text))


def head_of(post: Posting) -> str:
    """The part of a posting that names the role: title, location, company."""
    return f"{post.title} {post.location} {post.company}"


def is_fresher_post(post: Posting) -> bool:
    """Fresher test for a real posting: seniority words count only in the head
    (title/location/company); the body only has to clear the years-of-experience bar."""
    if FRESHER_EXCLUDE.search(head_of(post)) or BODY_EXCLUDE.search(post.text):
        return False
    return bool(FRESHER_INCLUDE.search(f"{head_of(post)} {post.text}"))


def is_tech_domain(post: Posting) -> bool:
    """Reject roles whose titles explicitly denote non-software domains (mechanical,
    sales, medical coding, desktop support) unless overridden by explicit software role terms."""
    title = post.title.lower()
    if DOMAIN_EXCLUDE.search(title) and not TECH_ROLE_OVERRIDE.search(title):
        return False
    return True


def is_spam_post(post: Posting) -> bool:
    """Detect bot roundups / newsletters on X/socials that pack multiple jobs into one."""
    return bool(SPAM_EXCLUDE.search(post.title))


def in_location(location: str = "", text: str = "") -> bool:
    """Location gate: passes Chennai, Remote/WFH. If location field is empty,
    fall back to stricter check on body text to avoid false positives on 'remote desktop'."""
    loc = location.strip()
    if loc:
        return bool(LOCATION_OK.search(loc))
    if not text.strip():
        return True  # Empty location passes (query already constrained it, e.g. LinkedIn/X)
    return bool(TEXT_LOCATION_OK.search(text))


def tier_of(text: str) -> str:
    if TIER_A.search(text):
        return "A"
    if TIER_B.search(text):
        return "B"
    return "C"


EXACT_ONLY_KEYWORDS = {"rust", "gemma", "bert", "dpo", "rag", "clip"}

SKILL_WEIGHTS = {
    # Core specializations (3x)
    "tokenizer": 3,
    "tokenizers": 3,
    "bpe": 3,
    "unsloth": 3,
    "lora": 3,
    "mlir": 3,
    "llvm": 3,
    "qwen": 3,
    "vlm": 3,
    "distillation": 3,
    "tamil": 3,
    # Advanced AI / ML / Systems stack (2x)
    "fastapi": 2,
    "pytorch": 2,
    "hugging": 2,
    "huggingface": 2,
    "chromadb": 2,
    "meilisearch": 2,
    "gemma": 2,
    "scikit": 2,
    "eval": 2,
    "datasets": 2,
    "dataset": 2,
    "rag": 2,
    "llm": 2,
    "nlp": 2,
}


def matched(keywords: list[str], text: str) -> list[str]:
    """Profile skills found in text. Single tokens match whole words or word
    prefixes (rust matches rusty, not trust); multi-word items match verbatim.
    Short ambiguous keywords (eval, rust, etc.) require exact word boundaries or domain context.
    Subsumed hits collapse (sql + sqlite counts once)."""
    haystack = text.lower()
    hits = []
    for kw in keywords:
        if kw == "eval":
            # Match technical eval: 'eval', 'evals', 'model evaluation', 'eval harness'
            # but reject HR boilerplate ('fair and consistent evaluation based on...')
            if re.search(
                r"\bevals?\b|\b(?:model|llm|prompt|human|benchmark|system|code)\s+eval\w*|eval\w*\s+harness\b",
                haystack,
            ):
                hits.append(kw)
        elif kw in EXACT_ONLY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"s?\b", haystack):
                hits.append(kw)
        elif re.fullmatch(r"[a-z0-9]+", kw):
            if re.search(r"\b" + re.escape(kw) + r"\w*", haystack):
                hits.append(kw)
        else:
            if kw in haystack:
                hits.append(kw)
    return [kw for kw in hits if not any(o != kw and kw in o for o in hits)]


def score_of(keywords: list[str], text: str) -> int:
    return len(matched(keywords, text))


def weighted_score_of(keywords: list[str], text: str) -> int:
    """Weighted relevance score prioritizing core specialization & AI/ML stack."""
    hits = matched(keywords, text)
    return sum(SKILL_WEIGHTS.get(k, 1) for k in hits)


def classify(post: Posting, keywords: list[str]) -> tuple[str, int, bool, str]:
    """Returns (tier, score, include_in_report, reason)."""
    blob = f"{post.title} {post.location} {post.company} {post.text}"
    if is_spam_post(post):
        return "C", 0, False, "spam-roundup"
    if not is_tech_domain(post):
        return "C", 0, False, "unrelated-domain"
    if not in_location(post.location, post.text):
        return "C", 0, False, "location"
    if not is_fresher_post(post):
        return "C", 0, False, "not-fresher"
    tier = tier_of(blob)
    score = score_of(keywords, blob)
    if tier == "C":
        return "C", score, False, "tier-c"
    if tier == "B" and score < MIN_TIER_B_SCORE:
        return "B", score, False, "score-threshold"
    if post.posted_at and post.posted_at < datetime.now(UTC) - timedelta(days=14):
        return tier, score, False, "stale"
    return tier, score, True, "ok"


def select_report_rows(rows: list[dict], limit: int = 20) -> list[dict]:
    """Tier A first, then Tier B, best score within each tier, capped.
    Tie-breaks on weighted skill score, and dedupes identical job requisitions
    (same company + normalized title)."""
    ordered = sorted(
        rows,
        key=lambda r: (
            r["tier"],
            -r.get("score", 0),
            -r.get("weighted_score", r.get("score", 0)),
        ),
    )
    seen_roles: set[tuple[str, str]] = set()
    deduped = []
    for r in ordered:
        comp = re.sub(r"[^a-z0-9]", "", (r.get("company") or "").lower())
        title_norm = re.sub(r"[^a-z0-9]", "", (r.get("title") or "").lower())
        key = (comp, title_norm)
        if comp and title_norm and key in seen_roles:
            continue
        if comp and title_norm:
            seen_roles.add(key)
        deduped.append(r)
        if len(deduped) >= limit:
            break
    return deduped
