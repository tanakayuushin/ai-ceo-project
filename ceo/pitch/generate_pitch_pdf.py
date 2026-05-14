# -*- coding: utf-8 -*-
"""
Emport AI - Yamaguchi University Venture Pitch PDF Generator (v2)
"""
from fpdf import FPDF

FONT_R  = r"C:\Windows\Fonts\meiryo.ttc"
FONT_B  = r"C:\Windows\Fonts\meiryob.ttc"
OUTPUT  = r"C:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\ceo\pitch\yamaguchi-univ-pitch.pdf"

LM     = 18
RM     = 18
LINE_H = 7


class PDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("R", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Emport AI  |  田中悠清  |  {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def section(self, title):
        self.ln(4)
        self.set_font("B", size=11)
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
            self.set_fill_color(240, 244, 255) if ri % 2 == 0 else self.set_fill_color(255, 255, 255)
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

    # ---- タイトル ----
    pdf.ln(4)
    pdf.set_font("B", size=20)
    pdf.set_text_color(20, 40, 100)
    pdf.cell(0, 12, "事業企画書", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("B", size=13)
    pdf.cell(0, 8, "Emport AI  ——  地方中小企業のためのAI経営支援", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("R", size=9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "田中悠清（山口大学 知能情報工学科）　2026年5月　山口大学ベンチャー企業支援プログラム 提出", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ---- コンセプト ----
    pdf.set_font("B", size=12)
    pdf.set_fill_color(235, 240, 255)
    pdf.set_draw_color(20, 40, 100)
    pdf.set_line_width(0.5)
    pdf.multi_cell(0, 9,
        "「AIが経営チームになる」\n——地方中小企業の業務を、AIで自動化する。",
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
    pdf.section("解決策（2本柱）")
    pdf.set_font("B", size=10)
    pdf.multi_cell(0, LINE_H, "① AIコンサルティング（現在の主力）")
    pdf.set_x(LM)
    pdf.body(
        "・ 企業ごとの課題に合わせてAI業務自動化の仕組みを設計・実装\n"
        "・ 最大450万円のIT導入補助金を活用し、導入コストをほぼゼロにできる\n"
        "・ 【実証済み】自社の経営業務に同じ仕組みを実際に導入・毎日稼働中"
    )
    pdf.set_font("B", size=10)
    pdf.multi_cell(0, LINE_H, "② Emport AI モバイルアプリ（開発完了・リリース準備中）")
    pdf.set_x(LM)
    pdf.table(
        ["項目", "内容"],
        [
            ["対応OS", "iOS / Android"],
            ["特徴", "建設業・製造業・小売業など業種に特化したAIアシスタント"],
            ["価格", "月額980円（ChatGPTの3分の1の価格）"],
            ["競合優位", "業種特化 × スマートフォン × 低価格 × IT補助金対象"],
        ],
        col_widths=[40, 130]
    )

    # ---- 市場 ----
    pdf.section("市場とターゲット")
    pdf.table(
        ["指標", "数値"],
        [
            ["日本の中小企業数", "約330万社"],
            ["AI未導入率", "約75%（4社に3社がまだ未導入）"],
            ["日本の対話型AI市場（2034年）", "約3,400億円（CAGR 16.6%）"],
            ["山口県の競合", "AI導入支援を専業とする競合は現時点でゼロ"],
        ],
        col_widths=[75, 95]
    )

    # ---- ビジネスモデル ----
    pdf.section("ビジネスモデル")
    pdf.table(
        ["フェーズ", "内容", "収益目標"],
        [
            ["現在〜6ヶ月", "AI業務効率化の導入コンサル", "単価30〜100万円"],
            ["6ヶ月〜1年", "Emport AIアプリ有料化", "月額980円×顧客数"],
            ["1年後〜", "月額SaaSへ移行", "月額3〜15万円/社"],
        ],
        col_widths=[35, 95, 40]
    )
    pdf.body("粗利率：80〜90%（AIのAPI利用料は売上の5〜10%）")

    # ---- ロードマップ ----
    pdf.section("ロードマップ")
    pdf.table(
        ["時期", "目標"],
        [
            ["2026年6月", "Emport AI App Store / Google Play リリース"],
            ["2026年9月", "初回コンサル契約3社獲得"],
            ["2026年11月", "顧客50社・月収200〜500万円"],
            ["2027年5月", "顧客200社・年商1億円"],
            ["2031年", "東証グロース市場上場"],
        ],
        col_widths=[35, 135]
    )

    # ---- なぜ今、なぜ私か ----
    pdf.section("なぜ今、なぜ私か")
    pdf.body(
        "① タイミング：AIが実用段階に達した2026年・IT補助金追い風・山口に競合ゼロ\n"
        "② 自分が顧客：毎日自社でこのシステムを使っており、改善サイクルが速い\n"
        "③ 地方からの逆張り：東京のスタートアップが狙わない市場でまず実績を積む\n"
        "④ 専門知識：知能情報工学科でAI・システム開発を学び、即実装できる"
    )

    # ---- 現在の状況 ----
    pdf.section("現在の状況（2026年5月時点）")
    pdf.table(
        ["項目", "状況"],
        [
            ["創業", "2026年5月"],
            ["見込み客", "13社（商工会議所経由含む）"],
            ["アプリ開発", "完了（リリース準備中）"],
            ["バックエンドAPI", "Railway（クラウド）上で稼働中"],
            ["商工会議所", "山口・下関 両商工会議所にコンタクト済み"],
            ["稼働中のAIシステム", "日次ニュース収集・SNS自動投稿・議事録整理"],
        ],
        col_widths=[55, 115]
    )

    # ---- 山口大学への支援要請 ----
    pdf.section("山口大学への支援要請")
    pdf.table(
        ["支援内容", "理由"],
        [
            ["メンタリング", "経営経験豊富な方からのアドバイスを希望"],
            ["ネットワーク", "山口県内企業・経営者との接点を広げたい"],
            ["信用補完", "「山口大学支援ベンチャー」としての信頼性向上"],
            ["資金調達支援", "将来的なVC・投資家紹介"],
        ],
        col_widths=[55, 115]
    )

    # ---- 連絡先 ----
    pdf.ln(4)
    pdf.set_font("R", size=10)
    pdf.set_draw_color(20, 40, 100)
    pdf.set_line_width(0.3)
    pdf.set_fill_color(245, 247, 255)
    pdf.multi_cell(0, LINE_H,
        "田中悠清（Emport AI）\n"
        "Email：tsubeyou081@gmail.com　TEL：080-2947-0736\n"
        "山口県山口市黒川995-1　https://emport-ai.vercel.app",
        fill=True, border=1
    )

    pdf.output(OUTPUT)
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    build()
