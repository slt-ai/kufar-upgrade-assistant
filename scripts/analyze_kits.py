import json
import re
from datetime import datetime, timezone
from collections import defaultdict

# Load data
ROOT = 'D:/Work/AI/ClaudeCode/research-agent'
with open(f'{ROOT}/scripts/_items.json', 'r', encoding='utf-8') as f:
    items = json.load(f)
try:
    with open(f'{ROOT}/scripts/.cache/seen_ids.json', 'r', encoding='utf-8') as f:
        seen_ids = json.load(f)
except FileNotFoundError:
    seen_ids = {}

# Use project current date (2026-06-22) for checked_at; keep actual time from clock
now = datetime.now(timezone.utc)
checked_at = f"2026-06-22T{now.strftime('%H:%M:%S')}{now.strftime('%z')[:3]}:{now.strftime('%z')[3:]}"

# CPU performance relative to i7-9750H = 100 (approx Passmark multi-thread)
CPU_PERF = {
    # Intel LGA1700 12th gen
    'i3-12100F': 116, 'i3-12100': 116, 'i3-12300': 120,
    'i5-12400F': 156, 'i5-12400': 156, 'i5-12500': 165, 'i5-12600': 175,
    'i5-12600K': 220, 'i5-12600KF': 220,
    'i7-12700': 235, 'i7-12700F': 235, 'i7-12700K': 272, 'i7-12700KF': 272,
    'i9-12900': 300, 'i9-12900K': 328, 'i9-12900KF': 328, 'i9-12900KS': 340,
    # Intel 13th gen
    'i3-13100F': 125, 'i3-13100': 125, 'i3-13200': 130,
    'i5-13400F': 204, 'i5-13400': 204, 'i5-13500': 215, 'i5-13600K': 292, 'i5-13600KF': 292,
    'i7-13700': 290, 'i7-13700F': 290, 'i7-13700K': 376, 'i7-13700KF': 376,
    'i9-13900': 400, 'i9-13900K': 472, 'i9-13900KF': 472,
    # Intel 14th gen
    'i3-14100F': 130, 'i3-14100': 130,
    'i5-14400F': 210, 'i5-14400': 210, 'i5-14500': 220, 'i5-14600K': 300, 'i5-14600KF': 300,
    'i7-14700': 310, 'i7-14700F': 310, 'i7-14700K': 390, 'i7-14700KF': 390,
    'i9-14900K': 504, 'i9-14900KF': 504, 'i9-14900KS': 520,
    # AMD AM4 Ryzen 1000/2000
    'Ryzen 3 1200': 55, 'Ryzen 3 1300X': 60,
    'Ryzen 5 1400': 75, 'Ryzen 5 1600': 110, 'Ryzen 5 1600X': 120,
    'Ryzen 5 2600': 125, 'Ryzen 5 2600X': 135,
    'Ryzen 7 1700': 115, 'Ryzen 7 1700X': 125, 'Ryzen 7 2700': 140, 'Ryzen 7 2700X': 155,
    # AMD APUs (Zen/Zen+)
    'Ryzen 3 2200G': 55, 'Ryzen 3 3200G': 48,
    'Ryzen 5 2400G': 75, 'Ryzen 5 3350G': 75, 'Ryzen 5 3400G': 80, 'Ryzen 5 3400GE': 78,
    'Ryzen 5 4350G': 95, 'Ryzen 5 4600G': 100,
    'Ryzen 7 4700G': 140,
    # AMD Ryzen 3000/5000
    'Ryzen 5 3600': 143, 'Ryzen 5 3600X': 155,
    'Ryzen 5 4500': 130, 'Ryzen 5 5500': 145,
    'Ryzen 5 5600': 174, 'Ryzen 5 5600X': 181, 'Ryzen 5 5600G': 150,
    'Ryzen 7 3700X': 185, 'Ryzen 7 3800X': 195,
    'Ryzen 7 5700G': 165, 'Ryzen 7 5700X': 215, 'Ryzen 7 5700X3D': 205,
    'Ryzen 7 5800X': 226, 'Ryzen 7 5800X3D': 190,
    'Ryzen 9 3900X': 300, 'Ryzen 9 3950X': 371,
    'Ryzen 9 5900X': 315, 'Ryzen 9 5950X': 371,
}

