import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from jobpipe import match, sources, store
from jobpipe.report import write_report
from jobpipe.sources import Posting, _parse_wa_file, jobportal

PROFILE = Path(__file__).parent.parent / "profile.json"


def test_profile_keywords_load():
    words = match.load_keywords(PROFILE)
    assert "python" in words
    assert "rust" in words
    assert "tokenizer" in words
    assert "llm" in words
    assert "lora" in words
    assert "hugging" in words
    assert "rayon" in words  # project tech is harvested too
    assert not any("english" in w for w in words)
    # junk fragments / generic words must not become keywords
    for junk in ("engineer", "plus", "yt", "dlp", "face", "native", "github"):
        assert junk not in words


def test_fresher_include():
    assert match.is_fresher("Looking for fresher python developers, batch 2026")
    assert match.is_fresher("0-2 years experience, fresh graduates welcome")
    assert match.is_fresher("Hiring interns for summer 2026")
    assert match.is_fresher("Entry level ML engineer")
    assert match.is_fresher("1-2 years of experience")
    assert match.is_fresher("2+ years experience")
    assert match.is_fresher("Trainee engineer wanted")
    assert match.is_fresher("Walk-in drive this Saturday")
    assert match.is_fresher("Apprentices welcome, class of 2026")
    assert not match.is_fresher("0-3 years experience")  # range ending >= 3
    assert not match.is_fresher("Hiring Python developers, apply now")


def test_fresher_exclude():
    assert not match.is_fresher("Senior python developer, 5+ years experience")
    assert not match.is_fresher("Staff engineer, 3 years experience required")
    assert not match.is_fresher("Principal engineer, experienced only")
    assert not match.is_fresher("We need 4 to 6 years of experience")
    assert not match.is_fresher("Solutions architect, fresher friendly")


def test_fresher_post_reads_body_only_for_the_years_bar():
    """Body prose about senior colleagues must not disqualify a fresher role."""
    kws = match.load_keywords(PROFILE)
    fresher = Posting(
        source="freehire",
        ext_id="1",
        url="http://x",
        title="Junior Network Engineer",
        location="Chennai",
        text="Work with senior engineers. 0-2 years experience, freshers welcome.",
        posted_at=datetime.now(UTC) - timedelta(days=1),
    )
    assert match.is_fresher_post(fresher)
    assert match.classify(fresher, kws)[3] != "not-fresher"

    # the years bar still applies inside the body
    assert not match.is_fresher_post(
        Posting(**{**fresher.__dict__, "text": "5+ years of experience needed."})
    )
    # seniority in the head still disqualifies
    assert not match.is_fresher_post(  # noqa: F601
        Posting(**{**fresher.__dict__, "title": "Senior Network Engineer"})
    )
    # "Principal Duties" is a heading, not a seniority signal
    assert match.is_fresher_post(
        Posting(**{**fresher.__dict__, "text": "*Principal Duties* Resolve escalations."})
    )


def test_location_gate():
    assert match.in_location("Chennai, Tamil Nadu")
    assert match.in_location("Remote, India")
    assert match.in_location("")
    assert not match.in_location("Jaipur, Rajasthan")
    assert not match.in_location("Mumbai, India")
    assert not match.in_location("IN - Bengaluru")
    assert not match.in_location("Remote Sensing, India")  # not remote work


def test_tiers_and_score():
    assert match.tier_of("GenAI engineer building LLM evals") == "A"
    assert match.tier_of("Python backend developer FastAPI") == "B"
    assert match.tier_of("Marketing coordinator") == "C"
    assert match.tier_of("LoRA fine-tuning for tokenizers") == "A"
    assert match.tier_of("Rust backend with Docker on AWS") == "B"
    assert match.tier_of("REST APIs developer") == "B"
    assert match.tier_of("Rapid growth marketer") == "C"  # rapid != APIs
    kw = ["python", "llm", "fastapi"]
    assert match.score_of(kw, "Python + FastAPI for LLM apps") == 3
    # word-prefix matching: rusty counts, trust does not
    assert match.score_of(["rust"], "Rust systems developer") == 1
    assert match.score_of(["rust"], "trust and safety team") == 0
    assert match.score_of(["sql"], "PostgreSQL and MySQL") == 0  # compounds need own keyword
    assert match.score_of(["sql", "postgresql"], "PostgreSQL admin") == 1  # subsumed
    assert match.score_of(["sql", "sqlite"], "SQLite database") == 1  # subsumed
    assert match.score_of(["eval"], "model evaluation harness") == 1
    assert match.score_of(["eval"], "retrieval pipeline") == 0


