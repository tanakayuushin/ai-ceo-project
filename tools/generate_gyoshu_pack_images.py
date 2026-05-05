"""
業種特化パック サービス画像生成スクリプト
設計方針:
  - 明るい背景 + 高コントラスト暗色テキスト（スマホでも見やすい）
  - 左：インダストリーカラーの帯 + 大漢字アイコン
  - 右：白地 + 大見出し + 明快な情報
  - テキストは自動でフォントサイズを調整してはみ出しを防ぐ
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\departments\sales\ококоナラ準備\業種特化パック\images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1280, 960
FONT_B = "C:/Windows/Fonts/YuGothB.ttc"
FONT_M = "C:/Windows/Fonts/YuGothM.ttc"
if not os.path.exists(FONT_B):
    FONT_B = FONT_M

WHITE  = (255, 255, 255)
DARK   = (18,  24,  50)
DGRAY  = (80,  90, 115)
LGRAY  = (230, 234, 242)

STRIP_W = 260   # 左帯の幅
TOP_H   = 18    # 上部アクセントバーの高さ
R_PAD   = 70    # 右エリアの左パディング
R_RIGHT = 60    # 右エリアの右パディング

# ===== 業種定義 =====
INDUSTRIES = [
    {
        "id": "restaurant",
        "file_prefix": "飲食店",
        "kanji": "食",
        "label": "飲食店専用",
        "headline": "飲食店の文章を、まとめます",
        "headline2": "6種類セットでお届け",
        "tagline": "HP・SNS・メニュー・Googleマップ・チラシ・求人まで",
        "includes_short": [
            "① HP・ホームページ紹介文",
            "② Googleマップ 説明文",
            "③ Instagram キャプション 10本",
            "④ メニュー・料理 説明文（10品）",
            "⑤ チラシ・ポップ コピー 3案",
            "⑥ スタッフ募集・求人票",
        ],
        "targets": [
            "開業・リニューアル前に文章をまとめて整えたい",
            "HP・Googleマップの文章が古いまま放置されている",
            "Instagramを始めたいが何を書けばいいかわからない",
            "文章を書く時間がない・苦手な個人経営者",
            "求人票の文章で困っているお店",
        ],
        "flow": [
            ("ご購入", "サービスをご購入ください"),
            ("ヒアリング", "お店の情報シートに\nご記入ください"),
            ("文章作成", "6種類の文章を\n丁寧に作成します"),
            ("納品", "完成文章一式を\nお届けします"),
            ("修正対応", "1回まで\n無料で修正します"),
        ],
        "sample_title": "納品サンプル（HP紹介文 イメージ）",
        "sample_text": (
            "【店名】は、地元素材にこだわった本格イタリアンを\n"
            "リーズナブルな価格でお楽しみいただけるお店です。\n\n"
            "シェフ歴15年の店主が、毎朝市場で仕入れた新鮮な\n"
            "食材を使い、ひとつひとつ丁寧に仕上げます。\n\n"
            "カウンター席もご用意しており、おひとり様や\n"
            "ランチ使いにも最適です。お気軽にお立ち寄りください。"
        ),
        "accent": (210, 75, 45),
        "light_bg": (255, 246, 242),
        "price": "モニター価格 ¥12,000",
        "regular": "通常 ¥22,000",
        "delivery": "納期 7日",
    },
    {
        "id": "beauty",
        "file_prefix": "美容サロン",
        "kanji": "美",
        "label": "美容サロン専用",
        "headline": "美容サロンの文章を、まとめます",
        "headline2": "6種類セットでお届け",
        "tagline": "HP・Hotpepper・SNS・メニュー・スタッフ紹介まで",
        "includes_short": [
            "① HP・コンセプト紹介文",
            "② ホットペッパービューティー掲載文",
            "③ Instagram キャプション 10本",
            "④ メニュー・コース 説明文（10点）",
            "⑤ Googleマップ 説明文",
            "⑥ スタッフ紹介文（1名）",
        ],
        "targets": [
            "開業・リニューアルに向けて文章を整えたい",
            "ホットペッパーの掲載文を魅力的にしたい",
            "Instagramを継続投稿したいが文章が続かない",
            "HPの文章が開業当時のまま更新できていない",
            "集客文章をまとめて一気に解決したい",
        ],
        "flow": [
            ("ご購入", "サービスをご購入ください"),
            ("ヒアリング", "サロンの情報シートに\nご記入ください"),
            ("文章作成", "6種類の文章を\n丁寧に作成します"),
            ("納品", "完成文章一式を\nお届けします"),
            ("修正対応", "1回まで\n無料で修正します"),
        ],
        "sample_title": "納品サンプル（Instagram キャプション イメージ）",
        "sample_text": (
            "【新メニュー】うるツヤ小顔コース、始めました✨\n\n"
            "フェイシャルと小顔矯正を組み合わせた\n"
            "【名前】サロンだけのオリジナルコースです。\n\n"
            "施術後はすぐに実感できる仕上がりに、\n"
            "リピーター続出中。気になる方はDMへ💌\n\n"
            "#美容室 #エステ #小顔 #モニター募集"
        ),
        "accent": (195, 65, 135),
        "light_bg": (255, 240, 250),
        "price": "モニター価格 ¥12,000",
        "regular": "通常 ¥22,000",
        "delivery": "納期 7日",
    },
    {
        "id": "seitai",
        "file_prefix": "整骨院整体",
        "kanji": "癒",
        "label": "整骨院・整体院専用",
        "headline": "整骨院の文章を、まとめます",
        "headline2": "6種類セットでお届け",
        "tagline": "HP・LINE・口コミ返信・コース説明・チラシまで",
        "includes_short": [
            "① HP・院長メッセージ紹介文",
            "② Googleマップ 説明文",
            "③ LINE配信 メッセージ 5本",
            "④ 症状別コース 説明文（5コース）",
            "⑤ チラシ・ポップ コピー 3案",
            "⑥ 口コミ・レビュー 返信例文 5本",
        ],
        "targets": [
            "開業・移転でHP文章を一新したい院長先生",
            "LINE公式を使いたいが配信文章が思いつかない",
            "Googleの口コミ返信を毎回悩んでいる",
            "コース説明が患者さんに伝わっていないと感じる",
            "集客文章をまとめて依頼したい",
        ],
        "flow": [
            ("ご購入", "サービスをご購入ください"),
            ("ヒアリング", "院の情報シートに\nご記入ください"),
            ("文章作成", "6種類の文章を\n丁寧に作成します"),
            ("納品", "完成文章一式を\nお届けします"),
            ("修正対応", "1回まで\n無料で修正します"),
        ],
        "sample_title": "納品サンプル（口コミ返信文 イメージ）",
        "sample_text": (
            "【5★レビューへの返信例】\n\n"
            "〇〇様、温かいお言葉をいただきありがとうございます。\n"
            "腰のお悩みが改善されてきたとのこと、大変嬉しいです。\n\n"
            "引き続き体の状態を見ながら丁寧にサポートしますので、\n"
            "何かお困りのことがあればお気軽にご相談ください。\n"
            "またのご来院を心よりお待ちしております。"
        ),
        "accent": (25, 148, 115),
        "light_bg": (235, 252, 247),
        "price": "モニター価格 ¥12,000",
        "regular": "通常 ¥22,000",
        "delivery": "納期 7日",
    },
]


# ===== ユーティリティ =====

def make_bg(w, h, color):
    img = Image.new("RGB", (w, h), color)
    return img


def fit_font(draw, text, font_path, max_size, min_size, max_width):
    for size in range(max_size, min_size - 1, -2):
        f = ImageFont.truetype(font_path, size)
        bb = draw.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_width:
            return f
    return ImageFont.truetype(font_path, min_size)


def draw_rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def badge(draw, x, y, text, font, fill, text_color=WHITE, pad_x=22, pad_y=10):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw_rounded_rect(draw, [x, y, x + tw + pad_x * 2, y + th + pad_y * 2], radius=7, fill=fill)
    draw.text((x + pad_x, y + pad_y), text, font=font, fill=text_color)
    return x + tw + pad_x * 2, y + th + pad_y * 2


def draw_check_item(draw, x, y, text, font, acc, r=15):
    cy = y + r
    draw.ellipse([x, y, x + r * 2, y + r * 2], fill=acc)
    draw.line([(x + 4, cy + 2), (x + r - 3, cy + 8), (x + r * 2 - 4, cy - 5)],
              fill=WHITE, width=2)
    draw.text((x + r * 2 + 14, y + 2), text, font=font, fill=DARK)
    bb = draw.textbbox((x + r * 2 + 14, y + 2), text, font=font)
    return bb[3]


# ===== 画像生成関数 =====

def gen_cover(ind):
    """カバー画像：インパクト重視・超大見出し・2カラム"""
    img = make_bg(W, H, ind["light_bg"])
    draw = ImageDraw.Draw(img, "RGBA")
    acc = ind["accent"]

    # ── 左帯 ──
    draw.rectangle([0, 0, STRIP_W, H], fill=acc)

    # 左帯：大漢字（薄く）
    f_kanji = ImageFont.truetype(FONT_B, 200)
    kb = draw.textbbox((0, 0), ind["kanji"], font=f_kanji)
    kw, kh = kb[2] - kb[0], kb[3] - kb[1]
    draw.text((STRIP_W // 2 - kw // 2, H // 2 - kh // 2 - 40),
              ind["kanji"], font=f_kanji, fill=(*WHITE, 55))

    # 左帯：ラベル（下部）
    f_label = ImageFont.truetype(FONT_B, 26)
    lb = draw.textbbox((0, 0), ind["label"], font=f_label)
    lw = lb[2] - lb[0]
    draw.text((STRIP_W // 2 - lw // 2, H - 72), ind["label"], font=f_label, fill=(*WHITE, 230))

    # 左帯：縦区切りライン（右端）
    draw.rectangle([STRIP_W - 4, 0, STRIP_W, H], fill=(*acc, 200))

    # ── 上部バー（全幅）──
    draw.rectangle([0, 0, W, TOP_H], fill=acc)

    # ── 右エリア（白）──
    draw.rectangle([STRIP_W, TOP_H, W, H], fill=WHITE)

    rx = STRIP_W + R_PAD
    avail_w = W - rx - R_RIGHT
    y = 50

    # カテゴリバッジ
    f_badge = ImageFont.truetype(FONT_B, 26)
    _, by2 = badge(draw, rx, y, "集客文章パック 6種類セット", f_badge, (*acc, 220))
    y = by2 + 28

    # ── メインヘッドライン ──
    f_h1 = fit_font(draw, ind["headline"], FONT_B, 84, 58, avail_w)
    draw.text((rx, y), ind["headline"], font=f_h1, fill=DARK)
    hb1 = draw.textbbox((rx, y), ind["headline"], font=f_h1)
    y = hb1[3] + 10

    # ── サブヘッドライン（アクセントカラー）──
    f_h2 = fit_font(draw, ind["headline2"], FONT_B, 62, 44, avail_w)
    draw.text((rx, y), ind["headline2"], font=f_h2, fill=acc)
    hb2 = draw.textbbox((rx, y), ind["headline2"], font=f_h2)
    y = hb2[3] + 18

    # 区切り
    draw.rectangle([rx, y, rx + 120, y + 5], fill=acc)
    y += 24

    # タグライン
    f_tag = fit_font(draw, ind["tagline"], FONT_M, 30, 22, avail_w)
    draw.text((rx, y), ind["tagline"], font=f_tag, fill=DGRAY)
    tb = draw.textbbox((rx, y), ind["tagline"], font=f_tag)
    y = tb[3] + 28

    # ── 6種類リスト（2列×3行）──
    f_item = ImageFont.truetype(FONT_M, 28)
    col_w = avail_w // 2
    items = ind["includes_short"]
    row_h = 46
    for i, item in enumerate(items):
        col = i % 2
        row = i // 2
        ix = rx + col * col_w
        iy = y + row * row_h
        draw_check_item(draw, ix, iy, item, f_item, acc, r=13)

    y += (len(items) // 2) * row_h + 24

    # ── 下部：価格・納期 ──
    draw.rectangle([rx, y, W - R_RIGHT, y + 2], fill=(*LGRAY, 200))
    y += 18

    f_price = ImageFont.truetype(FONT_B, 38)
    f_info  = ImageFont.truetype(FONT_M, 28)

    px2, py2 = badge(draw, rx, y, ind["price"], f_price, acc)
    draw.text((px2 + 24, y + 8), ind["delivery"], font=f_info, fill=DGRAY)
    draw.text((px2 + 24, y + 46), ind["regular"], font=ImageFont.truetype(FONT_M, 24), fill=(*DGRAY, 160))

    # 右下：安心マーク
    f_sm = ImageFont.truetype(FONT_M, 24)
    msg = "修正1回無料  |  購入後すぐにヒアリングシートをお送りします"
    mb = draw.textbbox((0, 0), msg, font=f_sm)
    mw = mb[2] - mb[0]
    draw.text((W - R_RIGHT - mw, H - 44), msg, font=f_sm, fill=(*DGRAY, 180))

    path = os.path.join(OUTPUT_DIR, f"{ind['file_prefix']}_01_カバー.png")
    img.save(path)
    print(f"  生成: {os.path.basename(path)}")


def gen_includes(ind):
    """提供内容：6種類を大きく・詳しく見せる"""
    img = make_bg(W, H, ind["light_bg"])
    draw = ImageDraw.Draw(img, "RGBA")
    acc = ind["accent"]

    draw.rectangle([0, 0, STRIP_W, H], fill=acc)
    f_kanji = ImageFont.truetype(FONT_B, 200)
    kb = draw.textbbox((0, 0), ind["kanji"], font=f_kanji)
    draw.text((STRIP_W // 2 - (kb[2] - kb[0]) // 2, H // 2 - (kb[3] - kb[1]) // 2 - 40),
              ind["kanji"], font=f_kanji, fill=(*WHITE, 55))
    f_label = ImageFont.truetype(FONT_B, 26)
    lb = draw.textbbox((0, 0), ind["label"], font=f_label)
    draw.text((STRIP_W // 2 - (lb[2] - lb[0]) // 2, H - 72), ind["label"], font=f_label, fill=(*WHITE, 230))
    draw.rectangle([0, 0, W, TOP_H], fill=acc)
    draw.rectangle([STRIP_W, TOP_H, W, H], fill=WHITE)

    rx = STRIP_W + R_PAD
    avail_w = W - rx - R_RIGHT
    y = 44

    f_badge = ImageFont.truetype(FONT_B, 26)
    _, by2 = badge(draw, rx, y, "提供内容", f_badge, (*acc, 220))
    y = by2 + 18

    f_title = fit_font(draw, "6種類の文章をセットでお届けします", FONT_B, 62, 44, avail_w)
    draw.text((rx, y), "6種類の文章をセットでお届けします", font=f_title, fill=DARK)
    tb = draw.textbbox((rx, y), "6種類の文章をセットでお届けします", font=f_title)
    y = tb[3] + 10
    draw.rectangle([rx, y, rx + 120, y + 5], fill=acc)
    y += 28

    # カードグリッド（2列×3行）
    card_w = (avail_w - 24) // 2
    card_h = 168
    gap = 16
    f_num  = ImageFont.truetype(FONT_B, 22)
    f_item_title = ImageFont.truetype(FONT_B, 30)
    f_item_desc  = ImageFont.truetype(FONT_M, 24)

    # 6アイテムの詳細説明
    details = [
        ("HP・ホームページ紹介文", "400〜600字で店舗の魅力を表現\nコンセプト・こだわり・雰囲気を凝縮"),
        ("Googleマップ 説明文", "検索流入を最大化する150字\n「行ってみたい」と思わせる一文"),
        ("Instagram キャプション 10本", "季節・メニュー・お知らせ等\nそのままコピペして使えます"),
        ("メニュー・サービス 説明文", "10品目/10点まで対応\n食欲・購買意欲を高める表現で"),
        ("チラシ・ポップ コピー", "3パターンのキャッチコピー\n近隣配布・店頭掲示に使える"),
        ("求人票・スタッフ募集文", "Indeed・ハローワーク対応\n応募者が集まる求人文に"),
    ]

    for i, (title, desc) in enumerate(details):
        col = i % 2
        row = i // 2
        cx = rx + col * (card_w + gap)
        cy = y + row * (card_h + gap)

        # カード背景
        draw_rounded_rect(draw, [cx, cy, cx + card_w, cy + card_h],
                          radius=10, fill=ind["light_bg"], outline=(*acc, 80), width=2)

        # 番号バッジ
        num_text = f"0{i+1}"
        draw_rounded_rect(draw, [cx + 12, cy + 12, cx + 52, cy + 42], radius=6, fill=acc)
        nb = draw.textbbox((0, 0), num_text, font=f_num)
        nw, nh = nb[2] - nb[0], nb[3] - nb[1]
        draw.text((cx + 32 - nw // 2, cy + 27 - nh // 2), num_text, font=f_num, fill=WHITE)

        # タイトル
        draw.text((cx + 64, cy + 14), title, font=f_item_title, fill=DARK)

        # 説明（改行対応）
        lines = desc.split("\n")
        dy = cy + 56
        for line in lines:
            draw.text((cx + 16, dy), line, font=f_item_desc, fill=DGRAY)
            dy += 30

    y += 3 * (card_h + gap) + 14

    # 下部
    f_note = ImageFont.truetype(FONT_M, 26)
    note = "※ 全6種類を一度にまとめてご依頼いただくため、文章のトーン・世界観が統一されます"
    draw.text((rx, y), note, font=f_note, fill=DGRAY)

    path = os.path.join(OUTPUT_DIR, f"{ind['file_prefix']}_02_提供内容.png")
    img.save(path)
    print(f"  生成: {os.path.basename(path)}")


def gen_target(ind):
    """こんな方向け：痛みポイント共感型"""
    img = make_bg(W, H, ind["light_bg"])
    draw = ImageDraw.Draw(img, "RGBA")
    acc = ind["accent"]

    draw.rectangle([0, 0, STRIP_W, H], fill=acc)
    f_kanji = ImageFont.truetype(FONT_B, 200)
    kb = draw.textbbox((0, 0), ind["kanji"], font=f_kanji)
    draw.text((STRIP_W // 2 - (kb[2] - kb[0]) // 2, H // 2 - (kb[3] - kb[1]) // 2 - 40),
              ind["kanji"], font=f_kanji, fill=(*WHITE, 55))
    f_label = ImageFont.truetype(FONT_B, 26)
    lb = draw.textbbox((0, 0), ind["label"], font=f_label)
    draw.text((STRIP_W // 2 - (lb[2] - lb[0]) // 2, H - 72), ind["label"], font=f_label, fill=(*WHITE, 230))
    draw.rectangle([0, 0, W, TOP_H], fill=acc)
    draw.rectangle([STRIP_W, TOP_H, W, H], fill=WHITE)

    rx = STRIP_W + R_PAD
    avail_w = W - rx - R_RIGHT
    y = 44

    f_badge = ImageFont.truetype(FONT_B, 26)
    _, by2 = badge(draw, rx, y, "こんな方におすすめ", f_badge, (*acc, 220))
    y = by2 + 18

    # タイトル
    title = "こんなお悩み、ありませんか？"
    f_title = fit_font(draw, title, FONT_B, 72, 50, avail_w)
    draw.text((rx, y), title, font=f_title, fill=DARK)
    tb = draw.textbbox((rx, y), title, font=f_title)
    y = tb[3] + 10
    draw.rectangle([rx, y, rx + 120, y + 5], fill=acc)
    y += 32

    # 吹き出し風アイテム
    f_item = ImageFont.truetype(FONT_M, 34)
    f_check = ImageFont.truetype(FONT_B, 28)
    balloon_h = 76
    balloon_gap = 18

    for i, target in enumerate(ind["targets"]):
        bx1 = rx
        by1 = y + i * (balloon_h + balloon_gap)
        bx2 = W - R_RIGHT
        by2b = by1 + balloon_h

        # 吹き出し背景（カード風）
        alpha_base = 255 - i * 20
        draw_rounded_rect(draw, [bx1, by1, bx2, by2b], radius=12,
                          fill=(*acc, 18 + i * 8), outline=(*acc, 60), width=1)

        # 左のアクセント縦線
        draw.rectangle([bx1, by1, bx1 + 8, by2b], fill=acc)

        # テキスト
        draw.text((bx1 + 28, by1 + (balloon_h - 38) // 2), "▶", font=f_check, fill=acc)
        draw.text((bx1 + 68, by1 + (balloon_h - 38) // 2), target, font=f_item, fill=DARK)

    y += len(ind["targets"]) * (balloon_h + balloon_gap) + 20

    # 解決メッセージ
    draw.rectangle([rx, y, W - R_RIGHT, y + 3], fill=(*acc, 100))
    y += 20
    f_sol = ImageFont.truetype(FONT_B, 38)
    sol = "全部まとめてお任せください。"
    sb = draw.textbbox((0, 0), sol, font=f_sol)
    sw = sb[2] - sb[0]
    draw.text((rx + avail_w // 2 - sw // 2, y), sol, font=f_sol, fill=acc)

    path = os.path.join(OUTPUT_DIR, f"{ind['file_prefix']}_03_おすすめ対象.png")
    img.save(path)
    print(f"  生成: {os.path.basename(path)}")


def gen_flow(ind):
    """購入の流れ：縦型ステップ"""
    img = make_bg(W, H, ind["light_bg"])
    draw = ImageDraw.Draw(img, "RGBA")
    acc = ind["accent"]

    draw.rectangle([0, 0, STRIP_W, H], fill=acc)
    f_kanji = ImageFont.truetype(FONT_B, 200)
    kb = draw.textbbox((0, 0), ind["kanji"], font=f_kanji)
    draw.text((STRIP_W // 2 - (kb[2] - kb[0]) // 2, H // 2 - (kb[3] - kb[1]) // 2 - 40),
              ind["kanji"], font=f_kanji, fill=(*WHITE, 55))
    f_label = ImageFont.truetype(FONT_B, 26)
    lb = draw.textbbox((0, 0), ind["label"], font=f_label)
    draw.text((STRIP_W // 2 - (lb[2] - lb[0]) // 2, H - 72), ind["label"], font=f_label, fill=(*WHITE, 230))
    draw.rectangle([0, 0, W, TOP_H], fill=acc)
    draw.rectangle([STRIP_W, TOP_H, W, H], fill=WHITE)

    rx = STRIP_W + R_PAD
    avail_w = W - rx - R_RIGHT
    y = 44

    f_badge = ImageFont.truetype(FONT_B, 26)
    _, by2 = badge(draw, rx, y, "購入の流れ", f_badge, (*acc, 220))
    y = by2 + 18

    title = "ご購入からお届けまでの流れ"
    f_title = fit_font(draw, title, FONT_B, 66, 48, avail_w)
    draw.text((rx, y), title, font=f_title, fill=DARK)
    tb = draw.textbbox((rx, y), title, font=f_title)
    y = tb[3] + 10
    draw.rectangle([rx, y, rx + 120, y + 5], fill=acc)
    y += 28

    # ステップ（縦型）
    f_step_name = ImageFont.truetype(FONT_B, 36)
    f_step_desc = ImageFont.truetype(FONT_M, 26)
    f_num_s = ImageFont.truetype(FONT_B, 28)
    circle_r = 34
    circle_x = rx + circle_r
    step_h = 144
    prev_cy = None

    for i, (name, desc) in enumerate(ind["flow"]):
        cy = y + circle_r

        # 接続ライン
        if prev_cy is not None:
            draw.line([(circle_x, prev_cy + circle_r + 2), (circle_x, cy - circle_r - 2)],
                      fill=(*acc, 140), width=4)

        # ステップ円
        draw.ellipse([circle_x - circle_r, cy - circle_r,
                      circle_x + circle_r, cy + circle_r], fill=acc)
        num = str(i + 1)
        nb = draw.textbbox((0, 0), num, font=f_num_s)
        nw, nh = nb[2] - nb[0], nb[3] - nb[1]
        draw.text((circle_x - nw // 2, cy - nh // 2), num, font=f_num_s, fill=WHITE)

        # ステップ名ボックス
        bx = circle_x + circle_r + 24
        sb = draw.textbbox((0, 0), name, font=f_step_name)
        sw, sh = sb[2] - sb[0], sb[3] - sb[1]
        box_top = cy - 20
        draw_rounded_rect(draw, [bx, box_top, bx + sw + 28, box_top + sh + 16],
                          radius=8, fill=(*acc, 50), outline=(*acc, 120), width=1)
        draw.text((bx + 14, box_top + 8), name, font=f_step_name, fill=DARK)

        # 説明（改行対応）
        dy = box_top + sh + 24
        for line in desc.split("\n"):
            draw.text((bx + 4, dy), line, font=f_step_desc, fill=DGRAY)
            dy += 32

        prev_cy = cy
        y += step_h

    # 下部メッセージ
    y = H - 72
    f_note = ImageFont.truetype(FONT_M, 26)
    note = "ご不明な点はお気軽にメッセージください。返信は1時間以内を目標にしています。"
    nb = draw.textbbox((0, 0), note, font=f_note)
    nw = nb[2] - nb[0]
    draw.text((STRIP_W + (W - STRIP_W) // 2 - nw // 2, y), note, font=f_note, fill=(*acc, 200))

    path = os.path.join(OUTPUT_DIR, f"{ind['file_prefix']}_04_購入の流れ.png")
    img.save(path)
    print(f"  生成: {os.path.basename(path)}")


def gen_sample(ind):
    """サンプルプレビュー：実際の納品物イメージを見せる"""
    img = make_bg(W, H, ind["light_bg"])
    draw = ImageDraw.Draw(img, "RGBA")
    acc = ind["accent"]

    draw.rectangle([0, 0, STRIP_W, H], fill=acc)
    f_kanji = ImageFont.truetype(FONT_B, 200)
    kb = draw.textbbox((0, 0), ind["kanji"], font=f_kanji)
    draw.text((STRIP_W // 2 - (kb[2] - kb[0]) // 2, H // 2 - (kb[3] - kb[1]) // 2 - 40),
              ind["kanji"], font=f_kanji, fill=(*WHITE, 55))
    f_label = ImageFont.truetype(FONT_B, 26)
    lb = draw.textbbox((0, 0), ind["label"], font=f_label)
    draw.text((STRIP_W // 2 - (lb[2] - lb[0]) // 2, H - 72), ind["label"], font=f_label, fill=(*WHITE, 230))
    draw.rectangle([0, 0, W, TOP_H], fill=acc)
    draw.rectangle([STRIP_W, TOP_H, W, H], fill=WHITE)

    rx = STRIP_W + R_PAD
    avail_w = W - rx - R_RIGHT
    y = 44

    f_badge = ImageFont.truetype(FONT_B, 26)
    _, by2 = badge(draw, rx, y, "納品物サンプル", f_badge, (*acc, 220))
    y = by2 + 18

    title = "実際の納品文章（イメージ）"
    f_title = fit_font(draw, title, FONT_B, 66, 48, avail_w)
    draw.text((rx, y), title, font=f_title, fill=DARK)
    tb = draw.textbbox((rx, y), title, font=f_title)
    y = tb[3] + 10
    draw.rectangle([rx, y, rx + 120, y + 5], fill=acc)
    y += 24

    # サンプルカード
    card_top = y
    card_right = W - R_RIGHT
    card_bottom = H - 120

    # カード背景（白＋影風ボーダー）
    draw_rounded_rect(draw, [rx, card_top, card_right, card_bottom],
                      radius=14, fill=WHITE, outline=LGRAY, width=2)
    draw.rectangle([rx, card_top, card_right, card_top + 52],
                   fill=(*acc, 230))
    draw_rounded_rect(draw, [rx, card_top, card_right, card_top + 52],
                      radius=14, fill=(*acc, 230))
    draw.rectangle([rx, card_top + 26, card_right, card_top + 52], fill=(*acc, 230))

    # カードヘッダーテキスト
    f_card_title = ImageFont.truetype(FONT_B, 28)
    draw.text((rx + 20, card_top + 12), ind["sample_title"], font=f_card_title, fill=WHITE)

    # サンプルテキスト
    f_sample = ImageFont.truetype(FONT_M, 29)
    sy = card_top + 72
    for line in ind["sample_text"].split("\n"):
        draw.text((rx + 28, sy), line, font=f_sample, fill=DARK)
        sy += 40

    # 下部ポイント説明
    y = card_bottom + 18
    f_pt = ImageFont.truetype(FONT_M, 26)
    points = [
        "実際の納品は、ヒアリング内容をもとにあなたのお店専用の文章を作成します",
        "文章はテキスト形式でトークルーム内に納品。コピーしてそのままご利用いただけます",
    ]
    for pt in points:
        draw.text((rx, y), f"▷  {pt}", font=f_pt, fill=DGRAY)
        y += 36

    path = os.path.join(OUTPUT_DIR, f"{ind['file_prefix']}_05_サンプル.png")
    img.save(path)
    print(f"  生成: {os.path.basename(path)}")


# ===== 実行 =====
print("業種特化パック サービス画像を生成中...\n")
for ind in INDUSTRIES:
    print(f"【{ind['file_prefix']}】")
    gen_cover(ind)
    gen_includes(ind)
    gen_target(ind)
    gen_flow(ind)
    gen_sample(ind)
    print()

print(f"完了: {OUTPUT_DIR}")
