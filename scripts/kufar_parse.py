"""
kufar.by incremental listing fetcher.

By default runs in INCREMENTAL mode: reads the timestamp of the last run
from scripts/.cache/_last_run.json and only walks category pages until it
reaches listings whose list_time <= that timestamp (minus a safety margin).
Kufar's default sort is newest-first, so once the top ad on a page is older
than the cutoff, pagination stops. The freshly collected ads are merged into
the existing scripts/_out.json (new ads overwrite old ones by id), so
kit-analyzer still sees the full pool. Only the delta is also written to
scripts/_out_delta.json.

Pass --full to force a full re-walk (ignores the cutoff, rewrites _out.json
from scratch, and re-marks stale entries against the fresh listing).

Output:
  scripts/.cache/_last_run.json — timestamp of the last run (full or incr).
  scripts/.cache/seen_ids.json — registry of all ad_ids ever seen, with
    first_seen, last_seen, last_list_time, removed (bool), defect (bool).
  scripts/_out.json — current visible listings (merged pool in incr mode).
  scripts/_out_delta.json — only the ads collected this (incremental) run.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_LISTINGS = os.path.join(ROOT, ".cache", "listings")
CACHE_REGISTRY = os.path.join(ROOT, "scripts", ".cache", "seen_ids.json")
LAST_RUN_PATH = os.path.join(ROOT, "scripts", ".cache", "_last_run.json")
OUT_PATH = os.path.join(ROOT, "scripts", "_out.json")
OUT_DELTA_PATH = os.path.join(ROOT, "scripts", "_out_delta.json")

DEFAULT_URLS = [
    ("mb", "https://www.kufar.by/l/r~minsk/materinskie-platy"),
    ("cpu", "https://www.kufar.by/l/r~minsk/processory"),
]

PAGE_DELAY = 2.5
# Safety margin: collect ads published within MARGIN_MINUTES before the last
# run too, so ads whose list_time landed just before we recorded the run are
# not missed.
MARGIN_MINUTES = 5


def safe_filename(url: str) -> str:
    # Cache key — keep query so filtered URLs don't collide. Use a short hash
    # suffix so long cursor tokens cannot be truncated into collisions.
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", url)[:60].strip("_")
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]
    return f"{safe}_{digest}"


def fetch(url: str) -> str:
    os.makedirs(CACHE_LISTINGS, exist_ok=True)
    cache_path = os.path.join(CACHE_LISTINGS, f"{safe_filename(url)}.html")
    if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < 180:
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "ru,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    charset = "utf-8"
    try:
        c = r.headers.get_content_charset()
        if c:
            charset = c
    except Exception:
        pass
    try:
        html = raw.decode(charset, errors="replace")
    except (LookupError, UnicodeDecodeError):
        html = raw.decode("utf-8", errors="replace")
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html


def parse_ads(html: str) -> tuple[list[dict], int, int]:
    """Return (ads, total_count, page_count) from a listing page."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return [], 0, 0
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return [], 0, 0
    state = data.get("props", {}).get("initialState", {}).get("listing", {})
    ads = state.get("ads") or []
    total = state.get("total") or 0
    pagination = state.get("pagination") or []
    # last numeric page in the pagination list
    last = 1
    for p in pagination:
        n = p.get("num")
        if isinstance(n, int) and n > last:
            last = n
    return ads, total, last


def clean_ad(ad: dict) -> dict:
    params = ad.get("ad_parameters") or []
    flat_params = {p.get("p"): p.get("v") for p in params if isinstance(p, dict)}
    return {
        "id": ad.get("ad_id") or ad.get("list_id"),
        "price_byn": ad.get("price_byn"),
        "currency": ad.get("currency", "BYR"),
        "url": ad.get("ad_link"),
        "list_time": ad.get("list_time"),
        "category_raw": ad.get("category"),
        "params": flat_params,
    }


