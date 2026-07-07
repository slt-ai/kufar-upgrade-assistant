#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reprocess kufar kit analyzer output with 4-DIMM and other constraints."""

import json
import re
from pathlib import Path
from datetime import datetime, timezone

BASELINE_CPU = "Intel Core i7-9750H"
BASELINE_PERF = 100

# CPU performance table relative to i7-9750H = 100
# Aligned with the project's previous scale where possible.
CPU_PERF = {
    # Intel
    "i3-10100": 130, "i3-10100f": 130, "i3-10105": 135, "i3-10105f": 135,
    "i3-12100": 110, "i3-12100f": 110, "i3-12300": 120, "i3-14100f": 130,
    "i5-10400": 230, "i5-10400f": 230, "i5-10600k": 260, "i5-10600kf": 260,
    "i5-11400": 240, "i5-11400f": 240, "i5-11600k": 280,
    "i5-12400": 240, "i5-12400f": 240, "i5-12500": 250, "i5-12600": 260,
    "i5-12600k": 300, "i5-13400": 280, "i5-13400f": 280, "i5-13500": 300,
    "i5-13600k": 360, "i5-14600k": 400,
    "i7-10700k": 260, "i7-11700k": 290,
    "i7-12700": 330, "i7-12700f": 330, "i7-12700k": 370,
    "i7-13700k": 470, "i7-13700f": 450, "i7-14700k": 510, "i7-14700kf": 510,
    "i9-10900k": 380, "i9-10900kf": 380, "i9-11900k": 420,
    "i9-12900k": 410, "i9-12900kf": 410, "i9-12900ks": 430,
    "i9-13900k": 540, "i9-13900kf": 540, "i9-14900k": 540, "i9-14900kf": 540, "i9-14900ks": 560,

    # AMD
    "r3-1200": 95, "r3-1300x": 100, "r3-2200g": 110, "r3-3200g": 120, "r3-4100": 120,
    "r5-1400": 140, "r5-1500x": 150, "r5-1600": 170, "r5-1600af": 180,
    "r5-2600": 180, "r5-2600x": 190,
    "r5-3500x": 190, "r5-3600": 200, "r5-3600x": 210, "r5-4500": 220,
    "r5-5500": 230, "r5-5600": 240, "r5-5600x": 250, "r5-5600g": 190,
    "r5-4600g": 210, "r5-4650g": 210, "r5-4700g": 230,
    "r7-1700": 190, "r7-1700x": 200, "r7-2700": 220, "r7-2700x": 240,
    "r7-3700x": 260, "r7-5700g": 240, "r7-5700x": 300, "r7-5800x": 320,
    "r7-4700g": 230,
    "r9-3900x": 360, "r9-3950x": 400, "r9-5900x": 430, "r9-5950x": 470,
}

# Phrases that are defect markers on their own (the negation is part of the phrase).
DIRECT_DEFECT_PHRASES = [
    "не работает", "не работают", "не работал", "не работала",
    "не включается", "не включаются", "не включает",
    "не запускается", "не стартует", "нет старта", "без старта",
    "не определяется", "перестали работать", "перестал работать",
    "вышел из строя", "вышли из строя", "выйшел из строя", "выйшла из строя",
    "коротит", "короткое замыкание", "сгорел", "сгорела", "погорел", "погорела",
    "утоплен", "утоплена", "материнка умерла", "плата умерла",
]

# Words/stems that describe a defect, but may be negated by "без/нет/не".
NEGATABLE_DEFECT_MARKERS = [
    "дефект", "сломан", "убит", "разбит", "трещина", "глючит", "глючный",
    "отлетевш", "отвалилась", "неисправ", "сгоревш", "битый", "битая",
]

CLAUSE_SEPARATORS = set(".!?;:—–(),")


def _is_negated(text_lower, marker_idx):
    """Check whether the defect marker at marker_idx is negated by без/нет/не in the same clause."""
    window = text_lower[max(0, marker_idx - 50):marker_idx]
    # Find the last occurrence of a negation word before the marker.
    best_pos = -1
    for neg in ("без ", "нет ", "не "):
        pos = window.rfind(neg)
        if pos > best_pos:
            best_pos = pos
    if best_pos == -1:
        return False
    # If a clause separator sits between the negation and the marker, the negation
    # does not apply to this marker.
    between = window[best_pos:]
    if any(ch in CLAUSE_SEPARATORS for ch in between):
        return False
    return True


