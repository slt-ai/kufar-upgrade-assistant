---
name: ryzen-3950x-smt-defect
description: Lot 1073399967 (Ryzen 9 3950X, 490 BYN) has a partial SMT defect — 2 faulty logical threads; was prev AMD rank-3, now excluded
metadata:
  type: project
---

Lot 1073399967 ("AMD Ryzen 9 3950x", 490 BYN, Минск Центральный, seller Дмитрий) has a hardware defect disclosed in the body: "Есть проблемы с 30, 31 логическими ядрами (их можно отключить в Биосе). С физическими ядрами все в порядке."

**Why:** This is a partial defect — SMT threads 30 and 31 are faulty but disableable in BIOS. It was the previous report's AMD future_ready rank-3 (B550 Aorus Master + 3950X = 1040 BYN). The cached `seen_ids.json` had `defect=false` (the fetcher's defect flag did not fire — likely because the marker "проблемы с ... ядрами" is not in the standard defect-vocabulary list). Rule 10 (read body) caught it on manual review.

**How to apply:** Exclude this lot from any tier (defect=true, partial — 2 SMT threads faulty). For AMD future_ready, replace with Ryzen 9 5950X (1073227393, 880 BYN, perf 400, Zen 3, no defect) or Ryzen 9 5900X (1074911306, 850 BYN, perf 330). Also: add "проблемы с ... ядрами" / "есть проблемы с" to the defect-marker vocabulary for future runs — it indicates a hardware fault even though seller hedges with "можно отключить".

Related: [[lga1700-am4-top-combos-2026-07-05]], [[defect-filter-false-positives]].