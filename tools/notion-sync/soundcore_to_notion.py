#!/usr/bin/env python3
"""
Soundcore文字起こし → Claude要約 → Notion自動保存システム

【フロー】
1. Soundcoreアプリで録音・文字起こし
2. テキストをエクスポート → 監視フォルダ (SOUNDCORE_INBOX) に保存
3. 本スクリプトが新ファイルを検出
4. Claude APIで要約・タイトル・アクション抽出
5. Notion APIで自動ページ作成（NOTION_PAGE_ID の子ページ）
6. 処理済みファイルをアーカイブフォルダへ移動

【.envに必要な設定】
ANTHROPIC_API_KEY=sk-ant-...
NOTION_TOKEN=secret_...
NOTION_PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  ← 保存先NotionページのID
SOUNDCORE_INBOX=C:\Users\tsube\OneDrive\Soundcore\inbox
"""

import os
import sys
import json
import time
import shutil
import urllib.request
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("watchdog が未インストールです。`pip install watchdog` を実行してください。")
    sys.exit(1)

# ── .env 読み込み ─────────────────────────────────────────────────────────

def load_env(env_path: Path):
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

_project_root = Path(__file__).parent.parent.parent
load_env(_project_root / ".env")

# ── 設定 ──────────────────────────────────────────────────────────────────

INBOX_DIR   = Path(os.environ.get(
    "SOUNDCORE_INBOX",
    r"C:\Users\tsube\OneDrive\Soundcore\inbox"
))
ARCHIVE_DIR = INBOX_DIR.parent / "archive"
SUPPORTED_EXT = {".txt", ".md"}

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
NOTION_TOKEN      = os.environ.get("NOTION_TOKEN", "")
NOTION_PAGE_ID    = os.environ.get("NOTION_PAGE_ID", "")

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE


# ── Claude API ────────────────────────────────────────────────────────────

def summarize_with_claude(transcript: str) -> dict:
    """Claude Haiku で要約・タイトル・アクション・キーワードを生成"""
    prompt = f"""以下はSoundcoreで録音・文字起こしされた音声テキストです。
ビジネスの記録として活用するために、以下のJSON形式で分析してください。

【テキスト】
{transcript[:8000]}

【出力形式（JSONのみ）】
{{
  "title": "内容を端的に表す20字以内のタイトル",
  "summary": "・箇条書きで3〜5行の要約（各行を・で始める）",
  "action_items": ["アクション1", "アクション2"],
  "keywords": ["キーワード1", "キーワード2", "キーワード3"],
  "category": "ミーティング・アイデア・日報・計画・その他 のいずれか"
}}"""

    body = json.dumps({
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "messages":   [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body, method="POST",
    )
    req.add_header("x-api-key",          ANTHROPIC_API_KEY)
    req.add_header("anthropic-version",  "2023-06-01")
    req.add_header("content-type",       "application/json")

    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            text = json.loads(r.read().decode())["content"][0]["text"]
            s, e = text.find("{"), text.rfind("}") + 1
            return json.loads(text[s:e])
    except Exception as ex:
        print(f"  Claude APIエラー: {ex}")
        return {
            "title": "録音メモ",
            "summary": transcript[:200],
            "action_items": [],
            "keywords": [],
            "category": "その他",
        }


# ── Notion API ────────────────────────────────────────────────────────────

def rich(text: str) -> list:
    """Notion rich_text ブロックを生成（2000字制限対応）"""
    chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    return [{"type": "text", "text": {"content": c}} for c in chunks]


def create_notion_page(transcript: str, analysis: dict, filename: str) -> str:
    """NOTION_PAGE_ID の子ページとして録音メモを作成"""
    now   = datetime.now()
    title = f"[{now.strftime('%Y-%m-%d %H:%M')}] {analysis['title']}"

    blocks = []

    # ── 要約 ──
    blocks.append({
        "object": "block", "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "📋"},
            "rich_text": rich(analysis.get("summary", "（要約なし）")),
            "color": "blue_background",
        },
    })

    # ── アクション ──
    if analysis.get("action_items"):
        blocks.append({
            "object": "block", "type": "heading_3",
            "heading_3": {"rich_text": rich("✅ アクション")},
        })
        for item in analysis["action_items"]:
            blocks.append({
                "object": "block", "type": "to_do",
                "to_do": {
                    "rich_text": rich(item),
                    "checked":   False,
                },
            })

    # ── キーワード ──
    if analysis.get("keywords"):
        kw_text = "　".join(f"#{k}" for k in analysis["keywords"])
        blocks.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": rich(kw_text), "color": "gray"},
        })

    # ── 区切り ──
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # ── 全文 ──
    blocks.append({
        "object": "block", "type": "heading_3",
        "heading_3": {"rich_text": rich("📝 全文テキスト")},
    })
    for i in range(0, len(transcript), 1900):
        blocks.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": rich(transcript[i:i+1900])},
        })

    page_data = {
        "parent":     {"page_id": NOTION_PAGE_ID},
        "icon":       {"type": "emoji", "emoji": "🎙️"},
        "properties": {
            "title": {"title": rich(title)},
        },
        "children": blocks[:100],
    }

    body = json.dumps(page_data, ensure_ascii=False).encode("utf-8")
    req  = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=body, method="POST",
    )
    req.add_header("Authorization",    f"Bearer {NOTION_TOKEN}")
    req.add_header("Notion-Version",   "2022-06-28")
    req.add_header("Content-Type",     "application/json")

    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            data = json.loads(r.read().decode())
            return data.get("url", "")
    except urllib.error.HTTPError as ex:
        print(f"  Notion APIエラー {ex.code}: {ex.read().decode()[:200]}")
        return ""


