---
name: items-grouped-richer
description: scripts/_items_grouped.json has 118 MB / 934 CPU with bodies — far richer than scripts/_items.json (23/167); check it first for cached bodies
metadata:
  type: reference
---

When recovering cached ad bodies (title + body text) for compatibility/defect checks, check `scripts/_items_grouped.json` FIRST — it contains 118 MB and 934 CPU entries with full bodies, versus `scripts/_items.json` which only has 23 MB and 167 CPU.

**Why:** The fetcher writes a grouped/merged detail cache that accumulates across runs, while `_items.json` is a smaller per-run snapshot. The grouped file recovered the body of 1072707195 (ASRock Z790 Pro RS → "4xDDR5") which was missing from `_items.json`, allowing a DDR5 exclusion that params alone would have missed.

**How to apply:** Read order for cached bodies: `scripts/_items_grouped.json` → `scripts/_items.json` → `scripts/.cache/seen_ids.json` (last resort, no body). Bodies in both files are mojibake (cp1251 bytes decoded as utf-8) — recover with `body.encode('utf-8', errors='ignore').decode('cp1251', errors='ignore')`. If still missing, fall back to WebFetch on the direct URL (throttled — see [[webfetch-kufar-ratelimit]]).

Related: [[params-ramtype-unreliable-z790]], [[price-field-scale-dual]].