def test_classify_decisions():
    kws = match.load_keywords(PROFILE)
    good = Posting(
        source="freehire",
        ext_id="1",
        url="http://x",
        title="Junior Python Developer",
        location="Chennai",
        text="0-2 years, freshers, python fastapi docker",
        posted_at=datetime.now(UTC) - timedelta(days=2),
    )
    tier, score, include, _ = match.classify(good, kws)
    assert include and tier in {"A", "B"} and score >= 3

    old = Posting(**{**good.__dict__, "posted_at": datetime.now(UTC) - timedelta(days=30)})
    *_, reason = match.classify(old, kws)
    assert reason == "stale"

    jaipur = Posting(**{**good.__dict__, "location": "Jaipur, Rajasthan"})
    *_, reason = match.classify(jaipur, kws)
    assert reason == "location"

    senior = Posting(**{**good.__dict__, "text": "senior developer 5+ years"})
    *_, reason = match.classify(senior, kws)
    assert reason == "not-fresher"

    sales = Posting(
        **{
            **good.__dict__,
            "title": "Sales executive",
            "location": "Chennai",
            "text": "fresher 0-1 years sales",
        }
    )
    *_, reason = match.classify(sales, kws)
    assert reason == "unrelated-domain"

    thin = Posting(
        **{
            **good.__dict__,
            "title": "Junior Coordinator",
            "location": "Chennai",
            "text": "fresher 0-1 years coordination",
        }
    )
    *_, reason = match.classify(thin, kws)
    assert reason == "tier-c"


def test_report_picks_top20_and_skips_stale(tmp_path):
    conn = store.connect(tmp_path / "jobs.db")
    now = datetime.now(UTC)
    posts = [
        Posting(
            source="freehire",
            ext_id=str(i),
            url=f"http://j/{i}",
            title=f"Python dev {i}",
            company="Acme",
            location="Chennai",
            text="fresher 0-2 years python fastapi llm",
            posted_at=now - timedelta(days=1) if i != 9 else now - timedelta(days=40),
        )
        for i in range(30)
    ]
    store.insert_new(conn, posts)
    kws = match.load_keywords(PROFILE)
    for p in posts:
        tier, score, include, _ = match.classify(p, kws)
        store.update_scores(conn, {(p.source, p.ext_id): (tier, score, include)})
    out = tmp_path / "report.md"
    shown = write_report(conn, tmp_path / "j.db", out, limit=20)
    assert shown == 20
    assert "Python dev 9" not in out.read_text(encoding="utf-8")

    assert store.prune(conn) == 0
    assert store.counts(conn)["freehire"] == 30
    assert "Python dev 0" in out.read_text(encoding="utf-8")

    # a Tier C post stays DB-only even with a high score
    store.update_scores(conn, {("freehire", "0"): ("C", 9, False)})
    shown_c = write_report(conn, tmp_path / "j.db", out, limit=20)
    assert shown_c == 20
    assert "Python dev 0" not in out.read_text(encoding="utf-8")


def test_linkedin_description_and_when_parsing(monkeypatch):
    detail = (
        '<div class="description__text">Fresher role: 0-2 years Python &amp; FastAPI. '
        "<p>Apply now.</p></div>"
    )
    monkeypatch.setattr(sources, "_get", lambda url, timeout=25: detail)
    got = sources._linkedin_description("123")
    assert "Fresher role" in got and "0-2 years" in got
    assert "&amp;" not in got  # html entities decoded
    assert "Apply now." in got

    def boom(url, timeout=25):
        raise OSError("404")

    monkeypatch.setattr(sources, "_get", boom)
    assert sources._linkedin_description("123") == ""  # dead page must not sink the run

    # "1 day ago" used to build timedelta(day=1) -> TypeError
    when = re.search(r"(\d+)\s+(minute|hour|day|week)s?\s+ago", "posted 1 day ago")
    parsed = sources._parse_when(when)
    assert parsed is not None
    assert abs((datetime.now(UTC) - parsed).days) == 1


def test_dedupe_by_source_and_id(tmp_path):
    conn = store.connect(tmp_path / "jobs.db")
    p = Posting(source="x", ext_id="abc", url="", title="hiring")
    assert store.insert_new(conn, [p]) == 1
    assert store.insert_new(conn, [p]) == 0


