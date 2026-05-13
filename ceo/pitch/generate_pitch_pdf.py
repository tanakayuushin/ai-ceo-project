# -*- coding: utf-8 -*-
"""
Emport AI - Yamaguchi University Venture Pitch PDF Generator
"""
from fpdf import FPDF

FONT_R = r"C:\Windows\Fonts\meiryo.ttc"
FONT_B = r"C:\Windows\Fonts\meiryob.ttc"
OUTPUT  = r"C:\Users\e046ffv\OneDrive\ai-ceo-project\ceo\pitch\yamaguchi-univ-pitch.pdf"

LM = 18
RM = 18
LINE_H = 7


class PDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("R", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Emport AI  |  {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def section(self, title):
        self.ln(4)
        self.set_font("B", size=12)
        self.set_fill_color(20, 40, 100)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body(self, text):
        self.set_font("R", size=10)
        self.multi_cell(0, LINE_H, text)
        self.ln(1)

    def table(self, headers, rows, col_widths):
        self.set_font("B", size=9)
        self.set_fill_color(20, 40, 100)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)
        for ri, row in enumerate(rows):
            self.set_font("R", size=9)
            if ri % 2 == 0:
                self.set_fill_color(240, 244, 255)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, cell, border=1, fill=True)
            self.ln()
        self.ln(2)


def build():
    pdf = PDF()
    pdf.add_font("R", "", FONT_R)
    pdf.add_font("B", "", FONT_B)
    pdf.set_margins(LM, LM, RM)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ---- タイトルブロック ----
    pdf.ln(4)
    pdf.set_font("B", size=20)
    pdf.set_text_color(20, 40, 100)
    pdf.cell(0, 12, "事業企画書", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("B", size=13)
    pdf.cell(0, 8, "Emport AI  ——  地方中小企業のためのAI経営支援", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("R", size=9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "田中悠清（山口大学 知能情報工学科）　2026年5月", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ---- 一言コンセプト ----
    pdf.set_font("B", size=12)
    pdf.set_fill_color(235, 240, 255)
    pdf.set_draw_color(20, 40, 100)
    pdf.set_line_width(0.5)
    pdf.multi_cell(0, 9,
        "「AIが経営チームになる」\n——中小企業オーナーの仕事量を、AIで10倍にする。",
        fill=True, border=1, align="C"
    )
    pdf.ln(4)

    # ---- 解決する問題 ----
    pdf.section("解決する問題")
    pdf.body(
        "日本の中小企業オーナー（従業員20〜300名）は、経営・営業・広報・管理を一人で担っています。\n"
        "AIブームが加速する中、大企業や都市部はAIで急速に生産性を高めています。\n"
        "一方、地方の中小企業にはAIを導入するノウハウや人材が不足しており、\n"
        "このままでは活用できる企業とそうでない企業の間に新たなAI格差が生まれます。"
    )
    pdf.table(
        ["経営者の悩み", "現実"],
        [
            ["情報収集", "業界ニュースを毎日見る時間がない"],
            ["営業", "メール・提案書作成に追われて商談に集中できない"],
            ["SNS発信", "週1本の投稿も難しい"],
            ["経営判断", "相談できる参謀が誰もいない"],
        ],
        col_widths=[45, 125]
    )

    # ---- 解決策 ----
    pdf.section("解決策")
    pdf.set_font("B", size=10)
    pdf.multi_cell(0, LINE_H, "AIを使った業務自動化・効率化の導入支援、およびAIツールの開発")
    pdf.ln(1)
    pdf.body(
        "・ 経営者の日常業務（情報収集・文書作成・SNS投稿・レポート作成）をAIで自動化\n"
        "・ 企業ごとの課題に合わせた仕組みを設計・実装\n"
        "・ 最大450万円のIT導入補助金を活用することで、導入コストをほぼゼロにできる\n"
        "・ 【実証済み】自社（Emport AI）の経営業務に同じ仕組みを実際に導入・稼働中"
    )

    # ---- 市場とターゲット ----
    pdf.section("市場とターゲット")
    pdf.body(
        "・ 日本の中小企業数：約330万社\n"
        "・ 初期ターゲット：山口県内の中小企業（旅館・建設・製造・食品・物流）\n"
        "・ 山口県内にAI導入支援を専業とする競合は現時点で存在しない"
    )

    # ---- ビジネスモデル ----
    pdf.section("ビジネスモデル")
    pdf.table(
        ["フェーズ", "内容", "収益"],
        [
            ["現在〜半年", "AI業務効率化の導入コンサル・ツール開発", "プロジェクト単価"],
            ["1年後〜", "月額サブスクリプション型AIサービスへ移行", "月額3〜15万円/社"],
        ],
        col_widths=[35, 105, 30]
    )
    pdf.body("粗利率80〜90%（AIのAPI利用料は売上の5〜10%）")

    # ---- ロードマップ ----
    pdf.section("ロードマップ")
    pdf.table(
        ["時期", "目標"],
        [
            ["2026年6月", "初回契約1社獲得"],
            ["2026年11月", "顧客50社・月収200〜500万円"],
            ["2027年5月", "顧客200社・年商1億円"],
            ["2031年", "東証グロース市場上場"],
        ],
        col_widths=[45, 125]
    )

    # ---- なぜ今、なぜ私か ----
    pdf.section("なぜ今、なぜ私か")
    pdf.body(
        "① タイミング：AIが実用段階に達した2026年・補助金追い風・山口に競合ゼロ\n"
        "② 自分が顧客：毎日自社でこのシステムを使っており、改善サイクルが速い\n"
        "③ 地方からの逆張り：東京のスタートアップが狙わない市場でまず実績を積む\n"
        "④ 専門知識：知能情報工学科でAI・システム開発を学んでいる"
    )

    # ---- 現在の状況 ----
    pdf.section("現在の状況")
    pdf.body(
        "・ 創業：2026年5月\n"
        "・ 見込み客：13社\n"
        "・ 売上：準備中（初回契約に向けて交渉中）\n"
        "・ 稼働中のシステム：自社経営業務への自動化パイプライン\n"
        "　（日次ブリーフィング・SNS投稿・議事録整理）"
    )

    # ---- 連絡先 ----
    pdf.ln(4)
    pdf.set_font("R", size=10)
    pdf.set_draw_color(20, 40, 100)
    pdf.set_line_width(0.3)
    pdf.set_fill_color(245, 247, 255)
    pdf.multi_cell(0, LINE_H,
        "田中悠清（Emport AI）\n"
        "Email：yuubisinesu@gmail.com　TEL：080-2947-0736\n"
        "山口県山口市黒川995-1",
        fill=True, border=1
    )

    pdf.output(OUTPUT)
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    build()
