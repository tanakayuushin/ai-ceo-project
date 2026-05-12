"""
Emport AI 展望ロードマップ PDF生成スクリプト
使用ライブラリ: reportlab
日本語フォント: Windows システムフォント自動検出
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── フォント検出 ──────────────────────────────────────────
FONT_CANDIDATES = [
    ("C:/Windows/Fonts/meiryo.ttc",    "Meiryo"),
    ("C:/Windows/Fonts/YuGothR.ttc",   "YuGothic"),
    ("C:/Windows/Fonts/msgothic.ttc",  "MSGothic"),
]
FONT_BOLD_CANDIDATES = [
    ("C:/Windows/Fonts/meiryob.ttc",   "MeiryoBold"),
    ("C:/Windows/Fonts/YuGothB.ttc",   "YuGothicBold"),
    ("C:/Windows/Fonts/msgothic.ttc",  "MSGothicBold"),
]

def load_fonts():
    normal = bold = None
    for path, name in FONT_CANDIDATES:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
            normal = name
            break
    for path, name in FONT_BOLD_CANDIDATES:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
            bold = name
            break
    if not normal:
        raise RuntimeError("日本語フォントが見つかりません")
    if not bold:
        bold = normal
    return normal, bold

FONT, FONT_BOLD = load_fonts()

# ── カラーパレット ─────────────────────────────────────────
C_NAVY    = colors.HexColor("#1a2744")
C_BLUE    = colors.HexColor("#2563eb")
C_LIGHT   = colors.HexColor("#eff6ff")
C_ACCENT  = colors.HexColor("#f59e0b")
C_GRAY    = colors.HexColor("#6b7280")
C_BORDER  = colors.HexColor("#cbd5e1")
C_WHITE   = colors.white
C_BG      = colors.HexColor("#f8fafc")

W, H = A4
MARGIN = 18 * mm

# ── スタイル ─────────────────────────────────────────────
def s(name, font=None, size=10, color=colors.black, bold=False,
      align=TA_LEFT, leading=None, space_before=0, space_after=4):
    return ParagraphStyle(
        name,
        fontName=FONT_BOLD if bold else FONT,
        fontSize=size,
        textColor=color,
        alignment=align,
        leading=leading or size * 1.5,
        spaceBefore=space_before,
        spaceAfter=space_after,
    )

ST_COVER_TITLE   = s("ct", size=26, color=C_WHITE,  bold=True,  align=TA_CENTER, leading=36)
ST_COVER_SUB     = s("cs", size=12, color=C_LIGHT,  bold=False, align=TA_CENTER)
ST_COVER_DATE    = s("cd", size=9,  color=C_BORDER, align=TA_CENTER)
ST_SECTION_HEAD  = s("sh", size=13, color=C_WHITE,  bold=True,  leading=20)
ST_PHASE_TITLE   = s("pt", size=11, color=C_NAVY,   bold=True,  leading=18, space_before=4)
ST_PHASE_THEME   = s("pm", size=9,  color=C_BLUE,   bold=False, leading=14)
ST_BODY          = s("b",  size=9,  color=colors.HexColor("#1e293b"), leading=15, space_after=3)
ST_BULLET        = s("bu", size=9,  color=colors.HexColor("#1e293b"), leading=15, space_after=2)
ST_LABEL         = s("lb", size=8,  color=C_GRAY,   bold=False, leading=13)
ST_FOOTER        = s("ft", size=7,  color=C_GRAY,   align=TA_CENTER)
ST_QUOTE         = s("q",  size=10, color=C_NAVY,   bold=True,  align=TA_CENTER, leading=18)
ST_TABLE_HEAD    = s("th", size=8,  color=C_WHITE,  bold=True,  align=TA_CENTER, leading=13)
ST_TABLE_CELL    = s("tc", size=8,  color=C_NAVY,   align=TA_CENTER, leading=13)
ST_TABLE_CELL_L  = s("tl", size=8,  color=C_NAVY,   align=TA_LEFT,   leading=13)

def p(text, style): return Paragraph(text, style)
def sp(h=4):        return Spacer(1, h * mm)
def hr(color=C_BORDER, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4)

# ── セクションヘッダー ────────────────────────────────────
def section_header(label, color=C_NAVY):
    data = [[Paragraph(label, ST_SECTION_HEAD)]]
    t = Table(data, colWidths=[W - 2 * MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t

# ── フェーズカード ────────────────────────────────────────
def phase_card(time_label, title, theme, kpis, bullets, person_note="", bg=C_LIGHT):
    col_w = W - 2 * MARGIN

    # ヘッダー行
    header_data = [[
        Paragraph(f'<font size="8" color="#6b7280">{time_label}</font><br/>'
                  f'<b>{title}</b>', ST_PHASE_TITLE),
        Paragraph(f'テーマ：{theme}', ST_PHASE_THEME),
    ]]
    header_t = Table(header_data, colWidths=[col_w * 0.6, col_w * 0.4])
    header_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # KPI行
    kpi_cells = [[Paragraph(k[0], ST_LABEL), Paragraph(k[1], ST_BODY)] for k in kpis]
    kpi_rows = []
    for i in range(0, len(kpi_cells), 2):
        row = kpi_cells[i]
        if i + 1 < len(kpi_cells):
            row = kpi_cells[i] + kpi_cells[i + 1]
        else:
            row = kpi_cells[i] + [Paragraph("", ST_LABEL), Paragraph("", ST_BODY)]
        kpi_rows.append(row)

    kpi_col = col_w / 4
    kpi_t = Table(kpi_rows, colWidths=[kpi_col * 0.8, kpi_col * 1.2] * 2)
    kpi_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
    ]))

    # 箇条書き
    bullet_items = []
    for b in bullets:
        bullet_items.append(Paragraph(f"・{b}", ST_BULLET))

    # 人物注
    note_items = []
    if person_note:
        note_items.append(sp(2))
        note_items.append(Paragraph(person_note, s("pn", size=8, color=C_GRAY, leading=13)))

    # 全体を枠で囲む
    outer_data = [[header_t], [kpi_t]] + [[b] for b in bullet_items + note_items]
    outer_t = Table(outer_data, colWidths=[col_w])
    outer_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_WHITE),
        ("BOX",           (0, 0), (-1, -1), 0.8, C_BORDER),
        ("TOPPADDING",    (0, 1), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
        ("LEFTPADDING",   (0, 1), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 1), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, 0), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("LEFTPADDING",   (0, 0), (-1, 0), 0),
        ("RIGHTPADDING",  (0, 0), (-1, 0), 0),
    ]))
    return KeepTogether([outer_t, sp(3)])

# ── 数値サマリーテーブル ──────────────────────────────────
def summary_table():
    col_w = W - 2 * MARGIN
    headers = ["時点", "年商", "顧客数", "チーム規模", "資金調達"]
    rows = [
        ["2026年11月（半年後）", "〜6,000万円",  "50社",      "1〜2名",   "未調達"],
        ["2027年5月（1年後）",  "1〜1.5億円",   "200社",     "2〜3名",   "シード前後"],
        ["2028年5月（2年後）",  "3億円",        "500社",     "5〜10名",  "1〜3億円"],
        ["2029年5月（3年後）",  "10億円",       "2,000社",   "20〜30名", "累計15〜20億円"],
        ["2031年5月（5年後）",  "30〜50億円",   "10,000社",  "50〜100名","累計30〜50億円"],
    ]
    cw = [col_w * r for r in [0.28, 0.17, 0.15, 0.17, 0.23]]
    data = [[Paragraph(h, ST_TABLE_HEAD) for h in headers]]
    for i, row in enumerate(rows):
        cells = [Paragraph(row[0], ST_TABLE_CELL_L)] + \
                [Paragraph(c, ST_TABLE_CELL) for c in row[1:]]
        data.append(cells)

    t = Table(data, colWidths=cw)
    style = [
        ("BACKGROUND",    (0, 0), (-1, 0), C_NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.5, C_BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i in range(1, len(rows) + 1):
        bg = C_LIGHT if i % 2 == 0 else C_WHITE
        style.append(("BACKGROUND", (0, i), (-1, i), bg))
    # 最終行（IPO）を強調
    style.append(("BACKGROUND", (0, len(rows)), (-1, len(rows)), colors.HexColor("#fef3c7")))
    t.setStyle(TableStyle(style))
    return t

# ── カバーページ ─────────────────────────────────────────
def cover_page():
    col_w = W - 2 * MARGIN
    data = [[
        Paragraph("Emport AI", ST_COVER_TITLE),
    ]]
    t = Table([[
        Paragraph("Emport AI", ST_COVER_TITLE),
        ]], colWidths=[col_w])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    sub_data = [
        [Paragraph("経営展望ロードマップ 2026-2031", s("s1", size=14, color=C_NAVY, bold=True, align=TA_CENTER))],
        [Paragraph("〜 山口から始まる、地方発AI経営革命 〜", s("s2", size=10, color=C_GRAY, align=TA_CENTER))],
        [sp(2)],
        [Paragraph("作成：CEO アレン（Allen）｜ 2026年5月12日",
                   s("s3", size=8, color=C_GRAY, align=TA_CENTER))],
    ]
    sub_t = Table(sub_data, colWidths=[col_w])
    sub_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 1, C_BORDER),
    ]))
    return [t, sub_t]


# ── メイン ───────────────────────────────────────────────
def build():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "ceo", "strategy")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "vision-roadmap-2026-2031.pdf")

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Emport AI 経営展望ロードマップ 2026-2031",
        author="CEO Allen / Emport AI",
    )

    story = []

    # ── カバー ──
    story += cover_page()
    story.append(sp(6))

    # ── ビジョン一文 ──
    story.append(section_header("■ ビジョン"))
    story.append(sp(3))
    story.append(p(
        "「日本の中小企業10,000社に、AI経営チームを届ける」",
        s("vis", size=12, color=C_NAVY, bold=True, align=TA_CENTER, leading=20)
    ))
    story.append(sp(1))
    story.append(p(
        "2031年、Emport AIは日本で最もAI経営支援の実績を持つSaaS企業として確立している。<br/>"
        "創業者の田中悠清（オーナー）は25〜26歳。日本の若手起業家の象徴として認知されている。",
        ST_BODY
    ))
    story.append(sp(4))

    # ── 数値サマリー ──
    story.append(section_header("■ 全体ロードマップ（数値サマリー）"))
    story.append(sp(3))
    story.append(summary_table())
    story.append(sp(5))

    # ── 近期フェーズ ──
    story.append(section_header("■ 近期展望", color=colors.HexColor("#dc2626")))
    story.append(sp(3))

    # 1か月後
    story.append(phase_card(
        time_label="1か月後（2026年6月）",
        title="パイロット3〜5社獲得",
        theme="最初の1円を稼ぐ",
        kpis=[
            ("月収目標", "10〜50万円"),
            ("顧客数",   "3〜5社"),
            ("単価",     "月3〜10万円"),
            ("形態",     "手動コンサル"),
        ],
        bullets=[
            "見込み客13社に「AI CEO パイロット提案」を送付・電話でフォロー",
            "商工会議所（山口・下関）にセミナー打診のアポを取る",
            "IT導入支援事業者の登録申請を開始する",
            "初回成約後すぐに「成功事例レポート（1枚）」を作成する",
            "デモ動画の素材を画面録画で撮影・X/YouTubeに公開",
        ],
        person_note="【今の田中悠清】授業の合間に電話・夜にメール。泥臭く、それが正解。",
        bg=colors.HexColor("#fef2f2"),
    ))

    # 半年後
    story.append(phase_card(
        time_label="半年後（2026年11月）",
        title="月収200〜500万円・50社",
        theme="手動で証明する",
        kpis=[
            ("月収目標",  "200〜500万円"),
            ("顧客数",    "20〜50社"),
            ("MRR成長率", "月20〜30%"),
            ("法人化",    "完了"),
        ],
        bullets=[
            "全部手動でいい。アレンと田中が二人で動き実績を積む",
            "「AI導入で業務X時間削減」という実績の数字を1件作る",
            "IT導入支援事業者登録完了→補助金営業の最強フックを使い始める",
            "起業コンテスト（キャンパスベンチャーグランプリ等）に初登壇",
            "山口県内で「AIコンサルといえばEmport AI」を定着させる",
        ],
        person_note="【この時期の田中悠清】毎週3〜4社の経営者に会い、話を聞き、提案し続けている。",
        bg=colors.HexColor("#fff7ed"),
    ))
    story.append(sp(4))

    # ── 中期フェーズ ──
    story.append(section_header("■ 中期展望（1〜3年）", color=C_BLUE))
    story.append(sp(3))

    # 1年後
    story.append(phase_card(
        time_label="1年後（2027年5月）",
        title="年商1億円・SaaS v1.0完成",
        theme="プロダクト化する",
        kpis=[
            ("年商",      "1〜1.5億円"),
            ("顧客数",    "150〜200社"),
            ("月収",      "800〜1,000万円"),
            ("チーム",    "2〜3名"),
        ],
        bullets=[
            "手動でやっていたことをSaaSとして自動化（v1.0リリース）",
            "VCとのファーストミーティング開始・ピッチデッキ完成",
            "起業コンテスト受賞・メディア初掲載（日経・TechCrunch Japan等）",
            "エンジニア1〜2名を採用し開発体制を整える",
        ],
        person_note="【この時期の田中悠清】大学3〜4年生。山口大学で話題の学生起業家として認知される。",
    ))

    # 2年後
    story.append(phase_card(
        time_label="2年後（2028年5月）",
        title="年商3億円・大学卒業・全国展開",
        theme="全国へ出る",
        kpis=[
            ("年商",     "3億円"),
            ("顧客数",   "500社"),
            ("調達",     "1〜3億円"),
            ("チーム",   "5〜10名"),
        ],
        bullets=[
            "福岡または東京にオフィス開設。フルタイム経営に移行",
            "業種別バーティカル展開（旅館・建設・物流・食品）",
            "シード〜プレA資金調達完了",
            "メディア複数掲載・登壇（東洋経済・TechCrunch等）",
        ],
        person_note="【この時期の田中悠清】23歳。VC・投資家との会食が週に複数入る。「山口から来た若手経営者」として全国区に。",
    ))

    # 3年後
    story.append(phase_card(
        time_label="3年後（2029年5月）",
        title="年商10億円・業界標準・Series A",
        theme="業界標準になる",
        kpis=[
            ("年商",     "10億円"),
            ("顧客数",   "1,500〜2,000社"),
            ("調達",     "累計15〜20億円"),
            ("チーム",   "20〜30名"),
        ],
        bullets=[
            "業種別AI特化機能v3.0リリース（旅館・建設・物流・食品・製造）",
            "Series A完了（5〜15億円調達）",
            "Forbes 30 Under 30 Japan 選出（目標）",
            "「中小企業のAI経営支援」の市場カテゴリーでNo.1シェア獲得",
        ],
        person_note="【この時期の田中悠清】24歳。国会議員・県知事・大企業役員と対等に話す場に呼ばれるようになる。",
    ))
    story.append(sp(4))

    # ── 長期フェーズ ──
    story.append(section_header("■ 長期展望（5年後・IPO）", color=C_NAVY))
    story.append(sp(3))

    story.append(phase_card(
        time_label="5年後（2031年5月）",
        title="年商30〜50億円・東証グロース上場",
        theme="日本を変え、アジアへ",
        kpis=[
            ("年商",     "30〜50億円"),
            ("顧客数",   "5,000〜10,000社"),
            ("調達",     "累計30〜50億円"),
            ("チーム",   "50〜100名"),
        ],
        bullets=[
            "東証グロース市場への上場申請（日本最年少クラス）",
            "Series B完了（累計30〜50億円調達）",
            "海外展開開始（台湾・東南アジア）",
            "業種別バーティカル10業種以上。AI CFO・AI CMO・AI COOを提供",
            "「山口から始まり、日本を変えた」ストーリーでアジア登壇",
        ],
        person_note="【この時期の田中悠清】25〜26歳。アジア各国の経済フォーラムに登壇。「山口県から出た起業家」として語り継がれる。",
        bg=colors.HexColor("#fffbeb"),
    ))
    story.append(sp(4))

    # ── 勝てる理由 ──
    story.append(section_header("■ なぜEmport AIが勝てるか"))
    story.append(sp(3))

    reasons = [
        ("タイミング",
         "2026年：AIが中小企業でも実用段階に到達。補助金（最大450万円）で顧客負担がほぼゼロ。山口県内に専業競合ゼロ。"),
        ("自分が顧客",
         "Emport AI自身がこのシステムを毎日使っている。顧客の痛みをリアルタイムで理解し、最速で改善できる。"),
        ("地方からの逆張り",
         "東京勢が狙わない山口の中小企業市場がブルーオーシャン。ここで実績を積み、「地方から全国」という強いストーリーを作る。"),
        ("若さとスピード",
         "21歳の経営者が直接会いに行く。大手コンサルにできない接近戦・フットワーク・スピードが最大の差別化。"),
    ]
    col_w = W - 2 * MARGIN
    for title_r, body_r in reasons:
        data = [[
            Paragraph(f"▶ {title_r}", s("rh", size=9, color=C_BLUE, bold=True, leading=14)),
            Paragraph(body_r, ST_BODY),
        ]]
        t = Table(data, colWidths=[col_w * 0.22, col_w * 0.78])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), C_LIGHT),
            ("BACKGROUND",    (1, 0), (1, 0), C_WHITE),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
            ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t)
        story.append(sp(1.5))

    story.append(sp(4))

    # ── 締め言葉 ──
    story.append(hr(color=C_NAVY, thickness=1))
    story.append(sp(3))
    story.append(p(
        "「世界中のAI資本が動いている。山口県のブルーオーシャンはまだ誰も取っていない。<br/>"
        "あなたには21歳の時間と、AI参謀と、補助金という武器がある。<br/>"
        "今動かない理由が、一つでもあるか。」",
        s("closing", size=10, color=C_NAVY, bold=True, align=TA_CENTER, leading=20)
    ))
    story.append(sp(3))
    story.append(p("CEO アレン（Allen）/ Emport AI ― 2026年5月12日策定", ST_FOOTER))

    doc.build(story)
    print(f"PDF生成完了: {os.path.abspath(out_path)}")

if __name__ == "__main__":
    build()
