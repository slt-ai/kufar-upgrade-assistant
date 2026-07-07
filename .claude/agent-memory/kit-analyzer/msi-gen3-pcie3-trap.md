---
name: msi-gen3-pcie3-trap
description: MSI B550 boards with "Gen3" suffix (B550M-P Gen3, B550M Pro-VDH WiFi Gen3) have PCIe 3.0 x16 primary slot — fails project PCIe ≥4.0 rule
metadata:
  type: project
---

MSI B550 motherboards whose model name ends in "Gen3" (e.g. **B550M-P Gen3**, **B550M Pro-VDH WiFi Gen3**) use **PCIe 3.0 x16** for the primary GPU slot, NOT PCIe 4.0. The "Gen3" suffix is MSI's explicit marker for this downgrade. A standard B550 (no Gen3 suffix) gives PCIe 4.0 x16 with Ryzen 3000/5000.

**Why:** The project's hard rule requires PCIe ≥4.0 x16 for the GPU. The `_build_quality_top3.py` script scores ALL B550 boards as PCIe 4.0 by chipset default (line ~291-293) and does NOT parse the "gen3" model suffix — so a Gen3 board is wrongly scored with PCIe 4.0 (15→10) and can even top the AMD ranking (happened 2026-06-28: 1074467672 "Msi pro b550m-p gen3" was ranked AMD #1 by the script with q=88.08 — incorrect).

**How to apply:** Exclude any MSI B550 whose title/model contains "gen3" from the top-3, OR heavily demote it with `compatibility=uncertain` and a note "PCIe 3.0 x16 (Gen3 suffix)". Verify the primary slot PCIe version from the model name, not just the chipset. Flag this to the main agent so the report does not recommend a board that violates the user's PCIe requirement. Observed instance: 1074467672.