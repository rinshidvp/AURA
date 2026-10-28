from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Table

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs' / 'AURA_CLASS_AND_ARCHITECTURE_EXPLANATION.md'
OUTPUT = ROOT / 'AURA_CLASS_AND_ARCHITECTURE_EXPLANATION.pdf'


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        alignment=1,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0B3B5B'),
        spaceBefore=18,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8,
    )
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        leftIndent=18,
        bulletIndent=12,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6,
    )

    content = []
    with SOURCE.open('r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    current_para = []
    bullets = []
    in_list = False

    def flush_paragraph():
        nonlocal current_para
        if current_para:
            text = ' '.join(current_para).strip()
            if text:
                content.append(Paragraph(text, body_style))
            current_para = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if stripped.startswith('# '):
            flush_paragraph()
            content.append(Paragraph(stripped[2:], title_style if stripped.startswith('# AURA') else heading_style))
            continue
        if stripped.startswith('## '):
            flush_paragraph()
            content.append(Paragraph(stripped[3:], heading_style))
            continue
        if stripped.startswith('### '):
            flush_paragraph()
            content.append(Paragraph(stripped[4:], ParagraphStyle('SubHeading', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=colors.HexColor('#1E3A5F'), spaceBefore=10, spaceAfter=6)))
            continue
        if stripped.startswith('- '):
            flush_paragraph()
            bullets.append(Paragraph(stripped[2:], bullet_style))
            continue
        if stripped.startswith('---'):
            flush_paragraph()
            content.append(Spacer(1, 12))
            continue
        current_para.append(stripped)

    flush_paragraph()
    if bullets:
        content.append(ListFlowable([ListItem(item, bulletType='bullet') for item in bullets], bulletType='bullet'))

    doc.build(content)
    print(f'Created PDF at: {OUTPUT}')


if __name__ == '__main__':
    build_pdf()
