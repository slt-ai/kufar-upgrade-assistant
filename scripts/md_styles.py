"""Альтернативные CSS-темы для md_to_html.py.

Каждая константа STYLE_* — полный набор CSS-переменных + базовые правила.
`BASE` — общая часть (layout, topbar, footer, scroll-margin), общая для всех тем.
В render() подставляется `BASE + STYLE_*`.
"""
from __future__ import annotations

BASE = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,"Helvetica Neue",Arial,sans-serif}
.topbar{position:sticky;top:0;z-index:10;background:var(--surface);
  border-bottom:1px solid var(--border)}
.topbar-inner{max-width:1000px;margin:0 auto;padding:10px 20px;
  display:flex;align-items:baseline;gap:14px}
.brand{font-weight:700;color:var(--accent);text-decoration:none;font-size:15px;white-space:nowrap}
.brand:hover{text-decoration:underline}
.topbar-title{color:var(--muted);font-size:13px;min-width:0;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.report{margin:26px auto 64px;padding:0 20px}
.report h1{line-height:1.25;margin:0 0 16px;padding-bottom:12px;
  border-bottom:2px solid var(--accent);scroll-margin-top:56px}
.report h2{margin:38px 0 12px;padding-bottom:8px;
  border-bottom:1px solid var(--border);scroll-margin-top:56px}
.report h3{margin:28px 0 10px;scroll-margin-top:56px}
.report p{margin:10px 0}
.report ul,.report ol{margin:10px 0;padding-left:22px}
.report li{margin:4px 0}
.report strong{font-weight:700}
.report a{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent}
.report a:hover{border-bottom-color:currentColor}
.report code{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  font-size:.88em;background:var(--code-bg);padding:1px 5px;border-radius:5px}
.report pre{background:var(--code-bg);padding:14px;border-radius:8px;overflow-x:auto}
.report pre code{background:none;padding:0}
.report blockquote{margin:14px 0;padding:10px 16px;border-left:4px solid var(--warn);
  background:var(--warn-soft);border-radius:0 8px 8px 0}
.report blockquote p:first-child{margin-top:0}
.report blockquote p:last-child{margin-bottom:0}
.report hr{border:none;border-top:1px solid var(--border);margin:24px 0}
.table-wrap{overflow-x:auto;margin:16px 0;border:1px solid var(--border);border-radius:10px}
.report table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:100%}
.report thead th{background:var(--thead-bg);color:var(--thead-fg);text-align:left;
  padding:9px 10px;font-weight:600;white-space:nowrap}
.report tbody td{padding:8px 10px;border-top:1px solid var(--border);vertical-align:top}
.report tbody tr:nth-child(even){background:var(--row-alt)}
.report tbody tr:hover{background:var(--accent-soft)}
.report td code,.report th code{white-space:nowrap}
.report-footer{max-width:1000px;margin:0 auto;padding:20px;color:var(--muted);
  font-size:12px;border-top:1px solid var(--border)}
.muted{color:var(--muted)}
.reports-list{list-style:none;padding:0;margin:20px 0}
.reports-list li{border-bottom:1px solid var(--border)}
.reports-list a{display:flex;gap:14px;align-items:baseline;padding:12px 6px;
  border-bottom:transparent}
.reports-list a:hover{background:var(--accent-soft);border-radius:8px}
.reports-list .date{font-variant-numeric:tabular-nums;color:var(--muted);
  font-size:13px;white-space:nowrap;min-width:130px}
