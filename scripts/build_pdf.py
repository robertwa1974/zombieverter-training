#!/usr/bin/env python3
"""
ZombieVerter VCU Training Series — PDF Builder
Reads markdown source files from the repo and generates zombieverter-training-manual.pdf
Run from the repo root: python3 scripts/build_pdf.py
"""

import re
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ── Constants ─────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "zombieverter-training-manual.pdf"

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm

# ── Colours ───────────────────────────────────────────────────
C_GREEN   = colors.HexColor('#00c896')
C_BLUE    = colors.HexColor('#00a0ff')
C_AMBER   = colors.HexColor('#ffaa00')
C_RED     = colors.HexColor('#ff4455')
C_DARK    = colors.HexColor('#1a1a2e')
C_MID     = colors.HexColor('#16213e')
C_LIGHT   = colors.HexColor('#e8f4f8')
C_WARN_BG = colors.HexColor('#fff3cd')
C_WARN_BD = colors.HexColor('#ffc107')
C_DNGR_BG = colors.HexColor('#fde8ea')
C_DNGR_BD = colors.HexColor('#ff4455')
C_INFO_BG = colors.HexColor('#e8f4ff')
C_TBL_HD  = colors.HexColor('#2d4a6b')
C_TBL_ALT = colors.HexColor('#f5f9ff')
C_CODE_BG = colors.HexColor('#f4f4f4')

TRACK_COLOURS = {
    'F': C_GREEN,
    'H': C_BLUE,
    'W': colors.HexColor('#20b2aa'),
    'C': colors.HexColor('#6a5acd'),
    'I': colors.HexColor('#e07b39'),
    'A': C_AMBER,
}


# ══════════════════════════════════════════════════════════════
# Styles
# ══════════════════════════════════════════════════════════════
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s['normal'] = ParagraphStyle('zv_normal', parent=base['Normal'],
        fontSize=9.5, leading=14, textColor=colors.HexColor('#222222'), spaceAfter=5)

    s['body'] = ParagraphStyle('zv_body', parent=s['normal'],
        leading=14.5, spaceAfter=7, alignment=TA_JUSTIFY)

    s['h1'] = ParagraphStyle('zv_h1', fontSize=17, textColor=C_GREEN,
        spaceBefore=14, spaceAfter=5, leading=21, fontName='Helvetica-Bold',
        parent=base['Normal'])

    s['h2'] = ParagraphStyle('zv_h2', fontSize=12.5, textColor=C_BLUE,
        spaceBefore=11, spaceAfter=4, leading=16, fontName='Helvetica-Bold',
        parent=base['Normal'])

    s['h3'] = ParagraphStyle('zv_h3', fontSize=10.5, textColor=C_DARK,
        spaceBefore=9, spaceAfter=3, leading=14, fontName='Helvetica-Bold',
        parent=base['Normal'])

    s['module_title'] = ParagraphStyle('zv_module_title', fontSize=21,
        textColor=C_DARK, fontName='Helvetica-Bold', leading=25, spaceAfter=4,
        parent=base['Normal'])

    s['bullet'] = ParagraphStyle('zv_bullet', parent=s['normal'],
        leftIndent=12, firstLineIndent=-10, spaceAfter=3, leading=14)

    s['num'] = ParagraphStyle('zv_num', parent=s['bullet'])

    s['code_inline'] = ParagraphStyle('zv_code', parent=s['normal'],
        fontName='Courier', fontSize=9, backColor=C_CODE_BG,
        borderPad=3, spaceAfter=5)

    s['note'] = ParagraphStyle('zv_note', parent=s['normal'],
        fontSize=8.5, textColor=colors.HexColor('#555555'),
        fontName='Helvetica-Oblique', spaceAfter=4)

    s['source'] = ParagraphStyle('zv_source', parent=s['normal'],
        fontSize=8, textColor=colors.HexColor('#888888'),
        fontName='Helvetica-Oblique', spaceAfter=2, spaceBefore=6)

    s['toc_track'] = ParagraphStyle('zv_toc_track', fontSize=10, textColor=C_GREEN,
        spaceBefore=8, spaceAfter=2, fontName='Helvetica-Bold', parent=base['Normal'])

    s['toc_item'] = ParagraphStyle('zv_toc_item', fontSize=9.5,
        leftIndent=10, spaceAfter=2, parent=base['Normal'])

    s['cover_title'] = ParagraphStyle('zv_cover_title', fontSize=32,
        textColor=C_GREEN, fontName='Helvetica-Bold', alignment=TA_CENTER,
        leading=38, parent=base['Normal'])

    s['cover_sub'] = ParagraphStyle('zv_cover_sub', fontSize=18,
        textColor=C_DARK, fontName='Helvetica-Bold', alignment=TA_CENTER,
        leading=24, parent=base['Normal'])

    s['cover_meta'] = ParagraphStyle('zv_cover_meta', fontSize=10,
        textColor=colors.HexColor('#555555'), alignment=TA_CENTER,
        leading=16, parent=base['Normal'])

    return s