def test_refetch_fills_in_a_field_the_first_fetch_could_not(tmp_path):
    """LinkedIn stored no description until the detail fetch existed; the row was
    already present, so the text has to be refreshed, not ignored."""
    conn = store.connect(tmp_path / "jobs.db")
    bare = Posting(source="linkedin", ext_id="1", url="", title="AI Engineer")
    assert store.insert_new(conn, [bare]) == 1
    filled = Posting(**{**bare.__dict__, "text": "Fresher role, 0-2 years python fastapi"})
    assert store.insert_new(conn, [filled]) == 0
    row = conn.execute("SELECT text, fetched_at FROM jobs").fetchone()
    assert row["text"] == "Fresher role, 0-2 years python fastapi"


def test_html_ui_embeds_all_jobs(tmp_path):
    from jobpipe import page

    conn = store.connect(tmp_path / "jobs.db")
    posts = [
        Posting(
            source="freehire",
            ext_id="1",
            url="https://example.com/job",
            title="Python Dev <fresher>",
            company="Acme",
            location="Chennai",
            text="0-2 years python",
            posted_at=datetime.now(UTC) - timedelta(days=1),
        ),
        Posting(source="whatsapp", ext_id="2", url="", title="Referral drive"),
    ]
    store.insert_new(conn, posts)
    store.update_scores(conn, {("freehire", "1"): ("A", 5, True)})
    out = tmp_path / "report.html"
    assert page.write_html(conn, out, ["python"]) == 2
    html = out.read_text(encoding="utf-8")
    assert "__DATA__" not in html and "__KEYWORDS__" not in html
    assert "__STARTUPS__" not in html and "__FAVICON__" not in html
    assert "__FONTFACE__" not in html and "__ICO_SEARCH__" not in html
    assert "Geist Pixel" in html and "pixelarticons" in html
    assert "font-family:'Geist Pixel'" in html
    assert "font-family:'Instrument Serif'" in html
    assert "Python Dev" in html and "Referral drive" in html
    assert '"in_report": true' in html
    assert '"python"' in html
    assert '"fetched":' in html
    assert "Today's matches" in html and "Browse all" in html
    assert "IITM Startups" in html and 'id="slist"' in html
    assert "Fresher tech roles" in html
    assert 'rel="icon"' in html  # sibling iitm-startups favicon embedded
    assert "</script>" not in html.split("const DATA =")[1].split(";")[0]


def test_whatsapp_parse():
    sample = (
        "[25/09/2026, 9:15:30 AM] Admin: Hiring batch 2026 passouts\n"
        "python backend role chennai\n"
        "[25/09/2026, 10:00:01 AM] Ravi: https://example.com/job\n"
    )
    msgs = _parse_wa_file(sample)
    assert len(msgs) == 2
    assert msgs[0][1] == "Admin"
    assert "python backend" in msgs[0][2]
    assert msgs[0][0].year == 2026


def test_whatsapp_android_format():
    sample = (
        "18/08/26, 15:51 - Messages and calls are end-to-end encrypted.\n"
        "25/09/26, 9:15 - Admin: Hiring batch 2026 passouts\n"
        "python backend role chennai\n"
        "25/09/26, 16:04 - +91 95006 17780 joined using a group link.\n"
    )
    msgs = _parse_wa_file(sample)
    assert len(msgs) == 3
    assert msgs[0][1] == "" and "encrypted" in msgs[0][2]
    assert msgs[1][1] == "Admin"
    assert "chennai" in msgs[1][2]
    assert msgs[1][0] is not None and msgs[1][0].hour == 9
    assert msgs[2][1] == ""


def test_whatsapp_zip_export(tmp_path):
    import zipfile

    from jobpipe.sources import whatsapp_exports

    sample = (
        "[25/09/2026, 9:15:30 AM] Admin: Hiring batch 2026 passouts\n"
        "python backend role chennai\n"
        "[25/09/2026, 10:00:01 AM] Ravi: fresher genai role remote india\n"
        "Apply Now: https://jobs.example.com/post/123?src=wa.\n"
        "25/09/26, 11:00 - +91 94251 89854 joined using a group link.\n"
        "25/09/26, 11:05 - Admin changed the subject to: Job Alerts\n"
    )
    folder = tmp_path / "exports"
    folder.mkdir()
    zpath = folder / "WhatsApp Chat with Job Alerts.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.writestr("WhatsApp Chat with Job Alerts/WhatsApp Chat with Job Alerts.txt", sample)
        zf.writestr("WhatsApp Chat with Job Alerts/img-20260925-wa0001.jpg", b"\xff\xd8fake")
        zf.writestr("WhatsApp Chat with Job Alerts/audio.mp3", b"ID3fake")

    got = whatsapp_exports(folder)
    assert len(got) == 2
    assert got[0].company == "Job Alerts"
    assert "chennai" in got[0].text
    assert got[0].posted_at is not None
    assert got[1].url == "https://jobs.example.com/post/123?src=wa"
    assert got[0].url == ""

    # media ignored, keys stable across re-reads
    again = whatsapp_exports(folder)
    assert {p.ext_id for p in got} == {p.ext_id for p in again}


