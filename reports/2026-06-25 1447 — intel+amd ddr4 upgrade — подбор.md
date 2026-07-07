# Подбор комплектов mb+cpu — 2026-06-25 1447

**Источник:** kufar.by Минск. **Сценарий:** кросс-комбинирование мат. плат и процессоров.

**Конфигурация ПК:** Intel Core i7-9750H / MSI B250M Pro-VDH / 48 ГБ DDR4 (4 планки) / NVIDIA GeForce RTX 5060 Ti.

**Фильтры:** DDR4 only, PCI-E ≥4.0 x16, Intel LGA1700 (DDR4) / AMD AM4, whitelist брендов мат. плат.

**Ранжирование:** quality score = motherboard_quality (0–100) + cpu_quality (0–30).
CPU вклад = (perf − 100) × 0.068, cap 30. i7-9750H=100 → 0, i9-14900K=540 → 30.

Веса для материнской платы (по указанию пользователя):

- **DIMM-слоты: 40** (4 → 40, 2 → 0). Критично: у пользователя 4 планки DDR4.
- **VRM-запас: 20** (15+ фаз → 20; 10+ → 16; 7+ → 10; иначе 4).
- **PCI-E версия: 15** (5.0 → 15, 4.0 → 10, 3.0 → 0).
- **M.2-слоты: 10** (2× → 10, 1× → 5).
- **Сеть: 5** (2.5G → 5, 1G → 2).
- **Разгон/BCLK/OC-серия: 5**.
- **Бренд-премиум (ASUS/MSI > ASRock/Gigabyte > Biostar): 5**.

CPU perf — относительная производительность vs Intel Core i7-9750H (baseline=100).

---

## Сводка

- **Intel top-1 (по качеству):** Asrock B660M PG Riptide + Intel Core i5-12400 (LGA 1700) — 1000 BYN (q=98.1).
  - **Приоритетная платформа:** ASRock B660M PG Riptide — единственная с 4 DIMM + 15-фаз VRM + 2.5G + 2× M.2 + BCLK.
