"""
Build final markdown/JSON/CSV report from kit-analyzer shortlist.

Input: scripts/_kit_shortlist.json
Output: reports/YYYY-MM-DD HHMM — intel+amd ddr4 upgrade — подбор.{md,json,csv}
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORTLIST = os.path.join(ROOT, "scripts", "_kit_shortlist.json")
OUT_DIR = os.path.join(ROOT, "reports")


def fmt_price(p):
    return f"{int(p)} BYN" if p is not None else "—"


def mb_link(c):
    mb = c["motherboard"]
    return f"[{mb['title']}]({mb['url']})"


def cpu_link(c):
    cpu = c["cpu"]
    return f"[{cpu['title']}]({cpu['url']})"


def tier_label(tier):
    return {
        "entry_upgrade": "Бюджетный апгрейд",
        "balanced": "Оптимальный perf/price",
        "future_ready": "Мощный с запасом",
    }.get(tier, tier)


def write_csv(rows, path):
    fieldnames = [
        "platform", "tier", "rank", "kit_price_byn", "mb_title", "mb_price_byn",
        "mb_url", "mb_seller", "mb_condition", "cpu_title", "cpu_price_byn",
        "cpu_url", "cpu_seller", "cpu_condition", "cpu_perf", "compatibility", "notes",
    ]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "platform": r["platform"],
                "tier": tier_label(r["tier"]),
                "rank": r["rank"],
                "kit_price_byn": int(r["kit_price_byn"]),
                "mb_title": r["motherboard"]["title"],
                "mb_price_byn": int(r["motherboard"]["price_byn"]),
                "mb_url": r["motherboard"]["url"],
                "mb_seller": r["motherboard"]["seller"],
                "mb_condition": r["motherboard"]["condition"],
                "cpu_title": r["cpu"]["title"],
                "cpu_price_byn": int(r["cpu"]["price_byn"]),
                "cpu_url": r["cpu"]["url"],
                "cpu_seller": r["cpu"]["seller"],
                "cpu_condition": r["cpu"]["condition"],
                "cpu_perf": r["cpu_perf"],
                "compatibility": r["compatibility"],
                "notes": "; ".join(r.get("notes", [])),
            })


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    with open(SHORTLIST, "r", encoding="utf-8") as f:
        data = json.load(f)

    now = dt.datetime.now()
    today = now.strftime("%Y-%m-%d")
    timetag = now.strftime("%H%M")
    base = f"{today} {timetag} — intel+amd ddr4 upgrade — подбор"
    md_path = os.path.join(OUT_DIR, f"{base}.md")
    json_path = os.path.join(OUT_DIR, f"{base}.json")
    csv_path = os.path.join(OUT_DIR, f"{base}.csv")

    # Top picks: one per tier per platform, if available.
    intel_picks = []
    for tier in ("entry_upgrade", "balanced", "future_ready"):
        arr = data.get("intel", {}).get(tier, [])
        if arr:
            intel_picks.append(arr[0])
    amd_picks = []
    for tier in ("entry_upgrade", "balanced", "future_ready"):
        arr = data.get("amd", {}).get(tier, [])
        if arr:
            amd_picks.append(arr[0])

    # CSV rows
    csv_rows = []
    for c in intel_picks:
        c_copy = dict(c)
        c_copy["platform"] = "Intel"
        csv_rows.append(c_copy)
    for c in amd_picks:
        c_copy = dict(c)
        c_copy["platform"] = "AMD"
        csv_rows.append(c_copy)

    md = []
    md.append(f"# Подбор комплектов mb+cpu — {today} {timetag}\n")
    md.append("**Источник:** kufar.by Минск. **Сценарий:** кросс-комбинирование мат. плат и процессоров.\n")
    md.append("**Конфигурация ПК:** Intel Core i7-9750H / MSI B250M Pro-VDH / 48 ГБ DDR4 / NVIDIA GeForce RTX 5060 Ti.\n")
    md.append("**Фильтры:** DDR4 only, PCI-E ≥4.0 x16, Intel LGA1700 (B660/B760/Z690/Z790) / AMD AM4 (B550/X570), whitelist брендов мат. плат.\n")
    md.append(f"**Статистика:** Intel — {data.get('_stats', {}).get('total_intel_pairs', 0)} валидных пар, AMD — {data.get('_stats', {}).get('total_amd_pairs', 0)}. Исключено {data.get('_stats', {}).get('total_excluded', 0)} лотов.\n")
    md.append("")

    # Summary
    md.append("## Сводка\n")
    md.append(f"- **Intel:** самый дешёвый валидный комплект — **{fmt_price(data.get('_stats', {}).get('cheapest_intel'))}** (ASRock H610M-HDV + Core i3-13100F), но все доступные Intel DDR4-платы сейчас имеют только **2 слота DIMM**, а у пользователя 4 планки DDR4.\n")
    md.append(f"- **AMD:** самый дешёвый валидный комплект — **{fmt_price(data.get('_stats', {}).get('cheapest_amd'))}** (X570 + Ryzen 5 1600), платы AM4 обычно имеют 4 DIMM-слота, поэтому текущие 48 ГБ DDR4 влезают.\n")
    md.append("- **Рекомендация:** если нужно сохранить все 4 планки DDR4 без дополнительных трат, AMD AM4 выглядит проще; для Intel потребуется либо найти B660/B760/Z690 DDR4 с 4 слотами, либо жертвовать частью ОЗУ/планок.\n")
    md.append("")

    def section(platform, picks):
        md.append(f"## Топ-3 варианта {platform}\n")
        if not picks:
            md.append(f"_Нет валидных комплектов для {platform}._\n")
            return
        md.append("| # | Уровень | Мат. плата | CPU | Сумма | PCI-E | Заметки |")
        md.append("|---|---|---|---|---|---|---|")
        for i, c in enumerate(picks, 1):
            notes_short = "; ".join(c.get("notes", [])).replace("|", " ")[:90]
            pcie_note = "PCIe 4.0 x16"
            if "PCIe 5.0" in notes_short or "5.0" in c["motherboard"]["title"]:
                pcie_note = "PCIe 5.0 x16"
            md.append(
                f"| {i} | {tier_label(c['tier'])} | {mb_link(c)} ({fmt_price(c['motherboard']['price_byn'])}) | "
                f"{cpu_link(c)} ({fmt_price(c['cpu']['price_byn'])}) | **{fmt_price(c['kit_price_byn'])}** | "
                f"{pcie_note} | {notes_short} |"
            )
        md.append("")
        for i, c in enumerate(picks, 1):
            md.append(f"### {platform} #{i} — {tier_label(c['tier'])} — {fmt_price(c['kit_price_byn'])}")
            mb = c["motherboard"]
            cpu = c["cpu"]
            md.append(f"- **Мат. плата:** {mb['title']} — {fmt_price(mb['price_byn'])} — {mb['seller']} ({mb['condition']}) — [ссылка]({mb['url']})")
            md.append(f"- **Процессор:** {cpu['title']} — {fmt_price(cpu['price_byn'])} — {cpu['seller']} ({cpu['condition']}) — [ссылка]({cpu['url']})")
            md.append(f"- **Совместимость:** {c['compatibility']}, CPU perf ≈ {c['cpu_perf']} vs i7-9750H (100)")
            md.append(f"- **Заметки:** {'; '.join(c.get('notes', []))}")
            md.append("")

    section("Intel", intel_picks)
    section("AMD", amd_picks)

    # Special note for Intel 4-DIMM kit
    md.append("## Особый вариант Intel с 4 DIMM-слотами\n")
    md.append("Единственный валидный Intel-лот с 4 DIMM-слотами в текущей выборке — готовый кит **ASRock B660M Pro RS + i5-13400 + 32 ГБ RAM** за **1700 BYN** ([объявление 1073979712](https://www.kufar.by/item/1073979712)).\n")
    md.append("В него входит 32 ГБ RAM; чтобы использовать свои 48 ГБ, придётся продать/заменить комплектную память.\n")
    md.append("")

    # Comparison table
    md.append("## Сравнение Intel vs AMD\n")
    md.append("| Параметр | Intel LGA1700 | AMD AM4 |")
    md.append("|---|---|---|")
    md.append("| Дешевый комплект | 340 BYN (H610 + i3-13100F) | 360 BYN (X570 + R5 1600) |")
    md.append("| PCI-E GPU | 4.0 x16 (Z/B/H серии) / 5.0 x16 на Z690/Z790 | 4.0 x16 |")
    md.append("| DDR4 | Только платы с пометкой DDR4/D4 | Вся платформа DDR4 |")
    md.append("| 4 DIMM-слота в текущей выборке | нет (кроме кита 1700 BYN) | есть |")
    md.append("| Процессоры в топе | 12–14 gen Core | Ryzen 3000/5000 |")
    md.append("| Дальнейший апгрейд | LGA1700 — последнее поколение на DDR4 | AM4 закончился, AM5 = DDR5 |")
    md.append("")

    md.append("## Файлы\n")
    md.append(f"- `{os.path.relpath(json_path, ROOT)}` — структурированная выгрузка (JSON).")
    md.append(f"- `{os.path.relpath(csv_path, ROOT)}` — таблица топ-пар (CSV).")
    md.append(f"- `{os.path.relpath(md_path, ROOT)}` — этот отчёт.")
    md.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # JSON report = full shortlist + report metadata
    report = dict(data)
    report["report_meta"] = {
        "generated_at": now.isoformat(timespec="seconds"),
        "md_path": os.path.relpath(md_path, ROOT),
        "json_path": os.path.relpath(json_path, ROOT),
        "csv_path": os.path.relpath(csv_path, ROOT),
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    write_csv(csv_rows, csv_path)

    print(f"[info] wrote {md_path}")
    print(f"[info] wrote {json_path}")
    print(f"[info] wrote {csv_path}")
    print(f"[info] intel_picks={len(intel_picks)}, amd_picks={len(amd_picks)}")


if __name__ == "__main__":
    main()
