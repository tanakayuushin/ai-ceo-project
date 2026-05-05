from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\departments\sales\ококоナラ準備"
W, H = 2560, 840

FONT_B = "C:/Windows/Fonts/YuGothB.ttc"
FONT_M = "C:/Windows/Fonts/YuGothM.ttc"
if not os.path.exists(FONT_B):
    FONT_B = FONT_M


def make_gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(top[0] + (bottom[0] - top[0]) * y / h)
        g = int(top[1] + (bottom[1] - top[1]) * y / h)
        b = int(top[2] + (bottom[2] - top[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def generate():
    img = make_gradient(W, H, (210, 230, 255), (160, 205, 250))
    draw = ImageDraw.Draw(img, "RGBA")

    ACCENT  = (50, 120, 230)
    DARK    = (20, 40, 100)
    MID     = (60, 90, 160)
    WHITE   = (255, 255, 255)
    TAG_BG  = (50, 120, 230, 210)
    TAG_TXT = (255, 255, 255)

    # ---- 背景装飾：大きな円（右側） ----
    draw.ellipse([W - 700, -200, W + 300, H + 200], fill=(180, 215, 255, 80))
    draw.ellipse([W - 550, -100, W + 150, H + 100], fill=(160, 200, 250, 60))
    # 左上ドット装飾
    for i, (dx, dy) in enumerate([(80,80),(140,80),(80,140),(140,140),(200,80),(80,200),(200,140)]):
        c = 160 if i % 2 == 0 else 120
        draw.ellipse([dx-10, dy-10, dx+10, dy+10], fill=(ACCENT[0], ACCENT[1], ACCENT[2], c))

    # ---- 上部アクセントライン ----
    draw.rectangle([0, 0, W, 12], fill=ACCENT)

    # ---- 左エリア：メインコピー ----
    font_catch  = ImageFont.truetype(FONT_B, 120)
    font_sub    = ImageFont.truetype(FONT_M, 56)
    font_tag    = ImageFont.truetype(FONT_B, 48)
    font_label  = ImageFont.truetype(FONT_M, 44)

    px = 140

    # キャッチコピー（2行）
    draw.text((px, 120), '"AIって難しい"を', font=font_catch, fill=DARK)
    draw.text((px, 260), 'なくす人', font=font_catch, fill=ACCENT)

    # 区切りライン
    draw.rectangle([px, 410, px + 120, 422], fill=ACCENT)

    # サブテキスト（2行に分割して右の円と被らないように）
    draw.text((px, 445), 'ChatGPT・生成AIの活用を、', font=font_sub, fill=MID)
    draw.text((px, 510), '現場の言葉でわかりやすくサポートします', font=font_sub, fill=MID)

    # ---- タグバッジ ----
    tags = ['ChatGPT', '生成AI活用', '業務効率化', '中小企業支援', 'AI相談']
    tx = px
    ty = 620
    pad_x, pad_y = 28, 16
    for tag in tags:
        bbox = draw.textbbox((0, 0), tag, font=font_tag)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        rx1 = tx + tw + pad_x * 2
        ry1 = ty + th + pad_y * 2
        draw.rounded_rectangle([tx, ty, rx1, ry1], radius=10, fill=TAG_BG)
        draw.text((tx + pad_x, ty + pad_y), tag, font=font_tag, fill=TAG_TXT)
        tx = rx1 + 20

    # ---- 右エリア：AIアイコン装飾 ----
    rx = W - 520
    ry = H // 2

    # 大きな円（背景）
    draw.ellipse([rx - 240, ry - 240, rx + 240, ry + 240], fill=(WHITE[0], WHITE[1], WHITE[2], 180))
    draw.ellipse([rx - 235, ry - 235, rx + 235, ry + 235], outline=ACCENT, width=6)

    # 内側の装飾円
    draw.ellipse([rx - 160, ry - 160, rx + 160, ry + 160], outline=(ACCENT[0], ACCENT[1], ACCENT[2], 80), width=3)

    # 「AI」文字
    font_ai_big  = ImageFont.truetype(FONT_B, 130)
    font_ai_sub  = ImageFont.truetype(FONT_M, 44)
    ai_text = "AI"
    bbox = draw.textbbox((0, 0), ai_text, font=font_ai_big)
    tw = bbox[2] - bbox[0]
    draw.text((rx - tw // 2, ry - 100), ai_text, font=font_ai_big, fill=ACCENT)

    sub_text = "活用サポート"
    bbox2 = draw.textbbox((0, 0), sub_text, font=font_ai_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((rx - tw2 // 2, ry + 58), sub_text, font=font_ai_sub, fill=MID)

    # ---- 下部：一言メッセージ ----
    draw.text((px, H - 110), '▶  まずはお気軽にご相談ください', font=font_label, fill=MID)

    out_path = os.path.join(OUTPUT_DIR, "プロフィールカバー画像.png")
    img.save(out_path)
    print(f"完了: {out_path}")


generate()
