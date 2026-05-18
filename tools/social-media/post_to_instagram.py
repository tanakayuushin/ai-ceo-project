#!/usr/bin/env python3
"""
Instagram自動投稿スクリプト (Meta Graph API 公式)

必要な環境変数:
  IG_USER_ID       Instagram Creator/Business アカウントのUser ID
  IG_ACCESS_TOKEN  長期アクセストークン（60日有効）
  IMGBB_API_KEY    画像ホスティング用 (imgbb.com 無料)

使い方:
  python post_to_instagram.py                          # pendingから自動選択
  python post_to_instagram.py --image img.jpg --caption "テキスト"
  python post_to_instagram.py --dry-run                # テスト実行
"""

import os
import sys
import json
import time
import base64
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

# ============================================================
# 設定
# ============================================================
IG_USER_ID     = os.environ.get("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IMGBB_API_KEY  = os.environ.get("IMGBB_API_KEY", "")

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"
PENDING_DIR    = Path(__file__).parent.parent.parent / "departments" / "marketing" / "instagram-posts" / "pending"
POSTED_DIR     = Path(__file__).parent.parent.parent / "departments" / "marketing" / "instagram-posts" / "posted"

# ============================================================
# 画像ホスティング (imgbb.com)
# ============================================================
def upload_image(image_path: str) -> str:
    """画像をimgbbにアップロードして公開URLを返す"""
    if not IMGBB_API_KEY:
        raise ValueError("IMGBB_API_KEY が設定されていません\n"
                         "https://imgbb.com/signup から無料取得してください")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    data = urllib.parse.urlencode({
        "key": IMGBB_API_KEY,
        "image": image_b64,
    }).encode("utf-8")

    req = urllib.request.Request("https://api.imgbb.com/1/upload", data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as res:
        result = json.loads(res.read().decode("utf-8"))

    if not result.get("success"):
        raise RuntimeError(f"imgbbアップロード失敗: {result}")

    url = result["data"]["url"]
    print(f"  📤 画像URL: {url}")
    return url

# ============================================================
# Instagram Graph API
# ============================================================
def _api_post(path: str, params: dict) -> dict:
    params["access_token"] = IG_ACCESS_TOKEN
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(f"{GRAPH_API_BASE}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"API エラー {e.code}: {body}")

def _api_get(path: str) -> dict:
    url = f"{GRAPH_API_BASE}/{path}&access_token={IG_ACCESS_TOKEN}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))

def create_container(image_url: str, caption: str) -> str:
    """ステップ1: メディアコンテナを作成"""
    result = _api_post(f"{IG_USER_ID}/media", {
        "image_url": image_url,
        "caption": caption,
    })
    if "id" not in result:
        raise RuntimeError(f"コンテナ作成失敗: {result}")
    return result["id"]

def wait_ready(creation_id: str, max_wait: int = 120):
    """コンテナがFINISHED状態になるまで最大2分待機"""
    for _ in range(max_wait // 5):
        result = _api_get(f"{creation_id}?fields=status_code,status")
        status = result.get("status_code", "")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"コンテナエラー: {result}")
        print(f"  ⏳ 処理中 ({status})...")
        time.sleep(5)
    raise TimeoutError("コンテナのready待機がタイムアウト（2分）しました")

def publish_container(creation_id: str) -> str:
    """ステップ2: コンテナを公開"""
    result = _api_post(f"{IG_USER_ID}/media_publish", {
        "creation_id": creation_id,
    })
    if "id" not in result:
        raise RuntimeError(f"公開失敗: {result}")
    return result["id"]

# ============================================================
# メイン処理
# ============================================================
def post_to_instagram(image_path: str, caption: str, dry_run: bool = False) -> str:
    """Instagram投稿のフルフロー"""
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        raise ValueError(
            "IG_USER_ID と IG_ACCESS_TOKEN が必要です\n"
            "セットアップ手順: docs/instagram-setup.md を参照"
        )

    print(f"\n📸 投稿画像: {Path(image_path).name}")
    print(f"📝 キャプション: {caption[:60]}{'...' if len(caption) > 60 else ''}")

    if dry_run:
        print("\n[DRY RUN] 実際には投稿しません ✓")
        return "dry-run"

    print("\n[1/4] 画像をアップロード中...")
    image_url = upload_image(image_path)

    print("[2/4] Instagramコンテナを作成中...")
    creation_id = create_container(image_url, caption)
    print(f"  Container ID: {creation_id}")

    print("[3/4] コンテナ処理完了を待機中...")
    wait_ready(creation_id)

    print("[4/4] 投稿を公開中...")
    post_id = publish_container(creation_id)

    return post_id

def find_pending() -> tuple[str, str]:
    """pendingフォルダから最初の画像+キャプションを取得"""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    images = sorted(list(PENDING_DIR.glob("*.jpg")) + list(PENDING_DIR.glob("*.png")))
    if not images:
        raise FileNotFoundError(
            f"pendingフォルダに画像がありません: {PENDING_DIR}\n"
            "YYYY-MM-DD_説明.jpg と YYYY-MM-DD_説明.txt を配置してください"
        )

    img = images[0]
    txt = img.with_suffix(".txt")
    caption = txt.read_text(encoding="utf-8").strip() if txt.exists() else img.stem.replace("-", " ").replace("_", " ")
    return str(img), caption

def archive(image_path: str):
    """投稿済みファイルをpostedフォルダに移動"""
    POSTED_DIR.mkdir(parents=True, exist_ok=True)
    img = Path(image_path)
    img.rename(POSTED_DIR / img.name)
    txt = img.with_suffix(".txt")
    if txt.exists():
        txt.rename(POSTED_DIR / txt.name)
    print(f"✅ アーカイブ完了: posted/{img.name}")

def write_log(image_path: str, post_id: str, caption: str):
    """投稿ログをMarkdownで保存"""
    log_dir = PENDING_DIR.parent
    log_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{date}.md"

    content = f"""# Instagram投稿 {date}

## 投稿画像
{Path(image_path).name}

## キャプション
{caption}

---

**投稿結果**: 成功（Post ID: {post_id}）
"""
    log_file.write_text(content, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Instagram自動投稿 (Meta Graph API)")
    parser.add_argument("--image", help="投稿する画像ファイルパス")
    parser.add_argument("--caption", help="キャプション（省略時は .txt ファイルから取得）")
    parser.add_argument("--dry-run", action="store_true", help="テスト実行（投稿しない）")
    args = parser.parse_args()

    if args.image:
        image_path = args.image
        caption = args.caption or Path(args.image).stem
        from_pending = False
    else:
        image_path, caption = find_pending()
        from_pending = True

    post_id = post_to_instagram(image_path, caption, dry_run=args.dry_run)

    if post_id != "dry-run":
        print(f"\n✅ Instagram投稿成功！ Post ID: {post_id}")
        if from_pending:
            archive(image_path)
            write_log(image_path, post_id, caption)

if __name__ == "__main__":
    main()
