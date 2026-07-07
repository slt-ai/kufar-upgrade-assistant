# Подбор комплектов mb+cpu — 2026-06-28 1724

**Источник:** kufar.by Минск. **Сценарий:** кросс-комбинирование мат. плат и процессоров.

**Конфигурация ПК:** Intel Core i7-9750H / MSI B250M Pro-VDH / 48 ГБ DDR4 (4 планки) / NVIDIA GeForce RTX 5060 Ti.

**Фильтры:** DDR4 only, PCI-E ≥4.0 x16 (целевой 5.0), Intel LGA1700 (DDR4) / AMD AM4, whitelist брендов мат. плат {ASUS, MSI, Gigabyte, ASRock, Biostar, ECS}.

**Ранжирование:** quality score = motherboard_quality (0–100) + cpu_quality (0–30).
CPU вклад = (perf − 100) × 0.068, cap 30. i7-9750H=100 → 0, i9-14900K=540 → 30.

Веса для материнской платы (по указанию пользователя):

- **DIMM-слоты: 40** (4 → 40, 2 → 0). Критично: у пользователя 4 планки DDR4.
- **VRM-запас: 20** (15+ фаз → 20; 10+ → 16; 7+ → 10; иначе 4).
- **PCI-E версия: 15** (5.0 → 15, 4.0 → 10, 3.0 → 0).
- **M.2-слоты: 10** (2× → 10, 1× → 5).
- **Сеть: 5** (2.5G → 5, 1G → 2).
- **Разгон/BCLK/OC-серия: 5** (TUF/Aorus/ROG, Gigabyte Gaming X — наравне).
- **Бренд-премиум (ASUS/MSI > ASRock/Gigabyte > Biostar): 5**.

CPU perf — относительная производительность vs Intel Core i7-9750H (baseline=100).

