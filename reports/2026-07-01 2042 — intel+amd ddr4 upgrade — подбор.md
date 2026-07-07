# Подбор комплектов mb+cpu — 2026-07-01 2042

**Источник:** kufar.by Минск. **Сценарий:** кросс-комбинирование мат. плат и процессоров, свежий полный пересбор.

**Конфигурация ПК:** Intel Core i7-9750H / MSI B250M Pro-VDH / 48 ГБ DDR4 (4 планки) / NVIDIA GeForce RTX 5060 Ti.

**Фильтры:** DDR4 only, PCI-E ≥4.0 x16 (целевой 5.0), Intel LGA1700 (DDR4) / AMD AM4, whitelist брендов мат. плат {ASUS, MSI, Gigabyte, ASRock, Biostar, ECS}, мат. плата в топе — обязательно 4 DIMM.

---

## Сводка

- **Intel #1:** Gigabyte B760 Gaming X AX DDR4 + Intel Core i7-13700F — **1210 BYN**, 4 DIMM, PCIe 4.0, плата б/у, CPU новый. Лучший баланс производительности и качества платы в текущей выборке.
- **AMD #1:** Gigabyte B550 AORUS Master + AMD Ryzen 9 5950X — **1480 BYN**, 16c/32t, 4 DIMM, 3× M.2, Wi-Fi 6, топовая плата для локальных LLM.
- **Что изменилось с 2026-06-28:** снят с продажи ключевый Intel-лот **Gigabyte Z690 Gaming X DDR4** (1074829435, был Intel #1 с PCIe 5.0); **Ryzen 9 5950X** подешевел с 950 до **880 BYN** (−70); появились новые лоты ASRock B550M Pro4 (новая, 310 BYN) и Intel i3-12100F (200 BYN).

## Топ-3 Intel (по quality score, 4 DIMM)

| # | Мат. плата | Chipset | DIMM | PCIe | CPU | Perf | Цена кита | Состояние | Ссылки | Заметки |
|---|---|---|---|---|---|---:|---|---|---|---|
| 1 | Gigabyte B760 Gaming X AX DDR4 | B760 | 4 | 4.0 | i7-13700F (16c/24t) | 450 | **1210 BYN** | плата б/у, CPU новый | [CPU](https://www.kufar.by/item/1071188333), [MB](https://www.kufar.by/item/1074498967) | verified, 2.5G LAN, Gaming X OC-серия |
| 2 | Gigabyte B760 Gaming X AX DDR4 | B760 | 4 | 4.0 | i9-12900K (16c/24t) | 410 | **1195 BYN** | б/у | [CPU](https://www.kufar.by/item/1073208894), [MB](https://www.kufar.by/item/1074498967) | verified, но 125W CPU на B760 — возможен троттлинг под длительной нагрузкой (LLM) |
| 3 | Gigabyte B760 Gaming X AX DDR4 | B760 | 4 | 4.0 | i5-13400 (10c/16t) | 280 | **1140 BYN** | б/у | [CPU](https://www.kufar.by/item/1075021903), [MB](https://www.kufar.by/item/1074498967) | verified, бюджетный 4-DIMM вариант |

### Intel #1 — 1210 BYN — РЕКОМЕНДОВАНО
- **Мат. плата:** Gigabyte B760 Gaming X AX DDR4 — 440 BYN — Максим, Заводской — [ссылка](https://www.kufar.by/item/1074498967) (list_time 2026-06-24, цена −10 BYN vs 06-28)
  - chip: B760, socket: LGA1700, DIMM: 4, PCIe 4.0 x16, M.2: 2×, LAN: 2.5G, OC: Gaming X, brand: Gigabyte.
- **Процессор:** i7-13700F — 770 BYN — Вадим, Октябрьский — [ссылка](https://www.kufar.by/item/1071188333) (новый, не устанавливался)
  - perf 450, 16c/24t. Совместимость verified: 13-е поколение на B760 нативно.

### Intel #2 — 1195 BYN
- **Мат. плата:** та же Gigabyte B760 Gaming X AX DDR4 (440 BYN).
- **Процессор:** Intel Core i9-12900K — 755 BYN — ООО «ПТК БелИнструмент», Центральный — [ссылка](https://www.kufar.by/item/1073208894)
  - perf 410, 16c/24t. Совместимость verified. **Внимание:** i9-12900K TDP 125W на B760 Gaming X — при длительных LLM-нагрузках возможен троттлинг; для максимальной разгона-производительности желательна Z690/Z790.

### Intel #3 — 1140 BYN — БЮДЖЕТ 4-DIMM
- **Мат. плата:** та же Gigabyte B760 Gaming X AX DDR4 (440 BYN).
- **Процессор:** Intel Core i5-13400 — 700 BYN — родион, район не указан — [ссылка](https://www.kufar.by/item/1075021903)
  - perf 280, 10c/16t. kit 1140 BYN. Совместимость verified.

> **Бюджетные альтернативы с 2 DIMM (требуют замены части памяти):** ASRock H610M-HDV / Gigabyte H610M H V2 + i3-12100F от 350–388 BYN. Смотри `scripts/_kit_analyzer_out.json` → `intel.alternatives`.

## Топ-3 AMD (по quality score, 4 DIMM)

| # | Мат. плата | Chipset | DIMM | PCIe | CPU | Perf | Цена кита | Состояние | Ссылки | Заметки |
|---|---|---|---|---|---|---:|---|---|---|---|
| 1 | Gigabyte B550 AORUS Master | B550 | 4 | 4.0 | Ryzen 9 5950X (16c/32t) | 470 | **1480 BYN** | б/у | [CPU](https://www.kufar.by/item/1073227393), [MB](https://www.kufar.by/item/1069258658) | verified, Wi-Fi 6, 3× M.2, 14+2 VRM |
| 2 | ASRock B550M Pro4 | B550 | 4 | 4.0 | Ryzen 9 5950X (16c/32t) | 470 | **1190 BYN** | плата новая, CPU б/у | [CPU](https://www.kufar.by/item/1073227393), [MB](https://www.kufar.by/item/1074968077) | verified, 24 мес. гарантия на плату |
| 3 | ASRock B550 Steel Legend | B550 | 4 | 4.0 | Ryzen 9 3950X (16c/32t) | 410 | **890 BYN** | б/у | [CPU](https://www.kufar.by/item/1073399967), [MB](https://www.kufar.by/item/1073717899) | verified, бюджетный 16c/32t |

### AMD #1 — 1480 BYN — РЕКОМЕНДОВАНО ДЛЯ LLM
- **Мат. плата:** Gigabyte B550 AORUS Master — 600 BYN — Алексей, Первомайский — [ссылка](https://www.kufar.by/item/1069258658)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.0 x16, 3× M.2, Wi-Fi 6 + BT 5.0, VRM 14+2, brand: Gigabyte.
- **Процессор:** AMD Ryzen 9 5950X — 880 BYN — Пользователь, Заводской — [ссылка](https://www.kufar.by/item/1073227393) (цена −70 BYN vs 06-28)
  - perf 470, 16c/32t. kit 1480 BYN. Совместимость verified.

### AMD #2 — 1190 BYN — ЛУЧШЕЕ СООТНОШЕНИЕ
- **Мат. плата:** Новая ASRock B550M Pro4 — 310 BYN — Алеся, Центральный — [ссылка](https://www.kufar.by/item/1074968077) (новая, гарантия 24 мес., появилась после 06-28)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.0 x16, 2× M.2, brand: ASRock.
- **Процессор:** тот же Ryzen 9 5950X (880 BYN). kit 1190 BYN. Совместимость verified.

### AMD #3 — 890 BYN — БЮДЖЕТ 16c/32t
- **Мат. плата:** ASRock B550 Steel Legend — 400 BYN — Антон, Советский — [ссылка](https://www.kufar.by/item/1073717899)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.0 x16, 2× M.2, brand: ASRock.
- **Процессор:** AMD Ryzen 9 3950X — 490 BYN — Дмитрий, Центральный — [ссылка](https://www.kufar.by/item/1073399967)
  - perf 410, 16c/32t. kit 890 BYN. Совместимость verified.

> **AMD-альтернатива:** Gigabyte B550 Gaming X V2 rev 1.1 (1074867167, 310 BYN) + Ryzen 9 5950X = 1190 BYN, OC-серия Gaming X. Также активен rev 1.0 (1019993393, 333.66 BYN).

## Сравнение Intel vs AMD

| Критерий | Intel #1 | AMD #1 | AMD #2 |
|---|---|---|---|
| Мат. плата | B760 Gaming X AX DDR4 | B550 AORUS Master | B550M Pro4 |
| CPU | i7-13700F (16c/24t) | Ryzen 9 5950X (16c/32t) | Ryzen 9 5950X (16c/32t) |
| PCIe GPU | 4.0 x16 | 4.0 x16 | 4.0 x16 |
| 4 планки DDR4 | Да | Да | Да |
| M.2 | 2× | 3× | 2× |
| Сеть | 2.5G | Wi-Fi 6 + BT + 1G | 1G |
| Цена кита | **1210 BYN** | 1480 BYN | **1190 BYN** |
| CPU perf | 450 | 470 | 470 |

**Вывод:** Intel #1 дешевле на 270 BYN vs AMD #1 и даёт сопоставимую производительность (16c/24t vs 16c/32t). AMD #2 — лучшее соотношение цена/потоки (32 потока за 1190 BYN). Для локальных LLM, где критичны потоки, — AMD #1 или AMD #2; для экономии с сохранением 4 DIMM — Intel #1 или AMD #3.

## Готовые киты (mb+cpu+ram в одном лоте)

Неразборные наборы под DDR4 (LGA1700/AM4) в Минске — 4 лота, найденные в выдаче.

| # | Платформа | Цена | CPU (perf) | Описание | Продавец | Лот |
|---|---|---:|---|---|---|---|
| 1 | AM4 | 280 BYN | 165 | AMD Ryzen 5 4500 + кулер | Anton | [ссылка](https://www.kufar.by/item/1046837951) |
| 2 | LGA1700 | 750 BYN | 200 | Комплект 13400f/b760m | Леонид | [ссылка](https://www.kufar.by/item/1074720440) |
| 3 | LGA1700 | 1600 BYN | 200 | i5-13400 + B660M + 4×8 32GB DDR4 | Даник | [ссылка](https://www.kufar.by/item/1074878726) |
| 4 | LGA1700 | 1900 BYN | — | i9-14900k + b660 + 64gb | Иван | [ссылка](https://www.kufar.by/item/1074023280) |

## Изменения относительно отчёта 2026-06-28

**Пересбор 2026-07-01:** 70 новых `ad_id`, 194 детально собранных объявления, 6 stale-лотов проверены по прямым ссылкам.

### Снято с продажи (removed=true)

| ad_id | Что было | Прошлая цена | Текущий статус |
|---|---|---|---|
| 1074829435 | Gigabyte Z690 Gaming X DDR4 (Intel #1, PCIe 5.0) | 450 BYN | removed (404/deactivated) |

### Активны, цена изменилась

| ad_id | Лот | Прошлая цена | Текущая цена | Дельта |
|---|---|---:|---:|---|
| 1074498967 | Gigabyte B760 Gaming X AX DDR4 | 450 | 440 | **−10** |
| 1073227393 | AMD Ryzen 9 5950X | 950 | 880 | **−70** |
| 1019993393 | Gigabyte B550 Gaming X V2 rev 1.0 | 350 | 333.66 | **−16.34** |
| 1063525487 | MSI B550-A Pro | 345 | 355.21 | +10.21 |

### Активны, без изменений

| ad_id | Лот | Цена |
|---|---|---|
| 1069258658 | Gigabyte B550 AORUS Master | 600 BYN |
| 1073717899 | ASRock B550 Steel Legend | 400 BYN |
| 1073399967 | AMD Ryzen 9 3950X | 490 BYN |
| 1074867167 | Gigabyte B550 Gaming X V2 rev 1.1 | 310 BYN |
| 1069364985 | ASUS TUF B450M Pro S | 230 BYN |

### Активны, но DDR5 — вне ограничений проекта

| ad_id | Лот | Текущая цена |
|---|---|---|
| 1049279891 | Gigabyte B760 Gaming X Gen5 | 387.64 BYN |
| 1029024019 | Gigabyte B760M Gaming X AX | 508.96 BYN |

### Новые лоты, вошедшие в топ-3

| ad_id | Лот | Позиция |
|---|---|---|
| 1075021903 | Intel Core i5-13400 | Intel #3 |
| 1074968077 | ASRock B550M Pro4 (новая, гарантия) | AMD #2 |

## Исключения (с указанием причины)

| ad_id | Причина |
|---|---|
| 1075318739 | defect: маркер в объявлении |
| 1067964836, 1071173866 | defect: «глючит» / «не работает» |
| 1073248395 | defect: «с отлетевшей звуковой картой» |
| 1070922366 | noname_mb: Soyo не в whitelist |
| 1066106609 | other: i9-13950HX «мутант» — нестандартный мобильный CPU на интерпосере, совместимость не гарантирована |
| 1049279891, 1029024019 | wrong_memory: DDR5 |
| 1074467672 (MSI B550M-P Gen3) | **PCIe 3.0 x16** — нарушает правило PCIe ≥4.0 |
| Ряд CPU без цены | no_price («договорная»/«торг») |

## Файлы

- `reports\2026-07-01 2042 — intel+amd ddr4 upgrade — подбор.md` — этот отчёт.
- `reports\2026-07-01 2042 — intel+amd ddr4 upgrade — подбор.json` — структурированная выгрузка топ-пар.
- `scripts\_items.json` — свежие детали 194 объявлений.
- `scripts\_out.json` — выборка 947 объявлений.
- `scripts\_kit_analyzer_out.json` — полный анализ kit-analyzer (тиры + top3 + alternatives + excluded).
- `scripts\.cache\seen_ids.json` — обновлённый реестр ad_id.
- `scripts\.cache\_manifest_2026-07-01.json` — манифест сбора.
- `scripts\.cache\_stale_verification_2026-07-01.json` — результаты прямой проверки 6 stale-лотов.
