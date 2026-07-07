---
name: intel-ddr4-minsk-availability
description: Intel DDR4 motherboard availability in Minsk kufar listings skews heavily toward H610 2-DIMM boards
metadata:
  type: project
---

In the 2026-06-21 fetch of kufar.by (Минск, материнские платы), the only non-defect/non-kit Intel DDR4 LGA1700 boards were H610 models with 2 DIMM slots. All B660/B760/Z690 DDR4 listings were either kits, had no price, or carried defect markers. This means Intel upgrade options for a user with 4 DDR4 sticks are currently limited; a B660/B760/Z690 DDR4 board with 4 DIMM slots should be explicitly requested in the next fetch.

**Why:** User wants to keep 4 DDR4 sticks; 2-slot H610 boards force them to drop half their RAM.

**How to apply:** When Intel shortlists repeatedly surface only 2-slot H610 boards, flag the limitation to the main agent and ask for a targeted re-fetch of B660/B760/Z690 DDR4 in Минск, plus direct-link checks on any previously seen 4-slot boards.
