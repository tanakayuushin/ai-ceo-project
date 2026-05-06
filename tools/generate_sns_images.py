"""
Emport AI - Instagram / X (Twitter) 用ブランド画像生成スクリプト
生成物:
  01_x_header.png          X ヘッダー画像 (1500x500)
  02_x_icon.png            X プロフィールアイコン (400x400)
  03_instagram_icon.png    Instagram プロフィールアイコン (1080x1080)
  04_ig_post_service.png   Instagram 投稿①：サービス紹介 (1080x1080)
  05_ig_post_hook.png      Instagram 投稿②：フック（悩み解決）(1080x1080)
  06_ig_post_price.png     Instagram 投稿③：料金案内 (1080x1080)
  07_ig_story.png          Instagram ストーリー (1080x1920)
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\departments\marketing\sns-images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── ブランドカラー ──────────────────────────────
NAVY      = (10,  27,  75)
DARK_BLUE = (18,  52, 130)
MID_BLUE  = (30,  90, 180)
ACCENT    = (64, 180, 255)
WHITE     = (255, 255, 255)
LIGHT     = (200, 220, 255)
YELLOW    = (255, 220,  60)


# ── ユーティリティ ─────────────────────────────

def make_gradient(w, h, top_color, bottom_color):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def get_font(size):
    """日本語フォントを取得（システムフォントを順に試す）"""
    candidates = [
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_centered_text(draw, text, y, font, color, img_width):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (img_width - w) // 2
    draw.text((x, y), text, font=font, fill=color)


def draw_circles_deco(draw, w, h):
    """背景装飾：薄い円を数個配置"""
    for cx, cy, r, alpha in [
        (w - 120, 80,  180, 20),
        (w - 60,  h - 60, 120, 15),
        (80,      h - 100, 90, 18),
        (w // 2,  h + 40, 250, 10),
    ]:
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=(*ACCENT, alpha), width=3)
        draw._image.paste(Image.alpha_composite(
            draw._image.convert("RGBA"), overlay).convert("RGB"))


def add_logo_text(draw, x, y, font_lg, font_sm, color_main=WHITE, color_sub=ACCENT):
    """'Emport AI' ロゴ風テキスト"""
    draw.text((x, y), "Emport AI", font=font_lg, fill=color_main)
    draw.text((x, y + font_lg.size + 4), "AIで、地方企業を強くする", font=font_sm, fill=color_sub)


# ── 01：X ヘッダー (1500x500) ─────────────────

def gen_x_header():
    W, H = 1500, 500
    img = make_gradient(W, H, NAVY, DARK_BLUE)
    draw = ImageDraw.Draw(img)

    # 装飾円
    for cx, cy, r in [(1350, 80, 220), (1420, 420, 160), (100, 400, 130)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                     outline=(*ACCENT, 25), width=2)

    # アクセントライン
    draw.rectangle([80, 160, 86, 340], fill=ACCENT)

    # テキスト
    f_main = get_font(80)
    f_sub  = get_font(36)
    f_tag  = get_font(28)

    draw.text((110, 145), "Emport AI", font=f_main, fill=WHITE)
    draw.text((112, 245), "山口県の中小企業に、AIの力を届ける", font=f_sub, fill=LIGHT)

    tags = ["#AI活用支援", "#中小企業DX", "#山口県", "#生成AI"]
    tx = 112
    for tag in tags:
        bbox = draw.textbbox((0, 0), tag, font=f_tag)
        tw = bbox[2] - bbox[0]
        draw.rounded_rectangle([tx - 8, 308, tx + tw + 8, 345],
                                radius=6, fill=(*MID_BLUE, 180))
        draw.text((tx, 310), tag, font=f_tag, fill=ACCENT)
        tx += tw + 28

    draw.text((112, 370), "yuubisinesu@gmail.com  |  X: @AI_chuusyou", font=f_tag, fill=LIGHT)

    out = os.path.join(OUTPUT_DIR, "01_x_header.png")
    img.save(out)
    print(f"OK: {out}")


# ── 02：X アイコン (400x400) ──────────────────

def gen_x_icon():
    S = 400
    img = make_gradient(S, S, DARK_BLUE, NAVY)
    draw = ImageDraw.Draw(img)

    # 外枠円
    draw.ellipse([10, 10, S-10, S-10], outline=ACCENT, width=4)

    # "E" ロゴ風（シンプルな図形）
    cx, cy = S//2, S//2 - 20
    r = 90
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=MID_BLUE)

    f_logo = get_font(100)
    f_sub  = get_font(30)
    bbox = draw.textbbox((0, 0), "EA", font=f_logo)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw//2, cy - th//2 - 5), "EA", font=f_logo, fill=WHITE)

    draw_centered_text(draw, "Emport AI", S - 80, f_sub, ACCENT, S)

    # 円形クロップ
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S, S], fill=255)
    result = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    result.paste(img.convert("RGBA"), mask=mask)

    out = os.path.join(OUTPUT_DIR, "02_x_icon.png")
    result.save(out)
    print(f"OK: {out}")


# ── 03：Instagramアイコン (1080x1080) ─────────

def gen_instagram_icon():
    S = 1080
    img = make_gradient(S, S, DARK_BLUE, NAVY)
    draw = ImageDraw.Draw(img)

    # 装飾円
    for cx, cy, r in [(S-150, 150, 300), (150, S-150, 250)]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                     outline=(*ACCENT, 30), width=4)

    # 中央ロゴ円
    cx, cy = S//2, S//2 - 60
    r = 240
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*MID_BLUE, 200))
    draw.ellipse([cx-r+6, cy-r+6, cx+r-6, cy+r-6], outline=ACCENT, width=5)

    f_logo = get_font(260)
    f_name = get_font(90)
    f_sub  = get_font(54)

    bbox = draw.textbbox((0, 0), "EA", font=f_logo)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx - tw//2, cy - th//2 - 10), "EA", font=f_logo, fill=WHITE)

    draw_centered_text(draw, "Emport AI", cy + r + 40,  f_name, WHITE, S)
    draw_centered_text(draw, "AIで、地方企業を強くする", cy + r + 148, f_sub, ACCENT, S)

    # 円形クロップ
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S, S], fill=255)
    result = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    result.paste(img.convert("RGBA"), mask=mask)

    out = os.path.join(OUTPUT_DIR, "03_instagram_icon.png")
    result.save(out)
    print(f"OK: {out}")


# ── 04：Instagram投稿①：サービス紹介 (1080x1080) ─

def gen_ig_service():
    S = 1080
    img = make_gradient(S, S, NAVY, DARK_BLUE)
    draw = ImageDraw.Draw(img)

    # 上部アクセントバー
    draw.rectangle([0, 0, S, 12], fill=ACCENT)

    f_badge = get_font(36)
    f_main  = get_font(72)
    f_sub   = get_font(44)
    f_item  = get_font(40)
    f_small = get_font(32)

    # バッジ
    draw.rounded_rectangle([60, 60, 340, 110], radius=10, fill=MID_BLUE)
    draw.text((75, 68), "Emport AI のサービス", font=f_badge, fill=ACCENT)

    # タイトル
    draw.text((60, 140), "AIを導入したいけど、", font=f_main, fill=WHITE)
    draw.text((60, 225), "どこから始めれば？", font=f_main, fill=YELLOW)

    # 区切り線
    draw.rectangle([60, 325, 340, 331], fill=ACCENT)

    # サービス3つ
    services = [
        ("01", "AI業務診断", "半日訪問＋課題レポート  ¥5〜10万"),
        ("02", "AI導入・実装", "業務フローへのAI実装支援  ¥50〜200万"),
        ("03", "運用サポート", "定着化・社内研修  月¥5〜15万"),
    ]
    y = 360
    for num, title, desc in services:
        draw.rounded_rectangle([60, y, S-60, y+130], radius=14,
                                fill=(*MID_BLUE, 140))
        draw.rounded_rectangle([68, y+8, 120, y+122], radius=8, fill=ACCENT)
        draw_centered_text(draw, num, y+42, get_font(36), NAVY, 188)
        draw.text((140, y+22), title, font=f_sub,   fill=WHITE)
        draw.text((140, y+76), desc,  font=f_small, fill=LIGHT)
        y += 150

    # フッター
    draw.rectangle([0, S-68, S, S], fill=MID_BLUE)
    draw_centered_text(draw, "Emport AI  |  yuubisinesu@gmail.com", S-54, f_small, LIGHT, S)

    # 下部アクセントバー
    draw.rectangle([0, S-8, S, S], fill=ACCENT)

    out = os.path.join(OUTPUT_DIR, "04_ig_post_service.png")
    img.save(out)
    print(f"OK: {out}")


# ── 05：Instagram投稿②：フック (1080x1080) ──────

def gen_ig_hook():
    S = 1080
    img = make_gradient(S, S, (8, 20, 60), DARK_BLUE)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, S, 12], fill=YELLOW)

    f_q    = get_font(88)
    f_main = get_font(76)
    f_sub  = get_font(46)
    f_cta  = get_font(42)
    f_foot = get_font(32)

    # 疑問フック
    draw.text((60, 80),  "こんな悩み、", font=f_q, fill=LIGHT)
    draw.text((60, 178), "ありませんか？", font=f_q, fill=YELLOW)

    # 悩みリスト
    pains = [
        "「AIって難しそう…」",
        "「何から始めればいいかわからない」",
        "「導入したけど使いこなせない」",
        "「社員がAIを使ってくれない」",
    ]
    y = 290
    for pain in pains:
        draw.rounded_rectangle([60, y, S-60, y+80], radius=10,
                                fill=(*MID_BLUE, 120))
        draw.text((100, y+18), pain, font=f_sub, fill=WHITE)
        y += 88

    # 解決策
    draw.rectangle([60, y+20, S-60, y+22], fill=ACCENT)
    y += 40
    draw.text((60, y+10), "Emport AI が", font=f_main, fill=WHITE)
    draw.text((60, y+98), "全部サポートします。", font=f_main, fill=ACCENT)

    # CTA
    draw.rounded_rectangle([60, S-180, S-60, S-100],
                            radius=14, fill=ACCENT)
    draw_centered_text(draw, "まずは無料相談から →", S-168, f_cta, NAVY, S)

    draw.rectangle([0, S-68, S, S], fill=(*NAVY, 200))
    draw_centered_text(draw, "Emport AI  |  yuubisinesu@gmail.com", S-54, f_foot, LIGHT, S)
    draw.rectangle([0, S-8, S, S], fill=YELLOW)

    out = os.path.join(OUTPUT_DIR, "05_ig_post_hook.png")
    img.save(out)
    print(f"OK: {out}")


# ── 06：Instagram投稿③：料金案内 (1080x1080) ─────

def gen_ig_price():
    S = 1080
    img = make_gradient(S, S, NAVY, (5, 15, 50))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, S, 12], fill=ACCENT)

    f_badge = get_font(36)
    f_title = get_font(74)
    f_plan  = get_font(48)
    f_price = get_font(64)
    f_desc  = get_font(36)
    f_foot  = get_font(32)

    draw.rounded_rectangle([60, 50, 300, 102], radius=10, fill=MID_BLUE)
    draw.text((75, 58), "料金プラン", font=f_badge, fill=ACCENT)

    draw.text((60, 128), "補助金を使えば", font=f_title, fill=WHITE)
    draw.text((60, 216), "実質 ¥0 から始められます", font=get_font(58), fill=YELLOW)

    plans = [
        ("ライトプラン",    "¥30,000/月", "SNS投稿文10本生成＋テンプレ提供"),
        ("スタンダード",    "¥50,000/月", "SNS投稿文無制限＋LINE配信文＋月1相談"),
        ("フルサポート",    "¥100,000/月","上記＋AI導入設定・社内レクチャー込み"),
    ]
    y = 340
    colors = [MID_BLUE, (20, 70, 160), (10, 50, 130)]
    for (name, price, desc), bg in zip(plans, colors):
        draw.rounded_rectangle([60, y, S-60, y+168], radius=14, fill=bg)
        draw.text((100, y+12), name,  font=f_plan,  fill=LIGHT)
        draw.text((100, y+62), price, font=f_price, fill=YELLOW)
        draw.text((100, y+132), desc, font=f_desc,  fill=LIGHT)
        y += 178

    draw.text((60, y+10), "※デジタル化・AI導入補助金2026（最大450万円）適用可", font=f_desc, fill=ACCENT)

    draw.rectangle([0, S-68, S, S], fill=MID_BLUE)
    draw_centered_text(draw, "Emport AI  |  yuubisinesu@gmail.com", S-54, f_foot, LIGHT, S)
    draw.rectangle([0, S-8, S, S], fill=ACCENT)

    out = os.path.join(OUTPUT_DIR, "06_ig_post_price.png")
    img.save(out)
    print(f"OK: {out}")


# ── 07：Instagramストーリー (1080x1920) ──────────

def gen_ig_story():
    W, H = 1080, 1920
    img = make_gradient(W, H, (8, 20, 65), DARK_BLUE)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 16], fill=ACCENT)

    f_logo  = get_font(72)
    f_title = get_font(90)
    f_sub   = get_font(54)
    f_item  = get_font(46)
    f_cta   = get_font(52)
    f_foot  = get_font(36)

    # ロゴ
    draw_centered_text(draw, "Emport AI", 80, f_logo, WHITE, W)
    draw_centered_text(draw, "AIで、地方企業を強くする", 166, f_item, ACCENT, W)

    # 区切り
    draw.rectangle([W//2 - 150, 250, W//2 + 150, 256], fill=ACCENT)

    # メインコピー
    draw.text((60, 290), "「AIを使いたいけど", font=f_title, fill=WHITE)
    draw.text((60, 390), "どこから始めれば", font=f_title, fill=WHITE)
    draw.text((60, 490), "いいかわからない」", font=f_title, fill=YELLOW)

    draw.text((60, 630), "そのお悩み、", font=f_sub, fill=LIGHT)
    draw.text((60, 696), "Emport AI が解決します。", font=f_sub, fill=WHITE)

    # サービス箇条書き
    items = [
        "▶  AI業務診断（半日 ¥5〜10万）",
        "▶  AI導入・実装サポート",
        "▶  社内AI研修・定着化支援",
        "▶  補助金申請サポート付き",
    ]
    y = 820
    for item in items:
        draw.rounded_rectangle([60, y, W-60, y+80], radius=12,
                                fill=(*MID_BLUE, 160))
        draw.text((90, y+16), item, font=f_item, fill=WHITE)
        y += 100

    # 補助金バナー
    draw.rounded_rectangle([60, y+40, W-60, y+160], radius=16, fill=(*ACCENT, 220))
    draw_centered_text(draw, "補助金で最大450万円補助！", y+56,  f_sub, NAVY, W)
    draw_centered_text(draw, "今すぐ無料相談受付中", y+116, f_sub, NAVY, W)

    # CTAボタン
    draw.rounded_rectangle([100, H-360, W-100, H-260], radius=20, fill=WHITE)
    draw_centered_text(draw, "yuubisinesu@gmail.com", H-330, f_cta, NAVY, W)

    draw.rounded_rectangle([100, H-230, W-100, H-130], radius=20,
                            outline=ACCENT, width=4)
    draw_centered_text(draw, "X: @AI_chuusyou", H-200, f_cta, ACCENT, W)

    draw.rectangle([0, H-68, W, H], fill=MID_BLUE)
    draw_centered_text(draw, "山口県 | Emport AI", H-54, f_foot, LIGHT, W)
    draw.rectangle([0, H-8, W, H], fill=ACCENT)

    out = os.path.join(OUTPUT_DIR, "07_ig_story.png")
    img.save(out)
    print(f"OK: {out}")


# ── メイン ─────────────────────────────────────

if __name__ == "__main__":
    print("Emport AI SNS image generation start...")
    gen_x_header()
    gen_x_icon()
    gen_instagram_icon()
    gen_ig_service()
    gen_ig_hook()
    gen_ig_price()
    gen_ig_story()
    print(f"\nDone: {OUTPUT_DIR}")
