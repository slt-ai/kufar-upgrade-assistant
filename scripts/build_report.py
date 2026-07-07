"""
Combines filtered motherboards and CPUs into the cheapest viable 3-kit
recommendations for each platform (Intel LGA1700, AMD AM4).

Inputs: scripts/_candidates.json
Output: reports/<date>-pc-upgrade-pick.md and reports/<date>-pc-upgrade-pick.json
"""
from __future__ import annotations

import datetime as dt
import itertools
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND_PATH = os.path.join(ROOT, "scripts", "_candidates.json")
REPORTS = os.path.join(ROOT, "reports")


def get_param(item, key):
    p = (item.get("params") or {}).get(key)
    if not p:
        return None
    return p.get("vl")


def is_intel_cpu_compatible(cpu, mb_chipset: str) -> bool:
    # LGA1700 supports 12/13/14 gen Core. We don't have generation in params,
    # but we'll filter out anything older than 12th gen by model name heuristics.
    blob = (cpu.get("title") or "") + " " + (cpu.get("subject") or "")
    blob_low = blob.lower()
    gen = None
    for g in (12, 13, 14):
        if f"i{g}-" in blob_low or f"i{g} " in blob_low or f"core™ {g}" in blob_low:
            gen = g
            break
        if f"{g}th gen" in blob_low or f"{g}-th" in blob_low:
            gen = g
            break
    return gen is not None  # if we can't tell, keep it; chipset filter below


def top_combos(mb_list, cpu_list, k: int = 3, max_price: int = 2000):
    """Return top-k cheapest entries: kit-MB stand alone, bare-MB pair with CPUs.

    A "kit" (MB+CPU+RAM+cooler in one lot) is shown at its own price; we do
    not pair it with another CPU. Bare motherboards are paired with every
    available CPU and sorted by total.
    """
    kits = []
    pairs = []
    for mb in mb_list:
        if (mb.get("_price_byn") or 0) <= 0:
            continue
        if (mb.get("_class") or {}).get("is_kit"):
            kits.append((mb["_price_byn"], mb, None))
            continue
        for cpu in cpu_list:
            total = (mb.get("_price_byn") or 0) + (cpu.get("_price_byn") or 0)
            if total <= 0 or total > max_price:
                continue
            pairs.append((total, mb, cpu))
    pairs.sort(key=lambda x: x[0])
    kits.sort(key=lambda x: x[0])
    # Kits first (cheapest complete build), then bare MB+CPU pairs.
    return (kits + pairs)[:k]


def fmt_row(idx, mb, cpu, total):
    mb_url = (mb.get("source_listing") or {}).get("url") or f"https://www.kufar.by/item/{mb.get('id')}"
    cpu_title = "— (в составе комплекта)" if cpu is None else (cpu.get("title") or cpu.get("subject") or "?")
    cpu_url = "—"
    if cpu is not None:
        cpu_url = (cpu.get("source_listing") or {}).get("url") or f"https://www.kufar.by/item/{cpu.get('id')}"
    mb_title = mb.get("title") or mb.get("subject") or "?"
    mb_chipset = (mb.get("_class") or {}).get("chipset", "—")
    mb_pcie_5 = (mb.get("_class") or {}).get("pcie_5", False)
    mb_price = mb.get("_price_byn")
    cpu_price = "—" if cpu is None else cpu.get("_price_byn")
    mb_region = mb.get("region") or "—"
    kit_tag = ", комплект" if (mb.get("_class") or {}).get("is_kit") else ""
    return (
        f"| {idx} | {mb_title} ({mb_chipset}"
        f"{', PCI-E 5.0' if mb_pcie_5 else ''}{kit_tag}) | "
        f"{mb_price} BYN | [ссылка]({mb_url}) | "
        f"{cpu_title} | {cpu_price} | [ссылка]({cpu_url}) | "
        f"**{total} BYN** | {mb_region} |"
    )