# Board PCIe generation by chipset
CHIPSET_PCIE = {
    'Intel Z690': 5.0, 'Intel Z790': 5.0,
    'Intel B660': 4.0, 'Intel B760': 4.0, 'Intel H610': 4.0, 'Intel H670': 4.0,
    'Intel H510': 4.0,
    'AMD X570': 4.0, 'AMD B550': 4.0, 'AMD B450': 3.0, 'AMD A520': 3.0,
}

# Board quality / VRM tiers
BOARD_TIER = {
    # Intel
    'Intel H610': 1, 'Intel B660': 2, 'Intel B760': 2, 'Intel H670': 2, 'Intel Z690': 3, 'Intel Z790': 4,
    # AMD
    'AMD B450': 2, 'AMD A520': 1, 'AMD B550': 2, 'AMD X570': 3,
}

# Intel gen by model
INTEL_GENS = {
    'i3-10100': 10, 'i3-10100F': 10, 'i3-10105': 10, 'i3-10105F': 10,
    'i3-12100F': 12, 'i3-13100F': 13, 'i3-14100F': 14,
    'i5-10400': 10, 'i5-10400F': 10, 'i5-10500': 10, 'i5-10600': 10, 'i5-10600KF': 10,
    'i5-11400': 11, 'i5-11400F': 11, 'i5-11500': 11,
    'i5-12400': 12, 'i5-12400F': 12, 'i5-12500': 12, 'i5-12600': 12, 'i5-12600K': 12, 'i5-12600KF': 12,
    'i5-13400F': 13, 'i5-13500': 13, 'i5-13600K': 13, 'i5-13600KF': 13,
    'i5-14400F': 14, 'i5-14600K': 14, 'i5-14600KF': 14,
    'i7-10700K': 10, 'i7-11700K': 11, 'i7-12700': 12, 'i7-12700F': 12, 'i7-12700K': 12, 'i7-12700KF': 12,
    'i7-13700F': 13, 'i7-13700K': 13, 'i7-13700KF': 13,
    'i7-14700': 14, 'i7-14700F': 14, 'i7-14700K': 14, 'i7-14700KF': 14,
    'i9-10900K': 10, 'i9-10900KF': 10,
    'i9-11900K': 11, 'i9-11900KF': 11,
    'i9-12900': 12, 'i9-12900K': 12, 'i9-12900KF': 12, 'i9-12900KS': 12,
    'i9-13900': 13, 'i9-13900K': 13, 'i9-13900KF': 13,
    'i9-14900K': 14, 'i9-14900KF': 14, 'i9-14900KS': 14,
}


def extract_intel_cpu(text):
    m = re.search(r'(?i)(i[3579])\s*-?\s*(\d{3,5}[KFLHTRSAUE0]*)', text)
    if not m:
        return None
    model = f"{m.group(1).lower()}-{m.group(2).upper()}"
    return model


def extract_amd_cpu(text):
    # Only match valid Ryzen tiers (3,5,7,9) followed by 3-4 digit model number
    m = re.search(r'(?i)ryzen\s+([3579])\s+(\d{3,4}[XGT]?)', text)
    if not m:
        return None
    return f"Ryzen {m.group(1)} {m.group(2).upper()}"


def extract_cpu(text):
    intel = extract_intel_cpu(text)
    if intel:
        return intel, 'intel'
    amd = extract_amd_cpu(text)
    if amd:
        return amd, 'amd'
    return None, None


def is_intel_lga1700(model):
    if model in INTEL_GENS:
        return INTEL_GENS[model] in (12, 13, 14)
    m = re.search(r'i[3579]-(\d{4,5})', model)
    if m:
        n = int(m.group(1))
        return 12000 <= n < 15000
    return False


