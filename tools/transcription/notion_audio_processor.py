# -*- coding: utf-8 -*-
"""
Soundcore Notion audio pipeline:
  child_page (per recording) -> file block (.ogg) -> Whisper -> Claude Haiku -> append summary to child page
Usage:
  python notion_audio_processor.py --test
  python notion_audio_processor.py
  python notion_audio_processor.py --watch
"""

import os
import sys
import json
import time
import argparse
import tempfile
import datetime
import requests
import urllib3
from pathlib import Path
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_PAGE_ID = os.environ.get("NOTION_PAGE_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

PROCESSED_FILE = Path(__file__).parent / ".processed_blocks.json"


def p(msg):
    print(msg, flush=True)


def load_processed():
    if PROCESSED_FILE.exists():
        return set(json.loads(PROCESSED_FILE.read_text(encoding="utf-8")))
    return set()


def save_processed(ids: set):
    PROCESSED_FILE.write_text(json.dumps(list(ids)), encoding="utf-8")


def notion_get(url):
    return requests.get(url, headers=NOTION_HEADERS, verify=False)


def notion_patch(url, data):
    return requests.patch(url, headers=NOTION_HEADERS, json=data, verify=False)


def notion_post(url, data):
    return requests.post(url, headers=NOTION_HEADERS, json=data, verify=False)


def test_connection():
    p(f"Notion page connection check... (ID: {NOTION_PAGE_ID})")
    r = notion_get(f"https://api.notion.com/v1/pages/{NOTION_PAGE_ID}")
    if r.status_code == 200:
        title = r.json().get("properties", {}).get("title", {}).get("title", [{}])
        name = title[0].get("plain_text", "(no title)") if title else "(no title)"
        p(f"[OK] Connected: {name}")
        return True
    else:
        p(f"[FAIL] {r.status_code} -- {r.text[:200]}")
        return False


def get_child_pages():
    """Get all child_page blocks at the top level."""
    pages = []
    cursor = None
    while True:
        url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        r = notion_get(url)
        if r.status_code != 200:
            p(f"[FAIL] {r.status_code}")
            return []
        data = r.json()
        for block in data.get("results", []):
            if block.get("type") == "child_page":
                pages.append(block)
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return pages


def get_file_block_in_page(page_id):
    """Find the first file block inside a child page."""
    r = notion_get(f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100")
    if r.status_code != 200:
        return None
    for block in r.json().get("results", []):
        if block.get("type") == "file":
            info = block.get("file", {})
            file_info = info.get("file") or info.get("external")
            if file_info and file_info.get("url"):
                return file_info["url"]
    return None


def download_audio(url):
    """Download audio from URL to temp file."""
    p(f"  Downloading audio...")
    r = requests.get(url, verify=False, timeout=60)
    if r.status_code != 200:
        p(f"  [FAIL] Download {r.status_code}")
        return None
    suffix = ".ogg"
    ct = r.headers.get("content-type", "")
    if "wav" in ct:
        suffix = ".wav"
    elif "mp3" in ct or "mpeg" in ct:
        suffix = ".mp3"
    elif "m4a" in ct or "mp4" in ct:
        suffix = ".m4a"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.close()
    p(f"  Saved: {tmp.name} ({len(r.content)//1024}KB)")
    return tmp.name


def transcribe(audio_path):
    """Local transcription with Whisper (free)."""
    try:
        import whisper
    except ImportError:
        p("  [WARN] whisper not installed. Run: pip install openai-whisper")
        return ""
    p("  Transcribing with Whisper (base model)...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="ja")
    text = result.get("text", "").strip()
    p(f"  Done: {len(text)} chars")
    return text


def summarize(transcript):
    """Summarize with Claude Haiku."""
    if not transcript:
        return "(文字起こし結果が空のため要約できませんでした)"
    p("  Summarizing with Claude Haiku...")
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": (
                "以下の音声文字起こしを日本語で3〜5行に要約してください。"
                "重要なポイントと決定事項があれば箇条書きにしてください。\n\n"
                + transcript[:3000]
            )}],
        },
        verify=False,
        timeout=30,
    )
    if r.status_code == 200:
        summary = r.json()["content"][0]["text"].strip()
        p(f"  Done: {len(summary)} chars")
        return summary
    else:
        p(f"  [WARN] Summary failed: {r.status_code}")
        return "(要約の生成に失敗しました)"


def append_to_page(page_id, transcript, summary):
    """Append transcription and summary blocks to existing child page."""

    def make_text_blocks(content, btype="paragraph"):
        lines = [content[i:i+1900] for i in range(0, len(content), 1900)]
        return [{"object": "block", "type": btype,
                 btype: {"rich_text": [{"type": "text", "text": {"content": line}}]}}
                for line in lines]

    children = (
        [{"object": "block", "type": "divider", "divider": {}}]
        + [{"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "要約"}}]}}]
        + make_text_blocks(summary)
        + [{"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "文字起こし（全文）"}}]}}]
        + make_text_blocks(transcript if transcript else "(文字起こし結果なし)")
    )

    r = notion_patch(
        f"https://api.notion.com/v1/blocks/{page_id}/children",
        {"children": children[:50]}
    )
    if r.status_code == 200:
        p(f"  [OK] Added to Notion page")
        return True
    else:
        p(f"  [FAIL] {r.status_code} -- {r.text[:300]}")
        return False


def process_once():
    p(f"\n{'='*50}")
    p(f"Run: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p("="*50)

    processed = load_processed()
    child_pages = get_child_pages()
    p(f"Found {len(child_pages)} child page(s) in AppSoundcore")

    new_count = 0
    for page_block in child_pages:
        pid = page_block["id"]
        title = page_block.get("child_page", {}).get("title", "")

        if pid in processed:
            p(f"  [skip] {title}")
            continue

        p(f"\nProcessing: {title} (id={pid})")
        audio_url = get_file_block_in_page(pid)
        if not audio_url:
            p("  No audio file found inside this page")
            processed.add(pid)
            save_processed(processed)
            continue

        audio_path = download_audio(audio_url)
        if not audio_path:
            p("  [FAIL] Could not download (URL may have expired)")
            processed.add(pid)
            save_processed(processed)
            continue

        try:
            transcript = transcribe(audio_path)
            summary = summarize(transcript)
            append_to_page(pid, transcript, summary)
            processed.add(pid)
            save_processed(processed)
            new_count += 1
        finally:
            try:
                os.unlink(audio_path)
            except Exception:
                pass

    if new_count == 0:
        p("No new recordings to process")
    else:
        p(f"\n[OK] Processed {new_count} recording(s)")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()

    if not test_connection():
        sys.exit(1)

    if args.test:
        return

    if args.watch:
        p("\nWatch mode: checking every 5 minutes. Ctrl+C to stop.")
        while True:
            process_once()
            p("\nWaiting 5 minutes...")
            time.sleep(300)
    else:
        process_once()


if __name__ == "__main__":
    main()