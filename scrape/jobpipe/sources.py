"""Job sources. Each returns list[Posting]; failures raise and are caught by run.py."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


@dataclass
class Posting:
    source: str
    ext_id: str
    url: str
    title: str
    company: str = ""
    location: str = ""
    text: str = ""
    posted_at: datetime | None = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_urgent: bool = False
    is_featured: bool = False


def _get(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed allowlist of hosts)
        return resp.read().decode("utf-8", errors="replace")


# --- freehire -----------------------------------------------------------------
FREEHIRE_API = "https://freehire.me/api/v1/agent/jobs/search"


def freehire(queries: list[str], days: int = 14, limit: int = 50) -> list[Posting]:
    out: list[Posting] = []
    for q in queries:
        params = urllib.parse.urlencode(
            [
                ("q", q),
                ("countries", "in"),
                ("posted_within_days", str(days)),
                ("limit", str(limit)),
                ("include_description", "true"),
                ("description_format", "text"),
            ]
        )
        data = json.loads(_get(f"{FREEHIRE_API}?{params}"))
        for row in data.get("data", []):
            posted = _parse_iso(row.get("posted_at"))
            out.append(
                Posting(
                    source="freehire",
                    ext_id=row.get("public_slug") or row["url"],
                    url=row.get("url", ""),
                    title=(row.get("title") or "").strip(),
                    company=(row.get("company") or "").strip(),
                    location=(row.get("location") or "").strip(),
                    text=_strip_html(row.get("description") or ""),
                    posted_at=posted,
                )
            )
    return out


# --- CareerValore (WordPress: `job` category of wp/v2/posts) --------------------
CAREERVALORE_API = "https://careervalore.com/wp-json/wp/v2/posts"
CAREERVALORE_JOB_CAT = 1362

_CV_SPLIT = re.compile(
    r"\s+(?:hiring(?: for)?|walk[\s-]?ins?|recruitment|off[\s-]?campus)\s+",
    re.I,
)
# "Citi – Hiring for Technology – Full Time Analyst @Chennai": the place is after
# the @, not after the first dash — matching a dash first parsed the location as
# "Full Time Analyst" and dropped 8 Chennai/Remote rows on the location gate.
_CV_AT = re.compile(r"\s@\s*([A-Z][\w\s.&()/]{1,40})")


def _cv_company_location(title: str) -> tuple[str, str]:
    """Best-effort `Company – Hiring for Role @ Place` split; empty when unsure."""
    parts = _CV_SPLIT.split(title, maxsplit=1)
    company = parts[0].strip(" –-|:") if len(parts) == 2 else ""
    at = _CV_AT.search(title)
    location = at.group(1).strip(" .,|") if at else ""
    return company, location


def careervalore(pages: int = 3, per_page: int = 100) -> list[Posting]:
    """Latest posts in the `job` category (job_listings type is stale spam)."""
    out: list[Posting] = []
    for page in range(1, pages + 1):
        params = urllib.parse.urlencode(
            {
                "categories": CAREERVALORE_JOB_CAT,
                "per_page": per_page,
                "page": page,
                "orderby": "date",
                "order": "desc",
                "_fields": "id,slug,date,link,title,content",
            }
        )
        data = json.loads(_get(f"{CAREERVALORE_API}?{params}"))
        if not data:
            break
        for row in data:
            title = _strip_html((row.get("title") or {}).get("rendered") or "")
            company, location = _cv_company_location(title)
            out.append(
                Posting(
                    source="careervalore",
                    ext_id=str(row.get("id")),
                    url=row.get("link", ""),
                    title=title,
                    company=company,
                    location=location,
                    text=_strip_html((row.get("content") or {}).get("rendered") or ""),
                    posted_at=_parse_iso(row.get("date")),
                )
            )
    return out


# --- FresherOffCampus (WordPress wp/v2/posts; latest posts are all fresher job ads) --
FRESHEROFFCAMPUS_API = "https://www.fresheroffcampus.com/wp-json/wp/v2/posts"

_FOC_OFF = re.compile(r"\s+off[\s-]?campus\s+", re.I)
_FOC_ROLE = re.compile(r"\bhiring freshers? for\b", re.I)


def fresheroffcampus(pages: int = 2, per_page: int = 100) -> list[Posting]:
    """Latest posts unfiltered: every recent post is a `Company Off Campus …` hiring ad."""
    out: list[Posting] = []
    for page in range(1, pages + 1):
        params = urllib.parse.urlencode(
            {
                "per_page": per_page,
                "page": page,
                "orderby": "date",
                "order": "desc",
                "_fields": "id,slug,date,link,title,content",
            }
        )
        data = json.loads(_get(f"{FRESHEROFFCAMPUS_API}?{params}"))
        if not data:
            break
        for row in data:
            title = _strip_html((row.get("title") or {}).get("rendered") or "")
            if "off campus" not in title.lower() or "fresher" not in title.lower():
                continue  # guides/roundups, not postings
            company = _FOC_OFF.split(title, maxsplit=1)[0].strip(" –-|:")
            rest = _FOC_ROLE.split(title, maxsplit=1)
            body = rest[1] if len(rest) == 2 else title
            role, sep, location = body.rpartition("|")
            if not sep:
                role, location = body, ""
            out.append(
                Posting(
                    source="fresheroffcampus",
                    ext_id=str(row.get("id")),
                    url=row.get("link", ""),
                    title=_clean(role),
                    company=company,
                    location=location.strip(" .,|"),
                    text=f"{title} {_strip_html((row.get('content') or {}).get('rendered') or '')}",
                    posted_at=_parse_iso(row.get("date")),
                )
            )
    return out


# --- CareerDiscover job portal (public JSON API, no auth) ------------------------
JOBPORTAL_API = "https://job-portal-zeta-two-46.vercel.app/api/v1/jobs"
JOBPORTAL_SITE = "https://job-portal-zeta-two-46.vercel.app"


def jobportal(limit: int = 100) -> list[Posting]:
    """Paginate the public /api/v1/jobs endpoint ({success, data, pagination})."""
    out: list[Posting] = []
    page = 1
    while page <= 10:
        params = urllib.parse.urlencode({"page": page, "limit": limit})
        data = json.loads(_get(f"{JOBPORTAL_API}?{params}"))
        for row in data.get("data", []):
            company = row.get("company") or {}
            cat = row.get("category") or {}
            loc = ", ".join(
                dict.fromkeys(
                    p for p in [row.get("city"), row.get("state"), row.get("country")] if p
                )
            )
            out.append(
                Posting(
                    source="jobportal",
                    ext_id=f"jp-{row.get('id')}",
                    url=f"{JOBPORTAL_SITE}/jobs/detail/{row.get('slug')}",
                    title=(row.get("title") or "").strip(),
                    company=(company.get("name") or "").strip(),
                    location=loc or (row.get("workMode") or ""),
                    text=" ".join(
                        p if isinstance(p, str) else " ".join(map(str, p))
                        for p in [
                            row.get("title"),
                            company.get("name"),
                            row.get("employmentType"),
                            row.get("experienceLevel"),
                            row.get("workMode"),
                            row.get("sector"),
                            cat.get("name"),
                            row.get("requiredSkills"),
                        ]
                        if p
                    ),
                    posted_at=_parse_iso(row.get("publishedAt") or row.get("createdAt")),
                    is_urgent=bool(row.get("isUrgent")),
                    is_featured=bool(row.get("isFeatured")),
                )
            )
        pg = data.get("pagination") or {}
        if page >= pg.get("totalPages", page):
            break
        page += 1
    return out


# --- FresherFlow India Jobs (public JSON on GitHub, no auth) ----------------------
FRESHERFLOW_JSON = (
    "https://raw.githubusercontent.com/FresherFlow/India-Jobs-Internships/main/data/jobs.json"
)


def fresherflow() -> list[Posting]:
    """Curated India fresher jobs/internships feed. Skips EXPIRED listings."""
    data = json.loads(_get(FRESHERFLOW_JSON))
    out: list[Posting] = []
    for row in data.get("jobs", []):
        if (row.get("status") or "").upper() != "PUBLISHED":
            continue
        locs = [str(loc) for loc in (row.get("locations") or [])]
        mode = (row.get("workMode") or "").strip()
        if mode and mode.lower() not in {loc.lower() for loc in locs}:
            locs.append(mode.title())
        posted = row.get("addedAt") or ""
        if not posted and row.get("dateAdded"):
            posted = f"{row['dateAdded']}T00:00:00Z"
        out.append(
            Posting(
                source="fresherflow",
                ext_id=row.get("id") or row.get("applyLink", ""),
                url=row.get("applyLink", ""),
                title=(row.get("title") or "").strip(),
                company=(row.get("company") or "").strip(),
                location=", ".join(locs),
                text=" ".join(
                    p
                    for p in [
                        row.get("title"),
                        row.get("company"),
                        row.get("type"),
                        mode,
                        " ".join(row.get("tags") or []),
                        row.get("notesHighlights"),
                    ]
                    if p
                ),
                posted_at=_parse_iso(posted or None),
            )
        )
    return out


# --- JobsAlertX (Supabase PostgREST when JOBSALERTX_ANON_KEY is set, else feed.xml) --
JOBSALERTX_FEED = "https://jobsalertx.com/feed.xml"
JOBSALERTX_PGREST = "https://pgrqwluwsizrjbfansdc.supabase.co/rest/v1/jobs"
JOBSALERTX_SITE = "https://jobsalertx.com"


def _rss_field(body: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", body, re.S)
    return m.group(1).strip() if m else ""


def _rss_items(text: str) -> list[dict]:
    items = []
    for chunk in re.split(r"<item[>\s]", text)[1:]:
        body = chunk.split("</item>")[0]
        items.append({t: _rss_field(body, t) for t in ("title", "link", "description", "pubDate")})
    return items


def _jobsalertx_postgrest(key: str, limit: int = 200) -> list[Posting]:
    """Direct read of Published jobs (reversed 2026-10-13: site queries Supabase
    PostgREST from client JS; the anon key is public by design)."""
    params = urllib.parse.urlencode(
        {
            "select": "*",
            "status": "eq.Published",
            "order": "created_at.desc",
            "limit": str(limit),
        }
    )
    req = urllib.request.Request(
        f"{JOBSALERTX_PGREST}?{params}",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:  # noqa: S310 (fixed host)
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    out: list[Posting] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        loc = (row.get("location") or "").strip()
        mode = (row.get("workplace") or "").strip()
        if mode and mode.lower() not in loc.lower():
            loc = f"{loc} ({mode})" if loc else mode
        out.append(
            Posting(
                source="jobsalertx",
                ext_id=str(row.get("id")),
                url=f"{JOBSALERTX_SITE}/jobs/{row.get('id')}",
                title=(row.get("title") or "").strip(),
                company=(row.get("company") or "").strip(),
                location=loc,
                text=" ".join(
                    p if isinstance(p, str) else " ".join(map(str, p))
                    for p in [
                        row.get("title"),
                        row.get("company"),
                        row.get("experience_label"),
                        row.get("job_type"),
                        mode,
                        row.get("salary_range"),
                        row.get("skills"),
                        _strip_html(row.get("description") or ""),
                    ]
                    if p
                ),
                posted_at=_parse_iso(row.get("posted_date") or row.get("created_at")),
            )
        )
    return out


def jobsalertx() -> list[Posting]:
    """PostgREST when the anon key resolves (env or site JS), else feed.xml fallback."""
    key = _jobsalertx_key()
    if key:
        try:
            return _jobsalertx_postgrest(key)
        except Exception:  # noqa: BLE001 — backend change must not sink the source
            pass
    return _jobsalertx_feed()


_JAX_KEY: str | None = None  # process cache: resolved once per run


def _jobsalertx_key() -> str:
    """Env first; else extract the public anon key from the site's own JS bundle."""
    global _JAX_KEY
    if _JAX_KEY is None:
        _JAX_KEY = os.environ.get("JOBSALERTX_ANON_KEY", "")
        if not _JAX_KEY:
            try:
                home = _get(f"{JOBSALERTX_SITE}/jobs/remote")
                for chunk in set(re.findall(r"/_next/static/[^\"']+\.js", home)):
                    js = _get(f"{JOBSALERTX_SITE}{chunk}")
                    m = re.search(
                        r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\."
                        r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
                        js,
                    )
                    if m:
                        _JAX_KEY = m.group(0)
                        break
                else:
                    _JAX_KEY = ""
            except Exception:  # noqa: BLE001 — extraction failure falls back to feed
                _JAX_KEY = ""
    return _JAX_KEY


