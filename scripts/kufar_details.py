"""
Single-ad detail fetcher for kufar.by.

Incremental: fetches details only for ad_ids that do not yet have a
cached detail file. Marks items as `defect` if title/body contains known
defect markers, so the filter can skip them.

Output: scripts/_items.json (current + historical, but defects flagged).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_ITEMS = os.path.join(ROOT, ".cache", "items")
REGISTRY_PATH = os.path.join(ROOT, "scripts", ".cache", "seen_ids.json")
OUT_PATH = os.path.join(ROOT, "scripts", "_items.json")
LOG = sys.stderr

DEFECT_MARKERS = (
    "не работает", "не работают", "не работающ", "слома", "дефект",
    "дифект",  # common typo
    "убит", "не включается", "не запускается", "не стартует",
    "битый", "бита", "трещина", "трещин", "глюк", "глючит",
    "не функцион", "вышел из строя", "вышла из строя", "вышли из строя",
    "перестал", "перестали", "отвал", "разбит", "разбита", "пробит",
    "прогорел", "вздут", "вздутие", "кз", "короткое замыкание",
    "не горит", "не подает признаков", "мертв", "мёртв",
    "одноканал", "одноканальн", "не работают два канала",
)
MB_BRAND_WHITELIST = {"ASUS", "MSI", "Gigabyte", "ASRock", "Biostar", "ECS"}
CPU_SOCKET_IDS = {"19", "16", "6"}  # LGA1700, LGA1200, AM4
ITEM_DELAY = float(os.environ.get("KUFAR_ITEM_DELAY", "0.5"))
ITEM_TTL = int(os.environ.get("KUFAR_ITEM_TTL", str(72 * 3600)))
MAX_RETRIES = int(os.environ.get("KUFAR_MAX_RETRIES", "2"))


def fix_cyr(s):
    if not isinstance(s, str):
        return s
    for _ in range(3):
        try:
            s2 = s.encode("cp1251").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return s
        if s2 == s:
            return s
        s = s2
    return s


def _is_negated_defect(blob: str, match_start: int) -> bool:
    """Return True if the word 'дефект' near match_start is negated.

    Handles phrases like 'без дефектов', 'нет дефектов', 'без скрытых дефектов',
    'не имеет дефектов', 'исправно без дефектов'.
    """
    window = blob[max(0, match_start - 40):match_start]
    negation_words = ("без", "нет", "не", "отсутствуют", "исправно", "исправная")
    return any(w in window for w in negation_words)


def has_defect(*texts: str) -> str | None:
    blob = " ".join((t or "") for t in texts).lower()
    for m in DEFECT_MARKERS:
        if m not in blob:
            continue
        # 'дефект' markers often appear in negated phrases ('без дефектов').
        # Skip those false positives.
        if "дефект" in m:
            for match in re.finditer(re.escape(m), blob):
                if not _is_negated_defect(blob, match.start()):
                    return m
            continue
        return m
    return None


def fetch_ad_page(ad_id: int) -> dict | None:
    os.makedirs(CACHE_ITEMS, exist_ok=True)
    cache_path = os.path.join(CACHE_ITEMS, f"{ad_id}.json")
    if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < ITEM_TTL:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    url = f"https://www.kufar.by/item/{ad_id}"
    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "ru,en;q=0.8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", errors="replace")
            break
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429 and attempt < MAX_RETRIES:
                backoff = 2 ** attempt * ITEM_DELAY
                print(f"[warn] 429 for {ad_id}, retry {attempt + 1}/{MAX_RETRIES} after {backoff:.1f}s", file=LOG)
                time.sleep(backoff)
                continue
            print(f"[warn] fetch failed {ad_id}: {e}", file=LOG)
            return None
        except Exception as e:
            print(f"[warn] fetch failed {ad_id}: {e}", file=LOG)
            return None
    else:
        print(f"[warn] fetch failed {ad_id}: {last_err}", file=LOG)
        return None
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    data = obj.get("props", {}).get("initialState", {}).get("adView", {}).get("data")
    if not data:
        return None
    adp = data.get("adParams") or {}
    out = {
        "id": ad_id,
        "fetched_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "title": fix_cyr(data.get("title")),
        "subject": fix_cyr(data.get("subject")),
        "body": fix_cyr(data.get("body")),
        "price": data.get("price"),
        "priceUsd": data.get("priceUsd"),
        "categoryId": data.get("categoryId"),
        "region": fix_cyr(data.get("region")),
        "address": fix_cyr(data.get("address")),
        "image": data.get("image"),
        "userName": fix_cyr(data.get("userName")),
        "companyName": fix_cyr(data.get("companyName")),
        "isCompanyAd": data.get("isCompanyAd"),
        "date": data.get("date"),
        "params": {
            k: {"p": v.get("p"), "v": v.get("v"), "vl": fix_cyr(v.get("vl"))}
            for k, v in adp.items()
        },
    }
    marker = has_defect(out["title"], out["subject"], out["body"])
    out["defect"] = bool(marker)
    out["defect_marker"] = marker
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out


def load_registry() -> dict:
    if os.path.exists(REGISTRY_PATH):
        try:
            return json.load(open(REGISTRY_PATH, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def listing_socket(listing: dict) -> str | None:
    return (listing.get("params") or {}).get("computers_component_socket")


def listing_brand_name(item: dict) -> str | None:
    brand = ((item.get("params") or {}).get("computersComponentBrand") or {})
    return brand.get("vl")


def detect_brand_from_text(*texts: str) -> str | None:
    blob = " ".join((t or "") for t in texts).lower()
    for brand in MB_BRAND_WHITELIST:
        if brand.lower() in blob:
            return brand
    return None


def listing_price_ok(listing: dict) -> bool:
    """Return True when source listing has a numeric fixed price."""
    params = listing.get("params") or {}
    if params.get("remuneration_type") not in (None, "1"):
        return False
    price = listing.get("price_byn")
    if not price:
        return False
    return bool(re.search(r"\d", str(price)))


def is_relevant(cat: str, listing: dict) -> bool:
    """Fetch details only for lots usable in the Intel/AMD report.

    Motherboards: fetch all (the MB URLs are already filtered).
    CPUs: only LGA1700 / LGA1200 / AM4.
    """
    if cat == "mb":
        return True
    if cat == "cpu":
        return listing_socket(listing) in CPU_SOCKET_IDS
    return True


def finalize_item(item: dict, registry: dict, cat: str) -> None:
    """Enrich item with defect/noname/price flags and mirror to registry."""
    aid = str(item.get("id"))
    source = item.get("source_listing") or {}
    item["defect"] = bool(has_defect(
        item.get("title"), item.get("subject"), item.get("body")
    ))
    item["no_price"] = not listing_price_ok(source)
    if cat == "mb":
        brand = listing_brand_name(item) or detect_brand_from_text(
            item.get("title"), item.get("subject"), item.get("body")
        )
        item["noname"] = (brand or "").lower() not in {b.lower() for b in MB_BRAND_WHITELIST}
    else:
        item["noname"] = False
    entry = registry.setdefault(aid, {})
    entry["defect"] = item["defect"]
    entry["no_price"] = item["no_price"]
    entry["noname"] = item.get("noname", False)


def main():
    # Need listings first; kufar_parse.py should have run already.
    listings_path = os.path.join(ROOT, "scripts", "_out.json")
    if not os.path.exists(listings_path):
        print("[fatal] run scripts/kufar_parse.py first", file=LOG)
        sys.exit(2)
    with open(listings_path, "r", encoding="utf-8") as f:
        listings = json.load(f)
    registry = load_registry()
    now = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    out: dict[str, list[dict]] = {"mb": [], "cpu": []}
    seen: set = set()
    # Build list of ids to fetch details for, in order. Accept any key
    # starting with "mb" (e.g. "mb_2" when two MB URLs were parsed in one
    # run) and "cpu" — not just the exact "mb"/"cpu" labels.
    to_fetch: list[tuple[str, int, dict]] = []
    def _matching_keys(d: dict, prefix: str) -> list[str]:
        return [k for k in d.keys()
                if k == prefix or k.startswith(f"{prefix}_") or k.startswith(f"{prefix}-")]
    for cat in _matching_keys(listings, "mb") + _matching_keys(listings, "cpu"):
        base_cat = cat.split("_")[0].split("-")[0]
        for ad in listings.get(cat, []):
            aid = ad.get("id")
            if not aid or aid in seen:
                continue
            seen.add(aid)
            if not is_relevant(base_cat, ad):
                continue
            cache_path = os.path.join(CACHE_ITEMS, f"{aid}.json")
            if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < ITEM_TTL:
                # use cached
                try:
                    cached = json.load(open(cache_path, encoding="utf-8"))
                    cached["source_listing"] = ad
                    cached["defect"] = bool(cached.get("defect")) or bool(has_defect(
                        cached.get("title"), cached.get("subject"), cached.get("body")
                    ))
                    out[base_cat].append(cached)
                    continue
                except (json.JSONDecodeError, OSError):
                    pass
            to_fetch.append((base_cat, aid, ad))
    print(f"[info] cached: mb={sum(1 for x in out['mb'])}, "
          f"cpu={sum(1 for x in out['cpu'])}; to fetch: {len(to_fetch)}", file=LOG)
    for cat, aid, listing in to_fetch:
        d = fetch_ad_page(aid)
        if d is None:
            continue
        d["source_listing"] = listing
        out[cat].append(d)
        registry.setdefault(str(aid), {})["last_detail_fetch"] = now
        print(f"[info] {cat} #{aid}: {d.get('title')!r}", file=LOG)
        time.sleep(ITEM_DELAY)
    for cat in out:
        for item in out[cat]:
            finalize_item(item, registry, cat)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    mb_count = len(out.get("mb", []))
    cpu_count = len(out.get("cpu", []))
    defects = sum(1 for cat in out for i in out[cat] if i.get("defect"))
    nonames = sum(1 for i in out.get("mb", []) if i.get("noname"))
    no_prices = sum(1 for cat in out for i in out[cat] if i.get("no_price"))
    print(f"[info] wrote {OUT_PATH}: mb={mb_count}, cpu={cpu_count}, "
          f"defect={defects}, noname={nonames}, no_price={no_prices}", file=LOG)


if __name__ == "__main__":
    main()
