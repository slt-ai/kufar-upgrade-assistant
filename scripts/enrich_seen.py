"""
Enrich scripts/.cache/seen_ids.json with defect / no_price / stale flags using
scripts/_candidates.json produced by kufar_filter.py.

Also prints a short stats line suitable for the fetcher report.
"""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN_PATH = os.path.join(ROOT, "scripts", ".cache", "seen_ids.json")
CANDIDATES_PATH = os.path.join(ROOT, "scripts", "_candidates.json")


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def main():
    seen = load_json(SEEN_PATH)
    candidates = load_json(CANDIDATES_PATH)
    if not candidates:
        print("[warn] no candidates file; nothing to enrich", file=sys.stderr)
        return

    defect_ids = set(
        str(x) for x in
        (candidates.get("skipped_defect_mb", []) + candidates.get("skipped_defect_cpu", []))
    )
    no_price_ids = set(
        str(x) for x in
        (candidates.get("skipped_no_price_mb", []) + candidates.get("skipped_no_price_cpu", []))
    )
    kit_cpu_ids = set(str(x) for x in candidates.get("skipped_kit_cpus", []))

    good_ids: set[str] = set()
    for key in ("intel_mb", "amd_mb", "intel_mb_kit", "amd_mb_kit",
                "intel_cpus", "amd_cpus"):
        for item in candidates.get(key, []):
            good_ids.add(str(item.get("id")))

    updated = 0
    for aid, entry in seen.items():
        changed = False
        if aid in defect_ids:
            if not entry.get("defect"):
                entry["defect"] = True
                changed = True
        if aid in no_price_ids:
            if not entry.get("no_price"):
                entry["no_price"] = True
                changed = True
        if aid in kit_cpu_ids:
            if not entry.get("kit_cpu"):
                entry["kit_cpu"] = True
                changed = True
        if aid in good_ids:
            # Candidate lots are confirmed defect-free and price-bearing.
            if entry.get("defect"):
                entry["defect"] = False
                changed = True
            if entry.get("no_price"):
                entry["no_price"] = False
                changed = True
        if changed:
            updated += 1

    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)

    mb_total = len(candidates.get("intel_mb", [])) + len(candidates.get("amd_mb", []))
    cpu_total = len(candidates.get("intel_cpus", [])) + len(candidates.get("amd_cpus", []))
    print(f"[info] enriched {updated} registry entries", file=sys.stderr)
    print(f"[stats] mb={mb_total} cpu={cpu_total} "
          f"defect_mb={len(candidates.get('skipped_defect_mb', []))} "
          f"defect_cpu={len(candidates.get('skipped_defect_cpu', []))} "
          f"no_price_mb={len(candidates.get('skipped_no_price_mb', []))} "
          f"no_price_cpu={len(candidates.get('skipped_no_price_cpu', []))} "
          f"kit_cpus={len(kit_cpu_ids)}", file=sys.stderr)


if __name__ == "__main__":
    main()