def has_defect_text(item):
    text = (item.get("title") or "") + " " + (item.get("body") or "")
    text_lower = text.lower()

    # Direct phrases always flag a defect.
    for phrase in DIRECT_DEFECT_PHRASES:
        if phrase in text_lower:
            return True

    # Negatable markers flag a defect only when not negated.
    for marker in NEGATABLE_DEFECT_MARKERS:
        idx = text_lower.find(marker)
        if idx == -1:
            continue
        if not _is_negated(text_lower, idx):
            return True
    return False


def parse_cpu(item):
    """Extract CPU brand/model/gen/perf from a CPU listing."""
    title = (item.get("title") or item.get("subject") or "").lower()
    body = (item.get("body") or "").lower()
    text = title + " " + body
    info = {"ad_id": str(item["id"]), "title": item.get("title", ""), "raw_text": text}

    # Intel explicit: i3-12100F, i3 12100f, I5 13600k, etc.
    m = re.search(r"\b(?:intel\s+)?(?:core\s+)?i\s*(3|5|7|9)[-\s]?(10|11|12|13|14)(\d{2,3})([kft]?)\b", text)
    if m:
        tier, gen, mid, suffix = m.group(1), m.group(2), m.group(3), m.group(4).upper()
        num = gen + mid
        model = f"Intel Core i{tier}-{num}{suffix}" if suffix else f"Intel Core i{tier}-{num}"
        info.update({"brand": "intel", "model": model, "tier": int(tier), "num": num, "suffix": suffix, "gen": int(gen)})
        return info

    # Intel older: i7-10700K, i5-7600K
    m = re.search(r"\b(?:intel\s+)?(?:core\s+)?i\s*(3|5|7|9)[-\s]?([2678])(\d{2,3})([kft]?)\b", text)
    if m:
        tier, gen, mid, suffix = m.group(1), m.group(2), m.group(3), m.group(4).upper()
        num = gen + mid
        model = f"Intel Core i{tier}-{num}{suffix}" if suffix else f"Intel Core i{tier}-{num}"
        info.update({"brand": "intel", "model": model, "tier": int(tier), "num": num, "suffix": suffix, "gen": int(gen)})
        return info

    # Intel bare number after "Intel": "Intel 12100f"
    m = re.search(r"\bintel\s+(?:core\s+)?(?:i\s*)?(3|5|7|9)?\s*(12|13|14)(\d{2,3})([kft]?)\b", text)
    if m:
        tier = m.group(1) or "5"
        mid = m.group(3)
        if not m.group(1):
            if mid.startswith("1"): tier = "3"
            elif mid.startswith(("2", "4")): tier = "5"
            elif mid.startswith(("5", "6", "7")): tier = "7"
            elif mid.startswith("9"): tier = "9"
            else: tier = "5"
        gen = m.group(2)
        num = gen + mid
        suffix = m.group(4).upper()
        model = f"Intel Core i{tier}-{num}{suffix}" if suffix else f"Intel Core i{tier}-{num}"
        info.update({"brand": "intel", "model": model, "tier": int(tier), "num": num, "suffix": suffix, "gen": int(gen)})
        return info

    # AMD: "Ryzen 5 5600X", "Ryzen 5600G", "Ryzen 7 3700x", etc.
    m = re.search(r"\bryzen\s+(?:([3579])\s+)?(\d{4})([xgt]?)\b", text)
    if m:
        tier, num, suffix = m.group(1), m.group(2), m.group(3).upper()
        if not tier:
            tier_map = {
                "1200": "3", "1300X": "3", "2200G": "3", "3200G": "3", "4100": "3",
                "1400": "5", "1500X": "5", "1600": "5", "1600AF": "5", "2600": "5", "2600X": "5",
                "3500X": "5", "3600": "5", "3600X": "5", "4500": "5", "5500": "5", "5600": "5",
                "5600X": "5", "5600G": "5", "4600G": "5", "4650G": "5", "4700G": "5",
                "1700": "7", "1700X": "7", "2700": "7", "2700X": "7", "3700X": "7",
                "5700G": "7", "5700X": "7", "5800X": "7",
                "3900X": "9", "3950X": "9", "5900X": "9", "5950X": "9",
            }
            key = num + suffix
            tier = tier_map.get(key, str(int(num[0])))
        model = f"AMD Ryzen {tier} {num}{suffix}" if suffix else f"AMD Ryzen {tier} {num}"
        info.update({"brand": "amd", "model": model, "tier": int(tier), "num": num, "suffix": suffix, "gen": int(num[0])})
        return info

    return None


