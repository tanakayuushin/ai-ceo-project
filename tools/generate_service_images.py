from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\departments\sales\ококоナラ準備\サービス説明画像"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1280, 960
FONT_B = "C:/Windows/Fonts/YuGothB.ttc"
FONT_M = "C:/Windows/Fonts/YuGothM.ttc"
if not os.path.exists(FONT_B):
    FONT_B = FONT_M

WHITE = (255, 255, 255)
LIGHT = (210, 225, 245)

SERVICES = [
    {
        "short": "01",
        "name": "AI活用相談",
        "grad_top": (10, 20, 60),
        "grad_bottom": (20, 50, 120),
        "accent": (80, 160, 255),
        "targets": [
            "ChatGPTを試したが使いこなせていない方",
            "業務のどこにAIを使えるか知りたい方",
            "AI初心者でまず誰かに相談したい方",
            "難しい説明なしに実用的なアドバイスが欲しい方",
            "専門用語なしで丁寧に教えてほしい方",
        ],
        "contents": [
            "ヒアリング（お悩み・業務内容の確認）",
            "ChatGPT等の使い方・活用アドバイス",
            "業務へのAI活用箇所の提案",
            "参考ツール・使い方のご案内",
            "プロンプト改善アドバイス",
        ],
        "flow": [
            ("購入", "サービスをご購入ください"),
            ("ヒアリング", "お悩みをメッセージでお知らせください"),
            ("アドバイス提案", "具体的な活用法をご提案します"),
            ("追加対応", "ご不明点があれば追加でお答えします"),
            ("取引完了", "ご評価いただけると大変励みになります"),
        ],
        "faq": [
            ("Q. 初心者でも大丈夫ですか？", "A. はい、専門用語なしで丁寧に対応します"),
            ("Q. どんな業種でも対応できますか？", "A. 基本OK。法律・医療判断が必要な内容は対応不可"),
            ("Q. 電話での相談はできますか？", "A. 現在テキストのみです。今後追加予定"),
            ("Q. 情報が外に漏れることはありますか？", "A. トークルーム内で厳重管理、外部開示は一切なし"),
        ],
        "price": "モニター価格 2,000円",
        "delivery": "納期 2日",
    },
    {
        "short": "02",
        "name": "AI活用アイデア出しレポート",
        "grad_top": (10, 45, 40),
        "grad_bottom": (15, 80, 100),
        "accent": (60, 200, 160),
        "targets": [
            "会社・個人事業の業務にAIを導入したい方",
            "AI化の可能性がどこにあるか整理したい方",
            "自分では気づけない効率化のヒントが欲しい方",
            "「何から手をつければいいか」を知りたい方",
            "実務に直結した提案が欲しい経営者・事業主",
        ],
        "contents": [
            "ヒアリングシートを送付（記入15〜30分）",
            "業務フローの整理・AI活用箇所を分析",
            "AI効率化できる業務を5〜10項目リストアップ",
            "各項目に具体的なツール・活用方法をご提案",
            "優先順位・取り組み難易度の目安付きで納品",
        ],
        "flow": [
            ("購入", "サービスをご購入ください"),
            ("ヒアリングシート", "業務内容を記入して返送してください"),
            ("分析・作成", "AIで使える箇所を調査・整理します"),
            ("レポート納品", "優先順位付きレポートをお届けします"),
            ("取引完了", "ご評価いただけると大変励みになります"),
        ],
        "faq": [
            ("Q. 業務が複雑でも大丈夫ですか？", "A. はい、ヒアリングで丁寧に確認します"),
            ("Q. 個人事業主でも依頼できますか？", "A. はい、小規模事業者を得意としています"),
            ("Q. レポートはどんな形式ですか？", "A. テキスト・箇条書きでチャット内に納品します"),
            ("Q. ヒアリングが難しい場合は？", "A. 空欄でもOK。チャットで補足確認します"),
        ],
        "price": "モニター価格 5,000円",
        "delivery": "納期 5日",
    },
    {
        "short": "03",
        "name": "ChatGPTプロンプト作成",
        "grad_top": (40, 10, 70),
        "grad_bottom": (80, 20, 120),
        "accent": (180, 100, 255),
        "targets": [
            "毎日繰り返す作業をChatGPTで効率化したい方",
            "ChatGPTを使っているがうまく使えていない方",
            "プロンプト作成に時間をかけたくない方",
            "文章作成・メール・報告書をAI化したい方",
            "業務専用のオーダーメイドプロンプトが欲しい方",
        ],
        "contents": [
            "ヒアリング（業務内容・使いたい場面を確認）",
            "業務専用プロンプトを 3本 作成・納品",
            "各プロンプトに使い方の説明を付属",
            "納品後 1回まで修正対応",
            "無料版・Plus版どちらにも対応可",
        ],
        "flow": [
            ("購入", "サービスをご購入ください"),
            ("ヒアリング", "業務内容・用途をお知らせください"),
            ("プロンプト作成", "3本をオーダーメイドで作成します"),
            ("納品", "使い方説明付きでお届けします"),
            ("修正対応", "1回まで無料で修正対応します"),
        ],
        "faq": [
            ("Q. 無料版でも使えますか？", "A. はい、基本は無料版対応。Plusではより高精度"),
            ("Q. 3本は少なくないですか？", "A. 数より質を重視。追加はオプションで対応可"),
            ("Q. うまく動かない場合は？", "A. 納品後7日以内に1回修正対応します"),
            ("Q. 商用利用できますか？", "A. 可。ただしプロンプト自体の転売・配布は不可"),
        ],
        "price": "モニター価格 8,000円",
        "delivery": "納期 5日",
    },
]