def main():
    with open(CAND_PATH, "r", encoding="utf-8") as f:
        c = json.load(f)

    intel_mb = sorted(c.get("intel_mb", []),
                      key=lambda x: (x.get("_price_byn") or 1_000_000))
    amd_mb = sorted(c.get("amd_mb", []),
                    key=lambda x: (x.get("_price_byn") or 1_000_000))
    intel_cpus = sorted(c.get("intel_cpus", []),
                         key=lambda x: (x.get("_price_byn") or 1_000_000))
    amd_cpus = sorted(c.get("amd_cpus", []),
                       key=lambda x: (x.get("_price_byn") or 1_000_000))

    intel_pairs = top_combos(intel_mb, intel_cpus)
    amd_pairs = top_combos(amd_mb, amd_cpus)

    today = dt.date.today().isoformat()
    out_md = os.path.join(REPORTS, f"{today}-pc-upgrade-pick.md")
    out_json = os.path.join(REPORTS, f"{today}-pc-upgrade-pick.json")
    os.makedirs(REPORTS, exist_ok=True)

    # JSON dump (for tooling)
    out_json_data = {
        "date": today,
        "intel": [{"mb": p[1], "cpu": p[2], "total_byn": p[0]} for p in intel_pairs],
        "amd": [{"mb": p[1], "cpu": p[2], "total_byn": p[0]} for p in amd_pairs],
        "intel_mb_count": len(intel_mb),
        "amd_mb_count": len(amd_mb),
        "intel_cpu_count": len(intel_cpus),
        "amd_cpu_count": len(amd_cpus),
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out_json_data, f, ensure_ascii=False, indent=2)

    md = []
    md.append("# Подбор комплекта (мат. плата + процессор) под RTX 5060 Ti")
    md.append("")
    md.append(f"Дата: {today}. Регион поиска: Минск. Источник: kufar.by, раздел б/у.")
    md.append("")
    md.append("## Что искали")
    md.append("")
    md.append("- Платформа с поддержкой PCI-E 4.0/5.0 x16 (цель — вывести RTX 5060 Ti на полную пропускную способность).")
    md.append("- Только DDR4 (текущие 48 ГБ DDR4 остаются).")
    md.append("- Intel: LGA1700 (B660/H670/Z690/Z790, варианты с пометкой D4/DDR4).")
    md.append("- AMD: AM4 (B550/X570), DDR4. AM5 исключён (DDR5, противоречит запрету).")
    md.append("")
    md.append(f"Собрано: плат Intel LGA1700 — {len(intel_mb)}, плат AM4 — {len(amd_mb)}, "
              f"CPU LGA1700 — {len(intel_cpus)}, CPU AM4 — {len(amd_cpus)}.")
    md.append("")
    md.append("## Топ-3 комплекта Intel (LGA1700, DDR4)")
    md.append("")
    if intel_pairs:
        md.append("| # | Мат. плата | Цена платы, BYN | Ссылка (плата) | Процессор | Цена CPU, BYN | Ссылка (CPU) | Сумма, BYN | Регион |")
        md.append("|---|------------|-----------------|----------------|-----------|---------------|--------------|------------|--------|")
        for i, (total, mb, cpu) in enumerate(intel_pairs, 1):
            md.append(fmt_row(i, mb, cpu, total))
    else:
        md.append("_Не найдено ни одной комбинации в пределах бюджета. См. сводку ниже._")
    md.append("")
    md.append("## Топ-3 комплекта AMD (AM4, DDR4)")
    md.append("")
    if amd_pairs:
        md.append("| # | Мат. плата | Цена платы, BYN | Ссылка (плата) | Процессор | Цена CPU, BYN | Ссылка (CPU) | Сумма, BYN | Регион |")
        md.append("|---|------------|-----------------|----------------|-----------|---------------|--------------|------------|--------|")
        for i, (total, mb, cpu) in enumerate(amd_pairs, 1):
            md.append(fmt_row(i, mb, cpu, total))
    else:
        md.append("_Не найдено ни одной комбинации._")
    md.append("")
    md.append("## Сравнение Intel vs AMD")
    md.append("")
    md.append("| Параметр | Intel LGA1700 | AMD AM4 |")
    md.append("|----------|---------------|---------|")
    md.append("| Макс. PCI-E | 5.0 (Z690/Z790) или 4.0 (B660/H670) | 4.0 (B550/X570) |")
    md.append("| Совместимость с DDR4 | Только платы с пометкой D4/DDR4 | Вся платформа |")
    md.append("| Дальнейший апгрейд | LGA1851 (новый сокет) → нужна новая плата | AM4 закончился (AM5 = DDR5) |")
    md.append("| Плат найдено | " + str(len(intel_mb)) + " | " + str(len(amd_mb)) + " |")
    md.append("| CPU найдено | " + str(len(intel_cpus)) + " | " + str(len(amd_cpus)) + " |")
    md.append("")
    md.append("## Сводка")
    md.append("")
    if intel_pairs:
        best_intel = intel_pairs[0]
        mb_t = best_intel[1].get("title") or best_intel[1].get("subject")
        if best_intel[2] is None:
            md.append(f"- Лучший комплект Intel: **{best_intel[0]} BYN** ({mb_t} — готовый набор).")
        else:
            cpu_t = best_intel[2].get("title") or best_intel[2].get("subject")
            md.append(f"- Лучший комплект Intel: **{best_intel[0]} BYN** ({mb_t} + {cpu_t}).")
    else:
        md.append("- Intel-комплект в пределах бюджета не собран: либо мало LGA1700-плат на kufar, либо цены выше ожидания. Стоит расширить бюджет или смотреть вручную.")
    if amd_pairs:
        best_amd = amd_pairs[0]
        mb_t = best_amd[1].get("title") or best_amd[1].get("subject")
        if best_amd[2] is None:
            md.append(f"- Лучший комплект AMD: **{best_amd[0]} BYN** ({mb_t} — готовый набор).")
        else:
            cpu_t = best_amd[2].get("title") or best_amd[2].get("subject")
            md.append(f"- Лучший комплект AMD: **{best_amd[0]} BYN** ({mb_t} + {cpu_t}).")
    else:
        md.append("- AMD-комплект не собран: AM4/ DDR4 на kufar встречается редко или выходит за бюджет.")
    md.append("- Конкретную рекомендацию Intel vs AMD дать не берусь: оба варианта улучшают ситуацию с PCI-E; выбор зависит от цены и того, какие платы/CPU окажутся в реально хорошем состоянии.")
    md.append("")
    md.append("## Файлы")
    md.append("")
    md.append(f"- `{os.path.relpath(out_json, ROOT)}` — структурированная выгрузка (JSON).")
    md.append(f"- `{os.path.relpath(out_md, ROOT)}` — этот отчёт.")
    md.append(f"- `scripts/_items.json` — сырые данные по объявлениям (43 платы + 43 CPU).")
    md.append("")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"[info] wrote {out_md}", file=sys.stderr)
    print(f"[info] wrote {out_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
