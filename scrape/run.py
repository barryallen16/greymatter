"""Daily entrypoint: fetch each source independently, store, classify, write report.

Usage: uv run run.py [--sources ...] [--limit 20] [--open]
Failures are logged to run.log and do not stop other sources (Q8).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import traceback
from datetime import UTC, datetime
from pathlib import Path

from jobpipe import match, page, report, store
from jobpipe.sources import (
    careervalore,
    freehire,
    fresherflow,
    fresheroffcampus,
    jobfound,
    jobportal,
    jobsalertx,
    linkedin_guest,
    threads,
    whatsapp_exports,
    x_twitter,
)

ROOT = Path(__file__).parent
DB = ROOT / "data" / "jobs.db"
REPORT = ROOT / "report.md"
HTML = ROOT / "report.html"
LOG = ROOT / "run.log"
EXPORTS = ROOT / "data" / "whatsapp_exports"
PROFILE = ROOT / "profile.json"

FREEHIRE_QUERIES = ["fresher python", "fresher genai", "junior backend developer"]
LINKEDIN_QUERIES = [
    ("fresher python", "Chennai, Tamil Nadu, India"),
    ("fresher machine learning", "Chennai, Tamil Nadu, India"),
    ("fresher python", "Remote, India"),
]
X_QUERIES = ["hiring fresher python", "hiring junior ML engineer", "fresher hiring Chennai"]
THREADS_QUERIES = ["chennai jobs", "remote hiring"]


def log(msg: str) -> None:
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def fetch(name: str) -> list:
    if name == "freehire":
        return freehire(FREEHIRE_QUERIES)
    if name == "linkedin":
        return linkedin_guest(LINKEDIN_QUERIES)
    if name == "x":
        return x_twitter(X_QUERIES)
    if name == "threads":
        return threads(THREADS_QUERIES)
    if name == "whatsapp":
        return whatsapp_exports(EXPORTS)
    if name == "jobportal":
        return jobportal()
    if name == "careervalore":
        return careervalore()
    if name == "jobsalertx":
        return jobsalertx()
    if name == "fresherflow":
        return fresherflow()
    if name == "fresheroffcampus":
        return fresheroffcampus()
    if name == "jobfound":
        return jobfound()
    raise ValueError(f"unknown source: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sources",
        default="freehire,linkedin,x,whatsapp,jobportal,fresherflow,careervalore,jobsalertx,fresheroffcampus,jobfound",
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--open", action="store_true", help="open report.html when done")
    args = parser.parse_args(argv)

    DB.parent.mkdir(exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    conn = store.connect(DB)
    keywords = match.load_keywords(PROFILE)
    log(f"start sources={args.sources} keywords={len(keywords)}")

    sources_list = [s.strip() for s in args.sources.split(",") if s.strip()]
    fetched_data: dict[str, list] = {}

    max_workers = min(len(sources_list), 6) if sources_list else 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_src = {executor.submit(fetch, name): name for name in sources_list}
        for future in concurrent.futures.as_completed(future_to_src):
            name = future_to_src[future]
            try:
                got = future.result()
                fetched_data[name] = got
            except Exception as exc:  # noqa: BLE001 — one source must not kill the run
                log(f"{name}: FAILED — {exc}\n{traceback.format_exc()}")

    for name in sources_list:
        if name in fetched_data:
            got = fetched_data[name]
            new = store.insert_new(conn, got)
            log(f"{name}: fetched={len(got)} new={new}")

    scored: dict[tuple[str, str], tuple[str, int, bool]] = {}
    for r in conn.execute("SELECT * FROM jobs").fetchall():
        post = store.row_to_posting(r)
        tier, score, include, _reason = match.classify(post, keywords)
        scored[(post.source, post.ext_id)] = (tier, score, include)
    store.update_scores(conn, scored)

    shown = report.write_report(conn, DB, REPORT, limit=args.limit, keywords=keywords)
    rows = page.write_html(conn, HTML, keywords)
    pruned = store.prune(conn)
    log(f"done shown={shown} html={rows} pruned={pruned} report={REPORT.name}")
    if args.open:
        os.startfile(HTML)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
