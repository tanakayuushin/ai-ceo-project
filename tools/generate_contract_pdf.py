"""
契約書 Markdown -> PDF 変換スクリプト
使用ライブラリ: reportlab, markdown
日本語フォント: Windows システムフォント (Meiryo / Yu Gothic / MS Gothic) を自動検出
"""

import sys
import os
import re
import markdown
from markdown.extensions.tables import TableExtension

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
pt = 1
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, ListFlowable, ListItem, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ========== 設定 ==========
INPUT_FILE = os.path.join(
    os.path.dirname(__file__),
    "..", "departments", "sales", "contract-template-standard.md"
)
OUTPUT_FILE = "contract_山田建設_20250422.pdf"
# ==========================

# ---------- フォント登録 ----------
FONT_CANDIDATES = [
    ("C:/Windows/Fonts/meiryo.ttc",  "C:/Windows/Fonts/meiryob.ttc",  0),
    ("C:/Windows/Fonts/YuGothR.ttc", "C:/Windows/Fonts/YuGothB.ttc",  0),
    ("C:/Windows/Fonts/msgothic.ttc","C:/Windows/Fonts/msgothic.ttc",  0),
]

def register_japanese_fonts():
    for regular, bold, idx in FONT_CANDIDATES:
        if os.path.exists(regular):
            try:
                pdfmetrics.registerFont(TTFont("JP",     regular, subfontIndex=idx))
                bold_path = bold if os.path.exists(bold) else regular
                pdfmetrics.registerFont(TTFont("JP-Bold", bold_path, subfontIndex=idx))
                print(f"フォント登録: {regular}")
                return
            except Exception as e:
                print(f"フォント登録失敗 ({regular}): {e}")
    raise RuntimeError("日本語フォントが見つかりませんでした。")

# ---------- スタイル定義 ----------
def build_styles():
    base = dict(fontName="JP", leading=18, textColor=colors.HexColor("#1a1a1a"))
    bold = dict(fontName="JP-Bold", leading=18, textColor=colors.HexColor("#1a1a1a"))

    return {
        "h1": ParagraphStyle("h1", fontSize=16, alignment=TA_CENTER,
                             spaceAfter=14, spaceBefore=4, **bold),
        "h2": ParagraphStyle("h2", fontSize=11, alignment=TA_LEFT,
                             spaceAfter=6, spaceBefore=14,
                             backColor=colors.HexColor("#eeeeee"),
                             borderPad=(4, 8, 4, 8),
                             leftIndent=0, **bold),
        "h3": ParagraphStyle("h3", fontSize=10.5, alignment=TA_LEFT,
                             spaceAfter=4, spaceBefore=8, **bold),
        "body": ParagraphStyle("body", fontSize=10, alignment=TA_JUSTIFY,
                               spaceAfter=6, **base),
        "li":   ParagraphStyle("li",   fontSize=10, alignment=TA_LEFT,
                               spaceAfter=3, leftIndent=12, **base),
        "th":   ParagraphStyle("th",   fontSize=9.5, **bold),
        "td":   ParagraphStyle("td",   fontSize=9.5, **base),
    }

# ---------- Markdown パーサー ----------
def parse_md_to_elements(md_text: str, styles: dict) -> list:
    """Markdown を reportlab Flowable のリストに変換する"""
    elements = []
    lines = md_text.splitlines()
    i = 0

    def add_para(text, style_key):
        # **bold** をそのまま表示（reportlab の <b> タグに変換）
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # インライン ` ` を除去
        text = re.sub(r'`(.+?)`', r'\1', text)
        if text.strip():
            elements.append(Paragraph(text, styles[style_key]))

    while i < len(lines):
        line = lines[i]

        # 水平線
        if re.match(r'^-{3,}$', line.strip()):
            elements.append(Spacer(1, 4))
            elements.append(HRFlowable(width="100%", thickness=0.5,
                                       color=colors.HexColor("#cccccc")))
            elements.append(Spacer(1, 4))
            i += 1
            continue

        # H1
        if line.startswith("# "):
            add_para(line[2:].strip(), "h1")
            elements.append(HRFlowable(width="100%", thickness=1.5,
                                       color=colors.HexColor("#1a1a1a")))
            elements.append(Spacer(1, 8))
            i += 1
            continue

        # H2
        if line.startswith("## "):
            add_para(line[3:].strip(), "h2")
            i += 1
            continue

        # H3
        if line.startswith("### "):
            add_para(line[4:].strip(), "h3")
            i += 1
            continue

        # テーブル（| で始まる行）
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            elements.append(_build_table(table_lines, styles))
            elements.append(Spacer(1, 6))
            continue

        # 番号付きリスト / 箇条書き
        if re.match(r'^\s*(\d+\.|[-*])\s', line):
            items = []
            while i < len(lines) and re.match(r'^\s*(\d+\.|[-*])\s', lines[i]):
                text = re.sub(r'^\s*(\d+\.|[-*])\s+', '', lines[i])
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                items.append(ListItem(Paragraph(text, styles["li"]), leftIndent=16))
                i += 1
            elements.append(ListFlowable(items, bulletType="bullet",
                                         bulletFontName="JP", bulletFontSize=9,
                                         leftIndent=8, spaceAfter=4))
            continue

        # 空行
        if line.strip() == "":
            elements.append(Spacer(1, 4))
            i += 1
            continue

        # 通常段落
        add_para(line, "body")
        i += 1

    return elements


def _build_table(table_lines: list, styles: dict) -> Table:
    """Markdown テーブルを reportlab Table に変換する"""
    rows = []
    is_header = True
    for line in table_lines:
        # 区切り行（|---|---|）をスキップ
        if re.match(r'^\|[-| :]+\|$', line.strip()):
            is_header = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        style_key = "th" if is_header else "td"
        rows.append([Paragraph(c, styles[style_key]) for c in cells])
        is_header = False  # 最初の行だけヘッダー

    col_count = max(len(r) for r in rows) if rows else 1
    col_width = (A4[0] - 40*mm) / col_count  # 余白 20mm × 2

    t = Table(rows, colWidths=[col_width] * col_count, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), "JP"),
        ("FONTNAME",    (0, 0), (-1, 0),  "JP-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#e8e8e8")),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#aaaaaa")),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
    ]))
    return t


# ---------- メイン ----------
def convert_md_to_pdf(input_path: str, output_path: str) -> None:
    print(f"読み込み中: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        md_text = f.read()

    register_japanese_fonts()
    styles = build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    elements = parse_md_to_elements(md_text, styles)

    print(f"PDF生成中: {output_path}")
    doc.build(elements)
    print(f"完了: {output_path}")


if __name__ == "__main__":
    input_path  = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_path = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE

    if not os.path.exists(input_path):
        print(f"エラー: ファイルが見つかりません -> {input_path}")
        sys.exit(1)

    convert_md_to_pdf(input_path, output_path)
