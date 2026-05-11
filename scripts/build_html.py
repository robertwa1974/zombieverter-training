#!/usr/bin/env python3
"""
ZombieVerter VCU Training Series - HTML Deck Builder
Reads markdown source files and generates zombieverter-training-complete.html
Run from the repo root: python3 scripts/build_html.py
"""

import re
import html
from pathlib import Path

REPO_ROOT   = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "index-slides.html"

# ── Module catalogue (mirrors build_pdf.py exactly) ───────────
MODULES = [
    ('F01', 'Foundation',    'What Is a VCU and Why Do You Need One',   'foundation/F01-what-is-a-vcu-and-why-do-you-need-one.md'),
    ('F02', 'Foundation',    'ZombieVerter Ecosystem Overview',          'foundation/F02-zombieverter-ecosystem-overview.md'),
    ('F03', 'Foundation',    'EV Drivetrain Fundamentals',               'foundation/F03-ev-drivetrain-fundamentals.md'),
    ('F04', 'Foundation',    'High Voltage Safety',                      'foundation/F04-high-voltage-safety.md'),
    ('H01', 'Hardware',      'VCU Hardware Walkthrough',                 'hardware/H01-vcu-hardware-walkthrough.md'),
    ('W01', 'Wiring',        'Wiring Philosophy and Best Practices',     'wiring/W01-wiring-philosophy-and-best-practices.md'),
    ('W02', 'Wiring',        'Throttle and Brake Wiring',                'wiring/W02-throttle-and-brake-wiring.md'),
    ('W03', 'Wiring',        'Contactor and Precharge Circuit',          'wiring/W03-contactor-and-precharge-circuit.md'),
    ('W04', 'Wiring',        'HVIL High Voltage Interlock Loop',         'wiring/W04-hvil-high-voltage-interlock-loop.md'),
    ('W05', 'Wiring',        'Cooling System Control',                   'wiring/W05-cooling-system-control.md'),
    ('W06', 'Wiring',        '12V Auxiliary and Ignition Wiring',        'wiring/W06-12v-auxiliary-and-ignition-wiring.md'),
    ('W07', 'Wiring',        'CAN Bus Wiring',                           'wiring/W07-can-bus-wiring.md'),
    ('W08', 'Wiring',        'ISA IVT-S Shunt: Complete Reference',      'wiring/W08-ivt-s-shunt-reference.md'),
    ('C00', 'Configuration', 'Firmware Version History',                 'configuration/C00-firmware-version-history.md'),
    ('C01', 'Configuration', 'Flashing Firmware',                        'configuration/C01-flashing-firmware.md'),
    ('C02', 'Configuration', 'Web Interface Walkthrough',                'configuration/C02-web-interface-walkthrough.md'),
    ('C03', 'Configuration', 'Essential Parameters: First Start',        'configuration/C03-essential-parameters-first-start.md'),
    ('C04', 'Configuration', 'Throttle Calibration',                     'configuration/C04-throttle-calibration.md'),
    ('C06', 'Configuration', 'Fault Codes and Status Flags',             'configuration/C06-fault-codes-and-status-flags.md'),
    ('I01', 'Integration',   'Nissan Leaf Inverter',                     'integration/I01-nissan-leaf-inverter.md'),
    ('I02', 'Integration',   'Tesla Drive Units SDU and LDU',            'integration/I02-tesla-ldu.md'),
    ('I03', 'Integration',   'GS450h Transaxle',                        'integration/I03-gs450h-transaxle.md'),
    ('I03-X','Integration',  'GS450h Wiring and Oil Pump Deep Dive',     'integration/I03-X-gs450h-wiring-and-oil-pump-deep-dive.md'),
    ('I04', 'Integration',   'Mitsubishi Outlander Drive Unit',          'integration/I04-mitsubishi-outlander-drive-unit.md'),
    ('A01', 'Advanced',      'Regen Tuning',                             'advanced/A01-regen-tuning.md'),
    ('A02', 'Advanced',      'Charge Control and Popular Chargers',      'advanced/A02-charge-control-and-chargers.md'),
    ('A03', 'Advanced',      'BMS Integration',                          'advanced/A03-bms-integration.md'),
    ('A04', 'Advanced',      'Gear Selectors and Shifters',              'advanced/A04-gear-selectors-and-shifters.md'),
    ('A05', 'Advanced',      'CAN Gateway and Multi-Node Systems',       'advanced/A05-can-gateway-and-multi-node-systems.md'),
    ('A06', 'Advanced',      'Firmware Customisation and Contributing',  'advanced/A06-firmware-customisation-and-contributing.md'),
]

