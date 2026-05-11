#!/usr/bin/env python3
"""
ZombieVerter VCU Training Series - Classroom Slide Deck Builder
Reads markdown source files and generates zombieverter-training-slides.html
Run from the repo root: python3 scripts/build_slides.py

Matches the existing deck format exactly:
- Dark theme with Barlow Condensed display font
- Per-section slides with scrollable content
- JS sidebar with module navigation, keyboard nav, progress bar
- Long modules auto-split at H2 boundaries (~CONTENT_SPLIT_LINES lines per slide)
"""

import re
import html
import json
from pathlib import Path

REPO_ROOT   = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "zombieverter-training-slides.html"

# Split a content slide when accumulated lines exceed this threshold
CONTENT_SPLIT_LINES = 28

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
    'Foundation':    '#8DC63F',
    'Hardware':      '#00a0ff',
    'Wiring':        '#ffaa00',
    'Configuration': '#00c896',
    'Integration':   '#ff6b6b',
    'Advanced':      '#c084fc',
}


# ── Inline markdown → slide HTML ──────────────────────────────
def md_inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`',
        lambda m: '<code style="font-family:var(--mono);color:var(--accent);'
                  'background:rgba(0,200,150,.1);padding:1px 4px;border-radius:2px;'
                  'font-size:11px;">' + html.escape(m.group(1)) + '</code>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', text)
    return text

def strip_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'_(.+?)_',       r'\1', text)
    text = re.sub(r'`(.+?)`',       r'\1', text)
    return text


# ── Markdown → list of (slide_title, html_content) ────────────
def md_to_slides(code, track, title, md_text):
    """
    Parse markdown into a list of (slide_title, html_body) tuples.
    - First slide: title/intro card
    - Subsequent slides: one per H2 section, auto-split if too long
    """
    lines = md_text.splitlines()
    colour = TRACK_COLOURS.get(track, '#00c896')

    # ── Title slide ───────────────────────────────────────────
    title_html = f'''  <div class="badge">TRACK {track.upper()} · MODULE {code}</div>
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">
    <h1 style="font-size:52px;">{html.escape(strip_inline(title))}</h1>
    <p style="font-size:17px;color:var(--muted);max-width:700px;line-height:1.6;">
      <strong>Track:</strong> {track}</p>
    <div style="margin-top:20px;font-family:var(--mono);font-size:11px;color:{colour};
         background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.06);
         border-radius:6px;padding:10px 16px;display:inline-block;">
      Track: {track} · Firmware: V2.40A
    </div>
  </div>'''

    slides = [(title, title_html)]

    # ── Parse body into sections split on H2 ─────────────────
    # Each section = (section_title, [content_lines])
    sections = []
    current_title = title
    current_lines = []
    in_code = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('```'):
            in_code = not in_code
            current_lines.append(line)
            continue

        if in_code:
            current_lines.append(line)
            continue

        # Skip H1 (module title) and metadata lines
        if re.match(r'^# ', stripped):
            continue
        if re.match(r'^\*\*(Track|Prerequisites|Audience|Estimated|Video source):', stripped):
            continue
        if stripped.startswith('*Source:') or stripped.startswith('*Last verified') \
                or stripped.startswith('Source:') or stripped.startswith('Last verified'):
            continue

        # H2 starts a new section
        m = re.match(r'^## (.+)', stripped)
        if m:
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = strip_inline(m.group(1))
            current_lines = []
            continue

        current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    # ── Render each section, splitting long ones ───────────────
    for sec_title, sec_lines in sections:
        slide_chunks = split_into_chunks(sec_lines, CONTENT_SPLIT_LINES)
        total_chunks = len(slide_chunks)
        for ci, chunk in enumerate(slide_chunks):
            chunk_title = sec_title
            if total_chunks > 1:
                chunk_title = f'{sec_title} ({ci+1}/{total_chunks})'
            body = render_content(chunk, code, track, sec_title)
            slide_html = f'''  <div class="badge">{code} — {html.escape(sec_title.upper())}</div>
  <h2 style="font-size:32px;margin-bottom:10px;">{html.escape(chunk_title)}<span class="sub">Module {code} · {track}</span></h2>
  <div style="flex:1;overflow-y:auto;padding-right:8px;">
{body}
  </div>'''
            slides.append((chunk_title, slide_html))

    return slides


