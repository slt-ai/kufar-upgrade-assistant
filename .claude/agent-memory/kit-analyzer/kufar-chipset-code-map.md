---
name: kufar-chipset-code-map
description: Kufar computers_component_chipset numeric codes → labels, built from _items.json params; needed because _out.json stores only codes
metadata:
  type: reference
---

`scripts/_out.json` and `scripts/_out_delta.json` store `params.computers_component_chipset` as a numeric code with NO label. Map (built from `scripts/_items.json` params.vl cross-reference):

**Intel (LGA1700):**
- 31 = Intel B660
- 32 = Intel B760
- 53 = Intel H610
- 75 = Intel Z790
- (Z690, H670, H770 codes not yet observed in Minsk pool)

**AMD (AM4):**
- 11 = AMD B550 (PCIe 4.0 — passes filter)
- 10 = AMD B450 (PCIe 3.0 — excluded)
- 9 = AMD B350 (PCIe 3.0 — excluded)
- 6 = AMD A320 (PCIe 3.0 — excluded)
- 20 = AMD X470 (PCIe 3.0 for GPU — excluded; not in whitelist {B550, X570})
- (X570 code not yet observed — no X570 boards in Minsk pool as of 2026-07-07)

**Socket codes:** 19 = LGA1700, 6 = AM4, 16 = LGA1200, 12 = LGA1151v2.
**Brand codes (whitelist pass):** 12 = ASRock, 13 = ASUS, 14 = BIOSTAR, 31 = Gigabyte, 54 = MSI. Exclude: 17 = Colorful, 51 = Maxsun, 41 = Intel (CPU brand), 9 = AMD (CPU brand).
**RAM type:** 4 = DDR4, 5 = DDR5. (Caveat: for Z790 the param is unreliable — see [[params-ramtype-unreliable-z790]].)
**DIMM slots:** 2 = 2 slots, 4 = 4 slots.
**Form factor:** 4 = ATX, 6 = mATX, 7 = miniITX.

**How to apply:** When filtering `_out.json`, decode chipset codes with this map. Boards with chipset=None need body/title fallback. AM4 boards with chipset ∉ {11 (B550)} are excluded by PCIe ≥4.0 rule (X570 would pass but is absent).

Related: [[params-ramtype-unreliable-z790]], [[items-grouped-richer]].