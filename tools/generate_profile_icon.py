from PIL import Image, ImageDraw
import os

OUTPUT_DIR = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\departments\sales\ококоナラ準備"
SIZE = 400


def make_gradient_bg(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(top[0] + (bottom[0] - top[0]) * y / h)
        g = int(top[1] + (bottom[1] - top[1]) * y / h)
        b = int(top[2] + (bottom[2] - top[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def generate():
    # 明るいグラデーション背景（ライトブルー → 水色）
    img = make_gradient_bg(SIZE, SIZE, (220, 235, 255), (175, 210, 250))
    draw = ImageDraw.Draw(img, "RGBA")

    cx = SIZE // 2

    SKIN    = (252, 220, 185)
    SKIN_S  = (235, 195, 158)   # 影
    HAIR    = (38, 26, 14)
    WHITE   = (255, 255, 255)
    EYE_BG  = (255, 255, 255)
    IRIS    = (48, 80, 160)     # 青い瞳（アニメ風）
    PUPIL   = (20, 14, 8)
    SHIRT   = (255, 255, 255)   # 白シャツ
    COLLAR  = (230, 238, 255)
    NECK    = SKIN

    # ---- 影（地面・首まわり） ----
    draw.ellipse([cx - 75, 318, cx + 75, 345], fill=(160, 190, 230, 120))

    # ---- 服（白シャツ）----
    draw.ellipse([cx - 95, 295, cx + 95, 430], fill=SHIRT)
    draw.rectangle([cx - 95, 330, cx + 95, 430], fill=SHIRT)
    # 襟
    draw.polygon([
        (cx, 295), (cx - 30, 328), (cx - 12, 320),
        (cx, 312), (cx + 12, 320), (cx + 30, 328),
    ], fill=COLLAR)
    # シャツのライン（縫い目）
    draw.line([(cx, 312), (cx, 400)], fill=(200, 215, 240), width=2)

    # ---- 首 ----
    draw.rounded_rectangle([cx - 18, 262, cx + 18, 302], radius=9, fill=NECK)
    # 首の影
    draw.rounded_rectangle([cx - 18, 262, cx - 10, 302], radius=5, fill=SKIN_S)

    # ---- 耳 ----
    draw.ellipse([cx - 102, 192, cx - 80, 226], fill=SKIN)
    draw.ellipse([cx + 80,  192, cx + 102, 226], fill=SKIN)
    draw.ellipse([cx - 99,  196, cx - 83, 222], fill=SKIN_S)
    draw.ellipse([cx + 83,  196, cx + 99, 222], fill=SKIN_S)

    # ---- 顔（輪郭） ----
    # 輪郭の影（奥行き感）
    draw.ellipse([cx - 81, 132, cx + 83, 272], fill=SKIN_S)
    # 顔本体
    draw.ellipse([cx - 83, 130, cx + 83, 270], fill=SKIN)

    # ---- 髪（アニメ風ショート）----
    # 頭全体のベース
    draw.ellipse([cx - 83, 80, cx + 83, 195], fill=HAIR)
    # 前髪の下端を決める（額を作る）
    draw.ellipse([cx - 78, 148, cx + 78, 270], fill=SKIN)
    draw.rectangle([cx - 78, 165, cx + 78, 195], fill=SKIN)

    # 前髪の形（アニメ風：センター分け気味）
    # 右流れの前髪
    draw.polygon([
        (cx - 20, 165), (cx + 5, 172), (cx + 32, 168),
        (cx + 45, 155), (cx + 20, 143), (cx - 5, 148),
    ], fill=HAIR)
    # 左サイドの前髪
    draw.polygon([
        (cx - 55, 155), (cx - 30, 163), (cx - 15, 165),
        (cx - 10, 152), (cx - 35, 142), (cx - 60, 148),
    ], fill=HAIR)

    # ---- 眉毛（アニメ風・やや太め・表情豊か） ----
    # 左眉
    draw.polygon([
        (cx - 60, 194), (cx - 26, 190),
        (cx - 26, 195), (cx - 60, 199),
    ], fill=HAIR)
    # 右眉
    draw.polygon([
        (cx + 26, 190), (cx + 60, 194),
        (cx + 60, 199), (cx + 26, 195),
    ], fill=HAIR)

    # ---- 目（アニメ風・大きめ） ----
    # 目の外枠（黒）
    draw.ellipse([cx - 62, 206, cx - 24, 234], fill=HAIR)
    draw.ellipse([cx + 24, 206, cx + 62, 234], fill=HAIR)
    # 白目
    draw.ellipse([cx - 61, 207, cx - 25, 233], fill=EYE_BG)
    draw.ellipse([cx + 25, 207, cx + 61, 233], fill=EYE_BG)
    # 虹彩（青）
    draw.ellipse([cx - 55, 209, cx - 31, 231], fill=IRIS)
    draw.ellipse([cx + 31, 209, cx + 55, 231], fill=IRIS)
    # 瞳孔
    draw.ellipse([cx - 48, 212, cx - 38, 228], fill=PUPIL)
    draw.ellipse([cx + 38, 212, cx + 48, 228], fill=PUPIL)
    # ハイライト（大）
    draw.ellipse([cx - 46, 212, cx - 40, 218], fill=WHITE)
    draw.ellipse([cx + 38, 212, cx + 44, 218], fill=WHITE)
    # ハイライト（小）
    draw.ellipse([cx - 41, 224, cx - 38, 227], fill=(220, 230, 255))
    draw.ellipse([cx + 40, 224, cx + 43, 227], fill=(220, 230, 255))
    # まつ毛（上）
    draw.arc([cx - 62, 206, cx - 24, 234], start=200, end=340, fill=HAIR, width=3)
    draw.arc([cx + 24, 206, cx + 62, 234], start=200, end=340, fill=HAIR, width=3)

    # ---- 鼻（シンプル・小さめ） ----
    draw.ellipse([cx - 5, 244, cx + 5, 252], fill=SKIN_S)

    # ---- 口（自然な笑顔） ----
    draw.arc([cx - 22, 256, cx + 22, 278], start=15, end=165, fill=(200, 110, 90), width=3)
    # 下唇のハイライト
    draw.ellipse([cx - 8, 271, cx + 8, 276], fill=(255, 200, 185, 150))

    # ---- ほほ ----
    draw.ellipse([cx - 68, 234, cx - 38, 252], fill=(255, 160, 140, 70))
    draw.ellipse([cx + 38, 234, cx + 68, 252], fill=(255, 160, 140, 70))

    # ---- 円形クロップ ----
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, SIZE, SIZE], fill=255)
    result = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    result.paste(img.convert("RGBA"), mask=mask)

    # 白い枠線
    border = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(border).ellipse(
        [2, 2, SIZE - 2, SIZE - 2],
        outline=(255, 255, 255, 230), width=5
    )
    result = Image.alpha_composite(result, border)

    out_path = os.path.join(OUTPUT_DIR, "プロフィール画像.png")
    result.save(out_path)
    print(f"完了: {out_path}")


generate()