# ── ファイル処理 ──────────────────────────────────────────────────────────

def process_file(filepath: Path):
    if filepath.suffix.lower() not in SUPPORTED_EXT:
        return
    if not filepath.exists():
        return

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{ts}] 処理開始: {filepath.name}")

    try:
        transcript = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        transcript = filepath.read_text(encoding="shift_jis", errors="replace")

    if len(transcript.strip()) < 10:
        print("  スキップ: テキストが短すぎます")
        return

    print("  Claude で要約中...")
    analysis = summarize_with_claude(transcript)
    print(f"  タイトル : {analysis['title']}")
    print(f"  カテゴリ : {analysis.get('category', '?')}")
    print(f"  アクション: {len(analysis.get('action_items', []))}件")

    print("  Notion にページ作成中...")
    url = create_notion_page(transcript, analysis, filepath.name)
    if url:
        print(f"  ✅ 完了: {url}")
    else:
        print("  ❌ Notion保存失敗")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{filepath.name}"
    shutil.move(str(filepath), str(ARCHIVE_DIR / archive_name))
    print(f"  📁 → archive/{archive_name}")


# ── フォルダ監視 ──────────────────────────────────────────────────────────

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)
            process_file(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            time.sleep(1)
            process_file(Path(event.dest_path))


def main():
    missing = [k for k, v in {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "NOTION_TOKEN":      NOTION_TOKEN,
        "NOTION_PAGE_ID":    NOTION_PAGE_ID,
    }.items() if not v]

    if missing:
        print(f"エラー: .env に以下が未設定です: {', '.join(missing)}")
        sys.exit(1)

    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Soundcore → Notion 自動同期 起動 ===")
    print(f"監視フォルダ : {INBOX_DIR}")
    print(f"Notion保存先: ...{NOTION_PAGE_ID[-8:]}")
    print("Ctrl+C で終了\n")

    # 起動時に既存ファイルを処理
    for f in sorted(INBOX_DIR.glob("*")):
        if f.suffix.lower() in SUPPORTED_EXT:
            process_file(f)

    observer = Observer()
    observer.schedule(InboxHandler(), str(INBOX_DIR), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