TRACK_COLOURS = {
    'F': '#00c896',
    'H': '#00a0ff',
    'W': '#20b2aa',
    'C': '#6a5acd',
    'I': '#e07b39',
    'A': '#ffaa00',
}

# ── Inline markdown → HTML ─────────────────────────────────────
def md_inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', text)
    return text

def strip_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'_(.+?)_',       r'\1', text)
    text = re.sub(r'`(.+?)`',       r'\1', text)
    return text

# ── Markdown block → HTML ──────────────────────────────────────
def md_to_html(md_text, skip_h1=True):
    lines = md_text.splitlines()
    out = []
    i = 0
    in_code = False
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        out.append('<div class="table-wrap"><table>')
        for ri, row in enumerate(table_rows):
            tag = 'th' if ri == 0 else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in row) + '</tr>')
        out.append('</table></div>')
        table_rows.clear()
        in_table = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith('```'):
            flush_table()
            in_code = not in_code
            if in_code:
                lang = stripped[3:].strip() or ''
                out.append(f'<pre><code class="lang-{lang}">')
            else:
                out.append('</code></pre>')
            i += 1
            continue

        if in_code:
            out.append(html.escape(line))
            i += 1
            continue

        # Blank line
        if not stripped:
            flush_table()
            i += 1
            continue

        # HR
        if re.match(r'^[-*_]{3,}$', stripped):
            flush_table()
            out.append('<hr>')
            i += 1
            continue

        # Table row
        if stripped.startswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if all(re.match(r'^[-: ]+$', c) for c in cells):
                i += 1
                continue
            in_table = True
            parsed = [md_inline(c) for c in cells]
            table_rows.append(parsed)
            i += 1
            continue
        else:
            flush_table()

        # Headings
        m = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if m:
            level = len(m.group(1))
            text = md_inline(m.group(2))
            if level == 1:
                if not skip_h1:
                    out.append(f'<h1>{text}</h1>')
            elif level == 2:
                out.append(f'<h2>{text}</h2>')
            elif level == 3:
                out.append(f'<h3>{text}</h3>')
            else:
                out.append(f'<h4>{text}</h4>')
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            raw = stripped.lstrip('> ').strip()
            text = md_inline(raw)
            upper = raw.upper()
            if 'DO NOT' in upper or 'WARNING' in upper or 'DANGER' in upper:
                cls = 'callout danger'
            elif upper.startswith('NOTE') or upper.startswith('💡'):
                cls = 'callout info'
            else:
                cls = 'callout warn'
            out.append(f'<div class="{cls}">{text}</div>')
            i += 1
            continue

        # Bullet list
        if re.match(r'^[-*]\s', stripped):
            out.append('<ul>')
            while i < len(lines) and re.match(r'^[-*]\s', lines[i].strip()):
                item = md_inline(lines[i].strip()[2:].strip())
                out.append(f'<li>{item}</li>')
                i += 1
            out.append('</ul>')
            continue

        # Numbered list
        if re.match(r'^\d+\.\s', stripped):
            out.append('<ol>')
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i].strip()):
                item = md_inline(re.sub(r'^\d+\.\s*', '', lines[i].strip()))
                out.append(f'<li>{item}</li>')
                i += 1
            out.append('</ol>')
            continue

        # Source / metadata lines
        if (stripped.startswith('*Source:') or stripped.startswith('*Last verified')
                or stripped.startswith('Source:') or stripped.startswith('Last verified')):
            out.append(f'<p class="source">{md_inline(stripped.strip("*"))}</p>')
            i += 1
            continue

        if re.match(r'^\*\*(Track|Prerequisites|Audience|Estimated|Video source):', stripped):
            out.append(f'<p class="meta">{md_inline(stripped)}</p>')
            i += 1
            continue

        # Default paragraph — merge continuation lines
        text = md_inline(stripped)
        while i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if (nxt
                    and not nxt.startswith('#')
                    and not nxt.startswith('|')
                    and not nxt.startswith('>')
                    and not nxt.startswith('```')
                    and not re.match(r'^[-*]\s', nxt)
                    and not re.match(r'^\d+\.\s', nxt)
                    and not re.match(r'^[-*_]{3,}$', nxt)):
                text += ' ' + md_inline(nxt)
                i += 1
            else:
                break
        out.append(f'<p>{text}</p>')
        i += 1

    flush_table()
    return '\n'.join(out)