def cpu_perf_key(info):
    if not info:
        return None
    # Table keys are lowercased like i3-12100f, r5-5600x.
    b = "i" if info["brand"] == "intel" else "r"
    key = f"{b}{info['tier']}-{info['num']}{info['suffix']}".lower()
    return key


def get_perf(info):
    key = cpu_perf_key(info)
    if key in CPU_PERF:
        return CPU_PERF[key]
    # conservative inference from generation and tier
    if info["brand"] == "intel":
        g = info["gen"]
        t = info["tier"]
        base = {10: 80, 11: 90, 12: 100, 13: 110, 14: 115}.get(g, 80)
        return int(base * (0.8 + 0.12 * t))
    else:
        g = info["gen"]
        t = info["tier"]
        base = {1: 35, 2: 40, 3: 45, 4: 48, 5: 50, 7: 65}.get(g, 45)
        return int(base * (0.7 + 0.12 * t))


def get_price(item):
    src = item.get("source_listing", {})
    price_byn = src.get("price_byn")
    if price_byn is None:
        return None
    try:
        return int(price_byn) / 100
    except (ValueError, TypeError):
        return None


def is_cpu_kit_ad(item):
    """Detect CPU ads that are actually motherboard+cpu combos and cannot be split."""
    text = (item.get("title") or "") + " " + (item.get("body") or "")
    text_lower = text.lower()
    # Only CPU-side markers: plus a board, or explicit kit wording, or mobile adapter kits
    markers = [
        "+ материн", "+ материнская", "+ mb", "+ motherboard",
        "+ a320", "+ b450", "+ b550", "+ x570", "+ h510", "+ h610", "+ b660", "+ b760", "+ z690", "+ z790",
        "комплект", "комплекте", "процессор intel core i5-13400 + b660m+4x8", "i9-14900kf + msi pro z790",
        "asus prime b560m-k + ", "asrock b560 pro4 + ", "ryzen 5 2600 + a320m", "r5 5500+32gb+",
        "3 платы z790", "топц modt", "modt", "qy0z", "qyz",
        "процессор + плата", "процессор и плата", "cpu + mb", "процессор в сборе",
    ]
    for marker in markers:
        if marker.lower() in text_lower:
            return True
    return False


def is_mb_kit_ad(item):
    """Motherboard ads that are actually full PC kits. Rare."""
    text = (item.get("title") or "") + " " + (item.get("body") or "")
    text_lower = text.lower()
    markers = ["комплект пк", "игровой пк", "готовый пк", "в сборе"]
    return any(marker in text_lower for marker in markers)


def is_mutant(item, info):
    text = (item.get("title") or "") + " " + (item.get("body") or "")
    text_lower = text.lower()
    if "13950hx" in text_lower or "мутант" in text_lower or "интерпосер" in text_lower:
        return True
    if info and info.get("num") == "13950":
        return True
    return False