def _jobsalertx_feed() -> list[Posting]:
    """Parse feed.xml (20 fresh jobs/day with location/type/level in description)."""
    from email.utils import parsedate_to_datetime

    out: list[Posting] = []
    for row in _rss_items(_get(JOBSALERTX_FEED)):
        link = row["link"]
        if "/jobs/" not in link:
            continue  # blog guides, not postings
        title, _, company = row["title"].rpartition(" at ")
        if not company:
            title, company = row["title"], ""
        # description head: "{Role} at {Company} — {Location} | TYPE | ...".
        head = row["description"].split("|")[0]
        _, sep, after = head.rpartition(" at ")
        if not sep:
            location = head.strip()
        else:
            dash = re.search(r"\s[—–-]\s", after)
            location = after[dash.end() :].strip() if dash else ""
        try:
            posted = parsedate_to_datetime(row["pubDate"]).astimezone(UTC)
        except (ValueError, TypeError):
            posted = None
        out.append(
            Posting(
                source="jobsalertx",
                ext_id=link.rstrip("/").rsplit("/", 1)[-1],
                url=link,
                title=_clean(title),
                company=_clean(company),
                location=location,
                text=_strip_html(row["description"]),
                posted_at=posted,
            )
        )
    return out


# --- JobFound (Next.js: homepage embeds a JSON-LD ItemList of the latest jobs) -----
JOBFOUND_URL = "https://jobfound.org/"