# ── Navigation sidebar entries ─────────────────────────────────
def build_nav(modules):
    out = []
    current_track = None
    for code, track, title, _ in modules:
        if track != current_track:
            if current_track is not None:
                out.append('</div>')
            colour = TRACK_COLOURS.get(code[0], '#00c896')
            out.append(f'<div class="nav-track">')
            out.append(f'<div class="nav-track-label" style="color:{colour}">{track.upper()}</div>')
            current_track = track
        short = strip_inline(title)
        out.append(f'<a class="nav-item" href="#mod-{code}" data-code="{code}">'
                   f'<span class="nav-code">{code}</span>'
                   f'<span class="nav-title">{short}</span></a>')
    out.append('</div>')
    return '\n'.join(out)


# ── Module slide ───────────────────────────────────────────────
def build_module(code, track, title, md_text):
    colour = TRACK_COLOURS.get(code[0], '#00c896')
    if 'X' in code:
        colour = '#ff4455'
    content = md_to_html(md_text, skip_h1=True)
    badge_text = f'TRACK {track.upper()} · MODULE {code}'
    return f'''
<section class="module" id="mod-{code}" data-track="{track.lower()}">
  <div class="module-header" style="border-color:{colour}">
    <div class="module-badge" style="background:{colour}">{badge_text}</div>
    <h1 class="module-title">{html.escape(strip_inline(title))}</h1>
  </div>
  <div class="module-body">
{content}
  </div>
</section>'''


# ── Full HTML document ─────────────────────────────────────────
def build_html(modules):
    nav = build_nav(modules)

    module_sections = []
    missing = []
    for code, track, title, rel_path in modules:
        md_path = REPO_ROOT / rel_path
        if not md_path.exists():
            print(f'  [SKIP] {code} - {md_path.name} not found')
            missing.append((code, title))
            colour = TRACK_COLOURS.get(code[0], '#888')
            module_sections.append(f'''
<section class="module module-missing" id="mod-{code}">
  <div class="module-header" style="border-color:{colour}">
    <div class="module-badge" style="background:{colour}">TRACK {track.upper()} · MODULE {code}</div>
    <h1 class="module-title">{html.escape(strip_inline(title))}</h1>
  </div>
  <div class="module-body">
    <div class="callout info">This module is planned but not yet written. Check the repository for the latest status.</div>
  </div>
</section>''')
            continue
        print(f'  [OK]   {code} - {title}')
        md_text = md_path.read_text(encoding='utf-8')
        module_sections.append(build_module(code, track, title, md_text))

    sections_html = '\n'.join(module_sections)
    total = len(modules)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZombieVerter VCU Training Series</title>