# ══════════════════════════════════════════════════════════════
# Shared rendering helpers
# ══════════════════════════════════════════════════════════════
def std_table(data, col_widths=None, header=True):
    w = PAGE_W - 2 * MARGIN
    if col_widths is None:
        n = len(data[0])
        col_widths = [w / n] * n
    ts = TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  C_TBL_HD),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  9),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, C_TBL_ALT]),
        ('FONTSIZE',      (0, 1), (-1, -1), 9),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
    ])
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(ts)
    return t


def warn_box(text, styles, kind='warn'):
    if kind == 'danger':
        bg, bd, icon = C_DNGR_BG, C_DNGR_BD, '⚠️ '
    elif kind == 'info':
        bg, bd, icon = C_INFO_BG, C_BLUE, 'ℹ️ '
    else:
        bg, bd, icon = C_WARN_BG, C_WARN_BD, '⚠️ '
    style = ParagraphStyle('_warn', parent=styles['normal'],
        backColor=bg, borderColor=bd, borderWidth=1.5,
        borderPad=7, spaceAfter=8)
    return Paragraph(icon + text, style)


def module_header(story, track, code, title, styles):
    colour = TRACK_COLOURS.get(code[0], C_GREEN)
    if 'X' in code:
        colour = C_RED
    badge = ParagraphStyle('_badge', parent=styles['normal'],
        fontSize=9, backColor=colour, textColor=colors.white,
        fontName='Helvetica-Bold', borderPad=4, leading=12, alignment=TA_CENTER)
    story.append(PageBreak())
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f'TRACK {track.upper()} · MODULE {code}', badge))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(title, styles['module_title']))
    story.append(HRFlowable(width='100%', thickness=2, color=colour, spaceAfter=8))


# ══════════════════════════════════════════════════════════════
# Markdown → flowables  (lightweight subset parser)
# ══════════════════════════════════════════════════════════════
def md_inline(text):
    """Convert inline markdown (bold, code, italics) to ReportLab XML."""
    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    # Inline code `text`
    text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
    return text


def md_to_story(md_text, styles, skip_h1=True):
    """
    Convert a markdown string to a list of reportlab flowables.
    skip_h1: if True, the top-level # heading is omitted (already rendered
              by module_header).
    """
    story = []
    lines = md_text.splitlines()
    i = 0
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        # Determine column widths evenly
        n_cols = max(len(r) for r in table_rows)
        w = PAGE_W - 2 * MARGIN
        col_w = [w / n_cols] * n_cols
        story.append(std_table(table_rows, col_widths=col_w))
        story.append(Spacer(1, 3 * mm))
        table_rows = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Blank line ─────────────────────────────────────────
        if not stripped:
            flush_table()
            i += 1
            continue

        # ── HR ─────────────────────────────────────────────────
        if re.match(r'^-{3,}$', stripped):
            flush_table()
            story.append(HRFlowable(width='100%', thickness=0.5,
                                     color=colors.HexColor('#dddddd'), spaceAfter=4))
            i += 1
            continue

        # ── Markdown table row ─────────────────────────────────
        if stripped.startswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            # Skip separator rows (---|---|--)
            if all(re.match(r'^[-: ]+$', c) for c in cells):
                i += 1
                continue
            table_rows.append([md_inline(c) for c in cells])
            i += 1
            continue
        else:
            flush_table()

        # ── Headings ───────────────────────────────────────────
        m = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if m:
            level = len(m.group(1))
            text = md_inline(m.group(2))
            if level == 1:
                if not skip_h1:
                    story.append(Paragraph(text, styles['h1']))
            elif level == 2:
                story.append(Paragraph(text, styles['h2']))
            elif level == 3:
                story.append(Paragraph(text, styles['h3']))
            else:
                story.append(Paragraph(f'<b>{text}</b>', styles['normal']))
            i += 1
            continue

        # ── Blockquote ─────────────────────────────────────────
        if stripped.startswith('>'):
            text = md_inline(stripped.lstrip('> ').strip())
            kind = 'danger' if '⚠️' in text or 'DO NOT' in text or 'WARNING' in text.upper() else 'info'
            story.append(warn_box(text, styles, kind=kind))
            i += 1
            continue

        # ── Bullet list ────────────────────────────────────────
        if re.match(r'^[-*]\s', stripped):
            text = md_inline(stripped[2:].strip())
            # Collect continuation lines (indented)
            while i + 1 < len(lines):
                nxt = lines[i + 1]
                if nxt.startswith('  ') and nxt.strip() and not re.match(r'^\s*[-*]\s', nxt):
                    text += ' ' + md_inline(nxt.strip())
                    i += 1
                else:
                    break
            story.append(Paragraph(f'• {text}', styles['bullet']))
            i += 1
            continue

        # ── Numbered list ──────────────────────────────────────
        if re.match(r'^\d+\.\s', stripped):
            text = md_inline(re.sub(r'^\d+\.\s*', '', stripped))
            story.append(Paragraph(text, styles['num']))
            i += 1
            continue

        # ── Bold-only line (section label) ─────────────────────
        if re.match(r'^\*\*.+\*\*$', stripped):
            story.append(Paragraph(md_inline(stripped), styles['h3']))
            i += 1
            continue

        # ── Source / metadata lines ────────────────────────────
        if stripped.startswith('*Source:') or stripped.startswith('*Last verified'):
            story.append(Paragraph(stripped.strip('*'), styles['source']))
            i += 1
            continue

        # ── Meta header lines (Track, Prerequisites, etc.) ─────
        if stripped.startswith('**Track:**') or stripped.startswith('**Prerequisites:'):
            story.append(Paragraph(md_inline(stripped), styles['note']))
            i += 1
            continue

        # ── Default: body paragraph ────────────────────────────
        text = md_inline(stripped)
        # Collect continuation lines
        while i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if (nxt and not nxt.startswith('#') and not nxt.startswith('|')
                    and not nxt.startswith('>') and not re.match(r'^[-*]\s', nxt)
                    and not re.match(r'^\d+\.\s', nxt) and not re.match(r'^-{3,}$', nxt)):
                text += ' ' + md_inline(nxt)
                i += 1
            else:
                break
        story.append(Paragraph(text, styles['body']))
        i += 1

    flush_table()
    return story