_JF_DATE_TAIL = re.compile(r"-\d{1,2}-[a-z]+-\d{4}/?$", re.I)
_JF_PLACE = re.compile(
    r"\b(bengaluru|bangalore|chennai|hyderabad|mumbai|pune|delhi|gurgaon|gurugram|"
    r"noida|kolkata|ahmedabad|kochi|coimbatore|jaipur|indore|remote|hybrid|india)\b",
    re.I,
)


def _jf_posted(url: str) -> datetime | None:
    """Slugs end in `-12-october-2026`; parse it, None when the shape changes."""
    m = re.search(r"(\d{1,2})-([A-Za-z]+)-(\d{4})/?$", url)
    if not m:
        return None
    try:
        return datetime.strptime(
            f"{m.group(1)}-{m.group(2).title()}-{m.group(3)}", "%d-%B-%Y"
        ).replace(tzinfo=UTC)
    except ValueError:
        return None


def jobfound() -> list[Posting]:
    """Parse the homepage JSON-LD job list (~45 fresh postings, one fetch, no auth)."""
    html = _get(JOBFOUND_URL)
    m = re.search(r'<script id="job-list-structured-data"[^>]*>(.*?)</script>', html, re.S)
    data = json.loads(m.group(1)) if m else {}
    out: list[Posting] = []
    for item in data.get("itemListElement", []):
        url = item.get("url") or ""
        if "/job/" not in url:
            continue
        name = item.get("name") or ""
        title, _, company = name.rpartition(" at ")
        if not company:
            title, company = name, ""
        slug = _JF_DATE_TAIL.sub("", url.rstrip("/").rsplit("/job/", 1)[-1])
        places = list(dict.fromkeys(p.title() for p in _JF_PLACE.findall(f"{name} {slug}")))
        out.append(
            Posting(
                source="jobfound",
                ext_id=slug,
                url=url,
                title=_clean(title),
                company=_clean(company),
                location=", ".join(places),
                text=_clean(f"{name} {slug.replace('-', ' ')}"),
                posted_at=_jf_posted(url),
            )
        )
    return out


