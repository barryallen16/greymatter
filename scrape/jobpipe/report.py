"""Write report.md: Tier A first, then Tier B (score >= 3), top 20, fresh only."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .match import MIN_TIER_B_SCORE, matched, select_report_rows, weighted_score_of
from .store import counts, reportable


def write_report(conn, db_path: Path, report_path: Path, limit: int = 20, keywords=()) -> int:
    rows = [
        r
        for r in (dict(x) for x in reportable(conn))
        if r["tier"] == "A" or (r["tier"] == "B" and r["score"] >= MIN_TIER_B_SCORE)
    ]
    for r in rows:
        blob = f"{r['title']} {r['location']} {r['company']} {r['text']}"
        r["weighted_score"] = weighted_score_of(keywords, blob)
    chosen = select_report_rows(rows, limit=limit)

    lines: list[str] = []
    lines.append(f"# Job report — {datetime.now(UTC).strftime('%Y-%m-%d')}")
    lines.append("")
    total = counts(conn)
    lines.append(
        "DB: "
        + (", ".join(f"{src} {n}" for src, n in total.items()) or "empty")
        + f" | shown: {len(chosen)} (Tier A → Tier B, ≥3 profile keywords, ≤14 days)"
    )
    lines.append("")

    for tier, label in (
        ("A", "Tier A — GenAI / ML / NLP / data"),
        ("B", "Tier B — Python / backend / TS"),
    ):
        section = [r for r in chosen if r["tier"] == tier]
        if not section:
            continue
        lines.append(f"## {label}")
        lines.append("")
        for r in section:
            title = r["title"] or "(untitled)"
            link = f" — [apply]({r['url']})" if r["url"] else ""
            posted = (r["posted_at"] or "")[:10] or "unknown"
            blob = f"{r['title']} {r['location']} {r['company']} {r['text']}"
            skills = ", ".join(matched(keywords, blob)[:6])
            extra = f" · skills: {skills}" if skills else ""
            lines.append(
                f"- **{title}**{link}  \n  {r['company']} · {r['location']} · "
                f"posted {posted} · score {r['score']}{extra} · {r['source']}"
            )
        lines.append("")

    if not chosen:
        lines.append("_No matching posts today. Check run.log._")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    conn.execute("UPDATE jobs SET in_report = 0")
    for r in chosen:
        conn.execute(
            "UPDATE jobs SET in_report = 1 WHERE source = ? AND ext_id = ?",
            (r["source"], r["ext_id"]),
        )
    conn.commit()
    return len(chosen)
