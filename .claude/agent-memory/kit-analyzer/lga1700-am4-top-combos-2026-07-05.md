---
name: lga1700-am4-top-combos-2026-07-05
description: Рабочие топ-комбо LGA1700/AM4 DDR4 на 2026-07-05 — какие пары MB+CPU прошли в топ и почему, для ре-валидации на следующем прогоне
metadata:
  type: project
---

Снимок шорт-листа на 2026-07-05 (прогон 22:12–22:24). Все цены в BYN, регион Минск.

**Intel (LGA1700, DDR4):**
- balanced winner: ASRock Z790M PG Lightning D4 (1075318739, 180) + i5-13400F (1075813244, 450) = 630 BYN, perf 200. Z790 = PCIe 5.0, 4 DIMM.
- future_ready: та же Z790 + i9-12900K (1073208894, 755) = 935 BYN, perf 400. Альтернатива i7-13700KF (1075797390, 749).
- entry: ASRock H610M-HDV (1073712669, 150) + i3-12100F (1075097174, 200) = 350 BYN — но 2 DIMM, для пользователя с 4×DDR4 хуже Z790-варианта.

**AMD (AM4, DDR4):**
- balanced: ASRock B550 ATX (1073248395, 200) + Ryzen 5 5600 (1072541437, 350) = 550 BYN, perf 180.
- future_ready: Gigabyte B550 Aorus Master (1075920044, 550) + Ryzen 9 3950X (1073399967, 490) = 1040 BYN, perf 350, 16c/32t — топ под локальные LLM.
- entry: ASRock B550 (200) + Ryzen 5 2600 (1075806076, 100) = 300 BYN, perf ~100 (не хуже baseline).

**Why:** эти пары максимизируют perf/price при соблюдении DDR4 + PCIe ≥4.0 + 4-DIMM + whitelist брендов. Z790 за 180 BYN — аномально дёшево для PCIe 5.0, та же плата в balanced и future_ready.

**How to apply:** на следующем прогоне сначала проверить, живы ли эти 7 ad_id (особенно 1075318739 — «аномально дёшево» часто = быстро купят). Если Z790 1075318739 снят, fallback на Gigabyte B760 Gaming X AX DDR4 (1074498967, 420, PCIe 4.0). Связано с [[intel-ddr4-minsk-availability]].