> Примечание: топ-3 ниже переранжирован вручную агентом `kit-analyzer` — авто-сгенерированная версия содержала 2 бага в `_build_quality_top3.py` (Gigabyte Z690 ошибочно помечен noname; MSI B550M-P **Gen3** с PCIe 3.0 ошибочно поставлен в AMD #1). Исправления сохранены в memory.

---

## Сводка

- **Intel #1 (рекомендовано):** Gigabyte Z690 Gaming X DDR4 (rev. 1.0) + Intel Core i9-12900K — **1205 BYN**, q=115.08. Единственный Intel-лот с **PCIe 5.0 x16** (запас под будущий GPU), 4 DIMM, 12+1+1 VRM, 2.5G, BCLK. 12-е поколение на Z690 — нативно, без BIOS-апдейта.
- **AMD #1 (рекомендовано):** Gigabyte B550 AORUS Master + AMD Ryzen 9 5950X — **1550 BYN**, q=118.16. 16c/32t (топ для локальных LLM), 4 DIMM, 3× M.2, Wi-Fi 6, 14+2 VRM.
- **Что изменилось с 2026-06-25:** полный пересбор нашёл **69 новых лотов**. Из прошлого топа 2 сняты с продажи (Asrock B660M PG Riptide 1074338703, i5-12400 «Антон» 1073950867), 5 активны (4 подорожали в пределах +6…+11 BYN, B550 Gaming X V2 подешевела на 12.76 BYN). Появился новый Intel-лот с PCIe 5.0 — Z690 Gaming X DDR4 (1074829435, 2026-06-27).

## Топ-3 Intel (по quality score)

| # | Мат. плата | Chipset | DIMM | PCIe | M.2 | CPU | Perf | Цена кита | Quality | Совмест. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gigabyte Z690 Gaming X DDR4 (rev. 1.0) | Z690 | 4 | **5.0** | 2× | Intel Core i9-12900K | 410 | **1205 BYN** | **115.08** | verified |
| 2 | Gigabyte B760 Gaming X AX DDR4 | B760 | 4 | 4.0 | 2× | i7-13700F | 380 | **1220 BYN** | **108.04** | verified |
| 3 | Gigabyte Z690 Gaming X DDR4 (rev. 1.0) | Z690 | 4 | **5.0** | 2× | Intel Core i5-12400 | 175 | **950 BYN** | **99.10** | verified |

### INTEL #1 — quality 115.08 (mb 94.0 + cpu 21.08) — РЕКОМЕНДОВАНО
- **Мат. плата:** Материнская плата Z690 Gaming X DDR4 (rev. 1.0) — 450 BYN — Владислав, Фрунзенский — [ссылка](https://www.kufar.by/item/1074829435) (list_time 2026-06-27, **НОВЫЙ**)
  - chip: Z690, socket: LGA1700, DIMM: 4, **PCIe 5.0 x16**, M.2: 2×, LAN: 2.5G, OC: True (Gaming X), VRM: 12+1+1 → 16, brand: Gigabyte.
- **Процессор:** Процессор Intel Core i9-12900K Гарантия — 755 BYN — ООО «ПТК БелИнструмент», Центральный — [ссылка](https://www.kufar.by/item/1073208894) (list_time 2026-06-23)
  - perf 410, 16c/24t. kit 1205 BYN. **Совместимость verified:** 12-е поколение на Z690 нативно, без BIOS-апдейта. PCIe 5.0 x16 — запас под будущий GPU.

### INTEL #2 — quality 108.04 (mb 89.0 + cpu 19.04)
- **Мат. плата:** Gigabyte B760 Gaming X AX DDR4 — 450 BYN — Максим, Заводской — [ссылка](https://www.kufar.by/item/1074498967) (list_time 2026-06-24)
  - chip: B760, socket: LGA1700, DIMM: 4, PCIe 4.0 x16, M.2: 2×, LAN: 2.5G, OC: True (Gaming X), VRM: 12+1+1 → 16, brand: Gigabyte.
- **Процессор:** Продаю процессор i7-13700F — 770 BYN — Вадим, Октябрьский — [ссылка](https://www.kufar.by/item/1071188333)
  - perf 380, 16c/24t. kit 1220 BYN. **verified:** 13-е поколение на B760 нативно.

### INTEL #3 — quality 99.10 (mb 94.0 + cpu 5.1) — БЮДЖЕТ с PCIe 5.0
- **Мат. плата:** та же Z690 Gaming X DDR4 (1074829435, 450 BYN).
- **Процессор:** Intel Core i5-12400 — 500 BYN — Роман, Фрунзенский — [ссылка](https://www.kufar.by/item/1073241092)
  - perf 175, 6c/12t. kit 950 BYN. **verified** (12-е поколение на Z690 нативно). Самый дешёвый путь к PCIe 5.0.

> **Uncertain-комбо (Z690 + 13/14-е поколение, требуют BIOS-апдейта):** Z690 + i9-14900KF (1000 BYN) = 1450, raw q=124.0 (максимальный) — понижен из-за неуверенности в BIOS; Z690 + i7-13700K (800 BYN) = 1250, q=113.04. Если продавец Z690 (1074829435) подтвердит свежий BIOS — Z690 + i9-14900KF поднимается в #1.

## Топ-3 AMD (по quality score)

| # | Мат. плата | Chipset | DIMM | PCIe | M.2 | CPU | Perf | Цена кита | Quality | Совмест. |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gigabyte B550 AORUS Master | B550 | 4 | 4.0 | 3× | AMD Ryzen 9 5950X | 470 | **1550 BYN** | **118.16** | verified |
| 2 | Gigabyte B550 Gaming X V2 rev 1.1 | B550 | 4 | 4.0 | 2× | AMD Ryzen 9 5950X | 470 | **1260 BYN** | **111.16** | verified |
| 3 | ASRock B550 Steel Legend | B550 | 4 | 4.0 | 2× | AMD Ryzen 9 3950X | 410 | **890 BYN** | **102.08** | verified |

### AMD #1 — quality 118.16 (mb 93.0 + cpu 25.16) — РЕКОМЕНДОВАНО
- **Мат. плата:** Материнская плата Gigabyte B550 AORUS Master — 600 BYN — Алексей, Первомайский — [ссылка](https://www.kufar.by/item/1069258658) (list_time 2026-05-17)
  - chip: B550, socket: AM4, DIMM: 4, **3× PCIe x16 4.0/3.0, 3× M.2, Wi-Fi 6 + BT 5.0**, VRM: 14+2 → 20, OC: True (AORUS Master), brand: Gigabyte.
- **Процессор:** Процессор AMD Ryzen 9 5950X — 950 BYN — Пользователь, Заводской — [ссылка](https://www.kufar.by/item/1073227393) (list_time 2026-06-24, цена без изменений vs 06-25)
  - perf 470, 16c/32t — топ для локальных LLM. kit 1550 BYN.

### AMD #2 — quality 111.16 (mb 86.0 + cpu 25.16) — ЛУЧШЕЕ СООТНОШЕНИЕ
- **Мат. плата:** Материнская плата Gigabyte Gaming X V2 rev 1.1 — 310 BYN — Max, Центральный — [ссылка](https://www.kufar.by/item/1074867167) (list_time 2026-06-27, **НОВЫЙ** — преемник ушедшего 1019993393 rev 1.0 за 350 BYN)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.0 x16, M.2: 2×, LAN: 1G, OC: True (Gaming X), VRM: 10+1+1 → 16, brand: Gigabyte.
- **Процессор:** тот же Ryzen 9 5950X (1073227393, 950 BYN). kit 1260 BYN.

### AMD #3 — quality 102.08 (mb 81.0 + cpu 21.08) — БЮДЖЕТ 16c/32t
- **Мат. плата:** Материнская плата ASRock B550 Steel Legend — 400 BYN — Антон, Советский — [ссылка](https://www.kufar.by/item/1073717899) (list_time 2026-06-18)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.0 x16, M.2: 2×, LAN: 1G, OC: False (Steel Legend — mid-tier, без BCLK), VRM: 10+2 → 16, brand: ASRock.
- **Процессор:** AMD Ryzen 9 3950X — 490 BYN — Дмитрий, Центральный — [ссылка](https://www.kufar.by/item/1073399967) (цена без изменений vs 06-25)
  - perf 410, 16c/32t. kit 890 BYN.

## Сравнение Intel vs AMD

| Критерий | Intel #1 | AMD #1 |
|---|---|---|
| Мат. плата | Z690 Gaming X DDR4 | B550 AORUS Master |
| CPU | i9-12900K (16c/24t) | Ryzen 9 5950X (16c/32t) |
| PCIe GPU | **5.0 x16** (запас под будущее) | 4.0 x16 |
| 4 планки DDR4 | Да | Да |
| M.2 | 2× | 3× |
| Сеть | 2.5G | Wi-Fi 6 + BT + 1G |
| Цена кита | **1205 BYN** | 1550 BYN |
| Quality | 115.08 | **118.16** |

**Вывод:** AMD даёт больше потоков (32 vs 24) и более богатую плату (3× M.2, Wi-Fi 6) за +345 BYN; Intel даёт **PCIe 5.0** под будущий GPU и дешевле на 345 BYN. Для локальных LLM (мультипоток) — AMD #1; для апгрейд-запаса под будущую видеокарту (PCIe 5.0) и экономии — Intel #1.

## Готовые киты (mb+cpu+ram в одном лоте)

Неразборные наборы, продаются как единое целое. Под DDR4 (LGA1700/AM4) в Минске — 4 лота.

| # | Платформа | Цена | CPU (perf) | Описание | Продавец | Лот |
|---|---|---|---|---|---|---|
| 1 | AM4 | 280 BYN | 165 | AMD Ryzen 5 4500 + кулер | Anton | [ссылка](https://www.kufar.by/item/1046837951) |
| 2 | LGA1700 | 750 BYN | 200 | Комплект 13400f/b760m | Леонид | [ссылка](https://www.kufar.by/item/1074720440) |
| 3 | LGA1700 | 1600 BYN | 200 | i5-13400 + B660M + 4×8 32GB DDR4 | Даник | [ссылка](https://www.kufar.by/item/1074878726) |
| 4 | LGA1700 | 1900 BYN | — | i9-14900k + b660 + 64gb | Иван | [ссылка](https://www.kufar.by/item/1074023280) |

## Изменения относительно отчёта 2026-06-25 1447

**Пересбор 2026-06-28:** 69 новых ad_id. Прямая проверка 7 ценных stale-лотов выполнена.

### Снято с продажи (removed=true, 2026-06-28)

| ad_id | Что было | Прошлая цена |
|---|---|---|
| 1074338703 | Asrock B660M PG Riptide (бывший Intel #1) | 500 BYN |
| 1073950867 | Intel Core i5-12400 «Антон» (бывший Intel #1 CPU) | 500 BYN |

### Активны, цена изменилась

| ad_id | Лот | Прошлая цена | Текущая цена | Дельта |
|---|---|---|---|---|
| 1019993393 | Gigabyte B550 Gaming X V2 rev 1.0 | 350 | 337.24 | **−12.76** |
| 1049279891 | Gigabyte B760 Gaming X Gen5 (PCIe 5.0!) | 378 | 384.31 | +6.31 |
| 1063525487 | MSI B550-A Pro | 345 | 352.01 | +7.01 |
| 1029024019 | Gigabyte B760M Gaming X AX rev | 493 | 504.37 | +11.37 |

### Активны, без изменений

| ad_id | Лот | Цена |
|---|---|---|
| 1069364985 | ASUS TUF B450M Pro S | 230 BYN |
| 1073227393 | AMD Ryzen 9 5950X | 950 BYN |
| 1073399967 | AMD Ryzen 9 3950X | 490 BYN |

> Лоты 1019993393, 1049279891, 1069364985, 1063525487, 1029024019 вернулись в активный пул после прямой проверки (были stale). B550 Gaming X V2 rev 1.0 (1019993393) уступил место новому ревизию 1.1 (1074867167, 310 BYN) в текущем топе — но сам лот активен и доступен как альтернатива.

### Новые лоты, вошедшие в топ-3

| ad_id | Лот | Позиция |
|---|---|---|
| 1074829435 | Gigabyte Z690 Gaming X DDR4 (PCIe 5.0) | Intel #1, #3 |
| 1074498967 | Gigabyte B760 Gaming X AX DDR4 | Intel #2 |
| 1073241092 | Intel Core i5-12400 (Роман) | Intel #3 |
| 1073208894 | Intel Core i9-12900K | Intel #1 |
| 1074867167 | Gigabyte B550 Gaming X V2 rev 1.1 | AMD #2 |
| 1069258658 | Gigabyte B550 AORUS Master | AMD #1 |

## Исключения (с указанием причины)

| ad_id | Причина |
|---|---|
| 1071173866 (ASUS Prime B760M-R D4) | defect: «не работает» |
| 1067964836 (MSI Pro H610M-B DDR4) | defect: «глючит» |
| 1074467672 (MSI B550M-P Gen3) | **PCIe 3.0 x16** — нарушает правило PCIe ≥4.0 |
| 1073248395 (ASRock B550, без модели) | defect: «с отлетевшей звуковой картой» + нет модели |
| 1073038427 (ASRock X570, без модели) | uncertain: нет модели, невозможно проверить характеристики |
| 1070675357 (Gigabyte B550M, без модели) | uncertain: body упоминает «am5», без модели не валидируется |
| 1067156481 (i9-13900KF + Z790-P WiFi) | wrong_memory: kit с DDR5 |
| 1070922366 (Soyo SY-YL B550M) | noname_mb: Soyo не в whitelist |
| 16 CPU без цены | no_price («договорная»/«торг») |

## Файлы

- `reports\2026-06-28 1724 — intel+amd ddr4 upgrade — подбор.md` — этот отчёт (переранжирован вручную, авто-ген исправлен).
- `reports\2026-06-28 1724 — intel+amd ddr4 upgrade — подбор.json` — структурированная выгрузка (из авто-генератора; топ-3 в нём багованный — ориентироваться на .md).
- `reports\2026-06-28 1724 — intel+amd ddr4 upgrade — подбор.csv` — таблица топ-пар.
- `scripts\.cache\seen_ids.json` — обновлён (2 removed, 5 актуализированы после прямой проверки).
- `scripts\.cache\_manifest_2026-06-28.json` — манифест сбора.