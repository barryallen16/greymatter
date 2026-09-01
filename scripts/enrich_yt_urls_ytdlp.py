#!/usr/bin/env python3
"""
Enrich youtube_video entries in results.jsonl via yt-dlp ytsearch1
- Reads results.jsonl
- For each category==youtube_video where extracted_data.url is null and title exists,
  runs: yt-dlp --skip-download --no-playlist --print-json "ytsearch1:QUERY"
- Writes results.enriched.jsonl (never overwrites input)
- Adds result.enrichment audit dict
- Resume cache: scripts/.enrich_cache.json
- Windows-safe, utf-8, atomic write

Usage:
  python scripts/enrich_yt_urls_ytdlp.py
  python scripts/enrich_yt_urls_ytdlp.py --limit 5 --dry-run
  python scripts/enrich_yt_urls_ytdlp.py --input results.jsonl --output results.enriched.jsonl
"""
import argparse
import json
import pathlib
import subprocess
import sys
import time
import re
import os
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent  # job-search
DEFAULT_INPUT = ROOT / "results.jsonl"
DEFAULT_OUTPUT = ROOT / "results.enriched.jsonl"
CACHE_PATH = pathlib.Path(__file__).resolve().parent / ".enrich_cache.json"
LOG_PATH = pathlib.Path(__file__).resolve().parent / "enrich.log"

