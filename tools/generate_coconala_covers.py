from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\departments\sales\ококоナラ準備\カバー画像"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1280, 960
FONT_PATH_BOLD = "C:/Windows/Fonts/YuGothB.ttc"
FONT_PATH = "C:/Windows/Fonts/YuGothM.ttc"

# 游ゴシックBoldがなければMediumで代替
if not os.path.exists(FONT_PATH_BOLD):
    FONT_PATH_BOLD = FONT_PATH


def make_gradient(w, h, color_top, color_bottom):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / h)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / h)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def draw_decorations(draw, w, h, accent):
    # 右下の大きな円（装飾）
    draw.ellipse([w - 320, h - 320, w + 80, h + 80], outline=(*accent, 40), width=3)
    draw.ellipse([w - 220, h - 220, w + 80, h + 80], outline=(*accent, 25), width=2)
    # 左上の小さなドット装飾
    for i, (dx, dy) in enumerate([(60, 60), (100, 60), (60, 100), (100, 100), (140, 60), (60, 140)]):
        alpha = 180 if i % 2 == 0 else 100
        draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(*accent, alpha))
    # 上部ライン
    draw.rectangle([0, 0, w, 6], fill=accent)


def draw_badge(draw, x, y, text, font_s, bg_color, text_color=(255, 255, 255)):
    bbox = draw.textbbox((0, 0), text, font=font_s)
    tw = bbox[2] - bbox[0]
    pad_x, pad_y = 24, 12
    rx0, ry0 = x, y
    rx1, ry1 = x + tw + pad_x * 2, y + (bbox[3] - bbox[1]) + pad_y * 2
    draw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=8, fill=bg_color)
    draw.text((rx0 + pad_x, ry0 + pad_y), text, font=font_s, fill=text_color)
    return rx1 - rx0


def generate_cover(filename, gradient_top, gradient_bottom, accent,
                   main_lines, sub_text, badge_text, tag_text):
    img = make_gradient(W, H, gradient_top, gradient_bottom)
    draw = ImageDraw.Draw(img, "RGBA")

    draw_decorations(draw, W, H, accent)

    font_main = ImageFont.truetype(FONT_PATH_BOLD, 72)
    font_sub = ImageFont.truetype(FONT_PATH, 36)
    font_badge = ImageFont.truetype(FONT_PATH_BOLD, 30)
    font_tag = ImageFont.truetype(FONT_PATH, 28)
    font_label = ImageFont.truetype(FONT_PATH, 26)

    # タグ（左上）
    draw_badge(draw, 60, 120, tag_text, font_tag, (*accent, 200))

    # メインテキスト
    y = 240
    for line in main_lines:
        draw.text((80, y), line, font=font_main, fill=(255, 255, 255))
        bbox = draw.textbbox((80, y), line, font=font_main)
        y += (bbox[3] - bbox[1]) + 16

    # 区切り線
    y += 24
    draw.rectangle([80, y, 80 + 80, y + 4], fill=accent)
    y += 32

    # サブテキスト
    draw.text((80, y), sub_text, font=font_sub, fill=(210, 220, 240))
    y += 80

    # バッジ（価格・モニター）
    draw_badge(draw, 80, y, badge_text, font_badge, accent)

    # ラベル（現在位置下部）
    draw.text((80, H - 80), "▶ まずはお気軽にご相談ください", font=font_label, fill=(180, 200, 230))

    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"生成: {filename}")


# サービス1：AI活用相談
generate_cover(
    filename="01_AI活用相談.png",
    gradient_top=(10, 20, 60),
    gradient_bottom=(20, 50, 120),
    accent=(80, 160, 255),
    main_lines=["AIの疑問・悩みを", "なんでも相談できます"],
    sub_text="ChatGPT・生成AIの活用をわかりやすくサポート",
    badge_text="◆ モニター価格 ¥2,000〜",
    tag_text="AI活用相談",
)

# サービス2：アイデア出しレポート
generate_cover(
    filename="02_AI活用アイデア出しレポート.png",
    gradient_top=(10, 45, 40),
    gradient_bottom=(15, 80, 100),
    accent=(60, 200, 160),
    main_lines=["あなたの業務に使える", "AI活用アイデアを提案します"],
    sub_text="ヒアリング → 効率化できる箇所をレポートで納品",
    badge_text="◆ モニター価格 ¥5,000〜",
    tag_text="AI活用レポート",
)

# サービス3：プロンプト作成
generate_cover(
    filename="03_ChatGPTプロンプト作成.png",
    gradient_top=(40, 10, 70),
    gradient_bottom=(80, 20, 120),
    accent=(180, 100, 255),
    main_lines=["業務専用", "ChatGPTプロンプトを作ります"],
    sub_text="そのまま使えるオーダーメイドプロンプト3本",
    badge_text="◆ モニター価格 ¥8,000〜",
    tag_text="プロンプト作成",
)

print("\n完了：departments/sales/ококоナラ準備/カバー画像/ に保存しました")
