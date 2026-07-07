---
name: webfetch-kufar-ratelimit
description: WebFetch on kufar.by item pages rate-limits hard — bursts >6 parallel → 429, then "unable to verify domain" block; throttle to 2-3 per batch
metadata:
  type: feedback
---

When point-checking kufar.by item URLs (rule 9 direct-link verification), do NOT fire many WebFetch calls in one batch.

**Why:** On 2026-07-07 I fired 16 WebFetch calls in parallel against `https://www.kufar.by/item/<id>`. The first ~6 returned useful data (some 200, some 404, some 429). After that, every subsequent call returned `HTTP 429 Too Many Requests`, and after a 40-60s pause the tool started returning `"Unable to verify if domain www.kufar.by is safe to fetch"` (a transient network-policy block, not a real safety issue). The block persisted across retries and prevented verifying several candidates.

**How to apply:**
- Throttle WebFetch to 2-3 calls per batch, then wait 30-60s before the next batch.
- 404 responses are reliable verdicts (kufar returns 404 for removed ads) — count them immediately.
- For 429s, retry individually after a pause rather than re-batching all at once.
- When WebFetch is blocked, fall back to cached bodies in `scripts/_items_grouped.json` (see [[items-grouped-richer]]) and mark un-fetched lots `compatibility=uncertain` with a `needs_main_agent.reverify_urls` entry — do NOT block the whole ranking on WebFetch availability.
- A 404 on a prev top candidate is a confirmed removal; a 200 with matching price confirms active+unchanged.

Related: [[items-grouped-richer]], [[params-ramtype-unreliable-z790]].