def check_ytdlp():
    try:
        r = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            print(f"[check] yt-dlp version: {r.stdout.strip()}")
            return True
        else:
            print(f"[check] yt-dlp failed: {r.stderr}", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("[check] yt-dlp not found. Install: pip install yt-dlp", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[check] error: {e}", file=sys.stderr)
        return False

def load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except:
            return {}
    return {}

def save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")

def clean_query(title, channel):
    # Build search query, strip emojis/control chars, truncate
    parts = []
    if title:
        parts.append(title)
    if channel:
        parts.append(channel)
    q = " ".join(parts).strip()
    # remove excessive whitespace, newlines
    q = re.sub(r"\s+", " ", q)
    # yt-dlp ytsearch handles unicode, but strip very long
    if len(q) > 120:
        q = q[:120]
    return q

def score_match(query_title, returned_title):
    if not query_title or not returned_title:
        return 0.0
    q = query_title.lower()
    r = returned_title.lower()
    # simple token overlap
    q_tokens = set(re.findall(r"\w+", q))
    r_tokens = set(re.findall(r"\w+", r))
    if not q_tokens:
        return 0.0
    overlap = len(q_tokens & r_tokens) / len(q_tokens)
    # bonus if exact substring
    if q in r or r in q:
        overlap = min(1.0, overlap + 0.2)
    return round(overlap, 3)

def yt_search(query, sleep_interval=0.0):
    """
    Run yt-dlp ytsearch1:query and return parsed json dict or None
    """
    search = f"ytsearch1:{query}"
    # Use --print-json which for ytsearch returns JSON for the matched video
    # Add --no-warn to reduce noise, --skip-download --no-playlist
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--no-playlist",
        "--no-warn",
        "--print-json",
        "--default-search", "ytsearch",
        search
    ]
    # Optional: add sleep intervals for yt-dlp internal
    # cmd.insert(1, "--sleep-interval"); cmd.insert(2, "1")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        if r.returncode != 0:
            # yt-dlp prints errors to stderr, stdout may be empty
            err = (r.stderr or "")[:500].replace("\n", " | ")
            return None, f"yt-dlp exit {r.returncode}: {err}"
        out = r.stdout.strip()
        if not out:
            return None, "empty stdout"
        # yt-dlp --print-json for search may output multiple lines if more than 1, but we asked ytsearch1 so 1
        # Take first JSON line
        first_line = out.splitlines()[0]
        data = json.loads(first_line)
        # data contains webpage_url, title, channel, id etc.
        url = data.get("webpage_url") or (f"https://www.youtube.com/watch?v={data.get('id')}" if data.get("id") else None)
        return {
            "url": url,
            "id": data.get("id"),
            "title": data.get("title"),
            "channel": data.get("channel") or data.get("uploader") or data.get("channel_id"),
            "duration": data.get("duration"),
            "view_count": data.get("view_count"),
            "webpage_url": data.get("webpage_url"),
        }, None
    except subprocess.TimeoutExpired:
        return None, "timeout 35s"
    except json.JSONDecodeError as e:
        return None, f"json decode: {e} | stdout={out[:300]}"
    except Exception as e:
        return None, str(e)

def main():
    # Fix Windows console encoding for unicode
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass
    ap = argparse.ArgumentParser(description="Enrich youtube_video urls via yt-dlp")
    ap.add_argument("--input", type=pathlib.Path, default=DEFAULT_INPUT, help="input results.jsonl")
    ap.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT, help="output results.enriched.jsonl")
    ap.add_argument("--limit", type=int, default=0, help="process only first N youtube_video null entries (0=all)")
    ap.add_argument("--offset", type=int, default=0, help="skip first N null entries")
    ap.add_argument("--dry-run", action="store_true", help="print queries without calling yt-dlp")
    ap.add_argument("--sleep", type=float, default=1.5, help="sleep seconds between yt-dlp calls")
    ap.add_argument("--youtube-only", action="store_true", help="if set, skip not yet used; kept for compat")
    ap.add_argument("--no-cache", action="store_true", help="ignore cache and re-query")
    ap.add_argument("--overwrite-null-only", action="store_true", default=True, help="only fill where url is null (default true)")
    args = ap.parse_args()

    inp = args.input
    out = args.output
    if not inp.exists():
        # try relative to ROOT
        alt = ROOT / inp
        if alt.exists():
            inp = alt
        else:
            print(f"[error] input not found: {inp}", file=sys.stderr)
            sys.exit(1)

    print(f"[info] input: {inp}")
    print(f"[info] output: {out}")
    print(f"[info] cache: {CACHE_PATH}")
    print(f"[info] limit={args.limit} offset={args.offset} dry_run={args.dry_run} sleep={args.sleep}")

    if not args.dry_run:
        if not check_ytdlp():
            sys.exit(1)

    cache = {} if args.no_cache else load_cache()
    print(f"[info] cache entries: {len(cache)}")

    # Load all lines
    raw_lines = inp.read_text(encoding="utf-8", errors="ignore").splitlines()
    print(f"[info] loaded {len(raw_lines)} lines")

    enriched_count = 0
    skipped_had_url = 0
    skipped_no_title = 0
    failed = 0
    low_conf = 0
    attempted = 0
    processed_null_index = -1  # index among null entries

    # For offset/limit handling, need to know null youtube entries in order
    # First pass: count
    yt_null_indices = []
    for idx, line in enumerate(raw_lines):
        try:
            j = json.loads(line)
        except:
            continue
        r = j.get("result", {})
        if isinstance(r, list):
            continue
        if not isinstance(r, dict):
            continue
        if r.get("category") != "youtube_video":
            continue
        ed = r.get("extracted_data") or {}
        if isinstance(ed, list):
            ed = {}
        url = ed.get("url")
        title = ed.get("title")
        # overwrite-null-only: skip if url exists
        if url:
            continue
        # need title to search
        if not title or not str(title).strip():
            continue
        yt_null_indices.append(idx)

    print(f"[info] youtube_video total null-with-title candidates: {len(yt_null_indices)}")
    # better compute
    total_yt2 = 0
    with_url = 0
    for l in raw_lines:
        try:
            j = json.loads(l)
            r = j.get("result",{})
            if isinstance(r, dict) and r.get("category")=="youtube_video":
                total_yt2+=1
                ed = r.get("extracted_data") or {}
                if isinstance(ed, dict) and ed.get("url"):
                    with_url+=1
        except: pass
    print(f"[stats] youtube_video total={total_yt2} with_url={with_url} null={total_yt2-with_url}")

    # Prepare output list
    output_lines = []

    # Cache key: file_name + title for stability
    for idx, line in enumerate(raw_lines):
        try:
            j = json.loads(line)
        except Exception as e:
            # keep line as is
            output_lines.append(line)
            continue

        r = j.get("result", {})
        # skip non-dict results (list etc)
        if not isinstance(r, dict):
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue

        if r.get("category") != "youtube_video":
            # not youtube, pass through unchanged (ensure json dump)
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue

        ed = r.get("extracted_data") or {}
        if isinstance(ed, list):
            ed = {}
            r["extracted_data"] = ed
            j["result"] = r

        url = ed.get("url")
        title = ed.get("title")
        channel = ed.get("channel_or_author")
        file_name = j.get("file_name", f"line{idx}")

        # Cases:
        # - has url -> skip enrichment, just add enrichment skipped
        if url:
            skipped_had_url += 1
            # add enrichment audit if not exists
            if "enrichment" not in j:
                j["enrichment"] = {"status": "skipped_had_url", "original_url": url, "at": datetime.now(timezone.utc).isoformat()}
            elif isinstance(j["enrichment"], dict) and "status" not in j["enrichment"]:
                j["enrichment"]["status"] = "skipped_had_url"
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue

        # no url but no title -> skip
        if not title or not str(title).strip():
            skipped_no_title += 1
            if "enrichment" not in j:
                j["enrichment"] = {"status": "skipped_no_title", "at": datetime.now(timezone.utc).isoformat()}
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue

        # This is a candidate
        processed_null_index += 1
        # apply offset/limit
        if processed_null_index < args.offset:
            # not yet in window, just pass through with pending status
            if "enrichment" not in j:
                j["enrichment"] = {"status": "pending_offset", "at": datetime.now(timezone.utc).isoformat()}
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue
        if args.limit and processed_null_index >= args.offset + args.limit:
            if "enrichment" not in j:
                j["enrichment"] = {"status": "pending_limit", "at": datetime.now(timezone.utc).isoformat()}
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue

        query = clean_query(str(title), str(channel) if channel else "")
        cache_key = f"{file_name}::{query}"
        # Use file_name as primary key for resume if query changes slightly
        alt_key = file_name

        if args.dry_run:
            print(f"[dry] {file_name} | query={query!r} | title={title!r} channel={channel!r}")
            # mark as dry
            j["enrichment"] = {"status": "dry_run", "yt_dlp_query": query, "at": datetime.now(timezone.utc).isoformat()}
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue

        # Check cache
        cached = cache.get(cache_key) or cache.get(alt_key)
        if cached and not args.no_cache:
            # use cached
            yt_data = cached.get("yt_data")
            err = cached.get("error")
            if yt_data and yt_data.get("url"):
                # fill
                ed["url"] = yt_data["url"]
                # ensure ed updated
                r["extracted_data"] = ed
                j["result"] = r
                j["enrichment"] = {
                    "status": "enriched_from_cache",
                    "yt_dlp_query": query,
                    "yt_dlp_url": yt_data["url"],
                    "yt_dlp_title": yt_data.get("title"),
                    "yt_dlp_channel": yt_data.get("channel"),
                    "yt_dlp_id": yt_data.get("id"),
                    "match_score": score_match(str(title), yt_data.get("title") or ""),
                    "at": datetime.now(timezone.utc).isoformat(),
                    "source": "cache"
                }
                enriched_count += 1
                if j["enrichment"]["match_score"] < 0.4:
                    low_conf += 1
            else:
                failed += 1
                j["enrichment"] = {"status": f"cached_failed: {err}", "yt_dlp_query": query, "at": datetime.now(timezone.utc).isoformat()}
            output_lines.append(json.dumps(j, ensure_ascii=False))
            continue

        # Actually call yt-dlp
        attempted += 1
        try:
            print(f"[{processed_null_index+1}/{len(yt_null_indices)}] querying: {query!r}  ({file_name})")
        except UnicodeEncodeError:
            print(f"[{processed_null_index+1}/{len(yt_null_indices)}] querying: {query.encode('ascii','replace')!r}  ({file_name})")
        yt_data, err = yt_search(query)
        # sleep regardless after attempt
        time.sleep(args.sleep)

        if yt_data and yt_data.get("url"):
            ed["url"] = yt_data["url"]
            r["extracted_data"] = ed
            j["result"] = r
            score = score_match(str(title), yt_data.get("title") or "")
            j["enrichment"] = {
                "status": "enriched",
                "yt_dlp_query": query,
                "yt_dlp_url": yt_data["url"],
                "yt_dlp_title": yt_data.get("title"),
                "yt_dlp_channel": yt_data.get("channel"),
                "yt_dlp_id": yt_data.get("id"),
                "match_score": score,
                "at": datetime.now(timezone.utc).isoformat(),
                "source": "yt-dlp ytsearch1"
            }
            # update cache
            cache[cache_key] = {"yt_data": yt_data, "error": None, "query": query, "at": j["enrichment"]["at"]}
            cache[alt_key] = cache[cache_key]
            save_cache(cache)
            enriched_count += 1
            if score < 0.4:
                low_conf += 1
                try:
                    print(f"  -> LOW_CONF {score} got: {yt_data.get('title')!r} url={yt_data['url']}")
                except UnicodeEncodeError:
                    print(f"  -> LOW_CONF {score} got: {repr(yt_data.get('title'))} url={yt_data['url']}")
            else:
                try:
                    print(f"  -> OK score={score} url={yt_data['url']}")
                except UnicodeEncodeError:
                    print(f"  -> OK score={score} url={yt_data['url'].encode('ascii','replace')}")
            # append log
            try:
                with LOG_PATH.open("a", encoding="utf-8") as lf:
                    lf.write(f"{datetime.now(timezone.utc).isoformat()} | {file_name} | query={query!r} | url={yt_data['url']} | score={score} | yt_title={yt_data.get('title')!r}\n")
            except: pass
        else:
            failed += 1
            print(f"  -> FAILED: {err}")
            j["enrichment"] = {"status": f"failed: {err}", "yt_dlp_query": query, "at": datetime.now(timezone.utc).isoformat()}
            cache[cache_key] = {"yt_data": None, "error": err, "query": query, "at": j["enrichment"]["at"]}
            cache[alt_key] = cache[cache_key]
            save_cache(cache)
            try:
                with LOG_PATH.open("a", encoding="utf-8") as lf:
                    lf.write(f"{datetime.now(timezone.utc).isoformat()} | {file_name} | query={query!r} | FAILED {err}\n")
            except: pass

        output_lines.append(json.dumps(j, ensure_ascii=False))
        # periodic flush to output file for resume safety? We'll write at end atomically, but also every 10 we could save temp
        if attempted % 10 == 0:
            # save intermediate cache already done
            pass

    # Write atomically to output
    # Ensure parent exists
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text("\n".join(output_lines), encoding="utf-8")
    # atomic replace
    os.replace(tmp, out)
    print("\n=== DONE ===")
    print(f"input lines: {len(raw_lines)}")
    print(f"youtube total: {total_yt2} with_url original: {with_url}")
    print(f"candidates null-with-title: {len(yt_null_indices)}")
    print(f"processed window: offset {args.offset} limit {args.limit or 'all'}")
    print(f"attempted yt-dlp calls this run: {attempted}")
    print(f"enriched: {enriched_count} (low_conf <0.4: {low_conf}) failed: {failed} skipped_had_url:{skipped_had_url} skipped_no_title:{skipped_no_title}")
    print(f"output: {out} ({len(output_lines)} lines)")
    print(f"cache: {CACHE_PATH} ({len(cache)} keys)")
    print(f"log: {LOG_PATH}")

if __name__ == "__main__":
    main()
