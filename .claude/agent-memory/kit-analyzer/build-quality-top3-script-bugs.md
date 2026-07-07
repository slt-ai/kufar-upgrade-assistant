---
name: build-quality-top3-script-bugs
description: _build_quality_top3.py fails on mojibake titles — use params.computersComponent* as ground truth, not title keywords
metadata:
  type: project
---

The `_build_quality_top3.py` ranking script has two bugs that silently drop valid boards from the top-3 when the kufar detail `title`/`body` are mojibake (UTF-8 Cyrillic stored correctly but title lacks ASCII brand/chipset keywords).

**Why:** `mb_ok()` requires `any(b in title for b in MB_WHITELIST)` — checks brand only in the title text, ignoring `params.computersComponentBrand.vl`. `parse_mb()` infers chipset/socket from title+body keywords, ignoring `params.computersComponentChipset.vl` / `computersComponentSocket.vl`. When a listing's title is generic ("Материнская плата Z690 Gaming X DDR4" — no "Gigabyte" word) or body is mojibake without chipset keywords, the board is dropped as `noname` or `other` even though params carry the authoritative brand/chipset/socket/DIMM.

**How to apply:** When validating/ranking, ALWAYS cross-check `params.computersComponentBrand.vl`, `computersComponentChipset.vl`, `computersComponentSocket.vl`, `computersComponentNumberSlots.vl` — these are kufar's structured fields and survive mojibake. Treat them as ground truth; use title/body only to fill gaps (VRM phases, M.2 count, LAN speed, OC series). Known false drops observed 2026-06-28: 1074829435 (Gigabyte Z690 Gaming X DDR4, falsely `noname`) and 1074867167 (Gigabyte B550 Gaming X V2 rev 1.1, falsely `other` via chipset=None). Also: `parse_mb` defaulted 1074086159 (ASRock B550M-HDV) to 4 DIMM, but params correctly say 2 DIMM — DIMM count must come from params, not mATX heuristic.

Related: [[price-uses-precomputed-field]] (always read `source_listing.price_byn`, not the display string).

Also note the script's `## Изменения относительно отчёта` table is hardcoded to compare against 2026-06-24 1622 (see CLAUDE.md memory `project-build-report-stale-naming`) — do not trust that section; recompute the diff yourself against the actual previous report.