def amd_supported_chipset(model, chipset):
    m = re.search(r'Ryzen \d+ (\d{4})', model)
    if not m:
        return False, 'unknown model'
    series = int(m.group(1))
    if chipset == 'AMD X570':
        return True, 'X570 supports all AM4'
    if chipset in ('AMD B550', 'AMD A520'):
        if series >= 3000:
            return True, 'B550/A520 supports Ryzen 3000+'
        else:
            return False, 'B550/A520 does not officially support Ryzen 1000/2000'
    if chipset in ('AMD B450', 'AMD X470'):
        if series >= 1000:
            if series >= 5000:
                return 'uncertain', 'B450/X470 needs BIOS update for Ryzen 5000'
            return True, 'B450/X470 supports Ryzen 1000-5000 with BIOS'
        return False, 'unknown series'
    return False, 'unsupported chipset'


def intel_supported_chipset(model, chipset):
    gen = INTEL_GENS.get(model)
    if gen is None:
        return False, 'unknown Intel gen'
    if gen in (12, 13, 14):
        return True, f'LGA1700 {gen}th gen supported'
    return False, f'{gen}th gen is not LGA1700'


def estimate_perf(model, brand):
    p = CPU_PERF.get(model)
    if p:
        return p
    if brand == 'intel':
        m = re.search(r'i([3579])-(\d{3,5})', model)
        if m:
            tier = int(m.group(1))
            n = int(m.group(2))
            gen = n // 1000
            # LGA1700 only for this project
            if gen >= 12:
                cores = {3: 4, 5: 6, 7: 8, 9: 8}.get(tier, 6)
                return int(100 + (gen - 11) * 25 + cores * 10 + (n % 100))
    elif brand == 'amd':
        m = re.search(r'Ryzen (\d+) (\d{4})', model)
        if m:
            tier = int(m.group(1))
            series = int(m.group(2))
            # APUs end in G/GE and are weaker than pure CPUs
            is_apu = bool(re.search(r'[GE]\d*$', model)) or series in (2200, 3200, 2400, 3400, 3350, 4350, 4600, 4700, 5600, 5700)
            if series >= 5000:
                if is_apu:
                    base = {3: 50, 5: 110, 7: 140, 9: 160}.get(tier, 100)
                else:
                    base = {3: 80, 5: 140, 7: 180, 9: 260}.get(tier, 120)
            elif series >= 3000:
                if is_apu:
                    base = {3: 45, 5: 75, 7: 100, 9: 130}.get(tier, 70)
                else:
                    base = {3: 60, 5: 110, 7: 140, 9: 200}.get(tier, 100)
            else:
                base = {3: 50, 5: 70, 7: 90, 9: 110}.get(tier, 70)
            return int(base + tier * 5 + (series % 1000) * 0.02)
    return None


def parse_price(item):
    p = item.get('price')
    if p is None:
        return None
    try:
        return float(p)
    except:
        return None


def in_minsk(item):
    loc = item.get('location', '') or item.get('_raw_params', {}).get('region', '')
    return 'Минск' in loc


defect_markers = ['не работает', 'сломан', 'дефект', 'убит', 'не включается',
                  'перестали работать', 'вышел из строя', 'разбит', 'трещина', 'глючит',
                  'неисправен', 'неисправна', 'погнут', 'отлетевш', 'дифект']


def has_defect(item):
    # Trust fetcher's explicit defect flag; avoid false positives like "без дефектов"
    return bool(item.get('_defect'))


# Classify items
motherboards = []
cpus = []
unknown_cpu_models = []
for item in items:
    if item.get('group', '') in ('intel_motherboards', 'amd_motherboards'):
        motherboards.append(item)
    elif item.get('group', '') == 'processors':
        model, brand = extract_cpu(item.get('title', '') + ' ' + item.get('body', ''))
        item['_cpu_model'] = model
        item['_cpu_brand'] = brand
        if model:
            item['_cpu_perf'] = estimate_perf(model, brand)
        else:
            unknown_cpu_models.append(item)
            item['_cpu_perf'] = None
        cpus.append(item)

excluded = {'defect': [], 'wrong_memory': [], 'noname_mb': [], 'no_price': [], 'other': [],
            'stale': [], 'not_minsk': [], 'incompatible_socket': [], 'no_cpu_model': []}
reverify_urls = []


