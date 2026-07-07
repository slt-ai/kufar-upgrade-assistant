---
name: price-field-scale-dual
description: scripts/_out.json хранит price_byn в копейках (×100), scripts/_items.json — уже в BYN; нужно нормализовать при объединении пулов
metadata:
  type: project
---

В `scripts/_out.json` поле `price_byn` хранится в копейках (например `"42000"` = 420 BYN, `"18888"` = 188.88 BYN), а в `scripts/_items.json` поле `price` уже в BYN (`"420 р."`, `"188.88 р."`).

**Why:** fetcher пишет `_out.json` из listing-API (где цена в минорных единицах), а `_items.json` — из detail-API с человекочитаемой строкой. При суммировании kit_price без нормализации получается 100× ошибка.

**How to apply:** перед любым `kit_price_byn = mb_price + cpu_price` проверять источник: если из `_out.json` — делить на 100, если из `_items.json` — брать как есть. В отчёт всегда писать BYN, не копейки. Связано с [[price-uses-precomputed-field]].