def split_into_chunks(lines, max_lines):
    """Split lines into chunks, breaking on blank lines near the limit."""
    if len(lines) <= max_lines:
        return [lines]

    chunks = []
    current = []
    in_code = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code

        current.append(line)

        # Don't split inside code blocks or tables
        if in_code or stripped.startswith('|'):
            continue

        # Split opportunity: blank line after threshold
        if len(current) >= max_lines and not stripped:
            # Look ahead — don't split just before a heading
            chunks.append(current)
            current = []

    if current:
        chunks.append(current)

    return chunks if chunks else [lines]


def render_content(lines, code, track, section_title):
    """Render a list of markdown lines to slide-format HTML."""
    out = []
    i = 0
    in_code = False
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        out.append('<table style="width:100%;border-collapse:collapse;font-size:13px;margin:8px 0;">')
        for ri, row in enumerate(table_rows):
            tag = 'th' if ri == 0 else 'td'
            style_th = ('style="padding:5px 8px;border-bottom:1px solid rgba(255,255,255,.06);'
                        'font-family:var(--mono);font-size:11px;color:var(--muted);'
                        'text-transform:uppercase;letter-spacing:.06em;"')
            style_td = ('style="padding:5px 8px;border-bottom:1px solid rgba(255,255,255,.06);'
                        'color:var(--muted);font-size:12px;"')
            style_td1 = ('style="padding:5px 8px;border-bottom:1px solid rgba(255,255,255,.06);'
                         'color:var(--muted);font-size:12px;font-family:var(--mono);'
                         'font-size:12px;color:var(--accent);"')
            cells = []
            for ci, c in enumerate(row):
                if tag == 'th':
                    cells.append(f'<th {style_th}>{c}</th>')
                elif ci == 0:
                    cells.append(f'<td {style_td1}>{c}</td>')
                else:
                    cells.append(f'<td {style_td}>{c}</td>')
            out.append('<tr>' + ''.join(cells) + '</tr>')
        out.append('</table>')
        table_rows.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block
        if stripped.startswith('```'):
            flush_table()
            in_code = not in_code
            if in_code:
                out.append('<div class="code" style="font-size:11px;line-height:1.7;margin:8px 0;">')
            else:
                out.append('</div>')
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
            i += 1
            continue

        # Table
        if stripped.startswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if all(re.match(r'^[-: ]+$', c) for c in cells):
                i += 1
                continue
            parsed = [md_inline(c) for c in cells]
            table_rows.append(parsed)
            i += 1
            continue
        else:
            flush_table()

        # H2 within chunk (continuation slide) — render as h3
        m = re.match(r'^## (.+)', stripped)
        if m:
            out.append(f'<h3 style="font-family:var(--display);font-size:18px;font-weight:600;'
                       f'color:var(--accent);margin:10px 0 6px;text-transform:uppercase;'
                       f'letter-spacing:.05em;">{md_inline(m.group(1))}</h3>')
            i += 1
            continue

        # H3
        m = re.match(r'^### (.+)', stripped)
        if m:
            out.append(f'<h3 style="font-family:var(--display);font-size:18px;font-weight:600;'
                       f'color:var(--accent);margin:10px 0 6px;text-transform:uppercase;'
                       f'letter-spacing:.05em;">{md_inline(m.group(1))}</h3>')
            i += 1
            continue

        # H4
        m = re.match(r'^#### (.+)', stripped)
        if m:
            out.append(f'<h3 style="font-family:var(--display);font-size:15px;font-weight:600;'
                       f'color:var(--accent2);margin:8px 0 4px;">{md_inline(m.group(1))}</h3>')
            i += 1
            continue

        # Blockquote / callout
        if stripped.startswith('>'):
            raw = stripped.lstrip('> ').strip()
            upper = raw.upper()
            if 'DO NOT' in upper or 'WARNING' in upper or 'DANGER' in upper:
                cls, lbl = 'danger', '⚠ WARNING'
            elif upper.startswith('NOTE') or upper.startswith('💡'):
                cls, lbl = 'blue', '💡 NOTE'
            else:
                cls, lbl = 'warn', '⚠ NOTE'
            out.append(f'<div class="callout {cls}" style="margin:6px 0;padding:8px 12px;">'
                       f'<p style="font-size:13px;">{md_inline(raw)}</p></div>')
            i += 1
            continue

        # Bullet list
        if re.match(r'^[-*]\s', stripped):
            while i < len(lines) and re.match(r'^[-*]\s', lines[i].strip()):
                item = md_inline(lines[i].strip()[2:].strip())
                out.append(f'<div style="display:flex;gap:8px;margin:3px 0;font-size:13px;'
                           f'color:var(--muted);"><span style="color:var(--accent);'
                           f'flex-shrink:0;">·</span><span>{item}</span></div>')
                i += 1
            continue

        # Numbered list
        if re.match(r'^\d+\.\s', stripped):
            num = 0
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i].strip()):
                num += 1
                item = md_inline(re.sub(r'^\d+\.\s*', '', lines[i].strip()))
                out.append(f'<div class="step"><div class="snum">{num}</div>'
                           f'<div><div class="sdesc">{item}</div></div></div>')
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
        out.append(f'<p style="font-size:14px;line-height:1.6;color:var(--muted);'
                   f'margin:6px 0;">{text}</p>')
        i += 1

    flush_table()
    return '\n'.join(out)