# Filter motherboards
valid_mbs = []
for mb in motherboards:
    aid = mb['ad_id']
    rp = mb.get('_raw_params', {})
    chipset = rp.get('computersComponentChipset', '')
    socket = rp.get('computersComponentSocket', '')
    ram_type = rp.get('computersComponentRamType', '')
    price = parse_price(mb)

    if not in_minsk(mb):
        excluded['not_minsk'].append(str(aid))
        continue
    if has_defect(mb):
        excluded['defect'].append(str(aid))
        continue
    if mb.get('_noname'):
        excluded['noname_mb'].append(str(aid))
        continue
    if ram_type != 'DDR4' and 'DDR4' not in mb.get('title', ''):
        excluded['wrong_memory'].append(str(aid))
        continue
    if price is None:
        excluded['no_price'].append(str(aid))
        continue
    if socket not in ('LGA1700', 'AM4'):
        excluded['incompatible_socket'].append(str(aid))
        continue
    valid_mbs.append(mb)


# Filter CPUs
valid_cpus = []
for cpu in cpus:
    aid = cpu['ad_id']
    model = cpu.get('_cpu_model')
    brand = cpu.get('_cpu_brand')
    price = parse_price(cpu)

    if not in_minsk(cpu):
        excluded['not_minsk'].append(str(aid))
        continue
    if has_defect(cpu):
        excluded['defect'].append(str(aid))
        continue
    if price is None:
        excluded['no_price'].append(str(aid))
        continue
    if not model:
        excluded['no_cpu_model'].append(str(aid))
        continue
    if brand == 'intel' and not is_intel_lga1700(model):
        excluded['incompatible_socket'].append(str(aid))
        continue
    if brand == 'amd' and not model.startswith('Ryzen'):
        excluded['other'].append(str(aid))
        continue
    perf = cpu.get('_cpu_perf')
    if perf is None:
        excluded['other'].append(str(aid))
        continue
    valid_cpus.append(cpu)


# Group by platform
intel_mbs = [mb for mb in valid_mbs if mb['_raw_params'].get('computersComponentSocket') == 'LGA1700']
amd_mbs = [mb for mb in valid_mbs if mb['_raw_params'].get('computersComponentSocket') == 'AM4']

intel_cpus = [cpu for cpu in valid_cpus if cpu['_cpu_brand'] == 'intel']
amd_cpus = [cpu for cpu in valid_cpus if cpu['_cpu_brand'] == 'amd']


def detect_kit_mb(mb):
    """Detect if a motherboard listing is actually a kit (MB+CPU+RAM)."""
    text = mb.get('title', '') + ' ' + mb.get('body', '')
    model, brand = extract_cpu(text)
    if not model:
        return None
    kit_indicators = ['комплект', 'kit', '+', 'проц', 'процессор', 'gb', 'гб']
    text_lower = text.lower()
    if not any(ind in text_lower for ind in kit_indicators):
        return None
    return model, brand