# --- LinkedIn guest (no auth, no cookies) -------------------------------------
LINKEDIN_GUEST = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
LINKEDIN_DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"
LINKEDIN_PAUSE = 1.2  # guest endpoints are ToS-gray: one detail GET, spaced out


def _linkedin_description(job_id: str) -> str:
    """Search cards carry no description, so every guest posting scored 0 and failed
    the fresher gate. One detail GET per posting fixes both; empty string on failure."""
    try:
        body = _get(f"{LINKEDIN_DETAIL}{job_id}", timeout=20)
    except Exception:  # noqa: BLE001 — a dead detail page must not sink the source
        return ""
    m = re.search(r"description__text[^>]*>(.*?)</div>", body, re.S) or re.search(
        r"show-more-less-html__markup[^>]*>(.*?)</div>", body, re.S
    )
    return _strip_html(m.group(1)) if m else ""


def linkedin_guest(queries: list[tuple[str, str]], days: int = 7) -> list[Posting]:
    """queries: list of (keywords, location). No account, no cookies: keep volume low.

    One detail fetch per card, spaced out — LinkedIn returns 10 cards per query.
    """
    out: list[Posting] = []
    tpr = f"r{days * 86400}"
    for keywords, location in queries:
        params = urllib.parse.urlencode(
            {"keywords": keywords, "location": location, "f_TPR": tpr, "start": 0}
        )
        html = _get(f"{LINKEDIN_GUEST}?{params}")
        for chunk in html.split("<li")[1:]:
            jid = re.search(r"urn:li:jobPosting:(\d+)", chunk)
            if not jid:
                continue
            title = re.search(r"<h3[^>]*>(.*?)</h3>", chunk, re.S)
            company = re.search(
                r"base-search-card__subtitle[^>]*>(.*?)</(?:a|span|div)>", chunk, re.S
            )
            href = re.search(r'base-card__full-link[^>]*href="([^"]+)"', chunk)
            when = re.search(r'<time[^>]*datetime="([^"]+)"', chunk) or re.search(
                r"(\d+)\s+(minute|hour|day|week)s?\s+ago", chunk
            )
            time.sleep(LINKEDIN_PAUSE)
            out.append(
                Posting(
                    source="linkedin",
                    ext_id=jid.group(1),
                    url=(href.group(1) if href else "").split("?")[0],
                    title=_clean(title.group(1) if title else ""),
                    company=_clean(company.group(1) if company else ""),
                    location=location,
                    text=_linkedin_description(jid.group(1)),
                    posted_at=_parse_when(when) if when else None,
                )
            )
    return out


