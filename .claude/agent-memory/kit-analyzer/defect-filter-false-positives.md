---
name: defect-filter-false-positives
description: Text-only defect detection on kufar.by matches seller reassurance phrases like 'без дефектов'
metadata:
  type: project
---

Text search for defect markers ('дефект', 'не работает', etc.) without context produces false positives when sellers write reassurance phrases such as 'без нюансов и скрытых дефектов' or 'идеальное состояние'. The kufar-listings-fetcher already sets an explicit `_defect` boolean per listing based on its own parser/heuristics. In kit-analyzer, trust `_defect` and avoid re-running naive substring checks.

**Why:** False positives eliminated valid listings (e.g., ASRock B660M Pro RS + i5-13400 kit at 1700 BYN was wrongly flagged because the body said 'без дефектов').

**How to apply:** Use `bool(item.get('_defect'))` as the sole defect signal. If the fetcher's flag looks wrong for a specific ad, ask the main agent to re-fetch that ad by direct URL rather than overriding locally.
