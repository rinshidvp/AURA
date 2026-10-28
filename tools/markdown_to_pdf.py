from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_progress_review as pdf

SOURCE = ROOT / "docs" / "AURA_TECHNICAL_LEARNING_MANUAL.md"
OUTPUT = ROOT / "AURA_TECHNICAL_LEARNING_MANUAL.pdf"
pdf.OUT = OUTPUT


def plain(value):
    value = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"__([^_]+)__", r"\1", value)
    value = re.sub(r"\*([^*]+)\*", r"\1", value)
    return value.strip()


def wrap_lines(text, width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = (current + " " + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def draw_paragraph(page, text, y, x=pdf.M, width=84, size=9.1, leading=12):
    for line in wrap_lines(plain(text), width):
        page.text(x, y, line, size, "F1", pdf.INK)
        y -= leading
    return y


def draw_code(page, lines, y):
    height = max(48, 22 + len(lines) * 9)
    if y - height < 56:
        return False, y
    page.rect(pdf.M, y - height, 507, height, (0.95, 0.97, 0.97), (0.28, 0.38, 0.42), 0.6)
    yy = y - 17
    for line in lines:
        page.text(pdf.M + 10, yy, line[:94], 6.5, "F1", (0.10, 0.13, 0.17))
        yy -= 9
    return True, y - height - 12


def draw_table(page, rows, y):
    if len(rows) < 2:
        return draw_paragraph(page, " | ".join(rows[0]) if rows else "", y)
    columns = max(len(row) for row in rows)
    if columns == 0:
        return y
    widths = [507 / columns] * columns
    headers = [plain(v) for v in rows[0]]
    body = [[plain(v) for v in row] for row in rows[2:]]
    estimated = len(body) * 31 + 40
    if y - estimated < 56:
        return None
    return pdf.table(page, pdf.M, y, widths, headers, body, 31, 6.6)


def parse_table(line):
    if not line.strip().startswith("|"):
        return None
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return cells


def build():
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    pages = []
    page_number = 1
    page = pdf.Page(page_number)
    page.heading("AURA Technical Learning Manual", "Markdown source rendered as a study PDF")
    y = 715
    code_mode = False
    code_lines = []
    table_lines = []
    title_seen = False

    def new_page():
        nonlocal page, page_number, y
        page.footer(); page.end(); pages.append(page)
        page_number += 1
        page = pdf.Page(page_number)
        page.heading("AURA Technical Learning Manual", "From-scratch technical learning guide")
        y = 715

    def ensure(height):
        nonlocal y
        if y - height < 56:
            new_page()
        return y

    def flush_table():
        nonlocal table_lines, y
        if not table_lines:
            return
        result = draw_table(page, table_lines, y)
        if result is None:
            new_page()
            result = draw_table(page, table_lines, y)
        y = result - 10 if result is not None else y
        table_lines = []

    def flush_code():
        nonlocal code_lines, y
        if not code_lines:
            return
        ok, result = draw_code(page, code_lines, y)
        if not ok:
            new_page()
            ok, result = draw_code(page, code_lines, y)
        y = result
        code_lines = []

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            flush_table()
            if code_mode:
                code_mode = False
                flush_code()
            else:
                code_mode = True
            continue
        if code_mode:
            code_lines.append(line.replace("\t", "    "))
            continue

        table = parse_table(line)
        if table is not None:
            table_lines.append(table)
            continue
        if table_lines and (not line.strip() or parse_table(line) is None):
            flush_table()

        if not line.strip():
            y -= 7
            if y < 56:
                new_page()
            continue
        if line.startswith("# "):
            if title_seen:
                new_page()
            title_seen = True
            ensure(60)
            page.text(pdf.M, y, plain(line[2:]), 20, "F2", pdf.NAVY)
            y -= 31
            page.line(pdf.M, y + 8, pdf.W - pdf.M, y + 8, pdf.GOLD, 1.2)
            y -= 13
        elif line.startswith("## "):
            ensure(38)
            page.text(pdf.M, y, plain(line[3:]), 14, "F2", pdf.TEAL)
            y -= 23
        elif line.startswith("### "):
            ensure(29)
            page.text(pdf.M, y, plain(line[4:]), 11, "F2", pdf.NAVY)
            y -= 18
        elif re.match(r"^[-*] ", line):
            ensure(17)
            y = draw_paragraph(page, "- " + line[2:], y, pdf.M + 10, 81, 8.8, 11)
        elif re.match(r"^\d+\. ", line):
            ensure(17)
            y = draw_paragraph(page, line, y, pdf.M + 10, 81, 8.8, 11)
        elif line.startswith("> "):
            ensure(30)
            page.rect(pdf.M, y - 5, 4, 25, pdf.GOLD)
            y = draw_paragraph(page, line[2:], y, pdf.M + 14, 78, 8.8, 11)
        elif re.match(r"^---+$", line.strip()):
            ensure(12)
            page.line(pdf.M, y, pdf.W - pdf.M, y, (0.80, 0.84, 0.85), 0.7)
            y -= 13
        else:
            needed = max(20, len(line) // 70 * 12 + 18)
            ensure(needed)
            y = draw_paragraph(page, line, y)

    if code_mode:
        flush_code()
    flush_table()
    page.footer(); page.end(); pages.append(page)
    pdf.build_pdf(pages)
    print(f"Wrote {OUTPUT} ({len(pages)} pages) from {SOURCE}")


if __name__ == "__main__":
    build()
