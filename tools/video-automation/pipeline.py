"""
DeskLab 動画自動生成パイプライン
----------------------------------
1. products.json から商品情報を読み込む
2. Claude API でTikTok用スクリプトを生成
3. HeyGen API でアバター動画を生成
4. Kling AI API で商品映像を生成
5. moviepy で動画を結合・テキスト挿入・BGM追加
6. output/ フォルダに保存
7. LINE Notifyで完了通知を送る

使い方:
  python pipeline.py                    # 全商品を処理
  python pipeline.py --product 001      # 特定商品のみ
  python pipeline.py --script-only      # スクリプト生成のみ（API節約）
"""

import os
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# ---- 設定 -------------------------------------------------------
BASE_DIR    = Path(__file__).parent
PRODUCTS_FILE = BASE_DIR / "products.json"
OUTPUT_DIR  = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HEYGEN_API_KEY    = os.environ.get("HEYGEN_API_KEY", "")
KLING_API_KEY     = os.environ.get("KLING_API_KEY", "")
KLING_API_SECRET  = os.environ.get("KLING_API_SECRET", "")
LINE_NOTIFY_TOKEN = os.environ.get("LINE_NOTIFY_TOKEN", "")

HEYGEN_AVATAR_ID  = os.environ.get("HEYGEN_AVATAR_ID", "")   # HeyGenダッシュボードで確認
HEYGEN_VOICE_ID   = os.environ.get("HEYGEN_VOICE_ID", "")    # 日本語音声のID

OUTPUT_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)
# -----------------------------------------------------------------


def load_products() -> list[dict]:
    with open(PRODUCTS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data["products"]


# ---- STEP 1: スクリプト生成（Claude API） -----------------------

def generate_script(product: dict) -> str:
    print(f"  [Claude] スクリプト生成中: {product['name']}")
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    prompt = f"""
DeskLab（デスク系雑貨のネット通販ショップ）の商品紹介TikTok動画用スクリプトを作ってください。

商品名: {product['name']}
価格: ¥{product['price']:,}
説明: {product['description']}
セールスポイント:
{chr(10).join(f'- {p}' for p in product['selling_points'])}

条件:
- 30秒・日本語・縦型動画（TikTok/Instagram用）
- ターゲット: 20代男性学生・社会人
- 最初の3秒で強いフック（疑問形や共感ワード）
- セールスポイントを2点紹介
- 最後にDeskLabで購入できる旨を伝える
- 1文ずつ改行して読みやすく
- 読み上げ時間が30秒になるよう文字数を調整

スクリプトのみを出力してください（説明文不要）。
"""
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}],
    }
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=body,
        timeout=30,
    )
    res.raise_for_status()
    script = res.json()["content"][0]["text"].strip()
    print(f"  [Claude] 完了 ({len(script)}文字)")
    return script


def save_script(product_id: str, script: str) -> Path:
    date_str = datetime.now().strftime("%Y%m%d")
    path = SCRIPTS_DIR / f"{date_str}_{product_id}.txt"
    path.write_text(script, encoding="utf-8")
    print(f"  [Script] 保存: {path.name}")
    return path


# ---- STEP 2: HeyGen アバター動画生成 ----------------------------

def generate_avatar_video(script: str, product_id: str) -> str | None:
    """
    HeyGen API でアバター動画を生成し、video_id を返す。
    Creator プラン以上が必要（$29/月）。
    """
    print(f"  [HeyGen] アバター動画生成リクエスト送信中...")
    if not HEYGEN_API_KEY:
        print("  [HeyGen] ⚠ HEYGEN_API_KEY が未設定。スキップします。")
        return None

    url = "https://api.heygen.com/v2/video/generate"
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": HEYGEN_AVATAR_ID,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": HEYGEN_VOICE_ID,
                    "speed": 1.0,
                },
                "background": {
                    "type": "color",
                    "value": "#FFFFFF",
                },
            }
        ],
        "dimension": {"width": 1080, "height": 1920},
        "aspect_ratio": "9:16",
    }
    res = requests.post(url, headers=headers, json=body, timeout=30)
    res.raise_for_status()
    video_id = res.json()["data"]["video_id"]
    print(f"  [HeyGen] video_id: {video_id}")
    return video_id


