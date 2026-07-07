"""
Filter kufar listings under the user's PC-upgrade criteria.

Inputs:
  scripts/_items.json  (from kufar_details.py)
  Report.txt           (current PC config, but only used for context here)

Output:
  scripts/_candidates.json  — two arrays: intel, amd

Criteria (from CLAUDE.md and the user's answers):
  - DDR4 only (DDR5 forbidden)
  - Intel: LGA1700 + chipsets Z690/Z790 (PCI-E 5.0) or B660/H670 (PCI-E 4.0),
    *D4 variants of these boards.
  - AMD: AM4 + chipsets B550/X570 (PCI-E 4.0).
  - Region: Минск (region id 7).
  - Condition: б/у is acceptable (condition=1).
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS_PATH = os.path.join(ROOT, "scripts", "_items.json")
OUT_PATH = os.path.join(ROOT, "scripts", "_candidates.json")

# Targets. Values match Kufar's `computersComponentChipset.vl` strings as
# observed in real data.
INTEL_TARGETS = {
    "sockets": {"LGA1700", "LGA1700*"},
    "chipsets": {
        # PCI-E 5.0
        "Intel Z690", "Intel Z790",
        # PCI-E 4.0
        "Intel B660", "Intel H670", "Intel H610", "Intel B760", "Intel H770",
    },
    "min_pcie": "4.0",
    "preferred_pcie": "5.0",
    "platform": "LGA1700",
}
AMD_TARGETS = {
    "sockets": {"AM4"},
    # AM4 with PCI-E 4.0: B550, X570. B650 = AM5 = DDR5 (excluded).
    # A320/A520/B450 = PCI-E 3.0, do NOT meet user's pcie_4.0 minimum.
    "chipsets": {"AMD B550", "AMD X570"},
    "min_pcie": "4.0",
    "preferred_pcie": "4.0",
    "platform": "AM4",
}

# Motherboards that match these criteria are LGA1700/DDR4 (B660M, H670, Z690
# variants marked "D4" / "DDR4") or AM4 (B550/X570). We rely on adParams' vl
# field to detect, with fallback to title/subject substring match.

DDR4_MARKERS = ("DDR4", " D4", "DDR4 ", "(D4)", "DDR4)")
DUAL_DDR_MARKERS = ("DDR4/DDR5", "DDR5/DDR4")  # exclude these — they are dual boards we should still allow only if DDR4 is one of the supported types. Kufar sometimes lists dual boards under "DDR4" ram_type.

REGION_MINSK = "Минск"

# Recognised motherboard brands. Anything not in this set is treated as
# no-name and excluded from the pick. Whitelist per project-mb-brand-policy:
# ASUS, MSI, Gigabyte, ASRock, Biostar, ECS — noname (Maxsun, Colorful,
# Machinist и т.п.) исключаются.
KNOWN_BRANDS = {"ASUS", "MSI", "Gigabyte", "ASRock", "Biostar", "ECS"}


def get_param(item, key):
    p = (item.get("params") or {}).get(key)
    if not p:
        return None
    return p.get("vl")


def ram_type_is_ddr4(item) -> bool:
    """Authoritative DDR4 check: prefer adParams, fall back to title text."""
    rt = (get_param(item, "computersComponentRamType") or "").strip()
    if rt:
        return "DDR4" in rt and "DDR5" not in rt.replace("DDR4", "")
    blob = " ".join(str(item.get(k) or "") for k in ("title", "subject", "body")).lower()
    if "ddr5" in blob and "ddr4" not in blob:
        return False
    return "ddr4" in blob


def text_says_pcie_5(item) -> bool:
    blob = " ".join(str(item.get(k) or "") for k in ("title", "subject", "body"))
    if re.search(r"pci[\-\s]?e\s*5", blob, re.I):
        return True
    if "pcie 5" in blob.lower():
        return True
    if "gen 5" in blob.lower() or "pcie gen5" in blob.lower():
        return True
    return False


def fix_mojibake_region(region: str) -> str:
    """Try to decode mis-encoded cyrillic in the region field.

    Some ads arrive with cp1251 bytes decoded as latin-1 (or double-encoded
    utf-8). Try common recovery paths.
    """
    if not region:
        return region
    if "Минск" in region:
        return region
    # cp1251 bytes misinterpreted as latin-1 → encode back, decode as cp1251
    for enc in ("cp1251", "cp1252", "latin-1"):
        try:
            decoded = region.encode(enc).decode("cp1251")
            if "Минск" in decoded:
                return decoded
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    # double-encoded utf-8 (cp1251→utf-8 bytes→latin-1)
    try:
        decoded = region.encode("latin-1").decode("utf-8")
        if "Минск" in decoded:
            return decoded
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return region


def classify_mb(item) -> dict | None:
    socket = get_param(item, "computersComponentSocket")
    chipset = get_param(item, "computersComponentChipset")
    brand = get_param(item, "computersComponentBrand")
    ram_type = get_param(item, "computersComponentRamType")
    region = fix_mojibake_region(item.get("region") or "")
    title = item.get("title") or ""
    subject = item.get("subject") or ""

    blob = f"{title} {subject}".lower()

    if REGION_MINSK not in region:
        return None

    is_kit = detect_kit(item)
    pcie_5 = text_says_pcie_5(item)

    # --- Intel LGA1700 ---
    # LGA1700 chipsets: Z790, Z690, B760, B660, H770, H670, H610.
    # These are exclusively LGA1700 — if a title mentions one, it IS LGA1700.
    matched_intel_cs = None
    if chipset and "Intel" in chipset and chipset in INTEL_TARGETS["chipsets"]:
        matched_intel_cs = chipset
    if not matched_intel_cs:
        for cs in INTEL_TARGETS["chipsets"]:
            if cs.split(" ", 1)[1].lower() in blob:
                matched_intel_cs = cs
                break
    is_lga1700 = (
        (socket or "").strip() == "LGA1700"
        or "lga1700" in blob
        or matched_intel_cs is not None
    )
    if is_lga1700:
        if not matched_intel_cs:
            return None  # claimed LGA1700 but no recognised chipset
        # DDR4 gate: must NOT be DDR5-only
        if ram_type and "DDR4" not in str(ram_type) and "DDR5" in str(ram_type):
            return None
        if not ram_type_is_ddr4(item):
            return None
        eff_brand = brand or guess_brand(blob)
        if not eff_brand or eff_brand not in KNOWN_BRANDS:
            return None
        return {
            "platform": "Intel LGA1700",
            "socket": "LGA1700",
            "chipset": matched_intel_cs,
            "brand": eff_brand,
            "pcie_5": pcie_5 or "Z690" in matched_intel_cs or "Z790" in matched_intel_cs,
            "score_chipset": score_intel_chipset(matched_intel_cs),
            "is_kit": is_kit,
        }

    # --- AMD AM4 ---
    if (socket or "").strip() == "AM4" or "am4" in blob:
        # DDR4 gate for AM4 — the whole platform is DDR4, but some ads have no ram_type
        if ram_type and "DDR4" not in str(ram_type) and "DDR5" in str(ram_type):
            return None
        if ram_type and not ram_type_is_ddr4(item):
            return None
        # Only B550 and X570 (PCI-E 4.0). Exclude A320/A520/B450/X470 (PCI-E 3.0).
        if chipset and "AMD" in chipset and chipset in AMD_TARGETS["chipsets"]:
            eff_brand = brand or guess_brand(blob)
            # brand whitelist per project-mb-brand-policy: noname (incl.
            # unknown brand like B550M-PRO GAMING) excluded.
            if not eff_brand or eff_brand not in KNOWN_BRANDS:
                return None
            return {
                "platform": "AMD AM4",
                "socket": "AM4",
                "chipset": chipset,
                "brand": eff_brand,
                "pcie_5": False,
                "score_chipset": score_amd_chipset(chipset),
                "is_kit": is_kit,
            }
        # Chipsets from title (B550, X570) — require brand in whitelist too.
        for cs in AMD_TARGETS["chipsets"]:
            if cs.split(" ", 1)[1].lower() in blob:
                eff_brand = brand or guess_brand(blob)
                if not eff_brand or eff_brand not in KNOWN_BRANDS:
                    return None
                return {
                    "platform": "AMD AM4",
                    "socket": "AM4",
                    "chipset": cs,
                    "brand": eff_brand,
                    "pcie_5": False,
                    "score_chipset": score_amd_chipset(cs),
                    "is_kit": is_kit,
                }
        return None

    return None


def guess_brand(blob_low: str) -> str:
    for b in ("asus", "msi", "gigabyte", "asrock", "biostar", "ecs"):
        if b in blob_low:
            return b.upper()
    return None


# Heuristics: a "kit" ad sells a motherboard+CPU+RAM+cooler in one lot
# (or at least a motherboard+CPU). When `is_kit` is true the report should
# show the lot price as-is, not pair it with a separately-listed CPU.
STRONG_KIT_MARKERS = (
    # Title-level: ad is explicitly framed as a bundle.
    "комплект", "набор", "в сборе",
)
CPU_IN_KIT_MARKERS = (
    # Anything pointing at an actual CPU being part of the lot.
    "процессор", "cpu", "с процессором", "с процом", "+ i", "+ i3", "+ i5", "+ i7",
    "ryzen", "core i", "athlon",
)
NON_KIT_BODY_HINTS = (
    # Phrases that show up in a *motherboard-only* ad: "top mat' pod AM4",
    # "polnyy komplekt (box/docs)", "materinskaya plata + zagolushki" etc.
    # If the body talks about the MB in singular ("мать под", "топовая мать")
    # and never mentions a CPU, it's a stand-alone MB.
    "мать под", "мать +", "материнская плата gigabyte", "материнская плата msi",
    "материнская плата asus", "материнская плата asrock", "материнская плата biostar",
    "материнка ", "мать ", "материнку",
    "коробк", "документ", "заглушк", "полный комплект поставки",
    "комплект поставки",
)


def detect_kit(item) -> bool:
    """Return True if the ad is selling a full bundle (MB+CPU+RAM+cooler).

    Kit detection rules (strict):
      1. title contains STRONG_KIT_MARKERS (комплект / набор / в сборе)
         AND title or body mentions an actual CPU line (процессор / ryzen / i3/i5/i7 / core i / athlon).
         A title with just "комплект" and "DDR4" is NOT a kit.
      2. body explicitly says "плата + процессор" / "материнская плата + процессор"
         (a "+" between two component names).

    Any of the non-kit body hints (e.g. "мать под АМ4", "коробка/документы в комплекте")
    override the kit signal — that's stand-alone-MB language, not bundle language.
    """
    title = (item.get("title") or "").lower()
    body = (item.get("body") or "").lower()
    subject = (item.get("subject") or "").lower()
    blob = f"{title} {subject} {body}"

    has_strong = any(m in title for m in STRONG_KIT_MARKERS) or \
                 any(m in subject for m in STRONG_KIT_MARKERS)
    title_cpu_kit = has_strong and any(
        c in title or c in subject for c in CPU_IN_KIT_MARKERS
    )

    # A title-level "комплект + CPU model" signal is authoritative: the body
    # may still describe the motherboard by name, but the lot is a bundle.
    if title_cpu_kit:
        return True

    # Override: stand-alone-MB language disqualifies kit even if "комплект"
    # appears (e.g. "полный комплект поставки" = box/docs/slots).
    if any(h in blob for h in NON_KIT_BODY_HINTS):
        return False

    if has_strong and any(c in blob for c in CPU_IN_KIT_MARKERS):
        return True

    # Explicit "mb + cpu" composition in the body (e.g. "Материнская плата:
    # ...; Процессор: ..." or "плата + процессор + кулер").
    if ("материнская плата" in blob or "материнка" in blob or "мать" in blob) \
            and "процессор" in blob and ("+" in blob or ";" in blob):
        return True

    # CPU ads titled "Processor X + Motherboard Y" (order can be CPU first).
    # Catches listings like "Процессор i5-7600K + Материнская плаата ASus z270k"
    # where the motherboard brand is present after a "+".
    ts = f"{title} {subject}"
    if "+" in ts:
        has_cpu = any(c in ts for c in CPU_IN_KIT_MARKERS)
        has_mb_brand = any(b in blob for b in ("asus", "gigabyte", "msi", "asrock", "biostar", "ecs"))
        has_mb_word = any(w in blob for w in ("материн", "мать", "mobo", "плата"))
        if has_cpu and has_mb_brand and has_mb_word:
            return True

    return False


def score_intel_chipset(chipset: str) -> int:
    order = ["Intel Z790", "Intel Z690", "Intel H770", "Intel B760",
             "Intel H670", "Intel B660", "Intel H610"]
    try:
        return -order.index(chipset)
    except ValueError:
        return -100


def score_amd_chipset(chipset: str) -> int:
    order = ["AMD X570", "AMD B550", "AMD B450"]
    try:
        return -order.index(chipset)
    except ValueError:
        return -100


def parse_price_byn(price_str) -> int:
    """`price` looks like '160 р.' or '1200 р.' (р. = BYN). Return int BYN.

    Returns None for "договорная" / "negotiable" / empty / non-numeric prices.
    Callers should skip such items (see no_price_skip).
    """
    if not price_str:
        return None
    s = str(price_str).replace("\xa0", " ").strip().lower()
    if not s:
        return None
    # "negotiable" markers — treat as no price (cannot be ranked/summed).
    if any(w in s for w in ("договорн", "договор", "торг", "negotiable", "обмен")):
        return None
    m = re.search(r"([\d\s,\.]+)", s)
    if not m:
        return None
    num = m.group(1).replace(" ", "").replace(",", ".")
    if not num:
        return None
    try:
        return int(float(num))
    except ValueError:
        return None


def amd_cpu_ryzen_tier(cpu: dict) -> int:
    """Return the Ryzen tier (5, 7, 9) or 0 if not a Ryzen 5+.

    Reads the model line from title/subject. Excludes Athlon, FX, Phenom,
    and Ryzen 3.
    """
    blob = " ".join(str(cpu.get(k) or "") for k in ("title", "subject", "body")).lower()
    if "ryzen" not in blob:
        return 0
    m = re.search(r"ryzen\s*(\d)", blob)
    if not m:
        return 0
    try:
        return int(m.group(1))
    except (ValueError, TypeError):
        return 0


def main():
    with open(ITEMS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Exclude items flagged as defect, removed, or without a numeric price.
    intel, amd, skipped_defect, skipped_no_price = [], [], [], []
    intel_kit, amd_kit = [], []
    for mb in data.get("mb", []):
        if mb.get("defect"):
            skipped_defect.append(mb.get("id"))
            continue
        cls = classify_mb(mb)
        if not cls:
            continue
        mb["_class"] = cls
        mb["_price_byn"] = parse_price_byn(mb.get("price"))
        # Skip "negotiable" / no-price lots — can't be ranked or summed.
        if mb["_price_byn"] is None:
            skipped_no_price.append(mb.get("id"))
            continue
        is_kit = cls.get("is_kit", False)
        target = intel if cls["platform"].startswith("Intel") else amd
        target_kit = intel_kit if cls["platform"].startswith("Intel") else amd_kit
        if is_kit:
            target_kit.append(mb)
        else:
            target.append(mb)
    # CPUs
    intel_cpus, amd_cpus, skipped_defect_cpu, skipped_kit, skipped_no_price_cpu = [], [], [], [], []
    for cpu in data.get("cpu", []):
        if cpu.get("defect"):
            skipped_defect_cpu.append(cpu.get("id"))
            continue
        # Skip CPU-lots that are actually full kits (MB+CPU). They're
        # represented in the MB list and pairing them with a separate CPU
        # would double-count.
        if detect_kit(cpu):
            skipped_kit.append(cpu.get("id"))
            continue
        socket = get_param(cpu, "computersComponentSocket")
        region = fix_mojibake_region(cpu.get("region") or "")
        if REGION_MINSK not in region:
            continue
        cpu["_socket"] = socket
        cpu["_price_byn"] = parse_price_byn(cpu.get("price"))
        if cpu["_price_byn"] is None:
            skipped_no_price_cpu.append(cpu.get("id"))
            continue
        if socket == "LGA1700":
            intel_cpus.append(cpu)
        elif socket == "AM4":
            # AMD CPU filter: only Ryzen 5 and above.
            # Kufar adParams do not expose the Ryzen series; we read it from
            # the title/subject via regex. Athlon, FX, Phenom, Ryzen 3 are
            # excluded.
            if amd_cpu_ryzen_tier(cpu) >= 5:
                cpu["_ryzen_tier"] = amd_cpu_ryzen_tier(cpu)
                amd_cpus.append(cpu)
    out = {
        "intel_mb": intel,
        "amd_mb": amd,
        "intel_mb_kit": intel_kit,
        "amd_mb_kit": amd_kit,
        "intel_cpus": intel_cpus,
        "amd_cpus": amd_cpus,
        "skipped_defect_mb": skipped_defect,
        "skipped_defect_cpu": skipped_defect_cpu,
        "skipped_kit_cpus": skipped_kit,
        "skipped_no_price_mb": skipped_no_price,
        "skipped_no_price_cpu": skipped_no_price_cpu,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[info] intel_mb={len(intel)} amd_mb={len(amd)} "
          f"intel_cpus={len(intel_cpus)} amd_cpus={len(amd_cpus)} "
          f"defect_mb={len(skipped_defect)} defect_cpu={len(skipped_defect_cpu)} "
          f"no_price_mb={len(skipped_no_price)} no_price_cpu={len(skipped_no_price_cpu)}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