.reports-list .title{color:var(--text);font-weight:500}
.reports-list a:hover .title{color:var(--accent)}
"""

# 1) Linear / Vercel-docs
STYLE_LINEAR = """
:root {
  --bg:#ffffff; --surface:#fafafa; --text:#0a0a0a; --muted:#6b7280;
  --accent:#0070f3; --accent-soft:#f5f9ff; --border:#eaeaea;
  --code-bg:#f4f4f5; --thead-bg:#fafafa; --thead-fg:#0a0a0a; --row-alt:#fafafa;
  --warn:#d97706; --warn-soft:#fffbeb; --ok:#059669; --ok-soft:#ecfdf5;
}
body{background:var(--bg);font:15px/1.65 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.report{max-width:760px}
.report h1{font-size:32px;font-weight:600;letter-spacing:-.02em}
.report h2{font-size:20px;font-weight:600;border-bottom-color:var(--border)}
.report table{font-size:13px}
"""

# 2) Stripe / фиолетовая типографика
STYLE_STRIPE = """
:root {
  --bg:#f6f9fc; --surface:#ffffff; --text:#1a1f36; --muted:#697386;
  --accent:#635bff; --accent-soft:#ebe9ff; --border:#e3e8ee;
  --code-bg:#f6f9fc; --thead-bg:#1a1f36; --thead-fg:#ffffff; --row-alt:#fafbfd;
  --warn:#e25950; --warn-soft:#fef0ef; --ok:#22c55e; --ok-soft:#ecfdf5;
}
body{background:var(--bg);font:16px/1.7 "Inter",ui-sans-serif,system-ui,sans-serif}
.report{max-width:880px;margin-top:32px}
.report h1{font-size:36px;font-weight:700;letter-spacing:-.025em;line-height:1.1;
  background:linear-gradient(135deg,#635bff,#00d4ff);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  border-bottom:none}
.report h2{font-size:22px;font-weight:600}
.table-wrap{border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.report thead th{padding:12px 14px}
.report tbody td{padding:12px 14px}
.report code{color:var(--accent);font-size:.85em}
"""

# 3) GitHub-PR / dark-first
STYLE_GITHUB = """
:root {
  --bg:#0d1117; --surface:#161b22; --text:#e6edf3; --muted:#7d8590;
  --accent:#2f81f7; --accent-soft:#1c2733; --border:#30363d;
  --code-bg:#161b22; --thead-bg:#21262d; --thead-fg:#e6edf3; --row-alt:#161b22;
  --warn:#d29922; --warn-soft:#2a2310; --ok:#3fb950; --ok-soft:#0f2419;
}
@media (prefers-color-scheme: light) {
  :root{--bg:#ffffff;--surface:#f6f8fa;--text:#1f2328;--muted:#59636e;
    --accent:#0969da;--accent-soft:#ddf4ff;--border:#d1d9e0;
    --code-bg:#eff1f3;--thead-bg:#f6f8fa;--thead-fg:#1f2328;--row-alt:#f6f8fa;
    --warn:#9a6700;--warn-soft:#fff8c5;--ok:#1a7f37;--ok-soft:#dafbe1}
}
body{background:var(--bg);font:14px/1.55 ui-sans-serif,system-ui,"Segoe UI",sans-serif}
.report{max-width:1012px;margin-top:24px}
.report h1{font-size:24px;font-weight:600}
.report h2{font-size:18px;font-weight:600;border-bottom:1px solid var(--border)}
.report h1{border-bottom:1px solid var(--border);border-bottom-width:1px}
.report h1{border-bottom-color:var(--border)}
.report table{font-size:12.5px}
.report thead th{padding:6px 12px}
.report tbody td{padding:6px 12px}
"""

# 4) Tailwind UI / cards
STYLE_TAILWIND = """
:root {
  --bg:#f9fafb; --surface:#ffffff; --text:#111827; --muted:#6b7280;
  --accent:#059669; --accent-soft:#ecfdf5; --border:#e5e7eb;
  --code-bg:#f3f4f6; --thead-bg:#f9fafb; --thead-fg:#111827; --row-alt:#fafafa;
  --warn:#d97706; --warn-soft:#fffbeb; --ok:#059669; --ok-soft:#ecfdf5;
}
body{background:var(--bg);font:15px/1.6 ui-sans-serif,system-ui,sans-serif}
.report{max-width:960px;margin-top:32px}
.report h1{font-size:30px;font-weight:800;letter-spacing:-.02em}
.report h1+p{color:var(--muted);margin-bottom:32px}
.report h2{font-size:20px;font-weight:700}
.report blockquote{background:var(--surface);border:1px solid var(--border);
  border-left:4px solid var(--accent);border-radius:8px;
  box-shadow:0 1px 2px rgba(0,0,0,.04);padding:14px 18px}
.table-wrap{border:1px solid var(--border);border-radius:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.04);overflow:hidden}
.report thead th{padding:12px 14px}
.report tbody td{padding:12px 14px}
.report strong{color:var(--accent);font-weight:600}
"""

# 5) Apple HIG / SF Pro лаконичность
STYLE_APPLE = """
:root {
  --bg:#fbfbfd; --surface:#ffffff; --text:#1d1d1f; --muted:#86868b;
  --accent:#bf5e3c; --accent-soft:#fdf3ef; --border:#e5e5e7;
  --code-bg:#f5f5f7; --thead-bg:#f5f5f7; --thead-fg:#1d1d1f; --row-alt:#fafafa;
  --warn:#bf5e3c; --warn-soft:#fdf3ef; --ok:#248a3d; --ok-soft:#e8f5ec;
}
body{background:var(--bg);font:17px/1.5 -apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif;
  letter-spacing:-.011em}
.report{max-width:820px;margin-top:64px;margin-bottom:96px}
.report h1{font-size:48px;font-weight:700;letter-spacing:-.025em;line-height:1.08;
  border-bottom:none}
.report h2{font-size:28px;font-weight:600;letter-spacing:-.018em}
.report p{font-size:17px}
.report ul li{font-size:17px}
.report table{font-size:14px}
.report thead th{padding:10px 12px;font-weight:600}
.report tbody td{padding:10px 12px}
.report code{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:.85em}
"""

# 6) Bloomberg Terminal / data-dense
STYLE_BLOOMBERG = """
:root {
  --bg:#000000; --surface:#0a0a0a; --text:#e8e8e8; --muted:#7a7a7a;
  --accent:#ffb800; --accent-soft:#2a2008; --border:#2a2a2a;
  --code-bg:#0a0a0a; --thead-bg:#000; --thead-fg:#ffb800; --row-alt:#0a0a0a;
  --warn:#ff6b00; --warn-soft:#2a1408; --ok:#00d68f; --ok-soft:#082a1c;
}
body{background:var(--bg);
  font:13px/1.45 ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  font-variant-numeric:tabular-nums}
.report{max-width:1100px;padding-top:24px;padding-bottom:64px}
.report h1{font-size:22px;color:var(--accent);font-weight:700;letter-spacing:.05em;
  text-transform:uppercase;border-bottom:2px solid var(--accent);padding-bottom:6px}
.report h2{font-size:15px;color:var(--accent);font-weight:700;
  text-transform:uppercase;letter-spacing:.08em;padding:4px 8px;
  background:var(--surface);border-left:3px solid var(--accent);border-bottom:none}
.report h3{font-size:13px;color:var(--text);font-weight:700;
  text-transform:uppercase}
.report strong{color:var(--accent);font-weight:700}
.report code{color:var(--accent);padding:1px 4px;border:1px solid var(--border);font-size:.92em}
.report blockquote{border-left:3px solid var(--warn);background:var(--surface);
  padding:8px 12px;color:var(--warn)}
.table-wrap{border:1px solid var(--border);border-radius:0}
.report table{font-size:12px}
.report thead th{background:#000;color:var(--accent);padding:6px 8px;
  font-weight:700;text-transform:uppercase;letter-spacing:.05em;
  border-bottom:1px solid var(--accent)}
.report tbody td{padding:6px 8px}
"""

# 7) Газетный / serif-editorial
STYLE_NEWS = """
:root {
  --bg:#faf6f0; --surface:#fffdf8; --text:#2a2520; --muted:#786c5f;
  --accent:#8b1e2c; --accent-soft:#f7e8e8; --border:#e0d6c2;
  --code-bg:#f0e8d8; --thead-bg:#2a2520; --thead-fg:#faf6f0; --row-alt:#f5ede0;
  --warn:#8b5e1e; --warn-soft:#faf0d8; --ok:#3a6b3a; --ok-soft:#e0eedc;
}
body{background:var(--bg);
  font:17px/1.7 "Charter","Iowan Old Style",Georgia,"Times New Roman",serif}
.report{max-width:680px;margin-top:48px;margin-bottom:80px}
.report h1{font-family:"Playfair Display",Georgia,serif;
  font-size:42px;font-weight:700;line-height:1.1;border-bottom:none;text-align:center}
.report h2{font-family:"Playfair Display",Georgia,serif;
  font-size:26px;font-weight:700}
.report h3{font-size:18px;font-weight:600;font-style:italic;color:var(--accent)}
.report p{hyphens:auto;text-align:justify}
.report blockquote{border-left:3px solid var(--accent);font-style:italic;
  color:var(--muted)}
.report table{font-size:14px;border-top:2px solid var(--text);
  border-bottom:2px solid var(--text)}
.report thead th{background:transparent;color:var(--text);
  border-bottom:1px solid var(--text);padding:10px 12px;font-weight:700;
  text-align:left;font-variant:small-caps;letter-spacing:.05em}
.report tbody td{padding:10px 12px}
.report code{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:.85em}
"""

# 8) autotune-style: глубокий тёмный фон, неон-зелёный акцент, glass-карточки.
# Референс: autotunellm.com (rgb(9,9,15) bg, rgb(232,232,240) fg, неон #00ff88).
STYLE_AUTOTUNE = """
:root {
  --bg:#09090f; --surface:#0e0e16; --text:#e8e8f0; --muted:#8b8b9c;
  --accent:#1aff9c; --accent-soft:#0a2a1c; --border:#1e1e2a;
  --code-bg:#131320; --thead-bg:#0e0e16; --thead-fg:#e8e8f0; --row-alt:#0a0a12;
  --warn:#ffb800; --warn-soft:#2a2008; --ok:#1aff9c; --ok-soft:#0a2a1c;
}
body{background:var(--bg);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,sans-serif;
  font-feature-settings:"ss01","cv11"}
.topbar{background:rgba(9,9,15,.85);backdrop-filter:saturate(180%) blur(12px);
  -webkit-backdrop-filter:saturate(180%) blur(12px);
  border-bottom:1px solid var(--border)}
.brand{color:var(--accent);letter-spacing:-.01em}
.topbar-title{color:#a0a0b0}
.report{max-width:920px;margin-top:32px}
.report h1{font-size:56px;font-weight:700;letter-spacing:-.035em;line-height:1.05;
  color:#fff;border-bottom:none;padding-bottom:0;margin-bottom:24px}
.report h1+p{color:#a0a0b0}
.report h2{font-size:24px;font-weight:600;letter-spacing:-.02em;
  color:#fff;border-bottom:none;margin-top:48px;margin-bottom:14px;
  padding-bottom:0}
.report h2:before{content:"";display:inline-block;width:6px;height:18px;
  background:var(--accent);border-radius:3px;margin-right:10px;
  vertical-align:-2px}
.report h3{font-size:17px;font-weight:600;color:#fff;margin-top:24px}
.report p{color:var(--text)}
.report a{color:var(--accent)}
.report a:hover{border-bottom-color:var(--accent)}
.report strong{color:#fff;font-weight:600}
.report code{background:var(--code-bg);color:var(--accent);
  border:1px solid var(--border);border-radius:6px;padding:2px 7px;
  font-size:.85em}
.report pre{background:var(--code-bg);border:1px solid var(--border);
  border-radius:12px}
.report blockquote{background:var(--surface);
  border:1px solid var(--border);border-left:3px solid var(--accent);
  border-radius:0 12px 12px 0;padding:14px 18px;color:#cfcfd8;
  box-shadow:0 1px 0 rgba(255,255,255,.02) inset}
.report blockquote p{color:#cfcfd8}
.report hr{border-top:1px solid var(--border);margin:32px 0}
.table-wrap{background:var(--surface);border:1px solid var(--border);
  border-radius:14px;box-shadow:0 1px 0 rgba(255,255,255,.02) inset,
  0 8px 32px rgba(0,0,0,.4);overflow:visible;width:100%}
.report table{font-size:12.5px;border-collapse:separate;border-spacing:0;
  width:100%;table-layout:auto}
.report thead th{background:rgba(255,255,255,.02);
  border-bottom:1px solid var(--border);padding:8px 10px;font-weight:600;
  color:#cfcfd8;letter-spacing:.01em;text-align:left;white-space:normal;
  font-size:11.5px;line-height:1.35}
.report tbody td{padding:8px 10px;border-top:1px solid var(--border);
  color:var(--text);font-size:12.5px;line-height:1.45;
  white-space:normal;word-break:break-word;overflow-wrap:anywhere;
  vertical-align:top;hyphens:auto}
.report tbody td a{word-break:break-all}
.report tbody tr:hover{background:rgba(26,255,156,.04)}
.report ul li::marker{color:var(--accent)}
.report ol li::marker{color:var(--accent);font-weight:600}
.reports-list a{border:1px solid var(--border);border-radius:10px;
  margin-bottom:8px;background:var(--surface)}
.reports-list a:hover{border-color:var(--accent);background:rgba(26,255,156,.04)}
.reports-list .title{color:#fff}
.reports-list a:hover .title{color:var(--accent)}
.report-footer{color:#6b6b7a;border-top:1px solid var(--border)}
"""


STYLES: dict[str, tuple[str, str, str]] = {
    # slug -> (title, desc, css)
    "1-linear":    ("Linear / Vercel-docs",   "нейтральная, узкая колонка, монохромный синий",            STYLE_LINEAR),
    "2-stripe":    ("Stripe / фиолетовая",    "продакшн-эстетика, фиолетовый градиент, скругления",       STYLE_STRIPE),
    "3-github":    ("GitHub-PR / dark-first", "плотная, разработческая, тёмная по умолчанию",             STYLE_GITHUB),
    "4-tailwind":  ("Tailwind UI / cards",    "карточный layout, мягкие тени, emerald-акцент",             STYLE_TAILWIND),
    "5-apple":     ("Apple HIG / SF Pro",     "большие отступы, тонкие разделители, терракотовый",         STYLE_APPLE),
    "6-bloomberg": ("Bloomberg Terminal",     "моноширинная, плотная, чёрно-жёлтая",                       STYLE_BLOOMBERG),
    "7-news":      ("Газетный / serif",       "засечный шрифт, тёплый фон, бордовый, журнальная",         STYLE_NEWS),
    "8-autotune":  ("autotune / neon-dark",   "глубокий тёмный фон, неон-зелёный, glass-карточки",         STYLE_AUTOTUNE),
}


def get_css(name: str | None) -> str:
    """Вернуть CSS для темы `name` (или текущую тему по умолчанию, имя None)."""
    if name and name in STYLES:
        return BASE + STYLES[name][2]
    # дефолт = autotune (тёмный neon) — выбран пользователем 2026-07-07
    return BASE + STYLES["8-autotune"][2]


# старая тема (то, что было в md_to_html.py до рефакторинга) — на случай если кто-то
# скриптовал на ней. md_to_html.py импортирует get_css() и при name=None вернёт её.
_LEGACY_CSS = """
:root {
  --bg:#f6f7f9; --surface:#ffffff; --text:#1e2330; --muted:#6b7280;
  --accent:#2563eb; --accent-soft:#eff6ff; --border:#e4e7ec;
  --code-bg:#f1f3f5; --thead-bg:#1e2330; --thead-fg:#ffffff; --row-alt:#f8fafc;
  --warn:#b45309; --warn-soft:#fffbeb; --ok:#047857; --ok-soft:#ecfdf5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#0f1115; --surface:#161a22; --text:#e6e8ee; --muted:#9aa3b2;
    --accent:#6ea8fe; --accent-soft:#16203a; --border:#272d3a;
    --code-bg:#1e2330; --thead-bg:#1e2330; --thead-fg:#e6e8ee; --row-alt:#1a1f2a;
    --warn:#fbbf24; --warn-soft:#2a2310; --ok:#34d399; --ok-soft:#0f2419;
  }
}
body{background:var(--bg)}
"""