def wait_and_download_heygen(video_id: str, product_id: str) -> Path | None:
    """HeyGen の動画生成完了を待ってダウンロードする（最大10分）"""
    if not video_id:
        return None
    print(f"  [HeyGen] 生成完了を待機中...")
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {"X-Api-Key": HEYGEN_API_KEY}

    for _ in range(60):
        time.sleep(10)
        res = requests.get(url, headers=headers, timeout=15)
        status = res.json()["data"]["status"]
        print(f"  [HeyGen] status: {status}")
        if status == "completed":
            video_url = res.json()["data"]["video_url"]
            out_path = OUTPUT_DIR / f"{product_id}_avatar.mp4"
            _download_file(video_url, out_path)
            print(f"  [HeyGen] ダウンロード完了: {out_path.name}")
            return out_path
        if status == "failed":
            print("  [HeyGen] ❌ 生成失敗")
            return None
    print("  [HeyGen] ⚠ タイムアウト（10分）")
    return None


# ---- STEP 3: Kling AI 商品映像生成 ------------------------------

def generate_product_footage(product: dict) -> str | None:
    """Kling AI API で商品映像を生成し、task_id を返す"""
    print(f"  [Kling] 商品映像生成リクエスト送信中...")
    if not KLING_API_KEY:
        print("  [Kling] ⚠ KLING_API_KEY が未設定。スキップします。")
        return None

    url = "https://api.klingai.com/v1/videos/text2video"
    headers = {
        "Authorization": f"Bearer {KLING_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model_name": "kling-v1-6",
        "prompt": product["image_prompt_en"],
        "negative_prompt": "blurry, low quality, watermark",
        "cfg_scale": 0.5,
        "mode": "std",
        "aspect_ratio": "9:16",
        "duration": "5",
    }
    res = requests.post(url, headers=headers, json=body, timeout=30)
    res.raise_for_status()
    task_id = res.json()["data"]["task_id"]
    print(f"  [Kling] task_id: {task_id}")
    return task_id


def wait_and_download_kling(task_id: str, product_id: str) -> Path | None:
    """Kling の動画生成完了を待ってダウンロードする（最大15分）"""
    if not task_id:
        return None
    print(f"  [Kling] 生成完了を待機中...")
    url = f"https://api.klingai.com/v1/videos/text2video/{task_id}"
    headers = {"Authorization": f"Bearer {KLING_API_KEY}"}

    for _ in range(90):
        time.sleep(10)
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()["data"]
        status = data["task_status"]
        print(f"  [Kling] status: {status}")
        if status == "succeed":
            video_url = data["task_result"]["videos"][0]["url"]
            out_path = OUTPUT_DIR / f"{product_id}_product.mp4"
            _download_file(video_url, out_path)
            print(f"  [Kling] ダウンロード完了: {out_path.name}")
            return out_path
        if status == "failed":
            print("  [Kling] ❌ 生成失敗")
            return None
    print("  [Kling] ⚠ タイムアウト（15分）")
    return None


# ---- STEP 4: 動画結合（moviepy） --------------------------------

def combine_videos(
    product: dict,
    avatar_path: Path | None,
    footage_path: Path | None,
    product_id: str,
) -> Path | None:
    """
    構成: [商品映像3秒] → [アバター紹介20秒] → [商品映像7秒]
    テキストオーバーレイ・BGMを追加して最終動画を書き出す
    """
    try:
        from moviepy.editor import (
            VideoFileClip, concatenate_videoclips,
            TextClip, CompositeVideoClip, AudioFileClip
        )
    except ImportError:
        print("  [編集] ⚠ moviepy が未インストール。結合をスキップします。")
        print("  [編集] → pip install moviepy で導入してください。")
        return None

    if not avatar_path or not footage_path:
        print("  [編集] ⚠ 素材が不足しているため結合をスキップ。")
        return None

    print(f"  [編集] 動画結合開始...")

    footage = VideoFileClip(str(footage_path)).resize((1080, 1920))
    avatar  = VideoFileClip(str(avatar_path)).resize((1080, 1920))

    hook_clip    = footage.subclip(0, min(3, footage.duration))
    avatar_clip  = avatar.subclip(0, min(20, avatar.duration))
    product_clip = footage.subclip(0, min(7, footage.duration))

    # テキストオーバーレイ
    hook_text = TextClip(
        f"デスクが散らかってない？",
        fontsize=60, color="white", stroke_color="black", stroke_width=3,
        font="Noto-Sans-CJK-JP-Bold",
        size=(1000, None), method="caption",
    ).set_position(("center", 80)).set_duration(3)

    price_text = TextClip(
        f"{product['name']}\n¥{product['price']:,}",
        fontsize=50, color="white", stroke_color="black", stroke_width=2,
        font="Noto-Sans-CJK-JP-Bold",
        size=(1000, None), method="caption",
    ).set_position(("center", 1700)).set_duration(7)

    cta_text = TextClip(
        "DeskLabで購入 → プロフのリンクから",
        fontsize=44, color="yellow", stroke_color="black", stroke_width=2,
        font="Noto-Sans-CJK-JP-Bold",
        size=(1000, None), method="caption",
    ).set_position(("center", 1750)).set_duration(7)

    hook_scene    = CompositeVideoClip([hook_clip, hook_text])
    product_scene = CompositeVideoClip([product_clip, price_text, cta_text])

    final = concatenate_videoclips([hook_scene, avatar_clip, product_scene])

    date_str  = datetime.now().strftime("%Y%m%d")
    out_path  = OUTPUT_DIR / f"{date_str}_{product_id}_final.mp4"
    final.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac")
    print(f"  [編集] 完成: {out_path.name}")
    return out_path