def extract_mb_features(item):
    params = item.get("params", {})
    brand = params.get("computersComponentBrand", {}).get("vl", "")
    socket = params.get("computersComponentSocket", {}).get("vl", "")
    chipset = params.get("computersComponentChipset", {}).get("vl", "")
    ram_type = params.get("computersComponentRamType", {}).get("vl", "")
    dimm_str = params.get("computersComponentNumberSlots", {}).get("vl", "")
    try:
        dimm_count = int(dimm_str) if dimm_str else 2
    except ValueError:
        dimm_count = 2
    title_lower = (item.get("title") or "").lower()
    body_lower = (item.get("body") or "").lower()
    text = title_lower + " " + body_lower

    # PCIe generation of primary x16 slot
    pcie = 4.0
    if "pcie 5.0" in text or "pci-e 5.0" in text or "pci express 5.0" in text:
        pcie = 5.0
    elif "pcie 4.0" in text or "pci-e 4.0" in text or "pci express 4.0" in text:
        pcie = 4.0
    elif "gen3" in text or "gen 3" in text or "3.0" in text:
        pcie = 3.0
    # MSI "Gen3" suffix on B550 = PCIe 3.0 primary slot
    if brand == "MSI" and "gen3" in text and "b550" in text:
        pcie = 3.0

    # VRM tier / board quality
    vrm = 3
    oc_series = False
    premium_series = ["aorus", "rog", "tuf", "gaming x", "gaming plus", "tomahawk", "steel legend", "pro4", "master", "edge"]
    for s in premium_series:
        if s in text:
            oc_series = True
            break

    chipset_lower = chipset.lower()
    if "z790" in chipset_lower or "x570" in chipset_lower:
        vrm = 8
    elif "z690" in chipset_lower:
        vrm = 7
    elif "b760" in chipset_lower:
        vrm = 5
    elif "b660" in chipset_lower:
        vrm = 4
    elif "h610" in chipset_lower:
        vrm = 2
    elif "b550" in chipset_lower:
        vrm = 5
    elif "x470" in chipset_lower or "x370" in chipset_lower:
        vrm = 6
    elif "b450" in chipset_lower:
        vrm = 4

    # Network: 2.5GbE / WiFi
    net_score = 0
    if "2.5g" in text or "2.5 гбит" in text or "5g" in text or "5 гбит" in text:
        net_score += 1
    if "wifi 6" in text or "wi-fi 6" in text or "wifi6" in text or "ax" in title_lower or "ax " in text:
        net_score += 1
    elif "wifi" in text or "wi-fi" in text:
        net_score += 1

    # M.2 count inference
    m2_count = text.count("m.2") + text.count("m2")
    if m2_count == 0:
        m2_count = 1

    return {
        "brand": brand,
        "socket": socket,
        "chipset": chipset,
        "ram_type": ram_type,
        "dimm_count": dimm_count,
        "pcie": pcie,
        "vrm": vrm,
        "oc_series": oc_series,
        "net_score": net_score,
        "m2_count": m2_count,
    }


def socket_for_cpu(info):
    if info["brand"] == "intel":
        gen = info["gen"]
        if gen >= 12:
            return "LGA1700"
        elif gen in (10, 11):
            return "LGA1200"
        elif gen in (6, 7, 8, 9):
            return "LGA1151"
        else:
            return None
    else:
        gen = info["gen"]
        if gen <= 5:
            return "AM4"
        elif gen >= 7:
            return "AM5"
        return None


def mb_supports_cpu(mb_features, info):
    socket_mb = mb_features["socket"]
    socket_cpu = socket_for_cpu(info)
    if not socket_cpu or socket_mb != socket_cpu:
        return False, f"socket mismatch {socket_mb} vs {socket_cpu}"
    chipset = mb_features["chipset"].lower()
    if info["brand"] == "intel":
        gen = info["gen"]
        if "h610" in chipset or "b660" in chipset or "z690" in chipset:
            if gen >= 12:
                return True, "verified"
            return False, f"{chipset} does not support {gen}th gen Intel"
        if "b760" in chipset or "z790" in chipset:
            if gen >= 12:
                return True, "verified"
            return False, f"{chipset} does not support {gen}th gen Intel"
        return False, f"unsupported Intel chipset {chipset}"
    else:
        num = int(info["num"])
        if "b550" in chipset or "x570" in chipset:
            if num >= 3000:
                return True, "verified"
            else:
                return True, "uncertain"
        if "b450" in chipset or "x470" in chipset:
            return True, "uncertain"
        if "a320" in chipset or "b350" in chipset or "x370" in chipset:
            return True, "uncertain"
        return False, f"unsupported AMD chipset {chipset}"