# --- X / Twitter via twitter-cli (burner cookies in env) ----------------------
def x_twitter(queries: list[str], max_results: int = 20) -> list[Posting]:
    """Shells out to `twitter-cli`. Needs TWITTER_AUTH_TOKEN + TWITTER_CT0 (burner account).

    Skips cleanly if the binary or the credentials are missing.
    """
    if not shutil.which("twitter"):
        raise RuntimeError("twitter-cli not installed (uv tool install twitter-cli)")
    out: list[Posting] = []
    for q in queries:
        proc = subprocess.run(  # noqa: S603 fixed argv, no shell
            ["twitter", "search", q, "-t", "Latest", "--max", str(max_results), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"twitter: no JSON (exit {proc.returncode}): {_stderr_tail(proc.stderr)}"
            ) from exc
        if not payload.get("ok", True):
            err = payload.get("error") or {}
            raise RuntimeError(err.get("message") if isinstance(err, dict) else str(err))
        if proc.returncode != 0:
            raise RuntimeError(f"twitter exit {proc.returncode}: {_stderr_tail(proc.stderr)}")
        for tw in payload.get("data") or []:
            if not isinstance(tw, dict):
                continue
            tid = str(tw.get("id") or tw.get("id_str") or tw.get("tweet_id") or "")
            text = tw.get("text") or tw.get("full_text") or ""
            if not isinstance(text, str):
                text = str(text)
            user = tw.get("user") if isinstance(tw.get("user"), dict) else {}
            author = tw.get("author")
            if not isinstance(author, dict):
                author = {}
            screen = (
                author.get("screenName")
                or author.get("screen_name")
                or user.get("screen_name")
                or tw.get("screen_name")
                or ""
            )
            company = author.get("name") or tw.get("author") or screen
            if not isinstance(company, str):
                company = str(company or "")
            url = tw.get("url")
            if not isinstance(url, str) or not url.startswith("http"):
                url = f"https://x.com/{screen}/status/{tid}" if screen and tid else ""
            created = tw.get("createdAtISO") or tw.get("createdAt") or tw.get("created_at")
            out.append(
                Posting(
                    source="x",
                    ext_id=tid or hashlib.sha1(text.encode()).hexdigest()[:16],  # noqa: S324
                    url=url,
                    title=_clean(text)[:120],
                    company=company or screen,
                    text=text,
                    posted_at=_parse_x_date(created),
                )
            )
    return out


# --- Threads via threads-comment-scraper (isolated uv tool, local patch) --------
THREADS_EXE = "threads-scraper"


def _parse_threads_csv(text: str) -> list[Posting]:
    """One Posting per unique post (prefer type=post rows over comment rows)."""
    by_post: dict[str, dict] = {}
    for row in csv.DictReader(text.splitlines()):
        code = (row.get("post_code") or "").strip()
        if not code:
            continue
        prev = by_post.get(code)
        if prev is None or (row.get("type") == "post" and prev.get("type") != "post"):
            by_post[code] = row
    out: list[Posting] = []
    for code, row in by_post.items():
        body = _clean(row.get("post_text") or "")
        if len(body) < 10:
            continue
        user = (row.get("username") or "").strip()
        try:
            posted = datetime.fromtimestamp(int(row.get("timestamp") or 0), UTC)
        except (ValueError, OSError):
            posted = None
        out.append(
            Posting(
                source="threads",
                ext_id=row.get("post_id") or code,
                url=f"https://www.threads.net/@{user}/post/{code}" if user else "",
                title=body[:120],
                company=f"@{user}" if user else "",
                text=body,
                posted_at=posted,
            )
        )
    return out


def threads(queries: list[str], limit: int = 15) -> list[Posting]:
    """Shell out to `threads-scraper` (uv tool install threads-comment-scraper).

    Skips cleanly if the binary is missing. Heavy (~1 min/query, Chromium):
    keep queries few. Output stays in a temp dir (never the repo).
    """
    exe = shutil.which(THREADS_EXE)
    if not exe:
        raise RuntimeError(f"{THREADS_EXE} not installed")
    out: list[Posting] = []
    with tempfile.TemporaryDirectory(prefix="threads_") as tmp:
        for i, q in enumerate(queries):
            csv_path = str(Path(tmp) / f"out{i}.csv")
            proc = subprocess.run(  # noqa: S603 fixed argv, no shell
                [
                    exe,
                    "--keywords",
                    q,
                    "--limit",
                    str(limit),
                    "--min-length",
                    "10",
                    "--delay-min",
                    "2",
                    "--delay-max",
                    "4",
                    "--output",
                    csv_path,
                    "--no-checkpoint",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=240,
                cwd=tmp,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"threads exit {proc.returncode}: {_stderr_tail(proc.stderr)}")
            try:
                text = Path(csv_path).read_text(encoding="utf-8-sig")
            except OSError:
                continue  # no results for this query
            out.extend(_parse_threads_csv(text))
    seen: set[str] = set()
    uniq = [p for p in out if p.ext_id not in seen and not seen.add(p.ext_id)]
    return uniq


def _stderr_tail(stderr: str, limit: int = 300) -> str:
    lines = [
        ln
        for ln in (stderr or "").splitlines()
        if ln.strip() and "SyntaxWarning" not in ln and "invalid escape" not in ln
    ]
    return "\n".join(lines)[-limit:]


# --- WhatsApp chat exports ----------------------------------------------------
# Accepts both export styles:
#   iOS/old  [25/09/2026, 9:15:30 AM] Author: message
#   Android  18/08/26, 15:51 - Author: message   (24h, 2-digit year, no brackets)
WA_LINE = re.compile(
    r"^\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?)\]?"
    r"(?:\s+-\s+|\s+)(.*)$"
)
WA_URL = re.compile(r"https?://[^\s<>\"']+")
# WhatsApp system events that are not jobs (joins, subject changes, notices)
WA_SYSTEM = re.compile(
    r"joined using a group link|created group|changed the subject to"
    r"|changed this group|Messages and calls are end-to-end encrypted"
    r"|added you|removed you|pinned a message|deleted this message",
    re.I,
)


def _first_url(text: str) -> str:
    m = WA_URL.search(text)
    return m.group(0).rstrip(".,;:!?)]}") if m else ""


def whatsapp_exports(folder: Path) -> list[Posting]:
    """Parse WhatsApp exports: plain .txt files or the .zip that
    \"Chat export -> Without media\" always produces (media files are ignored).
    """
    if not folder.exists():
        return []
    out: list[Posting] = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() == ".txt":
            content = path.read_text(encoding="utf-8", errors="replace")
            out.extend(_wa_posts(path.name, path.stem, content))
        elif path.suffix.lower() == ".zip":
            out.extend(_wa_posts_zip(path))
    return out


def _wa_posts_zip(path: Path) -> list[Posting]:
    out: list[Posting] = []
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            base = Path(name).name
            if not name.lower().endswith(".txt") or name.endswith("/"):
                continue
            if base.startswith("._") or "__MACOSX" in name:  # macOS junk in zips
                continue
            content = zf.read(name).decode("utf-8", errors="replace")
            chat = Path(name).stem.replace("WhatsApp Chat with ", "").strip()
            out.extend(_wa_posts(f"{path.name}|{name}", chat, content))
    return out


def _wa_posts(origin: str, group: str, content: str) -> list[Posting]:
    posts: list[Posting] = []
    for ts, author, body in _parse_wa_file(content):
        if not author or WA_SYSTEM.search(f"{author} {body}"):  # system events, not jobs
            continue
        clean = _clean(body)
        if not clean:  # <Media omitted> / whitespace-only placeholders
            continue
        key = hashlib.sha1(f"{origin}|{ts}|{author}|{body}".encode()).hexdigest()[:20]  # noqa: S324
        posts.append(
            Posting(
                source="whatsapp",
                ext_id=key,
                url=_first_url(body),
                title=clean[:120],
                company=group.replace("WhatsApp Chat with ", "").strip(),
                text=body,
                posted_at=ts,
            )
        )
    return posts


def _parse_wa_file(content: str) -> list[tuple[datetime | None, str, str]]:
    msgs: list[tuple[datetime | None, str, str]] = []
    for line in content.splitlines():
        m = WA_LINE.match(line)
        if m:
            ts = _parse_wa_date(m.group(1), m.group(2))
            rest = m.group(3)
            # "Author: body" — system lines (no author) keep the whole text
            parts = re.split(r":\s", rest, maxsplit=1)
            author, body = (parts[0].strip(), parts[1]) if len(parts) == 2 else ("", rest)
            msgs.append((ts, author, body))
        elif msgs and line.strip():
            ts, author, body = msgs[-1]
            msgs[-1] = (ts, author, f"{body}\n{line}")
    return msgs


# --- shared helpers -----------------------------------------------------------
def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(s))).strip()