def make_gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        r = int(top[0] + (bottom[0] - top[0]) * y / h)
        g = int(top[1] + (bottom[1] - top[1]) * y / h)
        b = int(top[2] + (bottom[2] - top[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def new_canvas(svc):
    img = make_gradient(W, H, svc["grad_top"], svc["grad_bottom"])
    draw = ImageDraw.Draw(img, "RGBA")
    acc = svc["accent"]
    draw.rectangle([0, 0, W, 8], fill=acc)
    for i, (dx, dy) in enumerate([(W-80,60),(W-130,60),(W-80,110),(W-130,110),(W-180,60)]):
        a = 110 if i % 2 == 0 else 60
        draw.ellipse([dx-7, dy-7, dx+7, dy+7], fill=(*acc, a))
    return img, draw


def draw_badge(draw, x, y, text, font, acc, alpha=200):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    px, py = 22, 11
    draw.rounded_rectangle([x, y, x+tw+px*2, y+th+py*2], radius=6, fill=(*acc, alpha))
    draw.text((x+px, y+py), text, font=font, fill=WHITE)
    return y + th + py*2 + 14


def draw_section_header(draw, y, title, font_title, acc, px=80):
    draw.text((px, y), title, font=font_title, fill=WHITE)
    bbox = draw.textbbox((px, y), title, font=font_title)
    ny = bbox[3] + 14
    draw.rectangle([px, ny, px+100, ny+5], fill=acc)
    return ny + 30


# ===== IMAGE 1: こんな方におすすめ =====
def gen_target(svc):
    img, draw = new_canvas(svc)
    acc = svc["accent"]

    font_tag   = ImageFont.truetype(FONT_B, 30)
    font_title = ImageFont.truetype(FONT_B, 68)
    font_item  = ImageFont.truetype(FONT_M, 36)
    font_sub   = ImageFont.truetype(FONT_M, 32)

    px = 80
    y = 30
    y = draw_badge(draw, px, y, svc["name"], font_tag, acc)
    y = draw_section_header(draw, y, "こんな方におすすめ", font_title, acc)
    y += 10

    for item in svc["targets"]:
        cy = y + 20
        draw.ellipse([px, y, px+40, y+40], fill=(*acc, 220))
        # Checkmark
        draw.line([(px+8, cy+3), (px+16, cy+10), (px+32, cy-6)], fill=WHITE, width=3)
        draw.text((px+54, y+4), item, font=font_item, fill=WHITE)
        y += 62

    y += 24
    draw.rectangle([px, y, W-px, y+2], fill=(*acc, 80))
    y += 20
    draw.text((px, y), f"{svc['price']}  /  {svc['delivery']}", font=font_sub, fill=acc)

    path = os.path.join(OUTPUT_DIR, f"{svc['short']}_01_おすすめ対象.png")
    img.save(path)
    print(f"生成: {os.path.basename(path)}")


# ===== IMAGE 2: 提供内容 =====
def gen_content(svc):
    img, draw = new_canvas(svc)
    acc = svc["accent"]

    font_tag   = ImageFont.truetype(FONT_B, 30)
    font_title = ImageFont.truetype(FONT_B, 68)
    font_item  = ImageFont.truetype(FONT_M, 36)
    font_num   = ImageFont.truetype(FONT_B, 26)
    font_sub   = ImageFont.truetype(FONT_M, 30)

    px = 80
    y = 30
    y = draw_badge(draw, px, y, svc["name"], font_tag, acc)
    y = draw_section_header(draw, y, "提供内容", font_title, acc)
    y += 10

    for i, item in enumerate(svc["contents"], 1):
        cy = y + 26
        cx = px + 26
        draw.ellipse([px, y, px+52, y+52], fill=acc)
        num = str(i)
        nb = draw.textbbox((0,0), num, font=font_num)
        nw, nh = nb[2]-nb[0], nb[3]-nb[1]
        draw.text((cx - nw//2, cy - nh//2), num, font=font_num, fill=WHITE)
        draw.text((px+66, y+10), item, font=font_item, fill=WHITE)
        y += 66

    y += 16
    draw.rectangle([px, y, W-px, y+2], fill=(*acc, 80))
    y += 18
    draw.text((px, y), f"{svc['price']}  |  {svc['delivery']}", font=font_sub, fill=LIGHT)

    path = os.path.join(OUTPUT_DIR, f"{svc['short']}_02_提供内容.png")
    img.save(path)
    print(f"生成: {os.path.basename(path)}")


# ===== IMAGE 3: 購入の流れ =====
def gen_flow(svc):
    img, draw = new_canvas(svc)
    acc = svc["accent"]

    font_tag   = ImageFont.truetype(FONT_B, 30)
    font_title = ImageFont.truetype(FONT_B, 68)
    font_step  = ImageFont.truetype(FONT_B, 34)
    font_desc  = ImageFont.truetype(FONT_M, 26)
    font_num   = ImageFont.truetype(FONT_B, 26)
    font_note  = ImageFont.truetype(FONT_M, 26)

    px = 80
    y = 30
    y = draw_badge(draw, px, y, svc["name"], font_tag, acc)
    y = draw_section_header(draw, y, "購入の流れ", font_title, acc)
    y += 10

    ccx = px + 36
    step_h = 122
    prev_cy = None

    for i, (step_name, step_desc) in enumerate(svc["flow"]):
        cy = y + 36

        # Vertical connector from previous circle
        if prev_cy is not None:
            draw.line([(ccx, prev_cy + 36), (ccx, cy - 36)], fill=(*acc, 120), width=3)

        # Step circle
        draw.ellipse([ccx-36, cy-36, ccx+36, cy+36], fill=acc)
        num = str(i + 1)
        nb = draw.textbbox((0,0), num, font=font_num)
        nw, nh = nb[2]-nb[0], nb[3]-nb[1]
        draw.text((ccx - nw//2, cy - nh//2), num, font=font_num, fill=WHITE)

        # Step name box
        bx = ccx + 56
        sb = draw.textbbox((0,0), step_name, font=font_step)
        sw, sh = sb[2]-sb[0], sb[3]-sb[1]
        by = cy - sh//2 - 10
        draw.rounded_rectangle([bx, by, bx+sw+28, by+sh+20], radius=8, fill=(*acc, 55))
        draw.rounded_rectangle([bx, by, bx+sw+28, by+sh+20], radius=8, outline=(*acc, 160), width=1)
        draw.text((bx+14, by+10), step_name, font=font_step, fill=WHITE)

        # Description
        draw.text((bx+4, by+sh+28), step_desc, font=font_desc, fill=LIGHT)

        prev_cy = cy
        y += step_h

    # Footer note
    y += 4
    note = "ご不明な点はお気軽にメッセージください。返信は1時間以内を目標にしています。"
    nb = draw.textbbox((0,0), note, font=font_note)
    nw = nb[2]-nb[0]
    draw.text((W//2 - nw//2, y), note, font=font_note, fill=(*acc, 200))

    path = os.path.join(OUTPUT_DIR, f"{svc['short']}_03_購入の流れ.png")
    img.save(path)
    print(f"生成: {os.path.basename(path)}")


# ===== IMAGE 4: よくある質問 =====
def gen_faq(svc):
    img, draw = new_canvas(svc)
    acc = svc["accent"]

    font_tag   = ImageFont.truetype(FONT_B, 30)
    font_title = ImageFont.truetype(FONT_B, 68)
    font_q     = ImageFont.truetype(FONT_B, 30)
    font_a     = ImageFont.truetype(FONT_M, 28)
    font_sub   = ImageFont.truetype(FONT_M, 26)

    px = 80
    y = 30
    y = draw_badge(draw, px, y, svc["name"], font_tag, acc)
    y = draw_section_header(draw, y, "よくある質問", font_title, acc)
    y += 10

    for q_text, a_text in svc["faq"]:
        # Q badge
        qb = draw.textbbox((0,0), q_text, font=font_q)
        qw, qh = qb[2]-qb[0], qb[3]-qb[1]
        draw.rounded_rectangle([px, y, px+qw+32, y+qh+18], radius=6, fill=(*acc, 185))
        draw.text((px+16, y+9), q_text, font=font_q, fill=WHITE)
        y += qh + 18 + 12

        # A text
        draw.text((px+16, y), a_text, font=font_a, fill=LIGHT)
        ab = draw.textbbox((px+16, y), a_text, font=font_a)
        y = ab[3] + 28

    # Bottom note
    y += 8
    note = f"{svc['price']}  |  {svc['delivery']}  |  返信1時間以内を目標"
    nb = draw.textbbox((0,0), note, font=font_sub)
    nw = nb[2]-nb[0]
    draw.text((W//2 - nw//2, y), note, font=font_sub, fill=(*acc, 200))

    path = os.path.join(OUTPUT_DIR, f"{svc['short']}_04_よくある質問.png")
    img.save(path)
    print(f"生成: {os.path.basename(path)}")


# ===== 実行 =====
print("サービス説明画像を生成中...\n")
for svc in SERVICES:
    print(f"--- {svc['name']} ---")
    gen_target(svc)
    gen_content(svc)
    gen_flow(svc)
    gen_faq(svc)
    print()

print(f"完了: {OUTPUT_DIR}")