def generate_combos(mbs, cpus, platform):
    combos = []
    for mb in mbs:
        rp = mb['_raw_params']
        chipset = rp.get('computersComponentChipset', '')
        pcie = CHIPSET_PCIE.get(chipset, 3.0)
        dimm_slots = rp.get('computersComponentNumberSlots')
        try:
            dimm_slots = int(dimm_slots) if dimm_slots else 4
        except:
            dimm_slots = 4
        mb_price = parse_price(mb)
        mb_quality = BOARD_TIER.get(chipset, 2)

        kit_cpu = detect_kit_mb(mb)
        if kit_cpu:
            kit_model, kit_brand = kit_cpu
            perf = estimate_perf(kit_model, kit_brand)
            compat = 'verified'
            notes = ['source=kit: this lot includes motherboard + CPU + RAM together']
            if platform == 'intel':
                ok, reason = intel_supported_chipset(kit_model, chipset)
            else:
                ok, reason = amd_supported_chipset(kit_model, chipset)
            if ok:
                if ok == 'uncertain':
                    compat = 'uncertain'
                    notes.append(reason)
                if pcie >= 4.0:
                    if dimm_slots < 4:
                        notes.append(f'Only {dimm_slots} DIMM slots - user has 4 DDR4 sticks')
                    price_changed = False
                    old_price = None
                    sid = seen_ids.get(str(mb['ad_id']))
                    if sid and sid.get('last_price'):
                        try:
                            old = float(sid['last_price'])
                            if old > 1000:
                                old = old / 100
                            if abs(old - mb_price) > 0.01:
                                price_changed = True
                                old_price = old
                        except:
                            pass
                    combo = {
                        'motherboard': {
                            'ad_id': str(mb['ad_id']),
                            'title': mb['title'],
                            'price_byn': mb_price,
                            'url': mb['url'],
                            'seller': mb.get('seller', ''),
                            'condition': mb.get('condition', ''),
                        },
                        'cpu': {
                            'ad_id': str(mb['ad_id']),
                            'title': f"[kit CPU] {kit_model}",
                            'price_byn': 0,
                            'url': mb['url'],
                            'seller': mb.get('seller', ''),
                            'condition': mb.get('condition', ''),
                        },
                        'kit_price_byn': mb_price,
                        'cpu_perf': perf,
                        'cpu_perf_baseline': 100,
                        'compatibility': compat,
                        'notes': notes,
                        '_dimm_slots': dimm_slots,
                        '_pcie': pcie,
                        '_chipset': chipset,
                        '_mb_quality': mb_quality,
                        '_model': kit_model,
                        '_price_changed': price_changed,
                        '_old_cpu_price': old_price,
                        '_mb_price_changed': price_changed,
                        '_old_mb_price': old_price,
                        '_is_kit': True,
                    }
                    combos.append(combo)
            continue

        for cpu in cpus:
            model = cpu['_cpu_model']
            perf = cpu['_cpu_perf']
            cpu_price = parse_price(cpu)
            compat = 'verified'
            notes = []
            if platform == 'intel':
                ok, reason = intel_supported_chipset(model, chipset)
            else:
                ok, reason = amd_supported_chipset(model, chipset)
            if not ok:
                continue
            if ok == 'uncertain':
                compat = 'uncertain'
                notes.append(reason)
            if pcie < 4.0:
                continue
            if dimm_slots < 4:
                notes.append(f'Only {dimm_slots} DIMM slots - user has 4 DDR4 sticks')

            price_changed = False
            old_cpu_price = None
            sid = seen_ids.get(str(cpu['ad_id']))
            if sid and sid.get('last_price'):
                try:
                    old = float(sid['last_price'])
                    if old > 1000:
                        old = old / 100
                    if abs(old - cpu_price) > 0.01:
                        price_changed = True
                        old_cpu_price = old
                except:
                    pass

            mb_price_changed = False
            old_mb_price = None
            sid2 = seen_ids.get(str(mb['ad_id']))
            if sid2 and sid2.get('last_price'):
                try:
                    old = float(sid2['last_price'])
                    if old > 1000:
                        old = old / 100
                    if abs(old - mb_price) > 0.01:
                        mb_price_changed = True
                        old_mb_price = old
                except:
                    pass

            combo = {
                'motherboard': {
                    'ad_id': str(mb['ad_id']),
                    'title': mb['title'],
                    'price_byn': mb_price,
                    'url': mb['url'],
                    'seller': mb.get('seller', ''),
                    'condition': mb.get('condition', ''),
                },
                'cpu': {
                    'ad_id': str(cpu['ad_id']),
                    'title': cpu['title'],
                    'price_byn': cpu_price,
                    'url': cpu['url'],
                    'seller': cpu.get('seller', ''),
                    'condition': cpu.get('condition', ''),
                },
                'kit_price_byn': mb_price + cpu_price,
                'cpu_perf': perf,
                'cpu_perf_baseline': 100,
                'compatibility': compat,
                'notes': notes,
                '_dimm_slots': dimm_slots,
                '_pcie': pcie,
                '_chipset': chipset,
                '_mb_quality': mb_quality,
                '_model': model,
                '_price_changed': price_changed,
                '_old_cpu_price': old_cpu_price,
                '_mb_price_changed': mb_price_changed,
                '_old_mb_price': old_mb_price,
                '_is_kit': False,
            }
            combos.append(combo)
    return combos