def vrm_warning(mb_features, info):
    chipset = mb_features["chipset"].lower()
    vrm = mb_features["vrm"]
    tdp = 65
    if info["brand"] == "intel":
        suffix = info.get("suffix", "")
        tier = info["tier"]
        gen = info["gen"]
        if "k" in suffix.lower():
            if tier >= 9:
                tdp = 125
            elif tier == 7 and gen >= 12:
                tdp = 125
            elif tier == 5 and gen >= 12:
                tdp = 125
            else:
                tdp = 95
        elif tier >= 7 and gen >= 12:
            tdp = 65
    else:
        tier = info["tier"]
        num = int(info["num"])
        if tier == 9:
            tdp = 105
        elif tier == 7 and num >= 5000:
            tdp = 65
        elif tier == 7 and num >= 3000:
            tdp = 65

    if tdp >= 125 and vrm <= 4:
        return True, f"VRM: {tdp}W CPU на плате {chipset} может ограничить turbo/троттлить"
    if tdp >= 125 and vrm <= 5 and ("b760" in chipset or "b660" in chipset or "h610" in chipset):
        return True, f"VRM: {tdp}W CPU на {chipset} — плата выдержит, но при длительной нагрузке (рендер, LLM) возможен троттлинг; желателен Z-чипсет"
    if tdp >= 105 and vrm <= 3:
        return True, f"VRM: {tdp}W CPU на бюджетной плате {chipset}"
    return False, ""


def quality_score(mb_features, info, kit_price):
    """Quality/future-proof score. Board quality and CPU perf both matter."""
    dimm = mb_features["dimm_count"]
    pcie = mb_features["pcie"]
    vrm = mb_features["vrm"]
    net = mb_features["net_score"]
    oc = mb_features["oc_series"]
    perf = get_perf(info)

    score = 0.0
    # 4 DIMM is critical
    if dimm >= 4:
        score += 25
    elif dimm == 2:
        score += 5
    # PCIe 5.0 bonus
    if pcie >= 5.0:
        score += 12
    elif pcie >= 4.0:
        score += 6
    # VRM/board quality
    score += vrm * 2.5
    # OC/premium series
    if oc:
        score += 6
    # Network premium
    score += net * 4
    # M.2
    score += min(mb_features["m2_count"], 3) * 1.5
    # Performance (strong weight: better CPU = better future-proofing)
    score += min(perf, 600) / 12
    # Price penalty
    if kit_price:
        score -= kit_price / 120
    return round(score, 2)


