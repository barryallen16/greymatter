"""SQLite store: dedupe by (source, ext_id), tier/score columns, retention."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .sources import Posting

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    source TEXT NOT NULL,
    ext_id TEXT NOT NULL,
    url TEXT DEFAULT '',
    title TEXT DEFAULT '',
    company TEXT DEFAULT '',
    location TEXT DEFAULT '',
    text TEXT DEFAULT '',
    posted_at TEXT,
    fetched_at TEXT NOT NULL,
    tier TEXT DEFAULT 'C',
    score INTEGER DEFAULT 0,
    in_report INTEGER DEFAULT 0,
    is_urgent INTEGER DEFAULT 0,
    is_featured INTEGER DEFAULT 0,
    PRIMARY KEY (source, ext_id)
);
"""


def connect(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    for stmt in (
        "ALTER TABLE jobs ADD COLUMN is_urgent INTEGER DEFAULT 0",
        "ALTER TABLE jobs ADD COLUMN is_featured INTEGER DEFAULT 0",
    ):
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError:
            pass  # column already exists (pre-migration DB)
    conn.commit()
    return conn


def row_to_posting(row: sqlite3.Row) -> Posting:
    """Rebuild a Posting from a stored row so classification is idempotent across runs."""
    return Posting(
        source=row["source"],
        ext_id=row["ext_id"],
        url=row["url"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        text=row["text"],
        posted_at=datetime.fromisoformat(row["posted_at"]) if row["posted_at"] else None,
        is_urgent=bool(row["is_urgent"]),
        is_featured=bool(row["is_featured"]),
    )


REFRESH = """
UPDATE jobs SET url=?, title=?, company=?, location=?, text=?, posted_at=?,
    is_urgent=?, is_featured=?
WHERE source=? AND ext_id=?
"""


def insert_new(conn: sqlite3.Connection, posts: list[Posting]) -> int:
    """Insert postings we have not seen before, then refresh the ones we have.

    Without the refresh a source that fills in a field later (LinkedIn used to
    store no description, because the search card has none) can never store it —
    the row is already there and INSERT OR IGNORE drops the update.
    Returns count of genuinely new rows.
    """
    new = 0
    for p in posts:
        cur = conn.execute(
            "INSERT OR IGNORE INTO jobs "
            "(source, ext_id, url, title, company, location, text, posted_at, fetched_at,"
            " is_urgent, is_featured) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                p.source,
                p.ext_id,
                p.url,
                p.title,
                p.company,
                p.location,
                p.text,
                p.posted_at.isoformat() if p.posted_at else None,
                p.fetched_at.isoformat(),
                int(p.is_urgent),
                int(p.is_featured),
            ),
        )
        new += cur.rowcount
    conn.executemany(
        REFRESH,
        [
            (
                p.url,
                p.title,
                p.company,
                p.location,
                p.text,
                p.posted_at.isoformat() if p.posted_at else None,
                int(p.is_urgent),
                int(p.is_featured),
                p.source,
                p.ext_id,
            )
            for p in posts
        ],
    )
    conn.commit()
    return new


def update_scores(
    conn: sqlite3.Connection, scored: dict[tuple[str, str], tuple[str, int, bool]]
) -> None:
    """Write tier/score/in_report back for rows we classified."""
    for (source, ext_id), (tier, score, in_report) in scored.items():
        conn.execute(
            "UPDATE jobs SET tier = ?, score = ?, in_report = ? WHERE source = ? AND ext_id = ?",
            (tier, score, int(in_report), source, ext_id),
        )
    conn.commit()


def reportable(conn: sqlite3.Connection, max_age_days: int = 14) -> list[sqlite3.Row]:
    """Rows fresh enough for the report, best score first."""
    cutoff = (datetime.now(UTC) - timedelta(days=max_age_days)).isoformat()
    return conn.execute(
        "SELECT * FROM jobs WHERE (posted_at IS NULL OR posted_at >= ?) "
        "ORDER BY tier ASC, score DESC, posted_at DESC",
        (cutoff,),
    ).fetchall()


def prune(conn: sqlite3.Connection, keep_days: int = 90) -> int:
    cutoff = (datetime.now(UTC) - timedelta(days=keep_days)).isoformat()
    cur = conn.execute("DELETE FROM jobs WHERE fetched_at < ?", (cutoff,))
    conn.commit()
    return cur.rowcount


def counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT source, COUNT(*) AS n FROM jobs GROUP BY source ORDER BY n DESC"
    ).fetchall()
    return {r["source"]: r["n"] for r in rows}