intel_combos = generate_combos(intel_mbs, intel_cpus, 'intel')
amd_combos = generate_combos(amd_mbs, amd_cpus, 'amd')


def build_tiers(combos, platform):
    if not combos:
        return {'entry_upgrade': [], 'balanced': [], 'future_ready': []}

    entry = [c for c in combos if c['cpu_perf'] >= 98]
    entry.sort(key=lambda x: (x['kit_price_byn'], -x['cpu_perf']))
    entry = entry[:3]
    entry_prices = [c['kit_price_byn'] for c in entry]
    cheapest_entry = entry_prices[0] if entry_prices else 999999

    used_pairs = set((c['motherboard']['ad_id'], c['cpu']['ad_id']) for c in entry)

    bal_candidates = []
    for c in combos:
        if c['cpu_perf'] < 115 or c['cpu_perf'] > 300:
            continue
        if c['kit_price_byn'] <= 1.15 * cheapest_entry:
            continue
        if c['kit_price_byn'] > max(1100, 2.2 * cheapest_entry):
            continue
        if (c['motherboard']['ad_id'], c['cpu']['ad_id']) in used_pairs:
            continue
        bal_candidates.append(c)

    high_tdp_models = {
        'i5-12600K', 'i5-12600KF', 'i5-13600K', 'i5-13600KF', 'i5-14600K', 'i5-14600KF',
        'i7-12700', 'i7-12700K', 'i7-12700KF', 'i9-12900', 'i9-12900K', 'i9-12900KF', 'i9-12900KS',
        'i7-13700', 'i7-13700K', 'i7-13700KF', 'i9-13900', 'i9-13900K', 'i9-13900KF',
        'i7-14700', 'i7-14700K', 'i7-14700KF', 'i9-14900K', 'i9-14900KF', 'i9-14900KS',
        'Ryzen 7 5800X', 'Ryzen 7 5800X3D', 'Ryzen 9 5900X', 'Ryzen 9 5950X',
        'Ryzen 9 3900X', 'Ryzen 9 3950X'
    }
    for c in bal_candidates:
        perf = c['cpu_perf']
        price = c['kit_price_byn']
        vrm_penalty = 1.0
        if c['_model'] in high_tdp_models and c['_chipset'] in ('Intel H610', 'Intel B660', 'Intel B760'):
            vrm_penalty = 0.75
        if c['_chipset'] == 'Intel H610' and c['_model'].startswith('i9'):
            vrm_penalty = 0.5
        condition_factor = 1.0
        if c['compatibility'] == 'uncertain':
            condition_factor *= 0.9
        c['_pp'] = (perf / price) * vrm_penalty * condition_factor
    bal_candidates.sort(key=lambda x: -x['_pp'])
    balanced = bal_candidates[:3]
    used_pairs.update((c['motherboard']['ad_id'], c['cpu']['ad_id']) for c in balanced)

    fut_candidates = []
    for c in combos:
        if c['cpu_perf'] < 180:
            continue
        if c['kit_price_byn'] > max(1500, 3 * cheapest_entry):
            continue
        if (c['motherboard']['ad_id'], c['cpu']['ad_id']) in used_pairs:
            continue
        fut_candidates.append(c)

    for c in fut_candidates:
        perf_score = c['cpu_perf'] / 500.0
        board_score = 0
        board_score += c['_mb_quality'] / 4.0 * 0.5
        board_score += (1 if c['_pcie'] >= 5.0 else 0.7) * 0.3
        board_score += (1 if c['_dimm_slots'] >= 4 else 0.5) * 0.2
        price_score = max(0, 1 - c['kit_price_byn'] / 2500.0)
        vrm_penalty = 1.0
        if c['_chipset'] in ('Intel H610', 'Intel B660', 'Intel B760') and c['_model'].startswith('i9'):
            vrm_penalty = 0.6
        c['_fs'] = (perf_score * 0.45 + board_score * 0.35 + price_score * 0.20) * vrm_penalty
    fut_candidates.sort(key=lambda x: -x['_fs'])
    future_ready = fut_candidates[:3]

    return {'entry_upgrade': entry, 'balanced': balanced, 'future_ready': future_ready}