def _strip_html(s: str) -> str:
    return _clean(re.sub(r"</p>|<br\s*/?>", "\n", s))


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _parse_when(match: re.Match[str]) -> datetime | None:
    """LinkedIn card timestamp: <time datetime="..."> or "3 days ago"."""
    if "datetime" in match.re.pattern and match.lastindex:
        return _parse_iso(match.group(1))
    if match.lastindex and match.lastindex >= 2 and match.group(2):
        n, unit = int(match.group(1)), match.group(2)
        # "1 day ago" used to build timedelta(day=1) -> TypeError, killing the source
        return datetime.now(UTC) - timedelta(**{f"{unit}s": n})
    return datetime.now(UTC) if "just now" in match.group(0) else None


def _parse_x_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").astimezone(UTC)
    except ValueError:
        return _parse_iso(value)


def _parse_wa_date(day: str, clock: str) -> datetime | None:
    date = None
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            date = datetime.strptime(day, fmt)
            break
        except ValueError:
            continue
    if date is None:
        return None
    clock = clock.strip().upper()
    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M:%S %p", "%I:%M %p"):
        try:
            t = datetime.strptime(clock, fmt).time()
            return date.replace(hour=t.hour, minute=t.minute, second=t.second, tzinfo=UTC)
        except ValueError:
            continue
    return date.replace(tzinfo=UTC)
