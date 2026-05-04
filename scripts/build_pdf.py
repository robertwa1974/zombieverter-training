#!/usr/bin/env python3
"""
ZombieVerter VCU Training Series - PDF Builder
Reads markdown source files from the repo and generates zombieverter-training-manual.pdf
Run from the repo root: python3 scripts/build_pdf.py
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)

# ── Register Unicode fonts (DejaVu - full glyph coverage) ─────
pdfmetrics.registerFont(TTFont('Body',     '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Body-Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Body-Italic','/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('Body-BoldItalic','/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf'))
pdfmetrics.registerFont(TTFont('Mono',     '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('Mono-Bold','/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'))
pdfmetrics.registerFontFamily('Body',
    normal='Body', bold='Body-Bold',
    italic='Body-Italic', boldItalic='Body-BoldItalic')

# ── Constants ─────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "zombieverter-training-manual.pdf"
PAGE_W, PAGE_H = A4
MARGIN = 20 * mm

# ── Colours ───────────────────────────────────────────────────
C_GREEN   = colors.HexColor('#00c896')
C_BLUE    = colors.HexColor('#00a0ff')
C_AMBER   = colors.HexColor('#ffaa00')
C_RED     = colors.HexColor('#ff4455')
C_DARK    = colors.HexColor('#1a1a2e')
C_WARN_BG = colors.HexColor('#fff3cd')
C_WARN_BD = colors.HexColor('#ffc107')
C_DNGR_BG = colors.HexColor('#fde8ea')
C_DNGR_BD = colors.HexColor('#ff4455')
C_INFO_BG = colors.HexColor('#e8f4ff')
C_TBL_HD  = colors.HexColor('#2d4a6b')
C_TBL_ALT = colors.HexColor('#f5f9ff')

TRACK_COLOURS = {
    'F': C_GREEN,
    'H': C_BLUE,
    'W': colors.HexColor('#20b2aa'),
    'C': colors.HexColor('#6a5acd'),
    'I': colors.HexColor('#e07b39'),
    'A': C_AMBER,
}

# ── Module catalogue ──────────────────────────────────────────
MODULES = [
    ('F01', 'Foundation',    'What Is a VCU and Why Do You Need One',  'foundation/F01-what-is-a-vcu-and-why-do-you-need-one.md'),
    ('F02', 'Foundation',    'ZombieVerter Ecosystem Overview',         'foundation/F02-zombieverter-ecosystem-overview.md'),
    ('F03', 'Foundation',    'EV Drivetrain Fundamentals',              'foundation/F03-ev-drivetrain-fundamentals.md'),
    ('F04', 'Foundation',    'High Voltage Safety',                     'foundation/F04-high-voltage-safety.md'),
    ('H01', 'Hardware',      'VCU Hardware Walkthrough',                'hardware/H01-vcu-hardware-walkthrough.md'),
    ('W01', 'Wiring',        'Wiring Philosophy and Best Practices',    'wiring/W01-wiring-philosophy-and-best-practices.md'),
    ('W02', 'Wiring',        'Throttle and Brake Wiring',               'wiring/W02-throttle-and-brake-wiring.md'),
    ('W03', 'Wiring',        'Contactor and Precharge Circuit',         'wiring/W03-contactor-and-precharge-circuit.md'),
    ('W04', 'Wiring',        'HVIL High Voltage Interlock Loop',        'wiring/W04-hvil-high-voltage-interlock-loop.md'),
    ('W05', 'Wiring',        'Cooling System Control',                  'wiring/W05-cooling-system-control.md'),
    ('W06', 'Wiring',        '12V Auxiliary and Ignition Wiring',       'wiring/W06-12v-auxiliary-and-ignition-wiring.md'),
    ('C00', 'Configuration', 'Firmware Version History',                'configuration/C00-firmware-version-history.md'),
    ('C01', 'Configuration', 'Flashing Firmware',                       'configuration/C01-flashing-firmware.md'),
    ('C02', 'Configuration', 'Web Interface Walkthrough',               'configuration/C02-web-interface-walkthrough.md'),
    ('C03', 'Configuration', 'Essential Parameters: First Start',       'configuration/C03-essential-parameters-first-start.md'),
    ('C04', 'Configuration', 'Throttle Calibration',                    'configuration/C04-throttle-calibration.md'),
    ('C06', 'Configuration', 'Fault Codes and Status Flags',            'configuration/C06-fault-codes-and-status-flags.md'),
    ('I01', 'Integration',   'Nissan Leaf Inverter',                    'integration/I01-nissan-leaf-inverter.md'),
    ('I02', 'Integration',   'Tesla Drive Units SDU and LDU',           'integration/I02-tesla-ldu.md'),
    ('I03', 'Integration',   'GS450h Transaxle',                       'integration/I03-gs450h-transaxle.md'),
    ('I03-X','Integration',  'GS450h Wiring and Oil Pump Deep Dive',    'integration/I03-X-gs450h-wiring-and-oil-pump-deep-dive.md'),
    ('I04', 'Integration',   'Mitsubishi Outlander Drive Unit',         'integration/I04-mitsubishi-outlander-drive-unit.md'),
    ('A01', 'Advanced',      'Regen Tuning',                            'advanced/A01-regen-tuning.md'),
    ('A02', 'Advanced',      'Charge Control and Popular Chargers',     'advanced/A02-charge-control-and-chargers.md'),
    ('A03', 'Advanced',      'BMS Integration',                         'advanced/A03-bms-integration.md'),
    ('A04', 'Advanced',      'Gear Selectors and Shifters',             'advanced/A04-gear-selectors-and-shifters.md'),
    ('A05', 'Advanced',      'CAN Gateway and Multi-Node Systems',      'advanced/A05-can-gateway-and-multi-node-systems.md'),
    ('A06', 'Advanced',      'Firmware Customisation and Contributing', 'advanced/A06-firmware-customisation-and-contributing.md'),
]

# ── Box-drawing / block characters that need monospace font ───
BOX_CHARS = set('█▓▒░─━│┃┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬═║▄▀■□▪▫')

def has_box_chars(text):
    return any(c in BOX_CHARS for c in text)


# ══════════════════════════════════════════════════════════════
# Styles
# ══════════════════════════════════════════════════════════════
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s['normal'] = ParagraphStyle('zv_normal', parent=base['Normal'],
        fontName='Body', fontSize=9.5, leading=14,
        textColor=colors.HexColor('#222222'), spaceAfter=5)

    s['body'] = ParagraphStyle('zv_body', parent=s['normal'],
        leading=14.5, spaceAfter=7, alignment=TA_JUSTIFY)

    s['h1'] = ParagraphStyle('zv_h1', parent=base['Normal'],
        fontName='Body-Bold', fontSize=17, textColor=C_GREEN,
        spaceBefore=14, spaceAfter=5, leading=21)

    s['h2'] = ParagraphStyle('zv_h2', parent=base['Normal'],
        fontName='Body-Bold', fontSize=12.5, textColor=C_BLUE,
        spaceBefore=11, spaceAfter=4, leading=16)

    s['h3'] = ParagraphStyle('zv_h3', parent=base['Normal'],
        fontName='Body-Bold', fontSize=10.5, textColor=C_DARK,
        spaceBefore=9, spaceAfter=3, leading=14)

    s['module_title'] = ParagraphStyle('zv_module_title', parent=base['Normal'],
        fontName='Body-Bold', fontSize=21, textColor=C_DARK,
        leading=25, spaceAfter=4)

    s['bullet'] = ParagraphStyle('zv_bullet', parent=s['normal'],
        leftIndent=12, firstLineIndent=-10, spaceAfter=3, leading=14)

    s['num'] = ParagraphStyle('zv_num', parent=s['bullet'])

    s['mono'] = ParagraphStyle('zv_mono', parent=base['Normal'],
        fontName='Mono', fontSize=8.5, leading=13,
        backColor=colors.HexColor('#f4f4f4'),
        borderPad=4, spaceAfter=3,
        textColor=colors.HexColor('#1a1a2e'))

    s['note'] = ParagraphStyle('zv_note', parent=s['normal'],
        fontName='Body-Italic', fontSize=8.5,
        textColor=colors.HexColor('#555555'), spaceAfter=4)

    s['source'] = ParagraphStyle('zv_source', parent=s['normal'],
        fontName='Body-Italic', fontSize=8,
        textColor=colors.HexColor('#888888'), spaceAfter=2, spaceBefore=6)

    s['toc_track'] = ParagraphStyle('zv_toc_track', parent=base['Normal'],
        fontName='Body-Bold', fontSize=10, textColor=C_GREEN,
        spaceBefore=8, spaceAfter=2)

    s['toc_item'] = ParagraphStyle('zv_toc_item', parent=base['Normal'],
        fontName='Body', fontSize=9.5, leftIndent=10, spaceAfter=2)

    s['cover_title'] = ParagraphStyle('zv_cover_title', parent=base['Normal'],
        fontName='Body-Bold', fontSize=32, textColor=C_GREEN,
        alignment=TA_CENTER, leading=38)

    s['cover_sub'] = ParagraphStyle('zv_cover_sub', parent=base['Normal'],
        fontName='Body-Bold', fontSize=18, textColor=C_DARK,
        alignment=TA_CENTER, leading=24)

    s['cover_meta'] = ParagraphStyle('zv_cover_meta', parent=base['Normal'],
        fontName='Body', fontSize=10,
        textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER, leading=16)

    return s


# ══════════════════════════════════════════════════════════════
# Inline markdown to ReportLab XML
# ══════════════════════════════════════════════════════════════
def safe_xml(text):
    return re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', text)


def md_inline(text):
    """Bold -> inline code (strips * _ inside) -> italic."""
    text = safe_xml(text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Inline code - strip * _ to prevent italic bleed
    def clean_code(m):
        inner = m.group(1).replace('*','').replace('_','')
        inner = inner.replace('<','&lt;').replace('>','&gt;')
        return '<font name="Mono">' + inner + '</font>'
    text = re.sub(r'`([^`]+)`', clean_code, text)
    # Italic single asterisk
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    # Italic underscore (word-boundary protected)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<i>\1</i>', text)
    return text


def strip_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'_(.+?)_',       r'\1', text)
    text = re.sub(r'`(.+?)`',       r'\1', text)
    return text


# ══════════════════════════════════════════════════════════════
# Rendering helpers
# ══════════════════════════════════════════════════════════════
def safe_para(text, style):
    try:
        return Paragraph(text, style)
    except Exception:
        plain = re.sub(r'<[^>]+>', '', text)
        try:
            return Paragraph(safe_xml(plain), style)
        except Exception:
            return Spacer(1, 2 * mm)


def std_table(data, col_widths=None):
    w = PAGE_W - 2 * MARGIN
    if col_widths is None:
        n = len(data[0])
        col_widths = [w / n] * n
    ts = TableStyle([
        ('BACKGROUND',     (0,0), (-1,0),  C_TBL_HD),
        ('TEXTCOLOR',      (0,0), (-1,0),  colors.white),
        ('FONTNAME',       (0,0), (-1,0),  'Body-Bold'),
        ('FONTSIZE',       (0,0), (-1,0),  9),
        ('ALIGN',          (0,0), (-1,-1), 'LEFT'),
        ('VALIGN',         (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_TBL_ALT]),
        ('FONTNAME',       (0,1), (-1,-1), 'Body'),
        ('FONTSIZE',       (0,1), (-1,-1), 9),
        ('GRID',           (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING',     (0,0), (-1,-1), 4),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 4),
        ('LEFTPADDING',    (0,0), (-1,-1), 5),
        ('RIGHTPADDING',   (0,0), (-1,-1), 5),
    ])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(ts)
    return t


def make_warn_para(text, styles, kind='warn'):
    if kind == 'danger':
        bg, bd, prefix = C_DNGR_BG, C_DNGR_BD, 'WARNING: '
    elif kind == 'info':
        bg, bd, prefix = C_INFO_BG, C_BLUE, 'Note: '
    else:
        bg, bd, prefix = C_WARN_BG, C_WARN_BD, 'Warning: '
    style = ParagraphStyle('_warn', parent=styles['normal'],
        backColor=bg, borderColor=bd, borderWidth=1.5, borderPad=7, spaceAfter=8)
    return safe_para(prefix + text, style)


def module_header(story, track, code, title, styles):
    colour = TRACK_COLOURS.get(code[0], C_GREEN)
    if 'X' in code:
        colour = C_RED
    badge = ParagraphStyle('_badge', parent=styles['normal'],
        fontName='Body-Bold', fontSize=9, backColor=colour,
        textColor=colors.white, borderPad=4, leading=12, alignment=TA_CENTER)
    story.append(PageBreak())
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('TRACK ' + track.upper() + ' - MODULE ' + code, badge))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(strip_inline(title), styles['module_title']))
    story.append(HRFlowable(width='100%', thickness=2, color=colour, spaceAfter=8))


# ══════════════════════════════════════════════════════════════
# Markdown block parser
# ══════════════════════════════════════════════════════════════
def md_to_story(md_text, styles, skip_h1=True):
    story = []
    lines = md_text.splitlines()
    i = 0
    table_rows = []
    in_code_block = False

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        n = max(len(r) for r in table_rows)
        w = PAGE_W - 2 * MARGIN
        story.append(std_table(table_rows, col_widths=[w/n]*n))
        story.append(Spacer(1, 3*mm))
        table_rows.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith('```'):
            flush_table()
            in_code_block = not in_code_block
            i += 1
            continue

        if in_code_block:
            story.append(safe_para(safe_xml(stripped), styles['mono']))
            i += 1
            continue

        # Blank line
        if not stripped:
            flush_table()
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}$', stripped):
            flush_table()
            story.append(HRFlowable(width='100%', thickness=0.5,
                color=colors.HexColor('#dddddd'), spaceAfter=4))
            i += 1
            continue

        # Table row
        if stripped.startswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if all(re.match(r'^[-: ]+$', c) for c in cells):
                i += 1
                continue
            table_rows.append([md_inline(c) for c in cells])
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
                    story.append(safe_para(text, styles['h1']))
            elif level == 2:
                story.append(safe_para(text, styles['h2']))
            elif level == 3:
                story.append(safe_para(text, styles['h3']))
            else:
                story.append(safe_para('<b>' + text + '</b>', styles['normal']))
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            raw = stripped.lstrip('> ').strip()
            text = md_inline(raw)
            upper = raw.upper()
            if 'DO NOT' in upper or 'WARNING' in upper or 'DANGER' in upper:
                kind = 'danger'
            elif 'NOTE' in upper[:10]:
                kind = 'info'
            else:
                kind = 'warn'
            story.append(make_warn_para(text, styles, kind=kind))
            i += 1
            continue

        # Bullet list
        if re.match(r'^[-*]\s', stripped):
            text = md_inline(stripped[2:].strip())
            while i + 1 < len(lines):
                nxt = lines[i + 1]
                if (nxt.startswith('  ') and nxt.strip()
                        and not re.match(r'^\s*[-*]\s', nxt)
                        and not re.match(r'^\s*\d+\.\s', nxt)):
                    text += ' ' + md_inline(nxt.strip())
                    i += 1
                else:
                    break
            story.append(safe_para('- ' + text, styles['bullet']))
            i += 1
            continue

        # Numbered list
        if re.match(r'^\d+\.\s', stripped):
            text = md_inline(re.sub(r'^\d+\.\s*', '', stripped))
            story.append(safe_para(text, styles['num']))
            i += 1
            continue

        # Source / Last verified lines
        if (stripped.startswith('*Source:') or stripped.startswith('*Last verified')
                or stripped.startswith('Source:') or stripped.startswith('Last verified')):
            story.append(safe_para(safe_xml(stripped.strip('*')), styles['source']))
            i += 1
            continue

        # Module metadata lines
        if re.match(r'^\*\*(Track|Prerequisites|Audience|Estimated|Video source):', stripped):
            story.append(safe_para(md_inline(stripped), styles['note']))
            i += 1
            continue

        # Lines containing box-drawing / block chars — render as monospace
        if has_box_chars(stripped):
            story.append(safe_para(safe_xml(stripped), styles['mono']))
            i += 1
            continue

        # Default: body paragraph — merge continuation lines
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
                    and not re.match(r'^[-*_]{3,}$', nxt)
                    and not has_box_chars(nxt)):
                text += ' ' + md_inline(nxt)
                i += 1
            else:
                break
        story.append(safe_para(text, styles['body']))
        i += 1

    flush_table()
    return story


# ══════════════════════════════════════════════════════════════
# Cover and TOC
# ══════════════════════════════════════════════════════════════
def build_cover(story, styles):
    story.append(Spacer(1, 28*mm))
    story.append(Paragraph('ZombieVerter VCU', styles['cover_title']))
    story.append(Paragraph('Training Series', styles['cover_sub']))
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width='60%', thickness=2, color=C_GREEN,
                              hAlign='CENTER', spaceAfter=8))
    story.append(Paragraph(
        'Complete reference guide for DIY EV conversion builders',
        styles['cover_meta']))
    story.append(Paragraph(
        str(len(MODULES)) + ' modules - 6 tracks - Firmware V2.30A (August 2025)',
        styles['cover_meta']))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph('github.com/robertwa1974/zombieverter-training',
                             styles['cover_meta']))
    story.append(Paragraph('openinverter.org - evbmw.com', styles['cover_meta']))
    story.append(Spacer(1, 10*mm))
    track_data = [
        ['Track', 'Name', 'Modules'],
        ['F', 'Foundation',    'F01-F04'],
        ['H', 'Hardware',      'H01'],
        ['W', 'Wiring',        'W01-W06'],
        ['C', 'Configuration', 'C00-C06'],
        ['I', 'Integration',   'I01-I04'],
        ['A', 'Advanced',      'A01-A06'],
    ]
    story.append(std_table(track_data, col_widths=[12*mm, 50*mm, 30*mm]))


def build_toc(story, styles):
    story.append(PageBreak())
    story.append(Paragraph('Table of Contents', styles['h1']))
    story.append(Spacer(1, 4*mm))
    current_track = None
    for code, track, title, _ in MODULES:
        if track != current_track:
            story.append(Paragraph(track.upper(), styles['toc_track']))
            current_track = track
        story.append(Paragraph(code + ' - ' + strip_inline(title), styles['toc_item']))


# ══════════════════════════════════════════════════════════════
# Page footer
# ══════════════════════════════════════════════════════════════
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Body', 7)
    canvas.setFillColor(colors.HexColor('#888888'))
    canvas.drawString(MARGIN, 12*mm,
        'github.com/robertwa1974/zombieverter-training - openinverter.org - V2.30A')
    canvas.drawRightString(PAGE_W - MARGIN, 12*mm, str(doc.page))
    canvas.setStrokeColor(colors.HexColor('#dddddd'))
    canvas.line(MARGIN, 14*mm, PAGE_W - MARGIN, 14*mm)
    canvas.restoreState()


# ══════════════════════════════════════════════════════════════
# Main build
# ══════════════════════════════════════════════════════════════
def build():
    print('Building PDF -> ' + str(OUTPUT_PATH))
    styles = make_styles()

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=18*mm, bottomMargin=20*mm,
        title='ZombieVerter VCU Training Series',
        author='Rob Wagstaff | openinverter.org community',
        subject='ZombieVerter VCU V2.30A - Complete Reference Manual',
    )

    story = []
    build_cover(story, styles)
    build_toc(story, styles)

    missing = []
    for code, track, title, rel_path in MODULES:
        md_path = REPO_ROOT / rel_path
        if not md_path.exists():
            print('  [SKIP] ' + code + ' - ' + md_path.name + ' not found')
            missing.append((code, title))
            continue

        print('  [OK]   ' + code + ' - ' + title)
        try:
            md_text = md_path.read_text(encoding='utf-8')
        except Exception as e:
            print('  [ERROR] Could not read ' + str(md_path) + ': ' + str(e))
            missing.append((code, title))
            continue

        module_header(story, track, code, title, styles)
        try:
            story.extend(md_to_story(md_text, styles, skip_h1=True))
        except Exception as e:
            print('  [ERROR] Failed to parse ' + code + ': ' + str(e))
            story.append(Paragraph(
                'Error rendering module ' + code + ' - see build log.',
                styles['note']))

    if missing:
        story.append(PageBreak())
        story.append(Paragraph('Modules In Progress', styles['h1']))
        story.append(Paragraph(
            'The following modules are planned but not yet written. '
            'Check the repository for the latest status.',
            styles['body']))
        for code, title in missing:
            story.append(safe_para(code + ' - ' + strip_inline(title), styles['bullet']))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    size_kb = OUTPUT_PATH.stat().st_size // 1024
    print('Done - ' + str(size_kb) + ' KB written to ' + str(OUTPUT_PATH))


if __name__ == '__main__':
    build()