- **AMD top-1 (по качеству):** Материнская плата Gigabyte B550 Gaming X V2 (rev.  + Процессор AMD Ryzen 9 5950X — 1300 BYN (q=100.16).
  - Сменился относительно 2026-06-24 1622 (был ASUS TUF B450M Pro S + 3950X). Причина: новая плата Gigabyte B550 Gaming X V2 (1019993393) ранее отфильтровывалась по ложному defect-маркеру «без дефектов» — после фикса фильтра получает +OC и попадает в топ-1. q=100.16 vs q=98.08, цена выросла с 720 до 1300 BYN.
- **Готовых китов (mb+cpu+ram):** 11 в Минске с DDR4 (LGA1700/AM4), от 170 BYN до 5300 BYN.
  - Лот 1073979712 (i5-13400 + B660M + 32 ГБ DDR4) — 1600 BYN, единственный готовый Intel-сет с B660 и 4 DIMM.
- **Бюджетный Intel (H610M, 2 DIMM):** Материнская плата GIGABYTE H610M H V3 DDR4 + Intel Core i5-12400 (LGA 1700) — 650 BYN (q=24.1, для тех, кому критична цена).

## Топ-3 Intel (по quality score)

| # | Мат. плата | Chipset | DIMM | PCIe | M.2 | CPU | Perf | Цена кита | Quality |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Asrock B660M PG Riptide | B660 | 4 | 4 | 2 | Intel Core i5-12400 (LGA 1700) | 175 | 1000 BYN | **98.1** |
| 2 | Материнская плата Gigabyte B760 Gaming X Gen5 | B760 | 4 | 4 | 1 | Продаю процессор i7-13700F | 380 | 1148 BYN | **88.04** |
| 3 | Материнская плата Gigabyte B760M Gaming X AX (rev. | B760 | 4 | 4 | 1 | Продаю процессор i7-13700F | 380 | 1263 BYN | **88.04** |

### INTEL #1 — quality 98.1 (mb 93.0 + cpu 5.1)
- **Мат. плата:** Asrock B660M PG Riptide — 500 BYN — Илья — [ссылка](https://www.kufar.by/item/1074338703)
  - chip: B660, socket: LGA1700, DIMM: 4, PCIe 4.x16, M.2: 2, LAN: 2.5G, OC: True, VRM: 15-фаз, brand: ASRock
- **Процессор:** Intel Core i5-12400 (LGA 1700) — 500 BYN — Антон — [ссылка](https://www.kufar.by/item/1073950867)
  - perf 175 (vs i7-9750H baseline=100), kit 1000 BYN
  - ПРИОРИТЕТНАЯ платформа: 4 DIMM + 15-фаз VRM + 2.5G + 2× M.2 + поддержка BCLK.

### INTEL #2 — quality 88.04 (mb 69.0 + cpu 19.04)
- **Мат. плата:** Материнская плата Gigabyte B760 Gaming X Gen5 — 378 BYN — ООО Медиастор — [ссылка](https://www.kufar.by/item/1049279891)
  - chip: B760, socket: LGA1700, DIMM: 4, PCIe 4.x16, M.2: 1, LAN: 1G, OC: True, VRM: 1-фаз, brand: Gigabyte
- **Процессор:** Продаю процессор i7-13700F — 770 BYN — Вадим — [ссылка](https://www.kufar.by/item/1071188333)
  - perf 380 (vs i7-9750H baseline=100), kit 1148 BYN

### INTEL #3 — quality 88.04 (mb 69.0 + cpu 19.04)
- **Мат. плата:** Материнская плата Gigabyte B760M Gaming X AX (rev. 1.x) — 493 BYN — ООО Медиастор — [ссылка](https://www.kufar.by/item/1029024019)
  - chip: B760, socket: LGA1700, DIMM: 4, PCIe 4.x16, M.2: 1, LAN: 1G, OC: True, VRM: 0-фаз, brand: Gigabyte
- **Процессор:** Продаю процессор i7-13700F — 770 BYN — Вадим — [ссылка](https://www.kufar.by/item/1071188333)
  - perf 380 (vs i7-9750H baseline=100), kit 1263 BYN

### Бюджетный вариант (не вошёл в топ-3 по качеству)

### INTEL #— — quality 24.1 (mb 19.0 + cpu 5.1)
- **Мат. плата:** Материнская плата GIGABYTE H610M H V3 DDR4 — 150 BYN — Тихон  — [ссылка](https://www.kufar.by/item/1073075382)
  - chip: H610, socket: LGA1700, DIMM: 2, PCIe 4.x16, M.2: 0, LAN: 1G, OC: False, VRM: 5-фаз, brand: Gigabyte
- **Процессор:** Intel Core i5-12400 (LGA 1700) — 500 BYN — Антон — [ссылка](https://www.kufar.by/item/1073950867)
  - perf 175 (vs i7-9750H baseline=100), kit 650 BYN
  - Слабый VRM, 2 DIMM — пользователю придётся пожертвовать планками. Только для тех, кому нужна минимальная цена.

## Топ-3 AMD (по quality score)

| # | Мат. плата | Chipset | DIMM | PCIe | M.2 | CPU | Perf | Цена кита | Quality |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Материнская плата Gigabyte B550 Gaming X V2 (rev.  | B550 | 4 | 4 | 1 | Процессор AMD Ryzen 9 5950X | 470 | 1300 BYN | **100.16** |
| 2 | Asus TUF Gaming B450M Pro S материнская плата AM4 | B550 | 4 | 4 | 1 | AMD Ryzen 9 3950x | 410 | 720 BYN | **98.08** |
| 3 | Материнская плата MSI B550-A Pro | B550 | 4 | 4 | 1 | Процессор AMD Ryzen 9 5950X | 470 | 1295 BYN | **97.16** |

### AMD #1 — quality 100.16 (mb 75.0 + cpu 25.16)
- **Мат. плата:** Материнская плата Gigabyte B550 Gaming X V2 (rev. 1.0) — 350 BYN — ООО Медиастор — [ссылка](https://www.kufar.by/item/1019993393)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.x16, M.2: 1, LAN: 1G, OC: True, VRM: 8-фаз, brand: Gigabyte
- **Процессор:** Процессор AMD Ryzen 9 5950X — 950 BYN — Пользователь — [ссылка](https://www.kufar.by/item/1073227393)
  - perf 470 (vs i7-9750H baseline=100), kit 1300 BYN

### AMD #2 — quality 98.08 (mb 77.0 + cpu 21.08)
- **Мат. плата:** Asus TUF Gaming B450M Pro S материнская плата AM4 — 230 BYN — Van — [ссылка](https://www.kufar.by/item/1069364985)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.x16, M.2: 1, LAN: 1G, OC: True, VRM: 8-фаз, brand: ASUS
- **Процессор:** AMD Ryzen 9 3950x — 490 BYN — Дмитрий — [ссылка](https://www.kufar.by/item/1073399967)
  - perf 410 (vs i7-9750H baseline=100), kit 720 BYN

### AMD #3 — quality 97.16 (mb 72.0 + cpu 25.16)
- **Мат. плата:** Материнская плата MSI B550-A Pro — 345 BYN — ООО Медиастор — [ссылка](https://www.kufar.by/item/1063525487)
  - chip: B550, socket: AM4, DIMM: 4, PCIe 4.x16, M.2: 1, LAN: 1G, OC: False, VRM: 8-фаз, brand: MSI
- **Процессор:** Процессор AMD Ryzen 9 5950X — 950 BYN — Пользователь — [ссылка](https://www.kufar.by/item/1073227393)
  - perf 470 (vs i7-9750H baseline=100), kit 1295 BYN

## Готовые киты

Готовые наборы mb+cpu (и часто +ram) в одном объявлении. Не разбираем на компоненты — продаются и работают как единое целое. Всего найдено 11 лотов в Минске под DDR4 (LGA1700/AM4).

| # | Платформа | Цена | CPU (perf) | Описание | Продавец | Лот |
|---|---|---|---|---|---|---|
| 1 | AM4 | 170 BYN | 125 | Комплект АМ4 | Виталий | [ссылка](https://www.kufar.by/item/1074495798) |
| 2 | AM4 | 245 BYN | — | Комплект Asrock Pro AB350+Ryzen 5 2400g | Алексей | [ссылка](https://www.kufar.by/item/1073870268) |
| 3 | AM4 | 280 BYN | 165 | Процессор AMD Ryzen 5 4500 в комплекте с кулером | Anton | [ссылка](https://www.kufar.by/item/1046837951) |
| 4 | AM4 | 350 BYN | 145 | КоМПЛЕКТ RYZEN 7 1700+ MB A320M-K+8Gb+ОХЛАД | Сергей | [ссылка](https://www.kufar.by/item/1064953017) |
| 5 | LGA1700 | 390 BYN | — | Комплект Xeon 2680+плата X79+кулер+32(64)gb DDR | ИП Рогачевский Г.В. | [ссылка](https://www.kufar.by/item/1062347171) |
| 6 | AM4 | 540 BYN | 170 | Комплект системного блока Ryzen 7 | Фрунзенский район  | [ссылка](https://www.kufar.by/item/1074495373) |
| 7 | AM4 | 720 BYN | 200 | Комплект Ryzen материнская плата ОЗУ проц кулер | Adel Nako | [ссылка](https://www.kufar.by/item/1074061887) |
| 8 | LGA1700 | 750 BYN | — | Полный игровой комплект или пк | Егор | [ссылка](https://www.kufar.by/item/1074109353) |
| 9 | AM4 | 1000 BYN | 150 | Комплект AM4 asus tuf b450 ryzen 3600 32gb | Николай | [ссылка](https://www.kufar.by/item/1074047062) |
| 10 | LGA1700 | 1600 BYN | 200 | комплект Intel Core i5-13400 + B660M + 32GB DDR4 | vlad | [ссылка](https://www.kufar.by/item/1073979712) |
| 11 | AM4 | 5300 BYN | 290 | КОМПЛЕКТ: мать + проц + кулер + память + карта | Мікіта | [ссылка](https://www.kufar.by/item/1073125074) |

**Заметки по конкретным лотам:**

- **1073979712 (1600 BYN)** — Intel Core i5-13400 (10c/16t, perf≈200) + ASRock B660M Pro RS + Kingston FURY Beast 4×8 ГБ DDR4-3600. **Единственный готовый Intel-сет с 4 DIMM и B660** в текущей выборке. Подходит для переиспользования планок RAM. PCIe 4.0 x16.

## Сравнение Intel vs AMD (по качеству)

| Платформа | Мат. плата | CPU | 4 планки DDR4 | Quality |
|---|---|---|---|---|
| Intel | Asrock B660M PG Riptide | Intel Core i5-12400 (LGA 1700) | ДА | 98.1 |
| AMD | Материнская плата Gigabyte B550 Gaming X | Процессор AMD Ryzen 9 5950X | ДА | 100.16 |

## Изменения относительно отчёта 2026-06-24 1622

Сравнение топ-3 и цен относительно предыдущего прогона:

| Платформа | Позиция | Что изменилось |
|---|---|---|
| Intel | #1 | Без изменений: ASRock B660M PG Riptide (500 BYN) + i5-12400 (500 BYN) = 1000 BYN, q=98.1 |
| AMD | #1 | **СМЕНИЛСЯ**: ранее ASUS TUF B450M Pro S + Ryzen 9 3950X (720 BYN, q=98.08), теперь Gigabyte B550 Gaming X V2 + Ryzen 9 5950X (1300 BYN, q=100.16). Причина: новая Gigabyte-плата 1019993393 (ранее отфильтрована по ложному defect-маркеру «без дефектов») теперь корректно проходит фильтр и получает +OC за «Gaming X». q=100.16 vs 98.08 — чистый выигрыш по scoring при росте цены на 580 BYN. |
| Intel | 1071062100 (MSI Pro B760M-A DDR4 II) | Цена **430.25 → 414.45 BYN** (−15.80, −3.7%); kit 1200 → 1184.45 BYN |
| Intel | 1042521893 (ASUS ROG Strix B760-F Gaming) | Без изменений (550 BYN) |
| AMD | 1063525487 (MSI B550-A Pro) | Цена **346 → 345.04 BYN** (−0.96, −0.3%); kit 1296 → 1295.04 BYN |
| AMD | 1020339850 (MSI B550M Pro-VDH WiFi) | Цена **322 → 318.03 BYN** (−3.97, −1.2%); kit 1272 → 1268.03 BYN |
| AMD | 1069364985 (ASUS TUF B450M Pro S) + 1073399967 (Ryzen 9 3950X) | Без изменений (230 + 490 = 720 BYN). Перешёл с #1 на #2 в AMD-топе из-за появления новой Gigabyte-платы. |
| Intel | 1049279891 (Gigabyte B760 Gaming X Gen5, 378.31 BYN) | **НОВАЯ** платформа Intel LGA1700 с 4 DIMM, попала в топ-3 Intel (#2, q=88.04). Gaming X → +OC. Без явного PCIe-Gen5-маркера в title — body mojibake; реальные характеристики требуют прямой проверки ссылки. |
| Intel | 1029024019 (Gigabyte B760M Gaming X AX rev.1.x, 493.21 BYN) | **НОВАЯ** платформа, попала в топ-3 Intel (#3, q=88.04). |
| Intel | 1074498967 (Gigabyte B760 Gaming X AX DDR4, 450 BYN) | **НОВАЯ** платформа Intel LGA1700 с 4 DIMM. По парсеру: B760, 4 DIMM, PCIe 4.0, ATX, Gaming X → +5 OC (mb_score=64). Не попала в топ-3 — body mojibake, реальные характеристики (2.5G, 2× M.2, 12+1+1 VRM) не подтверждены. Требует прямой проверки ссылки. |
| AMD | 1072583055 (Ryzen 7 3700X PRO, 320 BYN) | Цена **340 → 320 BYN** (−20, −5.9%). Прошла мимо топ-3 — комбинация с TUF B450M даёт q=89.6 vs q=100.16 у нового топ-1; 3700X PRO остаётся хорошим бюджетным вариантом для AMD-сборки. |
| AMD | 1019993393 (Gigabyte B550 Gaming X V2, 349.52 BYN) | **НОВАЯ** платформа (ранее отфильтрована по ложному defect-маркеру «без дефектов»). Занимает #1 AMD-топ. |
| Intel | 1074338703 (Asrock B660M PG Riptide) | Без изменений (500 BYN, B660, 4 DIMM, 15-фаз VRM). Включаем как Intel-платформу по требованию. |

## Файлы

- `reports\2026-06-25 1447 — intel+amd ddr4 upgrade — подбор.md` — этот отчёт.
- `reports\2026-06-25 1447 — intel+amd ddr4 upgrade — подбор.json` — структурированная выгрузка (JSON).
- `reports\2026-06-25 1447 — intel+amd ddr4 upgrade — подбор.csv` — таблица топ-пар (CSV).