def test_jobportal_parses_list(monkeypatch):
    payload = {
        "success": True,
        "data": [
            {
                "id": 120,
                "title": "AI Data Specialist - Telugu",
                "slug": "ai-data-specialist-telugu-at-rws-in-remote",
                "employmentType": "Contract",
                "experienceLevel": "Fresher",
                "workMode": "Remote",
                "city": "Remote",
                "state": "Remote",
                "country": "IN",
                "sector": "IT",
                "requiredSkills": "machine learning",
                "publishedAt": "2026-09-19T16:09:02.838Z",
                "isUrgent": True,
                "isFeatured": False,
                "company": {"name": "RWS"},
                "category": {"name": "TrainAI"},
            }
        ],
        "pagination": {"total": 1, "page": 1, "limit": 100, "totalPages": 1},
    }
    monkeypatch.setattr(sources, "_get", lambda url, timeout=25: json.dumps(payload))
    got = jobportal()
    assert len(got) == 1
    post = got[0]
    assert post.source == "jobportal"
    assert post.ext_id == "jp-120"
    assert post.url.endswith("/jobs/detail/ai-data-specialist-telugu-at-rws-in-remote")
    assert post.company == "RWS"
    assert post.location == "Remote, IN"
    assert "machine learning" in post.text
    assert post.posted_at is not None and post.posted_at.year == 2026
    assert post.is_urgent is True
    assert post.is_featured is False


def test_fresherflow_parses_feed_and_skips_expired(monkeypatch):
    payload = {
        "jobs": [
            {
                "id": "job_1",
                "title": "Application Engineering Intern",
                "company": "Google",
                "type": "INTERNSHIP",
                "status": "PUBLISHED",
                "locations": ["Bengaluru"],
                "workMode": "REMOTE",
                "applyLink": "https://example.com/apply/1",
                "addedAt": "2026-09-09T00:01:00.000Z",
                "tags": ["FAANG"],
                "notesHighlights": "Summer 2027 internship.",
            },
            {
                "id": "job_2",
                "title": "Old Role",
                "company": "Acme",
                "status": "EXPIRED",
                "locations": ["Mumbai"],
                "applyLink": "https://example.com/apply/2",
            },
        ]
    }
    monkeypatch.setattr(sources, "_get", lambda url, timeout=25: json.dumps(payload))
    got = sources.fresherflow()
    assert len(got) == 1
    post = got[0]
    assert post.source == "fresherflow"
    assert post.ext_id == "job_1"
    assert post.url == "https://example.com/apply/1"
    assert post.location == "Bengaluru, Remote"
    assert "internship" in post.text.lower()
    assert post.posted_at is not None and post.posted_at.year == 2026


def test_threads_csv_prefers_post_rows_and_dedupes():
    sample = (
        "post_code,post_id,post_text,comment_id,comment_text,username,"
        "like_count,reply_count,timestamp,keyword,type\n"
        'AAA,111,"Remote python fresher developer hiring",,,"boss1",5,0,1789516800,q,post\n'
        'BBB,222,"Chennai walk-in drive",c1,"interested",user2,1,3,1789516900,q,comment\n'
        'BBB,222,"Chennai walk-in drive",c2,"where",user3,0,0,1789517000,q,comment\n'
        'CCC,333,"hi",,,,0,0,,q,comment\n'
    )
    got = sources._parse_threads_csv(sample)
    assert {p.ext_id for p in got} == {"111", "222"}
    by_id = {p.ext_id: p for p in got}
    assert by_id["111"].source == "threads"
    assert by_id["111"].url == "https://www.threads.net/@boss1/post/AAA"
    assert by_id["111"].company == "@boss1"
    assert by_id["111"].posted_at is not None and by_id["111"].posted_at.year == 2026
    assert by_id["222"].title.startswith("Chennai walk-in")


