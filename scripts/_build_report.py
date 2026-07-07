"""
Build paired MB+CPU combo report from _candidates.json.

Сценарий: кросс-комбинирование мат. плат и процессоров (стандартный
kufar-upgrade). Топ-3 для каждой платформы по суммарной цене.

Output:
  reports/YYYY-MM-DD HHMM — intel+amd ddr4 upgrade — подбор.md
  reports/YYYY-MM-DD HHMM — intel+amd ddr4 upgrade — подбор.json
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
CANDIDATES = os.path.join(ROOT, "scripts", "_candidates.json")
OUT_DIR = os.path.join(ROOT, "reports")


def price_of(item):
    p = item.get("_price_byn")
    if p is not None:
        return p
    ps = item.get("price", "")
    m = re.search(r"([\d\s]+)", str(ps))
    if m:
        return int(m.group(1).replace(" ", ""))
    return None


def item_url(item):
    return item.get("source_listing", {}).get("url") or f"https://www.kufar.by/item/{item['id']}"


def fmt_price(p):
    return f"{p} BYN" if p is not None else "—"


def seller(item):
    company = item.get("companyName", "") or ""
    uname = item.get("userName", "") or ""
    if company and "Продавец:" in company:
        return company.replace("Продавец: ", "")
    return uname or company or "—"


def condition(item):
    c = (item.get("params") or {}).get("condition", {}).get("vl", "")
    return c or "—"


def chipset_vl(item):
    return (item.get("params") or {}).get("computersComponentChipset", {}).get("vl", "—")


def socket_vl(item):
    return (item.get("params") or {}).get("computersComponentSocket", {}).get("vl", "—")


def is_defect(item):
    blob = f"{(item.get('title') or '').lower()} {(item.get('body') or '').lower()}"
    if "одноканал" in blob:
        return True
    return False


def main():
    with open(CANDIDATES, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Raw listings for stats (counts per category, including any "mb_2" etc.)
    listings = json.load(open(os.path.join(ROOT, "scripts", "_out.json"), encoding="utf-8"))
    mb_visible = sum(len(v) for k, v in listings.items() if k == "mb" or k.startswith("mb_") or k.startswith("mb-"))
    cpu_visible = sum(len(v) for k, v in listings.items() if k == "cpu" or k.startswith("cpu_") or k.startswith("cpu-"))

    intel_mb = data.get("intel_mb", [])
    amd_mb = data.get("amd_mb", [])
    intel_cpus = data.get("intel_cpus", [])
    amd_cpus = data.get("amd_cpus", [])

    # Mark defective CPUs
    for cpu in intel_cpus + amd_cpus:
        cpu["_manual_defect"] = is_defect(cpu)

    # Build combos
    combos = {"intel": [], "amd": []}

    for mb in intel_mb:
        mb_price = price_of(mb)
        for cpu in intel_cpus:
            if cpu.get("_manual_defect"):
                continue
            cpu_price = price_of(cpu)
            total = (mb_price or 0) + (cpu_price or 0)
            combos["intel"].append({
                "mb_id": mb["id"],
                "mb_title": mb.get("title", ""),
                "mb_price": mb_price,
                "mb_url": item_url(mb),
                "mb_seller": seller(mb),
                "mb_condition": condition(mb),
                "mb_chipset": mb["_class"]["chipset"],
                "mb_brand": mb["_class"].get("brand", "—"),
                "mb_pcie_5": mb["_class"]["pcie_5"],
                "cpu_id": cpu["id"],
                "cpu_title": cpu.get("title", ""),
                "cpu_price": cpu_price,
                "cpu_url": item_url(cpu),
                "cpu_seller": seller(cpu),
                "cpu_condition": condition(cpu),
                "total": total,
            })

    for mb in amd_mb:
        mb_price = price_of(mb)
        for cpu in amd_cpus:
            if cpu.get("_manual_defect"):
                continue
            cpu_price = price_of(cpu)
            total = (mb_price or 0) + (cpu_price or 0)
            combos["amd"].append({
                "mb_id": mb["id"],
                "mb_title": mb.get("title", ""),
                "mb_price": mb_price,
                "mb_url": item_url(mb),
                "mb_seller": seller(mb),
                "mb_condition": condition(mb),
                "mb_chipset": mb["_class"]["chipset"],
                "mb_brand": mb["_class"].get("brand", "—"),
                "mb_pcie_5": mb["_class"]["pcie_5"],
                "cpu_id": cpu["id"],
                "cpu_title": cpu.get("title", ""),
                "cpu_price": cpu_price,
                "cpu_url": item_url(cpu),
                "cpu_seller": seller(cpu),
                "cpu_condition": condition(cpu),
                "cpu_ryzen": cpu.get("_ryzen_tier", ""),
                "total": total,
            })

    combos["intel"].sort(key=lambda c: c["total"])
    combos["amd"].sort(key=lambda c: c["total"])

    # Build kit entries shaped like combos (one price row, no separate CPU).
    def _kit_row(platform: str, mb: dict, ryzen_marker: str = "") -> dict:
        p = price_of(mb)
        return {
            "mb_id": mb["id"],
            "mb_title": mb.get("title", ""),
            "mb_price": p,
            "mb_url": item_url(mb),
            "mb_seller": seller(mb),
            "mb_condition": condition(mb),
            "mb_chipset": mb["_class"]["chipset"],
            "mb_brand": mb["_class"].get("brand", "—"),
            "mb_pcie_5": mb["_class"]["pcie_5"],
            "cpu_id": None,
            "cpu_title": "(в составе комплекта)",
            "cpu_price": None,
            "cpu_url": None,
            "cpu_seller": None,
            "cpu_condition": None,
            "cpu_ryzen": "",
            "total": p,
            "source": "kit",
            "platform": platform,
        }

    intel_kit_rows = [_kit_row("Intel", k) for k in data.get("intel_mb_kit", []) if price_of(k) is not None]
    amd_kit_rows = [_kit_row("AMD", k) for k in data.get("amd_mb_kit", []) if price_of(k) is not None]
    for r in combos["intel"]:
        r["source"] = "cross"
        r["platform"] = "Intel"
    for r in combos["amd"]:
        r["source"] = "cross"
        r["platform"] = "AMD"

    # Per-platform top-3: cross-combos + kits, ranked by total price.
    intel_pool = sorted(combos["intel"] + intel_kit_rows, key=lambda c: c["total"] or 1 << 30)
    amd_pool = sorted(combos["amd"] + amd_kit_rows, key=lambda c: c["total"] or 1 << 30)
    intel_top = intel_pool[:3]
    amd_top = amd_pool[:3]
    # Keep the unsorted kit lists around for the JSON "kits" section.
    intel_kits = data.get("intel_mb_kit", [])
    amd_kits = data.get("amd_mb_kit", [])
    intel_kits_sorted = sorted(intel_kits, key=lambda m: price_of(m) if price_of(m) is not None else 1 << 30)
    amd_kits_sorted = sorted(amd_kits, key=lambda m: price_of(m) if price_of(m) is not None else 1 << 30)

    # === File naming ===
    now = dt.datetime.now()
    today = now.strftime("%Y-%m-%d")
    timetag = now.strftime("%H%M")
    base = f"{today} {timetag} — intel+amd ddr4 upgrade — подбор"
    md_path = os.path.join(OUT_DIR, f"{base}.md")
    json_path = os.path.join(OUT_DIR, f"{base}.json")

    # === JSON ===
    report = {
        "datetime": now.isoformat(timespec="seconds"),
        "scenario": "intel+amd ddr4 upgrade (mb+cpu кросс-комбинирование)",
        "platforms": {
            "intel": {"mb_count": len(intel_mb), "cpu_count": len(intel_cpus),
                      "combos_total": len(combos["intel"]), "top": intel_top,
                      "kits": [
                          {"id": k["id"], "title": k.get("title"),
                           "price": price_of(k), "url": item_url(k),
                           "chipset": k["_class"]["chipset"],
                           "brand": k["_class"].get("brand"),
                           "pcie_5": k["_class"]["pcie_5"],
                           "seller": seller(k), "condition": condition(k)}
                          for k in intel_kits_sorted
                      ]},
            "amd": {"mb_count": len(amd_mb), "cpu_count": len(amd_cpus),
                    "combos_total": len(combos["amd"]), "top": amd_top,
                    "kits": [
                        {"id": k["id"], "title": k.get("title"),
                         "price": price_of(k), "url": item_url(k),
                         "chipset": k["_class"]["chipset"],
                         "brand": k["_class"].get("brand"),
                         "pcie_5": k["_class"]["pcie_5"],
                         "seller": seller(k), "condition": condition(k)}
                        for k in amd_kits_sorted
                    ]},
        },
        "excluded": {
            "defect_mb": data.get("skipped_defect_mb", []),
            "defect_cpu": data.get("skipped_defect_cpu", []),
            "kit_cpus_skipped": data.get("skipped_kit_cpus", []),
            "defect_cpu_manual": [c for c in intel_cpus + amd_cpus if c.get("_manual_defect")],
        }
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # === Markdown ===
    md = []
    md.append(f"# Подбор комплектов mb+cpu — {today} {timetag}\n")
    md.append("**Источник:** kufar.by Минск. **Сценарий:** кросс-комбинирование мат. плат и процессоров.\n")
    md.append("**Фильтры kufar (мат. платы):** Intel `ccch=32,31,75,55,74,54,53` · AMD `ccch=21,11`. "
              "Процессоры: вся категория `processory`, потом отбор по сокету.\n")
    md.append(f"**Прогон:** parse (3 URL: Intel MB / AMD MB / CPU) → details → filter → report. "
              f"Всего в выдаче: MB={mb_visible}, CPU={cpu_visible}. "
              f"После фильтра: intel_mb={len(intel_mb)} (defect={len(data.get('skipped_defect_mb', []))} "
              f"для всех mb), amd_mb={len(amd_mb)}, intel_cpus={len(intel_cpus)} "
              f"(defect={len(data.get('skipped_defect_cpu', []))}), amd_cpus={len(amd_cpus)}.\n")
    md.append("**Лоты с ценой «договорная» исключены** (нет числовой цены — невозможно ранжировать/суммировать).\n")
    md.append("")

    def section_intel():
        md.append("## Intel LGA1700 — топ-3 комплекта (mb+cpu, кросс-комбинирование + готовые kits)\n")
        if not intel_top:
            md.append("_Нет данных для Intel._\n")
        else:
            md.append("| # | Источник | Мат. плата (чипсет, цена) | Процессор (цена) | Сумма | Ссылка |")
            md.append("|---|---|---|---|---|---|")
            for i, c in enumerate(intel_top, 1):
                src = "🧩 kit" if c["source"] == "kit" else "🔀 cross"
                mb_link = f"[{c['mb_title'][:30]}]({c['mb_url']})"
                if c["source"] == "kit":
                    cpu_cell = "(в составе комплекта)"
                    cpu_link = f"[{c['mb_title'][:30]}]({c['mb_url']})"
                else:
                    cpu_link = f"[{c['cpu_title'][:30]}]({c['cpu_url']})"
                    cpu_cell = cpu_link + f" ({fmt_price(c['cpu_price'])})"
                md.append(f"| {i} | {src} | {mb_link} ({c['mb_chipset']}, {fmt_price(c['mb_price'])}) "
                          f"| {cpu_cell} | **{fmt_price(c['total'])}** | mb |")
            md.append("")
            for i, c in enumerate(intel_top, 1):
                tag = "🧩 Kit" if c["source"] == "kit" else "🔀 Cross"
                mb_brand = c.get("mb_brand", "—")
                md.append(f"### Intel #{i} — {fmt_price(c['total'])} ({tag})")
                md.append(f"- **MB:** {c['mb_title']} — {c['mb_chipset']} ({mb_brand}) — {fmt_price(c['mb_price'])} — "
                          f"{c['mb_seller']} ({c['mb_condition']}) — [объявление]({c['mb_url']})")
                if c["source"] == "cross":
                    md.append(f"- **CPU:** {c['cpu_title']} — {fmt_price(c['cpu_price'])} — "
                              f"{c['cpu_seller']} ({c['cpu_condition']}) — [объявление]({c['cpu_url']})")
                md.append(f"- **PCIe 5.0 (mb):** {'да' if c['mb_pcie_5'] else 'нет (4.0)'}")
                md.append("")

    def section_amd():
        md.append("## AMD AM4 — топ-3 комплекта (mb+cpu, кросс-комбинирование + готовые kits)\n")
        if not amd_top:
            md.append("_Нет данных для AMD._\n")
        else:
            md.append("| # | Источник | Мат. плата (чипсет, цена) | Процессор (tier, цена) | Сумма | Ссылка |")
            md.append("|---|---|---|---|---|---|")
            for i, c in enumerate(amd_top, 1):
                src = "🧩 kit" if c["source"] == "kit" else "🔀 cross"
                mb_link = f"[{c['mb_title'][:30]}]({c['mb_url']})"
                if c["source"] == "kit":
                    cpu_cell = "(в составе комплекта)"
                else:
                    cpu_link = f"[{c['cpu_title'][:30]}]({c['cpu_url']})"
                    cpu_cell = f"{cpu_link} (Ryzen {c['cpu_ryzen']}, {fmt_price(c['cpu_price'])})"
                md.append(f"| {i} | {src} | {mb_link} ({c['mb_chipset']}, {fmt_price(c['mb_price'])}) "
                          f"| {cpu_cell} | **{fmt_price(c['total'])}** | mb |")
            md.append("")
            for i, c in enumerate(amd_top, 1):
                tag = "🧩 Kit" if c["source"] == "kit" else "🔀 Cross"
                mb_brand = c.get("mb_brand", "—")
                md.append(f"### AMD #{i} — {fmt_price(c['total'])} ({tag})")
                md.append(f"- **MB:** {c['mb_title']} — {c['mb_chipset']} ({mb_brand}) — {fmt_price(c['mb_price'])} — "
                          f"{c['mb_seller']} ({c['mb_condition']}) — [объявление]({c['mb_url']})")
                if c["source"] == "cross":
                    md.append(f"- **CPU:** {c['cpu_title']} — Ryzen {c['cpu_ryzen']} — "
                              f"{fmt_price(c['cpu_price'])} — {c['cpu_seller']} ({c['cpu_condition']}) — "
                              f"[объявление]({c['cpu_url']})")
                md.append(f"- **PCIe 5.0 (mb):** {'да' if c['mb_pcie_5'] else 'нет (4.0)'}")
                md.append("")

    def section_summary():
        md.append("## Сводка\n")
        all_picks = []
        for c in intel_top:
            all_picks.append(("Intel", c))
        for c in amd_top:
            all_picks.append(("AMD", c))
        all_picks.sort(key=lambda x: (x[1]["total"] is None, x[1]["total"] or 0))
        for i, (label, c) in enumerate(all_picks, 1):
            tag = "kit" if c["source"] == "kit" else "cross"
            if c["source"] == "kit":
                md.append(f"- **{i}.** [{label} · {tag}] {c['mb_title']} = "
                          f"{fmt_price(c['total'])} — [объявление]({c['mb_url']})")
            else:
                md.append(f"- **{i}.** [{label} · {tag}] {c['mb_title']} + {c['cpu_title']} = "
                          f"{fmt_price(c['total'])} — [mb]({c['mb_url']}) / [cpu]({c['cpu_url']})")
        md.append("")

    section_intel()
    section_amd()
    section_summary()

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"[info] wrote {md_path}")
    print(f"[info] wrote {json_path}")
    print(f"[info] intel combos={len(combos['intel'])}, amd combos={len(combos['amd'])}")
    for c in intel_top:
        print(f"  Intel: {c['mb_title'][:50]} + {c['cpu_title'][:30]} = {c['total']} BYN")
    for c in amd_top:
        print(f"  AMD:   {c['mb_title'][:50]} + {c['cpu_title'][:30]} = {c['total']} BYN")


if __name__ == "__main__":
    main()
