import json
import pathlib
import re
from datetime import datetime

ROOT = pathlib.Path('D:/Work/AI/ClaudeCode/research-agent')
ITEMS_PATH = ROOT / 'scripts' / '_items.json'
SEEN_PATH = ROOT / 'scripts' / '.cache' / 'seen_ids.json'
REPORTS_DIR = ROOT / 'reports'

REPORTS_DIR.mkdir(exist_ok=True)

items = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))
seen = json.loads(SEEN_PATH.read_text(encoding='utf-8')) if SEEN_PATH.exists() else {}

MB_BRANDS = {'asus', 'msi', 'gigabyte', 'asrock', 'biostar', 'ecs'}
INTEL_CHIPSETS = {'Intel Z690', 'Intel Z790', 'Intel B660', 'Intel B760', 'Intel H610', 'Intel H670'}
AMD_CHIPSETS = {'AMD B550', 'AMD X570'}

INTEL_PERF = {
    'I3-12100': 38, 'I3-12100F': 35,
    'I3-13100': 45, 'I3-13100F': 42,
    'I5-12400': 65, 'I5-12400F': 65,
    'I5-12600K': 80, 'I5-12600KF': 78,
    'I5-13500': 85,
    'I7-12700': 90, 'I7-12700K': 95, 'I7-12700KF': 93,
    'I7-13700': 100, 'I7-13700F': 105, 'I7-13700K': 110, 'I7-13700KF': 108,
}

AMD_PERF = {
    'Ryzen 5 3500': 45,
    'Ryzen 5 3600': 60, 'Ryzen 5 3600X': 65,
    'Ryzen 5 5600': 80, 'Ryzen 5 5600X': 85,
    'Ryzen 7 3700X': 80,
    'Ryzen 7 5700X': 95,
    'Ryzen 7 5800X': 100,
    'Ryzen 5 5600X3D': 95,
    'Ryzen 7 5700X3D': 105,
    'Ryzen 7 5800X3D': 110,
}


def parse_price(item):
    sl = item.get('source_listing') or {}
    pb = sl.get('price_byn')
    if pb:
        try:
            return int(pb) / 100
        except Exception:
            pass
    pr = item.get('price', '')
    m = re.search(r'([\d\s]+)', pr.replace(' ', ''))
    if m:
        try:
            val = int(m.group(1).replace(' ', ''))
            return val / 100 if 'р' in pr else val
        except Exception:
            pass
    return 0.0


def _norm_cpu_model(s):
    # i5-12400 / i5 12400f / i5-12400F -> i512400f
    return re.sub(r'[\s\-]', '', s.lower())


def mb_is_kit(title, body):
    # Use title primarily; body only for explicit compatibility mentions should not trigger.
    t = title.lower()
    if 'комплект' in t and re.search(r'\b(core\s+i[357]|ryzen\s+[357]|pentium|celeron)\b', t):
        return True
    if re.search(r'\b(i[357]\s*[-]?\s*\d{4,5}[a-z]?)\s*\+\s*.*(b\d{3}|z\d{3}|x\d{3}|h\d{3})', t):
        return True
    if re.search(r'\b(ryzen\s+[357]\s+\d{4}[a-z]?)\s*\+\s*.*(b\d{3}|x\d{3}|a\d{3})', t):
        return True
    if re.search(r'\b(b\d{3}|x\d{3}|z\d{3}|h\d{3}).*\+\s*(процессор|cpu|i[357]|ryzen)', t):
        return True
    return False


def cpu_is_kit(title, body):
    t = title.lower()
    if 'комплект' in t:
        return True
    # ambiguous if more than one distinct CPU model is mentioned in the title
    models = re.findall(r'\b(ryzen\s+[357]\s+\d{4}[a-z]?|i[357]\s*[-]?\s*\d{4,5}[a-z]?)\b', t)
    unique = {_norm_cpu_model(m) for m in models}
    if len(unique) > 1:
        return True
    if re.search(r'\b(i[357]\s*[-]?\s*\d{4,5}[a-z]?|ryzen\s+[357]\s+\d{4}[a-z]?)\b.*[,+]\s*(b\d{3}|x\d{3}|z\d{3}|h\d{3}|a\d{3})', t):
        return True
    if re.search(r'\b(b\d{3}|x\d{3}|z\d{3}|h\d{3}|a\d{3}).*[,+]\s*(i[357]\s*[-]?\s*\d{4,5}[a-z]?|ryzen\s+[357]\s+\d{4}[a-z]?)\b', t):
        return True
    return False