# ── Build full HTML ────────────────────────────────────────────
def build():
    print('Building slide deck -> ' + str(OUTPUT_PATH))

    all_slides = []      # list of (slide_title_html, slide_body_html)
    modules_js = []      # for JS sidebar
    total_slides = 0

    for code, track, title, rel_path in MODULES:
        md_path = REPO_ROOT / rel_path
        colour = TRACK_COLOURS.get(track, '#00c896')

        if not md_path.exists():
            print(f'  [SKIP] {code} - {md_path.name} not found')
            # Placeholder title slide only
            placeholder = (
                f'  <div class="badge">TRACK {track.upper()} · MODULE {code}</div>'
                f'  <div style="flex:1;display:flex;flex-direction:column;justify-content:center;">'
                f'  <h1 style="font-size:52px;color:var(--muted);">{html.escape(title)}</h1>'
                f'  <p style="color:var(--muted);margin-top:16px;">Module not yet written.</p>'
                f'  </div>'
            )
            start = total_slides
            all_slides.append((title, placeholder))
            total_slides += 1
            modules_js.append({
                'code': code, 'track': track, 'title': title,
                'start': start, 'count': 1, 'color': colour
            })
            continue

        print(f'  [OK]   {code} - {title}')
        md_text = md_path.read_text(encoding='utf-8')
        slide_list = md_to_slides(code, track, title, md_text)
        start = total_slides
        for st, sb in slide_list:
            all_slides.append((st, sb))
            total_slides += 1
        modules_js.append({
            'code': code, 'track': track, 'title': title,
            'start': start, 'count': len(slide_list), 'color': colour
        })

    # ── Render slide divs ──────────────────────────────────────
    slides_html = []
    for idx, (stitle, sbody) in enumerate(all_slides):
        active = ' active' if idx == 0 else ''
        slides_html.append(
            f'<div class="slide{active}" data-title="{html.escape(stitle)}">\n{sbody}\n</div>'
        )

    modules_json = json.dumps(modules_js)

    # ── Assemble document ──────────────────────────────────────
    doc = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZombieVerter VCU — Training Series Slides</title>
