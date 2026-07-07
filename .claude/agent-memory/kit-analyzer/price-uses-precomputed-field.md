---
name: price-uses-precomputed-field
description: candidates.json items carry _price_byn (int BYN) precomputed by kufar_filter; naive float(item['price']) fails because item['price'] is a localised string like "150 р."
metadata:
  type: feedback
---

When consuming `scripts/_candidates.json` from the kit-analyzer, do **not** parse `item['price']` directly — it is a localised Cyrillic-encoded string (e.g. `"150 р."`) that fails `float()`. Instead, read `item['_price_byn']` (integer BYN) which `kufar_filter.parse_price_byn()` has already populated.

**Why:** `kit_analyzer_run.py` originally parsed `item['price']` directly via regex and saw 0 valid pairs because every candidate fell into `no_price`. The fix was a one-line change to prefer `_price_byn`.

**How to apply:** any future analyzer stage that consumes `scripts/_candidates.json` should use `_price_byn`. If for some reason the field is missing, fall back to a regex parser tolerant of Cyrillic (matches `([\d\s,\.]+)` then strips spaces and commas).