# ══════════════════════════════════════════════════════════════
# Module catalogue — maps module code → markdown path
# ══════════════════════════════════════════════════════════════
MODULES = [
    # (code, track_name, title, md_path_relative_to_repo_root)
    ('F01', 'Foundation',     'What Is a VCU and Why Do You Need One',        'foundation/F01-what-is-a-vcu.md'),
    ('F02', 'Foundation',     'ZombieVerter Ecosystem Overview',               'foundation/F02-zombieverter-ecosystem-overview.md'),
    ('F03', 'Foundation',     'EV Drivetrain Fundamentals',                    'foundation/F03-ev-drivetrain-fundamentals.md'),
    ('F04', 'Foundation',     'High Voltage Safety',                           'foundation/F04-high-voltage-safety.md'),
    ('H01', 'Hardware',       'VCU Hardware Walkthrough',                      'hardware/H01-vcu-hardware-walkthrough.md'),
    ('W01', 'Wiring',         'Wiring Philosophy & Best Practices',            'wiring/W01-wiring-philosophy.md'),
    ('W02', 'Wiring',         'Throttle & Brake Wiring',                       'wiring/W02-throttle-and-brake-wiring.md'),
    ('W03', 'Wiring',         'Contactor & Precharge Circuit',                 'wiring/W03-contactor-and-precharge-circuit.md'),
    ('W04', 'Wiring',         'HVIL — High Voltage Interlock Loop',            'wiring/W04-hvil.md'),
    ('W05', 'Wiring',         'Cooling System Control',                        'wiring/W05-cooling-system-control.md'),
    ('W06', 'Wiring',         '12V Auxiliary & Ignition Wiring',               'wiring/W06-12v-auxiliary-and-ignition-wiring.md'),
    ('C00', 'Configuration',  'Firmware Version History',                      'configuration/C00-firmware-version-history.md'),
    ('C01', 'Configuration',  'Flashing Firmware',                             'configuration/C01-flashing-firmware.md'),
    ('C02', 'Configuration',  'Web Interface Walkthrough',                     'configuration/C02-web-interface-walkthrough.md'),
    ('C03', 'Configuration',  'Essential Parameters: First Start',             'configuration/C03-essential-parameters-first-start.md'),
    ('C04', 'Configuration',  'Throttle Calibration',                          'configuration/C04-throttle-calibration.md'),
    ('C06', 'Configuration',  'Fault Codes & Status Flags',                    'configuration/C06-fault-codes-and-status-flags.md'),
    ('I01', 'Integration',    'Nissan Leaf Inverter',                          'integration/I01-nissan-leaf-inverter.md'),
    ('I02', 'Integration',    'Tesla Drive Units (SDU & LDU)',                 'integration/I02-tesla-ldu.md'),
    ('I03', 'Integration',    'GS450h Transaxle',                              'integration/I03-gs450h-transaxle.md'),
    ('I03-X','Integration',   'GS450h — Wiring & Oil Pump Deep Dive',          'integration/I03-X-gs450h-wiring-and-oil-pump-deep-dive.md'),
    ('I04', 'Integration',    'Mitsubishi Outlander Drive Unit',               'integration/I04-mitsubishi-outlander-drive-unit.md'),
    ('A01', 'Advanced',       'Regen Tuning',                                  'advanced/A01-regen-tuning.md'),
    ('A02', 'Advanced',       'Charge Control & Popular Chargers',             'advanced/A02-charge-control-and-chargers.md'),
    ('A03', 'Advanced',       'BMS Integration',                               'advanced/A03-bms-integration.md'),
    ('A04', 'Advanced',       'Gear Selectors & Shifters',                     'advanced/A04-gear-selectors-and-shifters.md'),
    ('A05', 'Advanced',       'CAN Gateway & Multi-Node Systems',              'advanced/A05-can-gateway-and-multi-node-systems.md'),
    ('A06', 'Advanced',       'Firmware Customisation & Contributing',         'advanced/A06-firmware-customisation-and-contributing.md'),
]