<style>@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow+Condensed:wght@300;400;600;700;900&family=Barlow:wght@300;400;500;600&display=swap');
:root{{--bg:#0b0f10;--surface:#131a1c;--accent:#00c896;--accent2:#00a0ff;--warn:#ffaa00;--danger:#ff4455;--text:#d8eeea;--muted:#4a6860;--border:#1e2d30;--sidebar:260px;--mono:'Share Tech Mono',monospace;--display:'Barlow Condensed',sans-serif;--body:'Barlow',sans-serif;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{height:100%;background:var(--bg);color:var(--text);font-family:var(--body);overflow:hidden;}}
.app{{display:flex;height:100%;}}
.sidebar{{width:var(--sidebar);flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;transition:width .25s;}}
.sidebar.collapsed{{width:0;}}
.sidebar-header{{padding:16px 16px 12px;border-bottom:1px solid var(--border);flex-shrink:0;}}
.sidebar-logo{{display:flex;align-items:center;gap:10px;margin-bottom:4px;}}
.logo-box{{width:32px;height:32px;background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:13px;font-weight:bold;color:#000;flex-shrink:0;}}
.sidebar-title{{font-family:var(--display);font-size:15px;font-weight:700;color:#fff;white-space:nowrap;}}
.sidebar-sub{{font-family:var(--mono);font-size:10px;color:var(--muted);white-space:nowrap;}}
.module-list{{flex:1;overflow-y:auto;padding:8px 0;}}
.module-list::-webkit-scrollbar{{width:3px;}}
.module-list::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px;}}
.track-label{{font-family:var(--mono);font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding:10px 16px 4px;white-space:nowrap;}}
.module-item{{display:flex;align-items:center;gap:10px;padding:8px 16px;cursor:pointer;transition:background .15s;border-left:3px solid transparent;white-space:nowrap;}}
.module-item:hover{{background:rgba(255,255,255,.03);}}
.module-item.active{{background:rgba(0,200,150,.06);border-left-color:var(--accent);}}
.module-code{{font-family:var(--mono);font-size:11px;font-weight:bold;width:42px;flex-shrink:0;}}
.module-name{{font-size:12px;color:var(--text);overflow:hidden;text-overflow:ellipsis;}}
.module-slides{{font-family:var(--mono);font-size:10px;color:var(--muted);margin-left:auto;flex-shrink:0;padding-left:6px;}}
.main{{flex:1;display:flex;flex-direction:column;overflow:hidden;position:relative;}}
.topbar{{background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;padding:8px 16px;flex-shrink:0;min-height:48px;}}
.toggle-btn{{width:32px;height:32px;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:16px;flex-shrink:0;transition:all .15s;}}
.toggle-btn:hover{{background:rgba(255,255,255,.08);color:var(--text);}}
.topbar-module{{font-family:var(--mono);font-size:11px;color:var(--accent);background:rgba(0,200,150,.08);border:1px solid rgba(0,200,150,.2);padding:3px 9px;border-radius:4px;flex-shrink:0;}}
.topbar-title{{font-family:var(--display);font-size:18px;font-weight:600;color:#fff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.topbar-slide{{font-family:var(--mono);font-size:11px;color:var(--muted);margin-left:auto;flex-shrink:0;}}
.fw-badge{{font-family:var(--mono);font-size:10px;color:var(--warn);background:rgba(255,170,0,.08);border:1px solid rgba(255,170,0,.2);padding:3px 9px;border-radius:4px;flex-shrink:0;}}
.deck{{flex:1;position:relative;overflow:hidden;}}
.slide{{position:absolute;inset:0;display:none;flex-direction:column;padding:44px 56px 70px;background:var(--bg);}}
.slide.active{{display:flex;}}
.slide::before{{content:'';position:absolute;top:0;left:0;width:6px;height:100%;background:linear-gradient(to bottom,var(--accent),var(--accent2));}}
.slide::after{{content:'';position:absolute;bottom:0;left:6px;right:0;height:2px;background:linear-gradient(to right,var(--accent),transparent);}}
.badge{{font-family:var(--mono);font-size:11px;color:var(--accent);background:rgba(0,200,150,.08);border:1px solid rgba(0,200,150,.25);padding:4px 10px;border-radius:4px;display:inline-block;margin-bottom:14px;letter-spacing:.1em;}}
h1{{font-family:var(--display);font-size:68px;font-weight:900;line-height:1;color:#fff;margin-bottom:14px;}}
h2{{font-family:var(--display);font-size:48px;font-weight:700;line-height:1.1;color:#fff;margin-bottom:18px;}}
h2 .sub{{font-size:26px;font-weight:400;color:var(--muted);display:block;margin-top:4px;}}
h3{{font-family:var(--display);font-size:24px;font-weight:600;color:var(--accent);margin-bottom:10px;text-transform:uppercase;letter-spacing:.05em;}}
p{{font-size:16px;line-height:1.6;color:var(--text);max-width:800px;}}
.row{{display:flex;gap:36px;flex:1;align-items:flex-start;}}
.col{{flex:1;}}
table{{width:100%;border-collapse:collapse;font-size:14px;}}
th{{font-family:var(--mono);font-size:10px;color:var(--muted);text-align:left;padding:5px 10px;border-bottom:1px solid rgba(255,255,255,.06);text-transform:uppercase;letter-spacing:.08em;}}
td{{padding:7px 10px;border-bottom:1px solid rgba(255,255,255,.04);vertical-align:top;font-size:13px;}}
td:first-child{{font-family:var(--mono);font-size:12px;color:var(--accent);}}
td:last-child{{color:var(--muted);}}
.callout{{padding:12px 16px;border-radius:8px;border-left:4px solid;margin:10px 0;}}
.callout.info{{background:rgba(0,200,150,.06);border-color:var(--accent);}}
.callout.warn{{background:rgba(255,170,0,.08);border-color:var(--warn);}}
.callout.danger{{background:rgba(255,68,85,.08);border-color:var(--danger);}}
.callout.blue{{background:rgba(0,160,255,.06);border-color:var(--accent2);}}
.callout p{{font-size:14px;line-height:1.5;max-width:none;}}
.code{{background:rgba(0,0,0,.4);border:1px solid rgba(0,200,150,.15);border-radius:8px;padding:12px 16px;font-family:var(--mono);font-size:12px;line-height:1.9;margin:10px 0;white-space:pre;overflow-x:auto;}}
.steps{{display:flex;flex-direction:column;gap:11px;}}
.step{{display:flex;gap:13px;align-items:flex-start;margin:3px 0;}}
.snum{{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:12px;font-weight:bold;color:#000;flex-shrink:0;margin-top:2px;}}
.sdesc{{font-size:13px;color:var(--muted);line-height:1.4;padding-top:6px;}}
nav{{position:absolute;bottom:0;left:0;right:0;background:var(--surface);border-top:1px solid var(--border);display:flex;align-items:center;padding:9px 18px;gap:10px;z-index:10;}}
.nbtn{{background:rgba(0,200,150,.1);border:1px solid rgba(0,200,150,.2);color:var(--accent);font-family:var(--mono);font-size:12px;padding:6px 14px;border-radius:5px;cursor:pointer;transition:all .15s;}}
.nbtn:hover{{background:rgba(0,200,150,.2);}}.nbtn:disabled{{opacity:.3;cursor:not-allowed;}}
.nbtn.jump{{background:rgba(255,255,255,.04);border-color:var(--border);color:var(--muted);}}
.nbtn.jump:hover{{border-color:var(--accent);color:var(--accent);background:rgba(0,200,150,.05);}}
.sctr{{font-family:var(--mono);font-size:12px;color:var(--muted);}}
.progress-bar{{flex:1;height:3px;background:var(--border);border-radius:2px;overflow:hidden;}}
.progress-fill{{height:100%;background:linear-gradient(to right,var(--accent),var(--accent2));border-radius:2px;transition:width .2s;}}
.kh{{font-family:var(--mono);font-size:10px;color:var(--muted);opacity:.4;}}
</style></head>
<body>
<div class="app">
<div class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <div class="sidebar-logo">
      <div class="logo-box">ZV</div>
      <div>
        <div class="sidebar-title">ZombieVerter</div>
        <div class="sidebar-sub" id="deckStats">{len(MODULES)} modules · {total_slides} slides · V2.40A</div>
      </div>
    </div>
  </div>
  <div class="module-list" id="moduleList"></div>
</div>
<div class="main">
<div class="topbar">
  <button class="toggle-btn" onclick="toggleSidebar()">☰</button>
  <span class="topbar-module" id="topbarModule">—</span>
  <span class="topbar-title" id="topbarTitle">ZombieVerter Training</span>
  <span class="fw-badge">V2.40A</span>
  <span class="topbar-slide" id="topbarSlide">Slide 1 of {total_slides}</span>
</div>
<div class="deck" id="deck">
{''.join(chr(10) + s for s in slides_html)}
</div>
<nav>
  <button class="nbtn" id="prevBtn" onclick="navigate(-1)" disabled>← Prev</button>
  <span class="sctr" id="ctr">1 / {total_slides}</span>
  <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:{100/total_slides:.2f}%"></div></div>
  <button class="nbtn jump" onclick="prevModule()">↑ Mod</button>
  <button class="nbtn jump" onclick="nextModule()">↓ Mod</button>
  <button class="nbtn" id="nextBtn" onclick="navigate(1)">Next →</button>
  <span class="kh">← → · ↑↓ Mod · Esc sidebar</span>
</nav>
</div></div>
<script>
const MODULES = {modules_json};
const TOTAL = {total_slides};
const slides = document.querySelectorAll('.slide');
let cur = 0;
const moduleList = document.getElementById('moduleList');
let lastTrack = '';
MODULES.forEach((m, mi) => {{
  if (m.track !== lastTrack) {{
    const lbl = document.createElement('div');
    lbl.className = 'track-label';
    lbl.textContent = '— ' + m.track;
    moduleList.appendChild(lbl);
    lastTrack = m.track;
  }}
  const item = document.createElement('div');
  item.className = 'module-item' + (mi === 0 ? ' active' : '');
  item.id = 'mod-' + mi;
  item.innerHTML = `<span class="module-code" style="color:${{m.color}}">${{m.code.replace('-X','')}}</span><span class="module-name">${{m.title}}</span><span class="module-slides">${{m.count}}</span>`;
  item.onclick = () => goTo(m.start);
  moduleList.appendChild(item);
}});
function getModuleAt(idx) {{ let c = MODULES[0]; for (const m of MODULES) {{ if (idx >= m.start) c = m; else break; }} return c; }}
function getModuleIndex(idx) {{ let i = 0; for (let j = 0; j < MODULES.length; j++) {{ if (idx >= MODULES[j].start) i = j; else break; }} return i; }}
function updateUI() {{
  slides.forEach((s, i) => s.classList.toggle('active', i === cur));
  document.getElementById('ctr').textContent = `${{cur + 1}} / ${{TOTAL}}`;
  document.getElementById('progressFill').style.width = `${{((cur + 1) / TOTAL * 100).toFixed(2)}}%`;
  const m = getModuleAt(cur);
  document.getElementById('topbarModule').textContent = m.code;
  document.getElementById('topbarTitle').textContent = m.title;
  document.getElementById('topbarSlide').textContent = `Slide ${{cur - m.start + 1}} of ${{m.count}} · ${{m.code}}`;
  const mi = getModuleIndex(cur);
  document.querySelectorAll('.module-item').forEach((el, i) => el.classList.toggle('active', i === mi));
  const el = document.getElementById('mod-' + mi);
  if (el) el.scrollIntoView({{ block: 'nearest' }});
  document.getElementById('prevBtn').disabled = cur === 0;
  document.getElementById('nextBtn').disabled = cur === TOTAL - 1;
}}
function goTo(n) {{ cur = Math.max(0, Math.min(n, TOTAL - 1)); updateUI(); }}
function navigate(d) {{ goTo(cur + d); }}
function prevModule() {{ const mi = getModuleIndex(cur); goTo(mi > 0 ? MODULES[mi - 1].start : 0); }}
function nextModule() {{ const mi = getModuleIndex(cur); if (mi < MODULES.length - 1) goTo(MODULES[mi + 1].start); }}
function toggleSidebar() {{ document.getElementById('sidebar').classList.toggle('collapsed'); }}
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || (e.key === ' ' && !e.shiftKey)) navigate(1);
  if (e.key === 'ArrowLeft'  || (e.key === ' ' && e.shiftKey))  navigate(-1);
  if (e.key === 'ArrowDown') nextModule();
  if (e.key === 'ArrowUp')   prevModule();
  if (e.key === 'Escape')    toggleSidebar();
}});
goTo(0);
</script>
</body></html>'''

    OUTPUT_PATH.write_text(doc, encoding='utf-8')
    size_kb = OUTPUT_PATH.stat().st_size // 1024
    print(f'Done - {size_kb} KB · {total_slides} slides · {len(MODULES)} modules -> {OUTPUT_PATH}')


if __name__ == '__main__':
    build()