def extract_intel_cpu(text):
    text = text.lower()
    patterns = [
        r'\bintel\s+core\s+i([357])\s+(\d{4,5})([a-z]*)\b',
        r'\bintel\s+i([357])\s*[-]?\s*(\d{4,5})([a-z]*)\b',
        r'\bcore\s+i([357])\s+(\d{4,5})([a-z]*)\b',
        r'\bi([357])\s*[-]?\s*(\d{4,5})([a-z]*)\b',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            series, num, suffix = m.group(1), m.group(2), m.group(3)
            gen = int(num[:2]) if len(num) >= 4 else None
            model = f'i{series}-{num}{suffix}'.upper()
            return model, gen, suffix
    return None, None, None


def extract_amd_cpu(text):
    text = text.lower()
    m = re.search(r'\bryzen\s+(5|7)\s+(\d{4})([a-z]*)\b', text)
    if m:
        series, num, suffix = m.group(1), m.group(2), m.group(3)
        gen = int(num[0])
        model = f'Ryzen {series} {num}{suffix}'
        return model, gen, suffix
    return None, None, None


def condition_label(item):
    if item.get('defect'):
        return 'удовлетворительное (есть дефект)'
    if item.get('defect_marker'):
        return 'удовлетворительное'
    vl = item.get('params', {}).get('condition', {}).get('vl', 'Б/у')
    return 'хорошее' if vl == 'Б/у' else vl


def item_notes(item):
    notes = []
    sid = str(item['id'])
    rec = seen.get(sid)
    if not rec:
        return notes
    if rec.get('removed'):
        notes.append('снято с продажи')
    if rec.get('stale'):
        notes.append('требует перепроверки (stale)')
    if rec.get('no_price'):
        notes.append('договорная цена')
    lp = rec.get('last_price')
    if lp:
        try:
            lp_val = int(lp) / 100
            if abs(lp_val - item['_parsed_price']) > 0.01:
                if item['_parsed_price'] < lp_val:
                    notes.append(f'цена снизилась с {lp_val:.0f} до {item["_parsed_price"]:.0f} р.')
                else:
                    notes.append(f'цена выросла с {lp_val:.0f} до {item["_parsed_price"]:.0f} р.')
        except Exception:
            pass
    return notes


mbs = []
for it in items.get('mb', []):
    if it.get('defect') or it.get('removed') or it.get('no_price') or it.get('noname'):
        continue
    price = parse_price(it)
    if price <= 0:
        continue
    brand = it.get('params', {}).get('computersComponentBrand', {}).get('vl', '')
    if not brand or brand.lower() not in MB_BRANDS:
        continue
    ram = it.get('params', {}).get('computersComponentRamType', {}).get('vl', '')
    if ram != 'DDR4':
        continue
    sock = it.get('params', {}).get('computersComponentSocket', {}).get('vl', '')
    chipset = it.get('params', {}).get('computersComponentChipset', {}).get('vl', '')
    if not sock:
        continue
    if sock not in ('LGA1700', 'AM4'):
        continue
    if sock == 'LGA1700' and chipset not in INTEL_CHIPSETS:
        continue
    if sock == 'AM4' and not (chipset in AMD_CHIPSETS or 'X570' in chipset):
        continue
    if mb_is_kit(it.get('title', ''), it.get('body', '')):
        continue
    it['_parsed_price'] = price
    it['_brand'] = brand
    it['_socket'] = sock
    it['_chipset'] = chipset
    it['_pcie'] = '5.0 x16' if chipset in ('Intel Z690', 'Intel Z790') else '4.0 x16'
    mbs.append(it)

cpus = []
for it in items.get('cpu', []):
    if it.get('defect') or it.get('removed') or it.get('no_price') or it.get('noname'):
        continue
    price = parse_price(it)
    if price <= 0:
        continue
    sock = it.get('params', {}).get('computersComponentSocket', {}).get('vl', '')
    if sock not in ('LGA1700', 'AM4'):
        continue
    if cpu_is_kit(it.get('title', ''), it.get('body', '')):
        continue
    text = it.get('title', '') + ' ' + it.get('body', '')
    if sock == 'LGA1700':
        model, gen, suffix = extract_intel_cpu(text)
        if not model or gen not in (12, 13):
            continue
    else:
        model, gen, suffix = extract_amd_cpu(text)
        if not model or gen not in (3, 5):
            continue
        if suffix.upper().startswith('G'):
            continue
        if 'X3D' in model.upper():
            m_num = re.search(r'\d{4}', model)
            if not m_num or int(m_num.group()) not in (5600, 5700, 5800):
                continue
    it['_parsed_price'] = price
    it['_model'] = model
    it['_gen'] = gen
    it['_socket'] = sock
    cpus.append(it)

pairs = []
for mb in mbs:
    for cpu in cpus:
        if mb['_socket'] != cpu['_socket']:
            continue
        notes = []
        if mb['_socket'] == 'LGA1700':
            if cpu['_gen'] == 13 and mb['_chipset'] in ('Intel H610', 'Intel B660', 'Intel Z690', 'Intel H670'):
                notes.append('для процессора 13-го поколения на этой плате может потребоваться обновление BIOS')
        else:
            if cpu['_gen'] == 5 and 'X570' in mb['_chipset']:
                notes.append('для Ryzen 5000 на X570 убедитесь в версии BIOS')
        total = mb['_parsed_price'] + cpu['_parsed_price']
        perf = INTEL_PERF.get(cpu['_model'].upper(), 50) if mb['_socket'] == 'LGA1700' else AMD_PERF.get(cpu['_model'], 50)
        pairs.append({
            'mb': mb,
            'cpu': cpu,
            'total': total,
            'perf': perf,
            'notes': notes,
        })

pairs.sort(key=lambda p: (p['total'], -p['perf']))

intel_pairs = [p for p in pairs if p['mb']['_socket'] == 'LGA1700']
amd_pairs = [p for p in pairs if p['mb']['_socket'] == 'AM4']


def fmt_item_table(item, kind):
    if kind == 'mb':
        return {
            'позиция': 'Материнская плата',
            'модель': item.get('title', ''),
            'сокет_чипсет': f"{item['_socket']}, {item['_chipset']}",
            'pci_e': item['_pcie'],
            'цена': item['_parsed_price'],
            'продавец': item.get('userName', ''),
            'состояние': condition_label(item),
            'ссылка': item.get('source_listing', {}).get('url', f"https://www.kufar.by/item/{item['id']}"),
            'ad_id': item['id'],
            'заметки': '; '.join(item_notes(item)) if item_notes(item) else '-',
        }
    else:
        return {
            'позиция': 'Процессор',
            'модель': item.get('title', ''),
            'сокет_поколение': f"{item['_socket']}, {item['_model']} (поколение {item['_gen']})",
            'цена': item['_parsed_price'],
            'продавец': item.get('userName', ''),
            'состояние': condition_label(item),
            'ссылка': item.get('source_listing', {}).get('url', f"https://www.kufar.by/item/{item['id']}"),
            'ad_id': item['id'],
            'заметки': '; '.join(item_notes(item)) if item_notes(item) else '-',
        }


def build_top(pairs_list, platform, limit=3):
    top = []
    for idx, p in enumerate(pairs_list[:limit], start=1):
        mb_entry = fmt_item_table(p['mb'], 'mb')
        cpu_entry = fmt_item_table(p['cpu'], 'cpu')
        extra_notes = list(p['notes'])
        top.append({
            'место': idx,
            'платформа': platform,
            'материнская_плата': mb_entry,
            'процессор': cpu_entry,
            'сумма': p['total'],
            'pci_e': p['mb']['_pcie'],
            'заметки': extra_notes,
        })
    return top


top_intel = build_top(intel_pairs, 'Intel', 3)
top_amd = build_top(amd_pairs, 'AMD', 3)

comparison_rows = []
for p in top_intel + top_amd:
    comparison_rows.append({
        'платформа': p['платформа'],
        'комплект': f"{p['материнская_плата']['модель']} + {p['процессор']['модель']}",
        'сокет_чипсет': f"{p['материнская_плата']['сокет_чипсет']}",
        'pci_e': p['pci_e'],
        'сумма': p['сумма'],
        'состояние': f"{p['материнская_плата']['состояние']} / {p['процессор']['состояние']}",
        'ссылки': f"{p['материнская_плата']['ссылка']} , {p['процессор']['ссылка']}",
        'заметки': '; '.join(p['заметки']) if p['заметки'] else '-',
    })

now = datetime.now()
date_str = now.strftime('%Y-%m-%d')
time_str = now.strftime('%H%M')
base_name = f"{date_str} {time_str} — intel+amd ddr4 upgrade — подбор"
md_path = REPORTS_DIR / f"{base_name}.md"
json_path = REPORTS_DIR / f"{base_name}.json"

md_lines = []
md_lines.append('# Подбор комплекта материнская плата + процессор (DDR4) для апгрейда ПК')
md_lines.append('')
md_lines.append('**Дата формирования:** ' + now.strftime('%Y-%m-%d %H:%M'))
md_lines.append('')
md_lines.append('## 1. Краткая сводка')
md_lines.append('')
md_lines.append('- **PCI-E 5.0 x16 в выборке не найден**; все подходящие платы обеспечивают **PCI-E 4.0 x16**, что соответствует допустимому минимуму для RTX 5060 Ti.')
md_lines.append('- В выборке оказалось **2 платы Intel LGA1700** (обе H610) и **6 плат AMD AM4** (B550/X570). Самый доступный Intel-комплект — **H610 + Core i3-13100F** за **340 р.**; для LLM лучше взять **i5-12400F/i5-12600K**, несмотря на переплату.')
md_lines.append('- Самый доступный AMD-комплект — **ASRock B550 + Ryzen 5 3500** за **345 р.**; для локальных моделей предпочтительнее **Ryzen 5 5600 / Ryzen 7 3700X**, которые дают больше ядер/кеша при небольшой доплате.')
md_lines.append('')


def render_top_section(title, top_list):
    md_lines.append(f'## {title}')
    md_lines.append('')
    if not top_list:
        md_lines.append('Подходящих комплектов не найдено.')
        md_lines.append('')
        return
    for entry in top_list:
        md = entry['материнская_плата']
        cd = entry['процессор']
        md_lines.append(f"### {entry['место']}. {md['модель']} + {cd['модель']} — **{entry['сумма']:.0f} р.**")
        md_lines.append('')
        md_lines.append('| Позиция | Модель | Сокет/чипсет/поколение | PCI-E | Цена | Продавец | Состояние | Ссылка |')
        md_lines.append('|---|---|---|---|---|---|---|---|')
        md_lines.append(f"| Мат. плата | {md['модель']} | {md['сокет_чипсет']} | {md['pci_e']} | {md['цена']:.0f} р. | {md['продавец']} | {md['состояние']} | [{md['ad_id']}]({md['ссылка']}) |")
        md_lines.append(f"| Процессор | {cd['модель']} | {cd['сокет_поколение']} | — | {cd['цена']:.0f} р. | {cd['продавец']} | {cd['состояние']} | [{cd['ad_id']}]({cd['ссылка']}) |")
        md_lines.append('')
        notes = []
        if md['заметки'] != '-':
            notes.append(f"Мат. плата: {md['заметки']}")
        if cd['заметки'] != '-':
            notes.append(f"Процессор: {cd['заметки']}")
        notes.extend(entry['заметки'])
        if notes:
            md_lines.append('**Заметки:** ' + ' ; '.join(notes))
        else:
            md_lines.append('**Заметки:** —')
        md_lines.append('')

render_top_section('2. Топ-3 Intel', top_intel)
render_top_section('3. Топ-3 AMD', top_amd)

md_lines.append('## 4. Сравнительная таблица Intel vs AMD')
md_lines.append('')
md_lines.append('| Платформа | Комплект | Сокет/чипсет | PCI-E x16 | Сумма | Состояние | Ссылки | Заметки |')
md_lines.append('|---|---|---|---|---|---|---|---|')
for row in comparison_rows:
    md_lines.append(f"| {row['платформа']} | {row['комплект']} | {row['сокет_чипсет']} | {row['pci_e']} | {row['сумма']:.0f} р. | {row['состояние']} | [плата]({row['ссылки'].split(',')[0].strip()}) / [проц]({row['ссылки'].split(',')[1].strip()}) | {row['заметки']} |")
md_lines.append('')
md_lines.append('## 5. Сохраненные файлы')
md_lines.append('')
md_lines.append(f'- `{md_path.name}`')
md_lines.append(f'- `{json_path.name}`')
md_lines.append('')

md_content = '\n'.join(md_lines)
md_path.write_text(md_content, encoding='utf-8')

report_data = {
    'meta': {
        'generated_at': now.isoformat(),
        'title': 'Подбор комплекта мат. плата + процессор (DDR4) для апгрейда ПК',
        'source_items': str(ITEMS_PATH),
        'source_seen': str(SEEN_PATH),
    },
    'summary': [
        'PCI-E 5.0 x16 в выборке не найден; все подходящие платы обеспечивают PCI-E 4.0 x16, что соответствует допустимому минимуму для RTX 5060 Ti.',
        'В выборке 2 платы Intel LGA1700 (обе H610) и 6 плат AMD AM4 (B550/X570). Самый доступный Intel-комплект — H610 + Core i3-13100F за 340 р.; для LLM лучше i5-12400F/i5-12600K.',
        'Самый доступный AMD-комплект — ASRock B550 + Ryzen 5 3500 за 345 р.; для локальных моделей предпочтительнее Ryzen 5 5600 / Ryzen 7 3700X.',
    ],
    'top3_intel': top_intel,
    'top3_amd': top_amd,
    'comparison': comparison_rows,
    'files': [str(md_path), str(json_path)],
}
json_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding='utf-8')

print('Saved markdown:', md_path)
print('Saved JSON:', json_path)
print('Intel top3 count:', len(top_intel))
print('AMD top3 count:', len(top_amd))
print('Total Intel pairs:', len(intel_pairs))
print('Total AMD pairs:', len(amd_pairs))
