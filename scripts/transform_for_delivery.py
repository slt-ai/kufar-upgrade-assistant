"""
Transform the grouped scripts/_items.json into the flat delivery schema and
add source_page to scripts/_out.json.

Requested fields per lot:
  ad_id, url, title, body/description, price (numeric), currency, condition,
  seller, location, listing_time/published_at, category, source_page,
  collected_at, images (optional).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS_IN = os.path.join(ROOT, "scripts", "_items.json")
ITEMS_OUT = os.path.join(ROOT, "scripts", "_items.json")
OUT_IN = os.path.join(ROOT, "scripts", "_out.json")
OUT_OUT = os.path.join(ROOT, "scripts", "_out.json")

SOURCE_URLS = {
    "mb": "https://www.kufar.by/l/r~minsk/materinskie-platy?ccch=v.or%3A32%2C31%2C75%2C55%2C74%2C54%2C53&ccrt=v.or%3A4&sort=lst.d",
    "mb_2": "https://www.kufar.by/l/r~minsk/materinskie-platy?ccch=v.or%3A21%2C11&ccrt=v.or%3A4&sort=lst.d",
    "cpu": "https://www.kufar.by/l/r~minsk/processory",
}

GROUP_LABEL = {
    "mb": "intel_motherboards",
    "mb_2": "amd_motherboards",
    "cpu": "processors",
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_numeric_price(item: dict) -> tuple[float | None, str]:
    sl = item.get("source_listing") or {}
    pb = sl.get("price_byn")
    currency = "BYN"
    if pb is not None:
        try:
            val = int(pb)
            if val > 0:
                return val / 100, currency
        except (ValueError, TypeError):
            pass
    pr = item.get("price") or ""
    ps = str(pr).replace("\xa0", " ").strip().lower()
    if any(w in ps for w in ("договорн", "договор", "торг", "negotiable", "обмен")):
        return None, currency
    m = re.search(r"([\d\s,.]+)", ps)
    if m:
        num = m.group(1).replace(" ", "").replace(",", ".")
        try:
            val = float(num)
            if "р" in ps or "byn" in ps or "byr" in ps:
                return val, "BYN"
            if "$" in ps or "usd" in ps:
                return val, "USD"
            return val, currency
        except ValueError:
            pass
    return None, currency


def transform_item(item: dict, group: str) -> dict:
    sl = item.get("source_listing") or {}
    params = item.get("params") or {}
    price_num, currency = parse_numeric_price(item)
    condition_vl = params.get("condition", {}).get("vl", "")
    seller = item.get("userName") or item.get("companyName") or ""
    region = item.get("region") or ""
    address = item.get("address") or ""
    location = region + (f", {address}" if address else "")
    category = params.get("computersComponentType", {}).get("vl", "")
    if not category:
        category = "Процессоры" if group == "cpu" else "Материнские платы"
    image = item.get("image")
    images = [image] if image else []
    published = item.get("date") or sl.get("list_time") or ""
    collected = item.get("fetched_at") or now_iso()
    return {
        "ad_id": item.get("id"),
        "url": sl.get("url") or f"https://www.kufar.by/item/{item.get('id')}",
        "title": item.get("title") or "",
        "body": item.get("body") or item.get("subject") or "",
        "price": price_num,
        "currency": currency,
        "condition": condition_vl,
        "seller": seller,
        "location": location,
        "category": category,
        "published_at": published,
        "listing_time": published,
        "source_page": SOURCE_URLS.get(group, ""),
        "collected_at": collected,
        "images": images,
        "group": GROUP_LABEL.get(group, group),
        "_raw_params": {k: v.get("vl") for k, v in params.items() if isinstance(v, dict)},
        "_defect": bool(item.get("defect")),
        "_no_price": price_num is None,
        "_noname": bool(item.get("noname")),
    }


def main():
    with open(OUT_IN, "r", encoding="utf-8") as f:
        out = json.load(f)

    # Correct ad_id -> source_page mapping from the raw grouped listing output.
    # The detail fetcher collapses mb_* keys into "mb", so we recover grouping here.
    adid_to_sourcepage: dict[int, str] = {}
    for group, arr in out.items():
        src = SOURCE_URLS.get(group, "")
        for ad in arr:
            ad["source_page"] = src
            aid = ad.get("id")
            if aid is not None:
                adid_to_sourcepage[aid] = src

    with open(ITEMS_IN, "r", encoding="utf-8") as f:
        grouped = json.load(f)
    flat = []
    for _, arr in grouped.items():
        for item in arr:
            aid = item.get("id")
            src = adid_to_sourcepage.get(aid, "")
            group_key = next((k for k, v in SOURCE_URLS.items() if v == src), "")
            flat.append(transform_item(item, group_key))

    with open(ITEMS_OUT, "w", encoding="utf-8") as f:
        json.dump(flat, f, ensure_ascii=False, indent=2)
    with open(OUT_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    stats = {}
    for group_label, src in SOURCE_URLS.items():
        arr = [x for x in flat if x["source_page"] == src]
        stats[group_label] = {
            "raw": len(arr),
            "defect": sum(1 for x in arr if x["_defect"]),
            "no_price": sum(1 for x in arr if x["_no_price"]),
            "noname": sum(1 for x in arr if x["_noname"]),
            "final": sum(1 for x in arr if not x["_defect"] and not x["_no_price"] and not x["_noname"]),
        }
    print("[stats]")
    for k, v in stats.items():
        print(f"{k}: {v}")
    print(f"[info] wrote flat {ITEMS_OUT}: {len(flat)} items")
    print(f"[info] updated {OUT_OUT}")


if __name__ == "__main__":
    main()
