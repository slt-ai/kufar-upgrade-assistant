#!/usr/bin/env python3
"""Конвертация отчёта-подбора .md -> standalone .html со встроенной стилизацией.

Использование:
    python scripts/md_to_html.py reports/2026-07-05\\ 2235\\ —\\ ....md
    python scripts/md_to_html.py --all            # все reports/*.md
    python scripts/md_to_html.py --all --out-dir reports

HTML самодостаточный (CSS inline, без внешних ассетов), с тёмной темой
через prefers-color-scheme, скроллящимися таблицами и стилизованными
blockquote-поправками. На сервер Caddy кладётся только *.html.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import markdown

from md_styles import STYLES, get_css

CSS = get_css(None)  # обратная совместимость: legacy-тема

TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/">← kufar upgrade reports</a>
    <span class="topbar-title">{title_short}</span>
  </div>
</header>
<main class="report">
{body}
</main>
<footer class="report-footer">Сгенерировано из Markdown · подбор комплектации на kufar.by</footer>
</body>
</html>
"""

EXTENSIONS = ["tables", "fenced_code", "attr_list", "sane_lists", "md_in_html", "footnotes", "def_list"]

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>kufar upgrade reports</title>
<style>{css}</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/">kufar upgrade reports</a>
    <span class="topbar-title">подбор комплектации · kufar.by · Минск</span>
  </div>
</header>
<main class="report">
  <h1>Отчёты подбора комплектации</h1>
  <p class="muted">kufar.by · Минск · DDR4 · Intel + AMD. Сортировка по имени, новые сверху.</p>
  <ul class="reports-list">
{items}
  </ul>
</main>
<footer class="report-footer">Сгенерировано из Markdown · подбор комплектации на kufar.by</footer>
</body>
</html>
"""

INDEX_ITEM = '    <li><a href="./{href}"><span class="date">{date}</span><span class="title">{title}</span></a></li>'


def _read_title(html_path: Path) -> str:
    m = re.search(r"<title>([^<]+)</title>", html_path.read_text(encoding="utf-8"))
    return m.group(1) if m else html_path.stem


def _date_label(stem: str) -> str:
    """Имя файла вида '2026-07-05 2235 — ...' -> '2026-07-05 22:35'."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})(?:\s+(\d{2})(\d{2}))?", stem)
    if not m:
        return stem
    if m.group(2):
        return f"{m.group(1)} {m.group(2)}:{m.group(3)}"
    return m.group(1)


def build_index(out_dir: Path) -> Path:
    """index.html со списком отчётов, отсортированных по имени убыванию (новые сверху)."""
    htmls = sorted(
        (p for p in out_dir.glob("*.html") if p.name != "index.html"),
        key=lambda p: p.name,
        reverse=True,
    )
    items = "\n".join(
        INDEX_ITEM.format(
            href=p.name.replace('"', "%22"),
            date=_date_label(p.stem),
            title=_read_title(p).replace("<", "&lt;").replace(">", "&gt;"),
        )
        for p in htmls
    )
    out = out_dir / "index.html"
    out.write_text(INDEX_TEMPLATE.format(css=CSS, items=items), encoding="utf-8")
    return out


def wrap_tables(html_body: str) -> str:
    """Обернуть каждую <table> в <div class=table-wrap> для горизонтального скролла."""
    return re.sub(r"(<table>.*?</table>)", r'<div class="table-wrap">\1</div>', html_body, flags=re.S)


def _fix_list_continuation(md_text: str) -> str:
    """CommonMark swallows lists into preceding paragraphs.

    If a line ending with ':', '**' (bold), or '>.' (block quote tail) is
    followed directly by a list item ('- ', '* ', or '1. '), insert a
    blank line so the list becomes its own block. Pure markdown content
    fix — preserves raw text on the rest.
    """
    out: list[str] = []
    prev_idx = -1
    for line in md_text.splitlines(keepends=True):
        # detect start of a list item
        stripped = line.lstrip()
        is_list = bool(
            re.match(r"([-*+])\s+", stripped)
            or re.match(r"\d+\.\s+", stripped)
        )
        # decide if we need to insert a blank line
        if is_list and 0 <= prev_idx < len(out):
            prev = out[prev_idx].rstrip("\n")
            if prev and not prev.endswith("```") and not prev.startswith("#"):
                tail = prev.rstrip()
                if (
                    tail.endswith(":")
                    or tail.endswith("**")
                    or tail.endswith("):")
                    or "</strong>" in tail[-80:]
                ):
                    # ensure exactly one blank line before the list
                    if out[prev_idx] != "\n" and not out[prev_idx].endswith("\n\n"):
                        out[prev_idx] = out[prev_idx].rstrip("\n") + "\n\n"
        out.append(line)
        prev_idx = len(out) - 1
    return "".join(out)


def render(md_path: Path, style: str | None = None) -> str:
    md_text = md_path.read_text(encoding="utf-8")
    md_text = _fix_list_continuation(md_text)
    body = markdown.markdown(
        md_text,
        extensions=EXTENSIONS,
        output_format="html5",
    )
    body = wrap_tables(body)
    m = re.search(r"^#\s+(.+)$", md_text, flags=re.M)
    title = m.group(1).strip() if m else md_path.stem
    if style:
        title = f"[{style}] {title}"
    return TEMPLATE.format(
        title=title.replace('"', "&quot;"),
        title_short=title.replace('"', "&quot;"),
        css=get_css(style),
        body=body,
    )


def convert(md_path: Path, out_dir: Path, style: str | None = None,
            suffix: str = "") -> Path:
    html = render(md_path, style=style)
    out = out_dir / (md_path.stem + (f".{style}" if style else "") + suffix + ".html")
    out.write_text(html, encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="kufar report .md -> .html")
    ap.add_argument("input", nargs="?", help="путь к .md (или используй --all)")
    ap.add_argument("--all", action="store_true", help="конвертировать все reports/*.md + собрать index.html")
    ap.add_argument("--index", action="store_true", help="только собрать index.html из уже готовых *.html")
    ap.add_argument("--out-dir", default=None, help="каталог назначения (по умолчанию рядом с .md)")
    ap.add_argument("--style", default=None, choices=list(STYLES.keys()),
                    help="тема оформления (по умолчанию legacy)")
    args = ap.parse_args()

    if not args.all and not args.input and not args.index:
        ap.error("укажи .md файл, --all или --index")

    if args.all:
        src = Path("reports")
        if not src.is_dir():
            print(f"каталог {src} не найден (запускай из корня проекта)", file=sys.stderr)
            return 1
        out_dir = Path(args.out_dir) if args.out_dir else src
        out_dir.mkdir(parents=True, exist_ok=True)
        mds = sorted(src.glob("*.md"))
        if not mds:
            print(f"в {src} нет .md файлов", file=sys.stderr)
            return 1
        for md in mds:
            o = convert(md, out_dir, style=args.style)
            print(f"  {md.name}  ->  {o.name}")
        idx = build_index(out_dir)
        print(f"готово: {len(mds)} html + {idx.name} в {out_dir}")
        return 0

    if args.index:
        src = Path("reports") if args.out_dir is None else Path(args.out_dir)
        if not src.is_dir():
            print(f"каталог {src} не найден", file=sys.stderr)
            return 1
        idx = build_index(src)
        print(idx)
        return 0

    md = Path(args.input)
    if not md.is_file():
        print(f"не найден {md}", file=sys.stderr)
        return 1
    out_dir = Path(args.out_dir) if args.out_dir else md.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    o = convert(md, out_dir, style=args.style)
    print(o)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())