<style>
  :root {{
    --accent:   #00c896;
    --accent2:  #00a0ff;
    --warn:     #ffaa00;
    --danger:   #ff4455;
    --dark:     #1a1a2e;
    --darker:   #13131f;
    --surface:  #22223a;
    --surface2: #2d2d4a;
    --text:     #e8e8f0;
    --text-dim: #9090b0;
    --border:   #3a3a5c;
    --nav-w:    280px;
    --font-body: 'Segoe UI', system-ui, sans-serif;
    --font-mono: 'Consolas', 'Fira Code', monospace;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: var(--font-body);
    background: var(--darker);
    color: var(--text);
    display: flex;
    min-height: 100vh;
  }}

  /* ── Sidebar nav ── */
  #sidebar {{
    width: var(--nav-w);
    min-width: var(--nav-w);
    background: var(--dark);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow: hidden;
  }}

  #sidebar-header {{
    padding: 16px 14px 12px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }}

  #sidebar-header h2 {{
    font-size: 12px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}

  #sidebar-header p {{
    font-size: 10px;
    color: var(--text-dim);
    margin-top: 3px;
  }}

  #search-wrap {{
    padding: 8px 10px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }}

  #search {{
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 6px 10px;
    color: var(--text);
    font-size: 12px;
    outline: none;
  }}

  #search:focus {{ border-color: var(--accent); }}
  #search::placeholder {{ color: var(--text-dim); }}

  #nav-scroll {{
    overflow-y: auto;
    flex: 1;
    padding: 6px 0 20px;
  }}

  #nav-scroll::-webkit-scrollbar {{ width: 4px; }}
  #nav-scroll::-webkit-scrollbar-track {{ background: transparent; }}
  #nav-scroll::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

  .nav-track {{ margin-bottom: 4px; }}

  .nav-track-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 8px 14px 3px;
  }}

  .nav-item {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 5px 14px;
    text-decoration: none;
    color: var(--text-dim);
    font-size: 12px;
    border-left: 2px solid transparent;
    transition: all 0.15s;
  }}

  .nav-item:hover {{
    color: var(--text);
    background: var(--surface);
  }}

  .nav-item.active {{
    color: var(--text);
    background: var(--surface);
    border-left-color: var(--accent);
  }}

  .nav-code {{
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--accent);
    min-width: 44px;
    flex-shrink: 0;
  }}

  .nav-title {{ line-height: 1.3; }}

  /* ── Main content ── */
  #main {{
    flex: 1;
    overflow-y: auto;
    scroll-behavior: smooth;
  }}

  #main::-webkit-scrollbar {{ width: 6px; }}
  #main::-webkit-scrollbar-track {{ background: var(--darker); }}
  #main::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

  /* ── Cover ── */
  #cover {{
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 40px;
    text-align: center;
    background: linear-gradient(160deg, var(--dark) 0%, var(--darker) 60%);
  }}

  #cover h1 {{
    font-size: 48px;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: -0.02em;
    line-height: 1.1;
  }}

  #cover h2 {{
    font-size: 22px;
    font-weight: 400;
    color: var(--text-dim);
    margin-top: 8px;
  }}

  .cover-divider {{
    width: 80px;
    height: 3px;
    background: var(--accent);
    margin: 24px auto;
    border-radius: 2px;
  }}

  .cover-meta {{
    font-size: 13px;
    color: var(--text-dim);
    line-height: 1.8;
  }}

  .cover-meta a {{
    color: var(--accent2);
    text-decoration: none;
  }}

  .track-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 32px;
    max-width: 560px;
  }}

  .track-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
    text-align: left;
  }}

  .track-card .tc-code {{
    font-size: 22px;
    font-weight: 800;
  }}

  .track-card .tc-name {{
    font-size: 11px;
    color: var(--text-dim);
    margin-top: 2px;
  }}

  .track-card .tc-range {{
    font-size: 10px;
    font-family: var(--font-mono);
    color: var(--text-dim);
    margin-top: 6px;
  }}

  /* ── Module sections ── */
  .module {{
    max-width: 900px;
    margin: 0 auto;
    padding: 48px 40px 60px;
    border-bottom: 1px solid var(--border);
    scroll-margin-top: 20px;
  }}

  .module-header {{
    border-left: 4px solid var(--accent);
    padding-left: 16px;
    margin-bottom: 28px;
  }}

  .module-badge {{
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: white;
    padding: 3px 10px;
    border-radius: 3px;
    margin-bottom: 8px;
  }}

  .module-title {{
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    line-height: 1.2;
  }}

  /* ── Content styles ── */
  .module-body h2 {{
    font-size: 17px;
    font-weight: 700;
    color: var(--accent2);
    margin: 28px 0 10px;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
  }}

  .module-body h3 {{
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
    margin: 20px 0 8px;
  }}

  .module-body h4 {{
    font-size: 13px;
    font-weight: 700;
    color: var(--text-dim);
    margin: 16px 0 6px;
  }}

  .module-body p {{
    font-size: 13.5px;
    line-height: 1.7;
    color: var(--text);
    margin-bottom: 10px;
  }}

  .module-body ul, .module-body ol {{
    padding-left: 20px;
    margin-bottom: 10px;
  }}

  .module-body li {{
    font-size: 13.5px;
    line-height: 1.65;
    color: var(--text);
    margin-bottom: 4px;
  }}

  .module-body code {{
    font-family: var(--font-mono);
    font-size: 12px;
    background: var(--surface2);
    color: var(--accent);
    padding: 1px 5px;
    border-radius: 3px;
  }}

  .module-body pre {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
    overflow-x: auto;
    margin: 12px 0;
  }}

  .module-body pre code {{
    background: none;
    padding: 0;
    font-size: 12px;
    color: var(--text);
    white-space: pre;
  }}

  .module-body hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
  }}

  .module-body strong {{ font-weight: 700; color: var(--text); }}
  .module-body em {{ font-style: italic; color: var(--text-dim); }}

  /* Callouts */
  .callout {{
    border-radius: 6px;
    padding: 12px 16px;
    margin: 14px 0;
    font-size: 13px;
    line-height: 1.6;
    border-left: 4px solid;
  }}

  .callout.warn {{
    background: #2a2000;
    border-color: var(--warn);
    color: #ffe0a0;
  }}

  .callout.danger {{
    background: #2a0810;
    border-color: var(--danger);
    color: #ffb0bc;
  }}

  .callout.info {{
    background: #001a2a;
    border-color: var(--accent2);
    color: #a0d4ff;
  }}

  /* Tables */
  .table-wrap {{
    overflow-x: auto;
    margin: 14px 0;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
  }}

  th {{
    background: #2d4a6b;
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
  }}

  td {{
    padding: 7px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    vertical-align: top;
  }}

  tr:nth-child(even) td {{ background: var(--surface); }}
  tr:hover td {{ background: var(--surface2); }}

  p.source, p.meta {{
    font-size: 11px;
    color: var(--text-dim);
    font-style: italic;
    margin-top: 4px;
  }}

  /* Missing module placeholder */
  .module-missing .module-title {{ color: var(--text-dim); }}

  /* ── Progress bar ── */
  #progress {{
    position: fixed;
    top: 0;
    left: var(--nav-w);
    right: 0;
    height: 2px;
    background: var(--accent);
    transform-origin: left;
    transform: scaleX(0);
    transition: transform 0.1s;
    z-index: 100;
  }}

  /* ── Back to top ── */
  #back-top {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-dim);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 16px;
    opacity: 0;
    transition: opacity 0.2s;
    text-decoration: none;
    z-index: 50;
  }}

  #back-top.visible {{ opacity: 1; }}
  #back-top:hover {{ background: var(--surface2); color: var(--text); }}

  /* ── Responsive ── */
  @media (max-width: 768px) {{
    #sidebar {{ display: none; }}
    .module {{ padding: 32px 20px 48px; }}
    .track-grid {{ grid-template-columns: repeat(2, 1fr); }}
    #cover h1 {{ font-size: 32px; }}
    #progress {{ left: 0; }}
  }}