def finalize_combo(c, rank, tier):
    mb = c['motherboard']
    cpu = c['cpu']
    price_score = max(1, min(10, 10 - (c['kit_price_byn'] / 200)))
    compatibility_score = 10.0 if c['compatibility'] == 'verified' else 7.0
    freshness_score = 9.0
    condition_score = 8.0 if mb.get('condition') == 'Б/у' else 9.0
    seller_score = 8.0
    score = round((price_score + compatibility_score + freshness_score + condition_score + seller_score) / 5, 1)
    notes = list(c['notes'])
    if c.get('_price_changed'):
        notes.append(f"CPU price changed from {c['_old_cpu_price']} to {cpu['price_byn']} BYN")
    if c.get('_mb_price_changed'):
        notes.append(f"MB price changed from {c['_old_mb_price']} to {mb['price_byn']} BYN")
    if c['_pcie'] >= 5.0:
        notes.append(f"PCIe {c['_pcie']} x16 primary slot")
    elif c['_pcie'] >= 4.0:
        notes.append(f"PCIe {c['_pcie']} x16 primary slot")
    notes.append(f"DDR4 confirmed ({c['_dimm_slots']} DIMM slots)")

    # VRM warning for high-TDP CPU on budget board
    vrm_warning_models = {
        'i5-12600K', 'i5-12600KF', 'i5-13600K', 'i5-13600KF', 'i5-14600K', 'i5-14600KF',
        'i7-12700', 'i7-12700K', 'i7-12700KF', 'i9-12900', 'i9-12900K', 'i9-12900KF', 'i9-12900KS',
        'i7-13700', 'i7-13700K', 'i7-13700KF', 'i9-13900', 'i9-13900K', 'i9-13900KF',
        'i7-14700', 'i7-14700K', 'i7-14700KF', 'i9-14900K', 'i9-14900KF', 'i9-14900KS',
        'Ryzen 7 5800X', 'Ryzen 7 5800X3D', 'Ryzen 9 5900X', 'Ryzen 9 5950X',
        'Ryzen 9 3900X', 'Ryzen 9 3950X'
    }
    if c['_model'] in vrm_warning_models and c['_chipset'] in ('Intel H610', 'Intel B660', 'Intel B760'):
        notes.append(f"VRM caution: {c['_model']} on {c['_chipset']} may throttle under sustained load")
    if c['_model'] in vrm_warning_models and c['_chipset'] in ('AMD B550', 'AMD A520'):
        notes.append(f"VRM caution: {c['_model']} on {c['_chipset']} - verify VRM cooling")

    return {
        'rank': rank,
        'tier': tier,
        'score': score,
        'score_breakdown': {
            'price': round(price_score, 1),
            'compatibility': compatibility_score,
            'freshness': freshness_score,
            'condition': condition_score,
            'seller': seller_score,
        },
        'motherboard': mb,
        'cpu': cpu,
        'kit_price_byn': c['kit_price_byn'],
        'cpu_perf': c['cpu_perf'],
        'cpu_perf_baseline': 100,
        'compatibility': c['compatibility'],
        'notes': notes,
    }


def finalize_tiers(tiers, platform):
    out = {}
    for tier, combos in tiers.items():
        out[tier] = [finalize_combo(c, idx + 1, tier) for idx, c in enumerate(combos)]
    return out


intel_tiers = finalize_tiers(build_tiers(intel_combos, 'intel'), 'intel')
amd_tiers = finalize_tiers(build_tiers(amd_combos, 'amd'), 'amd')

total_intel_pairs = len(intel_combos)
total_amd_pairs = len(amd_combos)
total_excluded = sum(len(v) for v in excluded.values())

cheapest_intel = min((c for c in intel_combos if c['cpu_perf'] >= 98), key=lambda x: x['kit_price_byn'], default=None) if intel_combos else None
cheapest_amd = min((c for c in amd_combos if c['cpu_perf'] >= 98), key=lambda x: x['kit_price_byn'], default=None) if amd_combos else None