# ══════════════════════════════════════════════════════════════
# Cover & TOC
# ══════════════════════════════════════════════════════════════
def build_cover(story, styles):
    story.append(Spacer(1, 28 * mm))
    story.append(Paragraph('ZombieVerter VCU', styles['cover_title']))
    story.append(Paragraph('Training Series', styles['cover_sub']))
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width='60%', thickness=2, color=C_GREEN,
                              hAlign='CENTER', spaceAfter=8))
    story.append(Paragraph(
        'Complete reference guide for DIY EV conversion builders',
        styles['cover_meta']))
    story.append(Paragraph(
        f'{len(MODULES)} modules · 6 tracks · Firmware V2.30A (August 2025)',
        styles['cover_meta']))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph('github.com/robertwa1974/zombieverter-training',
                             styles['cover_meta']))
    story.append(Paragraph('openinverter.org · evbmw.com', styles['cover_meta']))
    story.append(Spacer(1, 10 * mm))

    track_data = [
        ['Track', 'Name', 'Modules'],
        ['F', 'Foundation', 'F01–F04'],
        ['H', 'Hardware',   'H01'],
        ['W', 'Wiring',     'W01–W06'],
        ['C', 'Configuration', 'C00–C06'],
        ['I', 'Integration', 'I01–I04'],
        ['A', 'Advanced',   'A01–A06'],
    ]
    story.append(std_table(track_data, col_widths=[12 * mm, 50 * mm, 30 * mm]))


def build_toc(story, styles):
    story.append(PageBreak())
    story.append(Paragraph('Table of Contents', styles['h1']))
    story.append(Spacer(1, 4 * mm))

    current_track = None
    for code, track, title, _ in MODULES:
        if track != current_track:
            story.append(Paragraph(f'■ {track.upper()}', styles['toc_track']))
            current_track = track
        story.append(Paragraph(f'{code} · {title}', styles['toc_item']))


# ══════════════════════════════════════════════════════════════
# Main build
# ══════════════════════════════════════════════════════════════
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.HexColor('#888888'))
    canvas.drawString(MARGIN, 12 * mm,
        'github.com/robertwa1974/zombieverter-training · openinverter.org · V2.30A')
    canvas.drawRightString(PAGE_W - MARGIN, 12 * mm, str(doc.page))
    canvas.setStrokeColor(colors.HexColor('#dddddd'))
    canvas.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
    canvas.restoreState()


def build():
    print(f'Building PDF → {OUTPUT_PATH}')
    styles = make_styles()

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title='ZombieVerter VCU Training Series',
        author='Rob Wagstaff | openinverter.org community',
        subject='ZombieVerter VCU V2.30A — Complete Reference Manual',
    )

    story = []
    build_cover(story, styles)
    build_toc(story, styles)

    missing = []
    for code, track, title, rel_path in MODULES:
        md_path = REPO_ROOT / rel_path
        if not md_path.exists():
            print(f'  [SKIP] {code} — {md_path} not found')
            missing.append((code, title))
            continue

        print(f'  [OK]   {code} — {title}')
        md_text = md_path.read_text(encoding='utf-8')

        module_header(story, track, code, title, styles)
        story.extend(md_to_story(md_text, styles, skip_h1=True))

    if missing:
        # Append a "modules not yet written" notice at the end
        story.append(PageBreak())
        story.append(Paragraph('Modules In Progress', styles['h1']))
        story.append(Paragraph(
            'The following modules are planned but not yet written. '
            'Check the repository for the latest status.',
            styles['body']))
        for code, title in missing:
            story.append(Paragraph(f'• {code} — {title}', styles['bullet']))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f'Done — {OUTPUT_PATH.stat().st_size // 1024} KB, written to {OUTPUT_PATH}')


if __name__ == '__main__':
    build()
