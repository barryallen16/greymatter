"""Publish this pipeline's top fresher matches into the Grey Matter hub.

One write over the hub's stdlib KV API (`api/main.py`), no new deps:

  jobscrape-jobs-v1   today's Tier A/B matches — greymatter.isroot.in/jobs/ renders
                      them next to job-filter's list (that one keeps its own key,
                      jobfilter-jobs-v1, so a re-run there cannot wipe these rows).

Selection is report.md's locked Q9 rule: Tier A always, Tier B needs >= 3 profile
keywords, > 14 days is stale, top 20 after dedupe by (company, title).

Usage:
    uv run python publish.py                                    # local API
    uv run python publish.py --url https://greymatter.isroot.in  # VPS (what daily.bat does)
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jobpipe import match, store  # noqa: E402

KEY = "jobscrape-jobs-v1"
DB = ROOT / "data" / "jobs.db"
PROFILE = ROOT / "profile.json"
DESC_CHARS = 1500  # the page shows a preview; the full JD belongs on the tracker row
INTERN = re.compile(r"\bintern(?:ship)?s?\b", re.I)


def kv_put(base: str, key: str, value) -> bool:
    req = urllib.request.Request(
        f"{base}/api/store/{key}",
        data=json.dumps(value).encode("utf-8"),
        method="PUT",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (user-supplied hub URL)
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        sys.exit(f"PUT {key} failed: HTTP {exc.code}")
    except urllib.error.URLError as exc:
        sys.exit(
            f"Cannot reach Grey Matter at {base} ({exc.reason}).\n"
            "Local: cd job-search && PORT=8080 uv run python api/main.py\n"
            "VPS:   uv run python publish.py --url https://greymatter.isroot.in"
        )


def blob_of(row: dict) -> str:
    return f"{row['title']} {row['location']} {row['company']} {row['text']}"


def to_row(row: dict, keywords: list[str]) -> dict:
    """Hub row for the jobs page (same fields job-filter publishes)."""
    return {
        # unique per source; the jobs page prefixes tracker rows with js-
        "id": f"{row['source']}:{row['ext_id']}",
        "title": row["title"],
        "company": row["company"],
        "location": row["location"],
        "job_url": row["url"],
        "site": row["source"],
        "source_type": "scrape",
        "job_type": "intern" if INTERN.search(row["title"]) else "fulltime",
        "tier": row["tier"],
        "score": row["weighted_score"],
        "match_reasons": match.matched(keywords, blob_of(row))[:6],
        "min_exp_years": None,  # the fresher gate already cleared the posting
        "max_exp_years": None,
        "date_posted": row["posted_at"] or "",
        "discovered_at": row["fetched_at"],
        "description": (row["text"] or "")[:DESC_CHARS],
    }


def select(conn, keywords: list[str], limit: int) -> list[dict]:
    """report.md's rule, as rows the page can render: A first, best score within tier."""
    rows = [dict(r) for r in store.reportable(conn)]
    rows = [
        r
        for r in rows
        if r["tier"] == "A" or (r["tier"] == "B" and r["score"] >= match.MIN_TIER_B_SCORE)
    ]
    for r in rows:
        r["weighted_score"] = match.weighted_score_of(keywords, blob_of(r))
    return match.select_report_rows(rows, limit=limit)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--url",
        default=os.environ.get("GREYMATTER_URL", "http://127.0.0.1:8080"),
        help="Grey Matter base URL (default: $GREYMATTER_URL or http://127.0.0.1:8080)",
    )
    ap.add_argument("--limit", type=int, default=20, help="Cap how many matches go to the page")
    args = ap.parse_args()

    if not DB.exists():
        sys.exit(f"No database at {DB} — run `uv run run.py` first.")
    conn = store.connect(DB)
    keywords = match.load_keywords(PROFILE)
    chosen = select(conn, keywords, args.limit)
    conn.close()

    payload = [to_row(r, keywords) for r in chosen]
    print(f"Publishing {len(payload)} matches to {args.url}")
    kv_put(args.url, KEY, payload)
    print(f"  {KEY}: {len(payload)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
