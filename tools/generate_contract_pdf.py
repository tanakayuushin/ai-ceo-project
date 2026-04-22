"""
契約書 Markdown → PDF 変換スクリプト
使用ライブラリ: markdown, weasyprint
"""

import markdown
import sys
import os
from datetime import datetime
from weasyprint import HTML, CSS

# ========== 設定 ==========
INPUT_FILE = os.path.join(
    os.path.dirname(__file__),
    "..", "departments", "sales", "contract-template-standard.md"
)
OUTPUT_FILE = "contract_山田建設_20250421.pdf"
# ==========================

CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');

@page {
    size: A4;
    margin: 20mm 18mm 20mm 18mm;
}

body {
    font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: #1a1a1a;
}

h1 {
    font-size: 16pt;
    font-weight: 700;
    text-align: center;
    margin: 0 0 24pt 0;
    padding-bottom: 8pt;
    border-bottom: 2px solid #1a1a1a;
}

h2 {
    font-size: 11pt;
    font-weight: 700;
    margin: 16pt 0 6pt 0;
    padding: 4pt 8pt;
    background: #f0f0f0;
    border-left: 4px solid #333;
}

h3 {
    font-size: 10.5pt;
    font-weight: 700;
    margin: 10pt 0 4pt 0;
}

p {
    margin: 4pt 0 8pt 0;
    text-align: justify;
}

ul, ol {
    margin: 4pt 0 8pt 16pt;
    padding: 0;
}

li {
    margin: 3pt 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0 12pt 0;
    font-size: 10pt;
}

th, td {
    border: 1px solid #aaa;
    padding: 5pt 8pt;
    text-align: left;
    vertical-align: top;
}

th {
    background: #e8e8e8;
    font-weight: 700;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 14pt 0;
}

strong {
    font-weight: 700;
}

/* 署名欄 */
table:last-of-type td {
    padding: 10pt 8pt;
    min-height: 30pt;
}
"""

def convert_md_to_pdf(input_path: str, output_path: str) -> None:
    print(f"読み込み中: {input_path}")

    with open(input_path, encoding="utf-8") as f:
        md_text = f.read()

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "nl2br", "sane_lists"]
    )

    html_full = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <title>業務委託契約書</title>
</head>
<body>
{html_body}
</body>
</html>"""

    print(f"PDF生成中: {output_path}")
    HTML(string=html_full).write_pdf(
        output_path,
        stylesheets=[CSS(string=CSS_STYLE)]
    )
    print(f"完了: {output_path}")


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_path = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE

    if not os.path.exists(input_path):
        print(f"エラー: ファイルが見つかりません → {input_path}")
        sys.exit(1)

    convert_md_to_pdf(input_path, output_path)