def load_registry() -> dict:
    if os.path.exists(CACHE_REGISTRY):
        try:
            return json.load(open(CACHE_REGISTRY, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_registry(reg: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_REGISTRY), exist_ok=True)
    with open(CACHE_REGISTRY, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)


def load_last_run() -> str | None:
    """Return the ISO timestamp of the last run, or None if never run."""
    if os.path.exists(LAST_RUN_PATH):
        try:
            data = json.load(open(LAST_RUN_PATH, encoding="utf-8"))
            ts = data.get("last_run_at")
            if isinstance(ts, str) and ts:
                return ts
        except (json.JSONDecodeError, OSError):
            pass
    return None


def save_last_run(ts: str, mode: str, cutoff: str | None = None) -> None:
    os.makedirs(os.path.dirname(LAST_RUN_PATH), exist_ok=True)
    with open(LAST_RUN_PATH, "w", encoding="utf-8") as f:
        json.dump({"last_run_at": ts, "mode": mode, "cutoff": cutoff},
                  f, ensure_ascii=False, indent=2)


def load_previous_out() -> dict[str, list[dict]]:
    if os.path.exists(OUT_PATH):
        try:
            data = json.load(open(OUT_PATH, encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def parse_list_time(value) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def walk_category(label: str, base_url: str,
                  cutoff: str | None = None) -> list[dict]:
    """Walk pages, return cleaned ads (latest at the end).

    Kufar's server-rendered HTML returns page 1 regardless of `?page=N` for
    non-JS clients. Real pagination uses a base64 cursor token embedded in
    the listing's `pagination` array. We extract the first cursor and feed
    it back as `?cursor=<token>` on the next request.

    If `cutoff` is given (ISO string), incremental mode: kufar sorts newest-
    first, so we stop pagination once the top ad on a page has list_time <=
    cutoff, and we only keep ads with list_time > cutoff. Pass None for a
    full walk.
    """
    parsed = urllib.parse.urlparse(base_url)
    # Preserve query (kufar reads `ccch`/`ccrt`/`sort` from the query string
    # server-side; stripping it here turned filtered searches into "all of
    # category" and wasted pagination cycles). Note: incremental cutoff
    # relies on newest-first sort; a URL with a non-time sort will produce
    # an empty delta and should be re-run with --full.
    first_url = urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params,
         parsed.query, parsed.fragment)
    )
    html = fetch(first_url)
    _, total, last_page = parse_ads(html)
    print(f"[info] {label}: total={total}, last_page~{last_page}"
          + (f", cutoff={cutoff}" if cutoff else ", full walk"), file=sys.stderr)
    all_ads: list[dict] = []
    seen_ids: set = set()
    cursor = None
    page = 1
    while True:
        if cursor is None:
            url = first_url
        else:
            sep = "&" if "?" in first_url else "?"
            url = f"{first_url}{sep}cursor={urllib.parse.quote(cursor)}"
        try:
            html = fetch(url)
        except Exception as e:
            print(f"[warn] fetch failed: {url} :: {e}", file=sys.stderr)
            break
        ads, _, _ = parse_ads(html)
        if not ads:
            print(f"[info] {label} page {page}: empty, stopping", file=sys.stderr)
            break
        # Incremental stop: if the freshest ad on the page is at/older than
        # cutoff, everything below is too (newest-first sort) — stop walking.
        if cutoff:
            top_lt = None
            for ad in ads:
                top_lt = parse_list_time(clean_ad(ad).get("list_time"))
                if top_lt:
                    break
            if top_lt is None or top_lt <= cutoff:
                print(f"[info] {label} page {page}: top list_time "
                      f"{top_lt} <= cutoff {cutoff}, stopping", file=sys.stderr)
                break
        added = 0
        for ad in ads:
            cleaned = clean_ad(ad)
            ad_id = cleaned.get("id")
            if not ad_id or ad_id in seen_ids:
                continue
            lt = parse_list_time(cleaned.get("list_time"))
            if cutoff and lt and lt <= cutoff:
                # Past the cutoff — skip without stopping, in case a newer
                # ad appears on a later cursor page (rare).
                continue
            seen_ids.add(ad_id)
            all_ads.append(cleaned)
            added += 1
        # find the next cursor
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        next_cursor = None
        if m:
            try:
                st = json.loads(m.group(1))["props"]["initialState"]["listing"]
                for p in (st.get("pagination") or []):
                    if p.get("label") == "next" and p.get("token"):
                        next_cursor = p["token"]
                        break
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        print(f"[info] {label} page {page}: +{added} (total {len(all_ads)})"
              f" next={'yes' if next_cursor else 'no'}", file=sys.stderr)
        if not next_cursor or added == 0:
            break
        cursor = next_cursor
        page += 1
        time.sleep(PAGE_DELAY)
    return all_ads


def main():
    args = [a for a in sys.argv[1:] if a and not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}
    full_mode = "--full" in flags
    urls = args or [u for _, u in DEFAULT_URLS]
    label_for = {u: lbl for lbl, u in DEFAULT_URLS}
    # Fallback label by URL keyword: "materinskie-platy" → mb, "processory" → cpu.
    # Two MB URLs (Intel + AMD) with the same fallback would clobber each other,
    # so we disambiguate by appending a counter when the fallback is reused.
    fallback_seen: dict[str, int] = {}
    registry = load_registry()
    now = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # Decide incremental vs full. Incremental requires a prior run timestamp
    # AND an existing _out.json to merge into; otherwise we fall back to full
    # so kit-analyzer always has a complete pool.
    last_run = load_last_run()
    previous_out = load_previous_out()
    incremental = False
    cutoff = None
    if not full_mode and last_run and previous_out:
        try:
            last_dt = dt.datetime.fromisoformat(last_run.replace("Z", "+00:00"))
        except ValueError:
            last_dt = None
        if last_dt is not None:
            cutoff_dt = last_dt - dt.timedelta(minutes=MARGIN_MINUTES)
            cutoff = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            incremental = True
    mode = "incremental" if incremental else "full"
    print(f"[info] mode={mode}"
          + (f", last_run={last_run}, cutoff={cutoff}" if incremental else ""),
          file=sys.stderr)

    delta: dict[str, list[dict]] = {}
    out: dict[str, list[dict]] = {}
    for url in urls:
        label = label_for.get(url)
        if not label:
            base = "mb" if "materinskie-platy" in url else (
                "cpu" if "processory" in url else "other"
            )
            n = fallback_seen.get(base, 0) + 1
            fallback_seen[base] = n
            label = base if n == 1 and base not in out else f"{base}_{n}"
        ads = walk_category(label, url, cutoff=cutoff if incremental else None)
        delta[label] = list(ads)
        out.setdefault(label, []).extend(ads)
        # update registry: mark freshly collected ads as alive
        for a in ads:
            aid = a["id"]
            entry = registry.get(str(aid), {})
            entry["first_seen"] = entry.get("first_seen", now)
            entry["last_seen"] = now
            entry["last_list_time"] = a.get("list_time")
            entry["last_price"] = a.get("price_byn")
            entry["category"] = label
            entry["url"] = a.get("url")
            entry["removed"] = False
            entry["stale"] = False
            entry["last_check"] = now
            registry[str(aid)] = entry

    if incremental:
        # Merge: start from previous pool, drop ids we just refreshed, append
        # the fresh ones. Ads we did not re-fetch keep their previous record.
        merged: dict[str, list[dict]] = {}
        fresh_ids = {a["id"] for ads in delta.values() for a in ads}
        for label, prev_ads in previous_out.items():
            kept = [a for a in prev_ads if a.get("id") not in fresh_ids]
            merged[label] = kept
        for label, new_ads in out.items():
            merged.setdefault(label, []).extend(new_ads)
        out = merged
        newly_stale = 0  # not recomputed in incremental mode
    else:
        # Full mode: mark entries missing from the fresh listing as stale for
        # later direct-URL verification. Do NOT auto-mark removed.
        visible_all = {a["id"] for ads in out.values() for a in ads}
        newly_stale = 0
        for aid_str, entry in registry.items():
            if not entry.get("removed", False) and int(aid_str) not in visible_all:
                entry["stale"] = True
                entry["last_check"] = now
                newly_stale += 1

    save_registry(registry)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    if incremental:
        with open(OUT_DELTA_PATH, "w", encoding="utf-8") as f:
            json.dump(delta, f, ensure_ascii=False, indent=2)
    save_last_run(now, mode, cutoff=cutoff)

    delta_count = sum(len(v) for v in delta.values())
    pool_count = sum(len(v) for v in out.values())
    print(f"[info] mode={mode} delta={delta_count} pool={pool_count} "
          f"newly_stale={newly_stale} registry={len(registry)}", file=sys.stderr)
    print(f"[info] wrote {OUT_PATH}", file=sys.stderr)
    if incremental:
        print(f"[info] wrote {OUT_DELTA_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