def test_careervalore_parses_wp_posts(monkeypatch):
    payload = [
        {
            "id": 99,
            "slug": "x",
            "date": "2026-09-24T10:00:00",
            "link": "https://careervalore.com/vacancy-x/",
            "title": {"rendered": "Princeton IT Services – Hiring for Sales Support @ Gudivada"},
            "content": {"rendered": "<p>Fresher python role in office.</p>"},
        }
    ]
    monkeypatch.setattr(sources, "_get", lambda url, timeout=25: json.dumps(payload))
    got = sources.careervalore(pages=1)
    assert len(got) == 1
    post = got[0]
    assert post.source == "careervalore"
    assert post.ext_id == "99"
    assert post.company == "Princeton IT Services"
    assert post.location == "Gudivada"
    assert "Fresher python" in post.text
    assert post.posted_at is not None


def test_jobsalertx_parses_feed(monkeypatch):
    # no cached anon key from a live call earlier in the suite, else it hits PostgREST
    monkeypatch.setattr(sources, "_jobsalertx_key", lambda: "")
    feed = (
        '<?xml version="1.0"?><rss><channel>'
        "<item><title>Backend Engineer at Acme</title>"
        "<link>https://jobsalertx.vercel.app/jobs/abc-123</link>"
        "<description>Chennai, Tamil Nadu, India | FULL-TIME | Fresher python role.</description>"
        "<pubDate>Fri, 25 Sep 2026 03:04:15 GMT</pubDate></item>"
        "<item><title>Placement guide</title>"
        "<link>https://jobsalertx.vercel.app/blog/guide</link>"
        "<description>How to write resumes.</description>"
        "<pubDate>Mon, 02 Mar 2026 00:00:00 GMT</pubDate></item>"
        "<item><title>Backend Engineer — Intern at ethereal labs</title>"
        "<link>https://jobsalertx.vercel.app/jobs/def-456</link>"
        "<description>Backend Engineer — Intern at ethereal labs — "
        "Bengaluru, Karnataka, India | INTERNSHIP | 0-1 yr exp.</description>"
        "<pubDate>Fri, 25 Sep 2026 03:04:15 GMT</pubDate></item>"
        "</channel></rss>"
    )
    monkeypatch.setattr(sources, "_get", lambda url, timeout=25: feed)
    got = sources.jobsalertx()
    assert len(got) == 2  # blog guide skipped
    post = got[0]
    assert post.source == "jobsalertx"
    assert post.ext_id == "abc-123"
    assert post.title == "Backend Engineer"
    assert post.company == "Acme"
    assert post.location == "Chennai, Tamil Nadu, India"
    assert post.posted_at is not None and post.posted_at.year == 2026
    assert got[1].location == "Bengaluru, Karnataka, India"


def test_fresheroffcampus_parses_latest_posts(monkeypatch):
    payload = [
        {
            "id": 7,
            "slug": "virtusa-x",
            "date": "2026-10-12T10:00:00",
            "link": "https://www.fresheroffcampus.com/virtusa-x/",
            "title": {
                "rendered": "Virtusa Off Campus 2026 Hiring Fresher For Software Tester | Hyderabad"
            },
            "content": {"rendered": "<p>Fresher python role in office.</p>"},
        },
        {
            "id": 8,
            "slug": "guide",
            "date": "2026-10-11T10:00:00",
            "link": "https://www.fresheroffcampus.com/guide/",
            "title": {"rendered": "How to crack your first interview"},
            "content": {"rendered": "<p>Tips.</p>"},
        },
    ]
    monkeypatch.setattr(sources, "_get", lambda url, timeout=25: json.dumps(payload))
    got = sources.fresheroffcampus(pages=1)
    assert len(got) == 1  # guide skipped
    post = got[0]
    assert post.source == "fresheroffcampus"
    assert post.ext_id == "7"
    assert post.company == "Virtusa"
    assert post.title == "Software Tester"
    assert post.location == "Hyderabad"
    assert "Fresher python" in post.text
    assert post.posted_at is not None


def test_jobfound_parses_jsonld(monkeypatch):
    page = (
        '<html><script id="job-list-structured-data" type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"ItemList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Junior Software Engineer at GoAudits",'
        '"url":"https://jobfound.org/job/goaudits-is-hiring-for-junior-software-engineer-remote-india-12-october-2026"}'
        "]}</script></html>"
    )
    monkeypatch.setattr(sources, "_get", lambda url, timeout=25: page)
    got = sources.jobfound()
    assert len(got) == 1
    post = got[0]
    assert post.source == "jobfound"
    assert post.title == "Junior Software Engineer"
    assert post.company == "GoAudits"
    assert "Remote" in post.location and "India" in post.location
    assert post.posted_at is not None
    assert (post.posted_at.day, post.posted_at.month, post.posted_at.year) == (12, 10, 2026)


