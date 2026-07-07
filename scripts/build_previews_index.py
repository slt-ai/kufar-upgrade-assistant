"""Сборка каталога previews/index.html со ссылками на все темы.

Каждая карточка миниатюры окрашена в CSS-переменные своей темы (через
scoped <style> в data-атрибуте) — пользователь видит палитру до клика.

Использование: python scripts/build_previews_index.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREVIEWS = ROOT / "reports" / "previews"
sys.path.insert(0, str(ROOT / "scripts"))
from md_styles import BASE as _BASE, STYLES  # noqa: E402

SOURCE_MD = "2026-07-07 0059 — intel+amd ddr4 upgrade — подбор"  # stem отчёта


def _extract_vars(css: str) -> dict[str, str]:
    """Вытащить пары --name:value из :root{...} блока CSS темы."""
    out: dict[str, str] = {}
    m = re.search(r":root\s*\{([^}]+)\}", css, flags=re.S)
    if not m:
        return out
    for line in m.group(1).split(";"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if k.startswith("--") and v:
            out[k] = v
    return out


def _card_scoped_css(slug: str, css: str) -> str:
    """Сгенерировать CSS, который применяет палитру темы к .card-{slug}.

    Карточка получает тонкую обводку и слабый glow в accent-цвете темы —
    чтобы светлые темы не «светились белым» на тёмной подложке, а тёмные
    не сливались с фоном.
    """
    vars_ = _extract_vars(css)
    decls = ";".join(f"{k}:{v}" for k, v in vars_.items())
    return (
        # базовая карточка: фон/текст темы + accent-обводка
        f".card-{slug}{{"
        f"background:var(--surface);color:var(--text);"
        f"border:1px solid var(--border);"
        f"border-radius:14px;padding:18px 20px;display:block;text-decoration:none;"
        f"transition:transform .18s,border-color .18s,box-shadow .18s;"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
        f"position:relative"
        f"}}\n"
        # accent-ring снаружи карточки: 1px border в accent + слабый glow
        f".card-{slug}::before{{"
        f"content:'';position:absolute;inset:-1px;border-radius:14px;"
        f"padding:1px;background:var(--accent);-webkit-mask:"
        f"linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);"
        f"-webkit-mask-composite:xor;mask-composite:exclude;"
        f"opacity:.45;transition:opacity .18s;pointer-events:none"
        f"}}\n"
        f".card-{slug}:hover{{"
        f"transform:translateY(-3px);"
        f"box-shadow:0 0 0 1px var(--accent),0 12px 32px rgba(0,0,0,.45),"
        f"0 0 24px color-mix(in srgb,var(--accent) 35%,transparent)"
        f"}}\n"
        f".card-{slug}:hover::before{{opacity:1}}\n"
        f".card-{slug} .num{{color:var(--accent);font-size:12px;font-weight:600;"
        f"letter-spacing:.04em;text-transform:uppercase}}\n"
        f".card-{slug} .title{{font-size:18px;font-weight:700;margin:4px 0 8px;"
        f"color:var(--text)}}\n"
        f".card-{slug} .desc{{color:var(--muted);font-size:13.5px;line-height:1.5}}\n"
        f".card-{slug} .go{{margin-top:12px;font-size:12px;color:var(--accent);"
        f"font-weight:600;letter-spacing:.02em}}\n"
        f".card-{slug} .swatches{{display:flex;gap:6px;margin-top:12px}}\n"
        f".card-{slug} .sw{{"
        f"width:18px;height:18px;border-radius:5px;"
        f"border:1px solid rgba(127,127,127,.25)"
        f"}}\n"
        # навешиваем переменные темы (через дубликат селектора)
        f".card-{slug}{{" + decls + "}"
    )


def _build_cards() -> tuple[str, str]:
    """Возвращает (cards_html, all_scoped_css)."""
    cards_html: list[str] = []
    scoped_blocks: list[str] = []
    for n, (slug, (title, desc, _css)) in enumerate(STYLES.items(), 1):
        swatches = (
            '<div class="swatches">'
            '<div class="sw" style="background:var(--bg)"></div>'
            '<div class="sw" style="background:var(--surface)"></div>'
            '<div class="sw" style="background:var(--accent)"></div>'
            '<div class="sw" style="background:var(--text)"></div>'
            '</div>'
        )
        cards_html.append(
            f'    <li><a class="card-{slug}" href="./{SOURCE_MD}.{slug}.html">'
            f'<div class="num">№{n} · {slug}</div>'
            f'<div class="title">{title}</div>'
            f'<div class="desc">{desc}</div>'
            f'{swatches}'
            f'<div class="go">открыть →</div>'
            f'</a></li>'
        )
        scoped_blocks.append(_card_scoped_css(slug, _css))
    return "\n".join(cards_html), "\n".join(scoped_blocks)


CARDS, SCOPED = _build_cards()

HTML = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Стили оформления отчётов · kufar upgrade reports</title>
<style>
:root{{
  --page-bg:#0a0a12; --page-text:#e8e8f0; --page-muted:#8b8b9c;
  --page-border:#1e1e2a; --page-accent:#1aff9c;
}}
*{{box-sizing:border-box}}
html,body{{background:var(--page-bg);color:var(--page-text)}}
body{{margin:0;
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  min-height:100vh;
  background:
    radial-gradient(1200px 600px at 50% -200px,rgba(26,255,156,.06),transparent 70%),
    var(--page-bg);
}}
header.topbar{{background:rgba(10,10,18,.85);
  backdrop-filter:saturate(180%) blur(12px);
  -webkit-backdrop-filter:saturate(180%) blur(12px);
  border-bottom:1px solid var(--page-border);position:sticky;top:0;z-index:10}}
.topbar-inner{{max-width:1100px;margin:0 auto;padding:10px 20px;
  display:flex;align-items:baseline;gap:14px}}
.brand{{font-weight:700;color:var(--page-accent);text-decoration:none;font-size:15px}}
main{{max-width:1100px;margin:32px auto 80px;padding:0 20px}}
h1{{font-size:32px;margin:0 0 6px;padding-bottom:10px;
  border-bottom:2px solid var(--page-accent);letter-spacing:-.02em;
  color:#fff;font-weight:700}}
.subtitle{{color:var(--page-muted);margin:0 0 8px;font-size:15px}}
.hint{{color:var(--page-muted);font-size:13px;margin:0 0 28px}}
ul.cards{{list-style:none;padding:0;margin:0;
  display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));
  gap:18px}}
ul.cards li{{margin:0}}
footer{{max-width:1100px;margin:0 auto;padding:20px;color:var(--page-muted);
  font-size:12px;border-top:1px solid var(--page-border)}}
/* per-card scoped styles (палитра каждой темы) */
{SCOPED}
</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/">← kufar upgrade reports</a>
    <span style="color:var(--page-muted);font-size:13px">preview · {len(STYLES)} стилей</span>
  </div>
</header>
<main>
<h1>Стили оформления отчётов</h1>
<p class="subtitle">Один и тот же отчёт (2026-07-07, intel+amd ddr4 upgrade) в {len(STYLES)} визуалах.</p>
<p class="hint">Каждая карточка окрашена в палитру своей темы + accent-кольцо по контуру. Кликни, чтобы увидеть тему применённой к полному отчёту.</p>
<ul class="cards">
{CARDS}
</ul>
</main>
<footer>{len(STYLES)} preview-страниц · один и тот же MD-источник</footer>
</body>
</html>
"""


def main() -> int:
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    out = PREVIEWS / "index.html"
    out.write_text(HTML, encoding="utf-8")
    print(f"  {out.relative_to(ROOT)}")
    print(f"  превью-страниц: {len(STYLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