# ---- STEP 5: LINE 通知 ------------------------------------------

def notify_line(message: str) -> None:
    if not LINE_NOTIFY_TOKEN:
        print("  [LINE] ⚠ LINE_NOTIFY_TOKEN 未設定。通知をスキップ。")
        return
    requests.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"},
        data={"message": message},
        timeout=10,
    )
    print("  [LINE] 通知送信完了")


# ---- ユーティリティ -----------------------------------------------

def _download_file(url: str, out_path: Path) -> None:
    res = requests.get(url, stream=True, timeout=60)
    res.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)


# ---- メイン処理 --------------------------------------------------

def run_pipeline(products: list[dict], script_only: bool = False) -> None:
    print(f"\n{'='*50}")
    print(f"DeskLab 動画生成パイプライン開始")
    print(f"対象商品: {len(products)}件 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")

    results = []

    for product in products:
        pid = product["id"]
        print(f"\n▶ {product['name']} ({pid})")

        # STEP 1: スクリプト生成
        script = generate_script(product)
        script_path = save_script(pid, script)

        if script_only:
            results.append({"id": pid, "name": product["name"], "script": str(script_path)})
            continue

        # STEP 2: HeyGen アバター動画
        video_id   = generate_avatar_video(script, pid)
        avatar_vid = wait_and_download_heygen(video_id, pid)

        # STEP 3: Kling 商品映像
        task_id     = generate_product_footage(product)
        footage_vid = wait_and_download_kling(task_id, pid)

        # STEP 4: 動画結合
        final_vid = combine_videos(product, avatar_vid, footage_vid, pid)

        results.append({
            "id": pid,
            "name": product["name"],
            "script": str(script_path),
            "avatar": str(avatar_vid) if avatar_vid else "スキップ",
            "footage": str(footage_vid) if footage_vid else "スキップ",
            "final": str(final_vid) if final_vid else "スキップ",
        })

    # サマリー表示
    print(f"\n{'='*50}")
    print("完了サマリー")
    print(f"{'='*50}")
    for r in results:
        status = "✅" if r.get("final") and r["final"] != "スキップ" else "📝"
        print(f"{status} {r['name']}")
        if "final" in r:
            print(f"   最終動画: {r['final']}")
        print(f"   スクリプト: {r['script']}")

    # LINE通知
    completed = [r for r in results if r.get("final") and r["final"] != "スキップ"]
    msg = f"\n✅ DeskLab動画生成完了\n{len(completed)}/{len(results)}本が完成\noutput/フォルダを確認してください"
    notify_line(msg)
    print(f"\n{'='*50}\n全処理完了\n{'='*50}")


def main():
    parser = argparse.ArgumentParser(description="DeskLab 動画生成パイプライン")
    parser.add_argument("--product", help="特定商品IDのみ処理 (例: product_001)")
    parser.add_argument("--script-only", action="store_true", help="スクリプト生成のみ")
    args = parser.parse_args()

    products = load_products()

    if args.product:
        products = [p for p in products if p["id"] == args.product]
        if not products:
            print(f"❌ 商品ID '{args.product}' が見つかりません。")
            return

    run_pipeline(products, script_only=args.script_only)


if __name__ == "__main__":
    main()