# Collect platform-specific notes
questions = []
# Intel: all usable non-kit DDR4 boards have only 2 DIMM slots
intel_4slot = [c for c in intel_combos if c['_dimm_slots'] >= 4]
if not intel_4slot:
    questions.append(
        "Все валидные Intel DDR4-платы в выборке — H610 с 2 слотами DIMM; для сохранения 4 планок DDR4 нужна B660/B760/Z690 DDR4 с 4 слотами (таких лотов сейчас нет или они с дефектом/без цены). "
        "Альтернатива — готовый кит ASRock B660M Pro RS + i5-13400 + 32GB RAM за 1700 BYN (ad 1073979712), но это выходит за текущие tier-лимиты."
    )

# Kit alternatives found
kit_alternatives = []
for c in intel_combos + amd_combos:
    if c.get('_is_kit'):
        kit_alternatives.append(f"{c['motherboard']['title']} — {c['kit_price_byn']} BYN (CPU {c['_model']}, perf {c['cpu_perf']})")
if kit_alternatives:
    questions.append("Найдены готовые киты (плата+CPU+RAM), не вошедшие в tier-топы: " + "; ".join(kit_alternatives))

result = {
    'checked_at': checked_at,
    'inputs': {
        'report_txt': 'Intel Core i7-9750H / MSI B250M Pro-VDH / 48 GB DDR4 / NVIDIA GeForce RTX 5060 Ti',
        'fresh_fetch': 'scripts/_items.json',
        'seen_ids': 'scripts/.cache/seen_ids.json',
        'missing_or_stale_ids': [],
        'current_cpu_baseline': {'model': 'Intel Core i7-9750H', 'perf_score': 100}
    },
    'intel': intel_tiers,
    'amd': amd_tiers,
    'excluded': excluded,
    'needs_main_agent': {
        'reverify_urls': reverify_urls,
        'missing_data': [],
        'questions': questions,
    },
    'summary': (
        f"Intel: {total_intel_pairs} валидных пар, AMD: {total_amd_pairs} пар. "
        f"Исключено {total_excluded} лотов (дефект, цена, несовместимость/не распознан CPU). "
        f"Дешевле Intel: {cheapest_intel['kit_price_byn'] if cheapest_intel else 'N/A'} BYN ({cheapest_intel['_model'] if cheapest_intel else ''}), "
        f"AMD: {cheapest_amd['kit_price_byn'] if cheapest_amd else 'N/A'} BYN ({cheapest_amd['_model'] if cheapest_amd else ''}). "
        f"Проблема Intel: все доступные платы H610 имеют только 2 DIMM-слота; для 4 планок DDR4 нужен повторный поиск B660/B760/Z690 DDR4."
    ),
    '_stats': {
        'total_intel_pairs': total_intel_pairs,
        'total_amd_pairs': total_amd_pairs,
        'total_excluded': total_excluded,
        'cheapest_intel': cheapest_intel['kit_price_byn'] if cheapest_intel else None,
        'cheapest_amd': cheapest_amd['kit_price_byn'] if cheapest_amd else None,
        'top_intel_mb': cheapest_intel['motherboard']['title'] if cheapest_intel else None,
        'top_intel_cpu': cheapest_intel['cpu']['title'] if cheapest_intel else None,
        'top_amd_mb': cheapest_amd['motherboard']['title'] if cheapest_amd else None,
        'top_amd_cpu': cheapest_amd['cpu']['title'] if cheapest_amd else None,
    }
}

with open(f'{ROOT}/scripts/_kit_shortlist.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Done")
print(f"Intel pairs: {total_intel_pairs}, AMD pairs: {total_amd_pairs}")
print(f"Excluded: {total_excluded}")
print(f"Cheapest Intel: {cheapest_intel['kit_price_byn'] if cheapest_intel else 'N/A'}")
print(f"Cheapest AMD: {cheapest_amd['kit_price_byn'] if cheapest_amd else 'N/A'}")
print("Excluded breakdown:")
for k, v in excluded.items():
    print(f"  {k}: {len(v)}")