def main():
    root = Path("D:/Work/AI/ClaudeCode/research-agent")
    items_path = root / "scripts" / "_items.json"
    out_path = root / "scripts" / "_kit_analyzer_out.json"

    with open(items_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mbs_raw = data.get("mb", [])
    cpus_raw = data.get("cpu", [])

    whitelist = {"ASUS", "MSI", "Gigabyte", "ASRock", "Biostar", "ECS"}

    valid_mbs = []
    excluded = {"defect": [], "wrong_memory": [], "noname_mb": [], "no_price": [], "other": []}

    for mb in mbs_raw:
        mid = str(mb["id"])
        params = mb.get("params", {})
        region = params.get("region", {}).get("vl", "")
        if region and "минск" not in region.lower():
            continue
        if mb.get("defect") or has_defect_text(mb):
            excluded["defect"].append(mid)
            continue
        brand = params.get("computersComponentBrand", {}).get("vl", "")
        if brand not in whitelist:
            excluded["noname_mb"].append(mid)
            continue
        ram_type = params.get("computersComponentRamType", {}).get("vl", "")
        if ram_type != "DDR4":
            excluded["wrong_memory"].append(mid)
            continue
        price = get_price(mb)
        if price is None or price <= 0:
            excluded["no_price"].append(mid)
            continue
        if is_mb_kit_ad(mb):
            excluded["other"].append(mid)
            continue
        features = extract_mb_features(mb)
        if features["pcie"] < 4.0:
            excluded["other"].append(mid)
            continue
        features["price"] = price
        features["ad_id"] = mid
        features["title"] = mb.get("title", "")
        features["url"] = f"https://www.kufar.by/item/{mid}"
        features["seller"] = mb.get("companyName") or mb.get("userName") or ""
        features["condition"] = params.get("condition", {}).get("vl", "Б/у")
        features["list_time"] = mb.get("source_listing", {}).get("list_time", "")
        valid_mbs.append(features)

    valid_cpus = []
    for cpu in cpus_raw:
        cid = str(cpu["id"])
        params = cpu.get("params", {})
        region = params.get("region", {}).get("vl", "")
        if region and "минск" not in region.lower():
            continue
        if cpu.get("defect") or has_defect_text(cpu):
            continue  # do not enumerate defective CPUs
        info = parse_cpu(cpu)
        if not info:
            continue
        if is_mutant(cpu, info):
            excluded["other"].append(cid)
            continue
        socket = socket_for_cpu(info)
        if not socket:
            continue
        price = get_price(cpu)
        if price is None or price <= 0:
            continue
        if is_cpu_kit_ad(cpu):
            excluded["other"].append(cid)
            continue
        if info["brand"] == "amd" and socket == "AM5":
            excluded["wrong_memory"].append(cid)
            continue
        perf = get_perf(info)
        info["price"] = price
        info["ad_id"] = cid
        info["url"] = f"https://www.kufar.by/item/{cid}"
        info["seller"] = cpu.get("companyName") or cpu.get("userName") or ""
        info["condition"] = params.get("condition", {}).get("vl", "Б/у")
        info["list_time"] = cpu.get("source_listing", {}).get("list_time", "")
        info["perf"] = perf
        valid_cpus.append(info)

    # Build all compatible combos
    combos = []
    for mb in valid_mbs:
        for cpu in valid_cpus:
            ok, reason = mb_supports_cpu(mb, cpu)
            if not ok:
                continue
            kit_price = mb["price"] + cpu["price"]
            perf = cpu["perf"]
            mismatch, vrm_note = vrm_warning(mb, cpu)
            dimm_note = "4 DIMM-слота — подходит под 4 планки DDR4" if mb["dimm_count"] >= 4 else f"Плата имеет {mb['dimm_count']} DIMM-слота — текущие 4 планки DDR4 не влезут"
            pcie_note = f"PCIe {mb['pcie']} x16 на первичном слоте"
            notes = [pcie_note, dimm_note]
            if mismatch:
                notes.append(vrm_note)
            if reason == "uncertain":
                notes.append("Совместимость по BIOS не подтверждена явно — уточните у продавца")

            compatibility = "verified" if reason == "verified" else "uncertain"
            qscore = quality_score(mb, cpu, kit_price)
            combos.append({
                "motherboard": {
                    "ad_id": mb["ad_id"],
                    "title": mb["title"],
                    "price_byn": mb["price"],
                    "url": mb["url"],
                    "seller": mb["seller"],
                    "condition": mb["condition"],
                    "chipset": mb["chipset"],
                    "dimm_count": mb["dimm_count"],
                    "pcie": mb["pcie"],
                    "vrm": mb["vrm"],
                },
                "cpu": {
                    "ad_id": cpu["ad_id"],
                    "title": cpu["title"],
                    "price_byn": cpu["price"],
                    "url": cpu["url"],
                    "seller": cpu["seller"],
                    "condition": cpu["condition"],
                    "model": cpu["model"],
                },
                "kit_price_byn": kit_price,
                "cpu_perf": perf,
                "cpu_perf_baseline": BASELINE_PERF,
                "compatibility": compatibility,
                "notes": notes,
                "quality_score": qscore,
                "vrm_mismatch": mismatch,
                "mb_features": mb,
                "platform": "intel" if cpu["brand"] == "intel" else "amd",
            })

    def make_ranked(combo_list, tier):
        for i, c in enumerate(combo_list, 1):
            c["rank"] = i
            c["tier"] = tier
        return combo_list

    intel_combos = [c for c in combos if c["platform"] == "intel"]
    amd_combos = [c for c in combos if c["platform"] == "amd"]

    # Entry upgrade: cheapest that beats baseline (perf >= 98)
    intel_entry = sorted([c for c in intel_combos if c["cpu_perf"] >= 98], key=lambda c: c["kit_price_byn"])[:3]
    amd_entry = sorted([c for c in amd_combos if c["cpu_perf"] >= 98], key=lambda c: c["kit_price_byn"])[:3]

    intel_entry_cheapest = intel_entry[0]["kit_price_byn"] if intel_entry else None
    amd_entry_cheapest = amd_entry[0]["kit_price_byn"] if amd_entry else None

    def balanced_filter(combos_list, entry_cheapest, require_4dimm=False, amd_min_perf=None):
        if not entry_cheapest:
            return []
        min_price = entry_cheapest * 1.15
        max_price = max(1100, entry_cheapest * 2.2)
        candidates = []
        for c in combos_list:
            p = c["cpu_perf"]
            if not (115 <= p <= 300):
                continue
            if c["kit_price_byn"] <= min_price or c["kit_price_byn"] > max_price:
                continue
            if require_4dimm and c["mb_features"]["dimm_count"] < 4:
                continue
            if amd_min_perf and p < amd_min_perf:
                continue
            score = p / max(c["kit_price_byn"], 1)
            if c["vrm_mismatch"]:
                score *= 0.75
            if c["mb_features"]["chipset"].lower().startswith("h610") and c["cpu_perf"] >= 300:
                score *= 0.7
            c["ppd"] = score
            candidates.append(c)
        candidates.sort(key=lambda c: c["ppd"], reverse=True)
        return candidates[:3]

    # Intel balanced: priority 4 DIMM, otherwise 2-DIMM with warning
    intel_balanced_4dimm = balanced_filter(intel_combos, intel_entry_cheapest, require_4dimm=True)
    intel_balanced = intel_balanced_4dimm if intel_balanced_4dimm else balanced_filter(intel_combos, intel_entry_cheapest, require_4dimm=False)

    # AMD balanced: CPU perf >= 200
    amd_balanced = balanced_filter(amd_combos, amd_entry_cheapest, amd_min_perf=200)

    # Future ready: perf >= 180, price <= max(1500, 3x entry cheapest)
    def future_filter(combos_list, entry_cheapest):
        if not entry_cheapest:
            return []
        max_price = max(1500, entry_cheapest * 3.0)
        candidates = []
        for c in combos_list:
            if c["cpu_perf"] < 180:
                continue
            if c["kit_price_byn"] > max_price:
                continue
            q = c["quality_score"]
            if c["vrm_mismatch"]:
                q *= 0.6
            c["future_score"] = q
            candidates.append(c)
        candidates.sort(key=lambda c: c["future_score"], reverse=True)
        return candidates[:3]

    intel_future = future_filter(intel_combos, intel_entry_cheapest)
    amd_future = future_filter(amd_combos, amd_entry_cheapest)

    # Unified top3: 4-DIMM combos that at least beat baseline, ranked by quality_score
    def top3_filter(combos_list):
        cands = [c for c in combos_list if c["mb_features"]["dimm_count"] >= 4 and c["cpu_perf"] >= 100]
        cands.sort(key=lambda c: c["quality_score"], reverse=True)
        return cands[:3]

    intel_top3 = top3_filter(intel_combos)
    amd_top3 = top3_filter(amd_combos)

    # Alternatives: 2-DIMM or uncertain or VRM-warning combos
    def alternatives(combos_list, top3_ids):
        alts = []
        for c in combos_list:
            key = (c["motherboard"]["ad_id"], c["cpu"]["ad_id"])
            if key in top3_ids:
                continue
            if c["mb_features"]["dimm_count"] < 4 or c["compatibility"] == "uncertain" or c["vrm_mismatch"]:
                alts.append(c)
        alts.sort(key=lambda c: c["kit_price_byn"])
        return alts[:5]

    intel_top3_keys = {(c["motherboard"]["ad_id"], c["cpu"]["ad_id"]) for c in intel_top3}
    amd_top3_keys = {(c["motherboard"]["ad_id"], c["cpu"]["ad_id"]) for c in amd_top3}
    intel_alts = alternatives(intel_combos, intel_top3_keys)
    amd_alts = alternatives(amd_combos, amd_top3_keys)

    def combo_obj(c, rank=None, tier=None):
        return {
            "rank": rank or c.get("rank", 1),
            "tier": tier or c.get("tier", ""),
            "score": c.get("quality_score", 0),
            "score_breakdown": {
                "price": round(max(0, 10 - c["kit_price_byn"] / 200), 2),
                "compatibility": 10.0 if c["compatibility"] == "verified" else 6.0,
                "freshness": 9.0,
                "condition": 8.0 if c["motherboard"]["condition"] == "Б/у" else 9.0,
                "seller": 7.0,
            },
            "motherboard": {k: v for k, v in c["motherboard"].items() if k not in ("chipset", "dimm_count", "pcie", "vrm")},
            "cpu": c["cpu"],
            "kit_price_byn": c["kit_price_byn"],
            "cpu_perf": c["cpu_perf"],
            "cpu_perf_baseline": c["cpu_perf_baseline"],
            "compatibility": c["compatibility"],
            "quality_score": c["quality_score"],
            "notes": c["notes"],
        }

    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            old = json.load(f)
    else:
        old = {}

    current_ids = {str(it["id"]) for it in mbs_raw + cpus_raw}
    old_reverify = old.get("needs_main_agent", {}).get("reverify_urls", [])
    new_reverify = [url for url in old_reverify if url.split("/")[-1] not in current_ids]

    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "report_txt": "Intel Core i7-9750H / MSI B250M Pro-VDH / 48 GB DDR4 (4 sticks) / NVIDIA GeForce RTX 5060 Ti",
            "fresh_fetch": "scripts/_items.json",
            "seen_ids": "scripts/.cache/seen_ids.json",
            "missing_or_stale_ids": old.get("inputs", {}).get("missing_or_stale_ids", []),
            "current_cpu_baseline": {"model": BASELINE_CPU, "perf_score": BASELINE_PERF},
        },
        "intel": {
            "entry_upgrade": [combo_obj(c, rank=i+1, tier="entry_upgrade") for i, c in enumerate(make_ranked(intel_entry, "entry_upgrade"))],
            "balanced": [combo_obj(c, rank=i+1, tier="balanced") for i, c in enumerate(make_ranked(intel_balanced, "balanced"))],
            "future_ready": [combo_obj(c, rank=i+1, tier="future_ready") for i, c in enumerate(make_ranked(intel_future, "future_ready"))],
            "top3": [combo_obj(c, rank=i+1, tier="top3") for i, c in enumerate(intel_top3)],
            "alternatives": [combo_obj(c, rank=i+1, tier="alternative") for i, c in enumerate(intel_alts)],
        },
        "amd": {
            "entry_upgrade": [combo_obj(c, rank=i+1, tier="entry_upgrade") for i, c in enumerate(make_ranked(amd_entry, "entry_upgrade"))],
            "balanced": [combo_obj(c, rank=i+1, tier="balanced") for i, c in enumerate(make_ranked(amd_balanced, "balanced"))],
            "future_ready": [combo_obj(c, rank=i+1, tier="future_ready") for i, c in enumerate(make_ranked(amd_future, "future_ready"))],
            "top3": [combo_obj(c, rank=i+1, tier="top3") for i, c in enumerate(amd_top3)],
            "alternatives": [combo_obj(c, rank=i+1, tier="alternative") for i, c in enumerate(amd_alts)],
        },
        "excluded": excluded,
        "needs_main_agent": {
            "reverify_urls": new_reverify,
            "missing_data": old.get("needs_main_agent", {}).get("missing_data", []),
            "questions": old.get("needs_main_agent", {}).get("questions", []),
        },
        "summary": "",
    }

    summary_parts = []
    summary_parts.append(f"Intel: {len(intel_top3)} основных 4-DIMM рекомендаций; {len(intel_alts)} альтернативы с 2 DIMM/uncertain.")
    summary_parts.append(f"AMD: {len(amd_top3)} основных 4-DIMM рекомендаций; {len(amd_alts)} альтернативы.")
    if not intel_balanced_4dimm:
        summary_parts.append("Intel balanced пуст для 4-DIMM; использованы 2-DIMM варианты с предупреждением.")
    result["summary"] = " ".join(summary_parts)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Wrote {out_path}")
    print(f"Intel combos total: {len(intel_combos)}, top3: {len(intel_top3)}, alts: {len(intel_alts)}")
    print(f"AMD combos total: {len(amd_combos)}, top3: {len(amd_top3)}, alts: {len(amd_alts)}")
    print("Reverify URLs:", new_reverify)


if __name__ == "__main__":
    main()
