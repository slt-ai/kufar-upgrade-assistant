---
name: amd-cpu-extraction
description: AMD Ryzen CPU model regex must restrict tier to 3/5/7/9 to avoid bogus matches like 'Ryzen 5600 5700X'
metadata:
  type: project
---

Some kufar titles concatenate multiple models, e.g. 'Ryzen 5600 5700X 7500f 5500'. A naive regex like `ryzen\s+(\d+)\s+(\d{3,4}[XGT]?)` can match 'Ryzen 5600 5700' and produce an absurd model with tier=5600, leading to wildly inflated performance estimates. Restrict the tier group to [3579].

**Why:** Prevents garbage CPU models and huge performance scores that distort tier ranking.

**How to apply:** Always use `ryzen\s+([3579])\s+(\d{3,4}[XGT]?)` for model extraction and validate parsed tier is in {3,5,7,9} before scoring.