</style>
</head>
<body>

<div id="progress"></div>

<nav id="sidebar">
  <div id="sidebar-header">
    <h2>ZombieVerter VCU</h2>
    <p>Training Series · {total} modules · V2.40A</p>
  </div>
  <div id="search-wrap">
    <input type="search" id="search" placeholder="Search modules…" autocomplete="off">
  </div>
  <div id="nav-scroll">
{nav}
  </div>
</nav>

<main id="main">

  <div id="cover">
    <h1>ZombieVerter VCU</h1>
    <h2>Training Series</h2>
    <div class="cover-divider"></div>
    <div class="cover-meta">
      Complete reference guide for DIY EV conversion builders<br>
      {total} modules · 6 tracks · Firmware V2.40A (August 2025)<br>
      <a href="https://github.com/robertwa1974/zombieverter-training">github.com/robertwa1974/zombieverter-training</a> ·
      <a href="https://openinverter.org">openinverter.org</a>
    </div>
    <div class="track-grid">
      <div class="track-card"><div class="tc-code" style="color:#00c896">F</div><div class="tc-name">Foundation</div><div class="tc-range">F01–F04</div></div>
      <div class="track-card"><div class="tc-code" style="color:#00a0ff">H</div><div class="tc-name">Hardware</div><div class="tc-range">H01</div></div>
      <div class="track-card"><div class="tc-code" style="color:#20b2aa">W</div><div class="tc-name">Wiring</div><div class="tc-range">W01–W08</div></div>
      <div class="track-card"><div class="tc-code" style="color:#6a5acd">C</div><div class="tc-name">Configuration</div><div class="tc-range">C00–C06</div></div>
      <div class="track-card"><div class="tc-code" style="color:#e07b39">I</div><div class="tc-name">Integration</div><div class="tc-range">I01–I04</div></div>
      <div class="track-card"><div class="tc-code" style="color:#ffaa00">A</div><div class="tc-name">Advanced</div><div class="tc-range">A01–A06</div></div>
    </div>
  </div>