def test_jobsalertx_autoretrieves_key_from_site_js(monkeypatch):
    monkeypatch.delenv("JOBSALERTX_ANON_KEY", raising=False)
    monkeypatch.setattr(sources, "_JAX_KEY", None)
    fake_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ4In0.c2ln"

    def fake_get(url, timeout=25):
        if url.endswith(".js"):
            return f'var k="{fake_key}";'
        return '<html><script src="/_next/static/chunks/abc.js"></script></html>'

    monkeypatch.setattr(sources, "_get", fake_get)
    assert sources._jobsalertx_key() == fake_key
    monkeypatch.setattr(sources, "_JAX_KEY", None)


def test_llm_word_boundary_avoids_enrollment():
    # 'enrollment', 'fallback', 'skill matrix' must not trigger Tier A
    assert match.tier_of("Troubleshoot device enrollment and synchronization") == "C"
    assert match.tier_of("Skill matrix fallback plan") == "C"
    # Genuine LLM matches must trigger Tier A
    assert match.tier_of("Experience with LLMs and RAG pipelines") == "A"
    assert match.tier_of("Fine-tuning language models using LoRA") == "A"


def test_domain_exclusions():
    mech = Posting(
        source="careervalore",
        ext_id="1",
        url="http://x",
        title="micro1 – Hiring for Mechanical Engineering @ Remote",
        location="Remote",
        text="Audit AI Engineering Output: Evaluate prompt responses.",
        posted_at=datetime.now(UTC),
    )
    kws = match.load_keywords(PROFILE)
    *_, reason = match.classify(mech, kws)
    assert reason == "unrelated-domain"

    med = Posting(
        source="linkedin",
        ext_id="2",
        url="http://x",
        title="Medical Coding Jobs for Bioinfomatics Graduates",
        location="Chennai",
        text="Genome annotation, sequence analysis. Freshers welcome.",
        posted_at=datetime.now(UTC),
    )
    *_, reason = match.classify(med, kws)
    assert reason == "unrelated-domain"

    # Override: biotech software engineer should pass domain check
    biotech_sw = Posting(
        source="linkedin",
        ext_id="3",
        url="http://x",
        title="Biotechnology Software Engineer",
        location="Chennai",
        text="Python backend developer for sequencing data. 0-2 years.",
        posted_at=datetime.now(UTC),
    )
    *_, reason = match.classify(biotech_sw, kws)
    assert reason != "unrelated-domain"


def test_spam_roundup_exclusion():
    tweet = Posting(
        source="x",
        ext_id="101",
        url="http://x",
        title=(
            "🔄 8 fresh Web3 internships & junior roles found today (September 25, 2026):"
            " 💻 Remote Technical Intern"
        ),
        text="1. Remote Technical Intern 2. AI Researcher 3. Python dev",
        posted_at=datetime.now(UTC),
    )
    kws = match.load_keywords(PROFILE)
    *_, reason = match.classify(tweet, kws)
    assert reason == "spam-roundup"


def test_remote_text_location_guard():
    # Technical remote mentions without remote work mode must not pass
    assert not match.in_location("", "Troubleshoot remote desktop and configure remote servers.")
    assert not match.in_location("", "Experience in remote sensing applications.")
    # Genuine remote work statements in text must pass
    assert match.in_location("", "This is a 100% remote developer role across India.")
    assert match.in_location("", "Location: Remote. Python fresher required.")


def test_requisition_deduplication():
    # Twin postings from the same company with same normalized title should dedupe
    rows = [
        {
            "company": "Accenture in India",
            "title": "Custom Software Engineer",
            "tier": "A",
            "score": 2,
            "weighted_score": 2,
        },
        {
            "company": "Accenture in India",
            "title": "Custom Software Engineer",
            "tier": "A",
            "score": 2,
            "weighted_score": 2,
        },
        {
            "company": "Hitachi Energy",
            "title": "AI/ML Engineer",
            "tier": "A",
            "score": 2,
            "weighted_score": 3,
        },
    ]
    chosen = match.select_report_rows(rows, limit=20)
    assert len(chosen) == 2
    assert [r["company"] for r in chosen] == ["Hitachi Energy", "Accenture in India"]
