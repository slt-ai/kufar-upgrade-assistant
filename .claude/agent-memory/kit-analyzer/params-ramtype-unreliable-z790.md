---
name: params-ramtype-unreliable-z790
description: _out.json computers_component_ram_type=4 (DDR4) is unreliable for Z790 boards — body can say DDR5; always verify via body
metadata:
  type: project
---

For LGA1700 Z790 boards, the kufar `computers_component_ram_type` param (code 4 = "DDR4") is NOT authoritative — Z790 has both DDR4 and DDR5 variants and the param can mismatch the actual board.

**Why:** Lot 1072707195 "ASRock Z790 Pro RS" had `ram_type=4` (DDR4) in `scripts/_out.json` params, but the body text (recovered from `scripts/_items_grouped.json`) explicitly says "память 4xDDR5". The board is DDR5-only → must be excluded by the DDR4-only rule (§2.1).

**How to apply:** When a Z790 (chipset code 75) board appears, NEVER trust `params.computers_component_ram_type` alone. Always read the body (title + description) and look for "DDR4"/"DDR5"/"D4" markers before accepting or excluding. Same caution applies to Z690 (dual-variant boards). If body is unavailable (un-fetched delta lot), mark `compatibility=uncertain` and request main-agent body verification — do NOT rank it as a verified PCIe 5.0 candidate on params alone.

Related: [[kufar-chipset-code-map]], [[items-grouped-richer]].