{sections_html}

</main>

<a href="#" id="back-top" title="Back to top">↑</a>

<script>
// ── Active nav highlight on scroll ─────────────────────────────
const main = document.getElementById('main');
const navItems = document.querySelectorAll('.nav-item');
const sections = document.querySelectorAll('.module');
const progress = document.getElementById('progress');
const backTop  = document.getElementById('back-top');

function updateNav() {{
  const scrollTop  = main.scrollTop;
  const scrollH    = main.scrollHeight - main.clientHeight;
  const pct        = scrollH > 0 ? scrollTop / scrollH : 0;
  progress.style.transform = `scaleX(${{pct}})`;
  backTop.classList.toggle('visible', scrollTop > 300);

  let active = null;
  sections.forEach(sec => {{
    const top = sec.offsetTop - main.offsetTop;
    if (scrollTop + 80 >= top) active = sec.id;
  }});

  navItems.forEach(a => {{
    a.classList.toggle('active', a.getAttribute('href') === '#' + active);
  }});
}}

main.addEventListener('scroll', updateNav, {{ passive: true }});
updateNav();

// ── Smooth nav click ───────────────────────────────────────────
navItems.forEach(a => {{
  a.addEventListener('click', e => {{
    e.preventDefault();
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {{
      main.scrollTo({{ top: target.offsetTop - 20, behavior: 'smooth' }});
    }}
    // Keep active nav item in view
    const navScroll = document.getElementById('nav-scroll');
    const aTop = a.offsetTop - navScroll.offsetTop;
    navScroll.scrollTo({{ top: aTop - navScroll.clientHeight / 2, behavior: 'smooth' }});
  }});
}});

// ── Search filter ──────────────────────────────────────────────
document.getElementById('search').addEventListener('input', function() {{
  const q = this.value.toLowerCase().trim();
  navItems.forEach(a => {{
    const text = a.textContent.toLowerCase();
    a.style.display = (!q || text.includes(q)) ? '' : 'none';
  }});
  // Show/hide track labels
  document.querySelectorAll('.nav-track').forEach(track => {{
    const visible = [...track.querySelectorAll('.nav-item')]
      .some(a => a.style.display !== 'none');
    track.style.display = visible ? '' : 'none';
  }});
}});
</script>
</body>
</html>'''


def build():
    print('Building HTML deck -> ' + str(OUTPUT_PATH))
    content = build_html(MODULES)
    OUTPUT_PATH.write_text(content, encoding='utf-8')
    size_kb = OUTPUT_PATH.stat().st_size // 1024
    print(f'Done - {size_kb} KB written to {OUTPUT_PATH}')


if __name__ == '__main__':
    build()
