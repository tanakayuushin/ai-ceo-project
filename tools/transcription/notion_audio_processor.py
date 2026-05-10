# -*- coding: utf-8 -*-
"""
Notion audio block -> Whisper transcription -> Claude Haiku summary -> Notion child page
Usage:
  python notion_audio_processor.py --test     # connection test only
  python notion_audio_processor.py            # run once
  python notion_audio_processor.py --watch    # auto-monitor every 5 minutes
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
        p(f"[FAIL] Connection failed: {r.status_code} -- {r.text[:200]}")
        return False


def get_audio_blocks():
    blocks = []
    cursor = None
    while True:
        url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        r = notion_get(url)
        if r.status_code != 200:
            p(f"[FAIL] Block fetch failed: {r.status_code} -- {r.text[:200]}")
            return []
        data = r.json()
        for block in data.get("results", []):
            if block.get("type") in ("audio", "file", "video"):
                blocks.append(block)
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return blocks


def download_audio(block):
    btype = block.get("type")
    info = block.get(btype, {})
    file_info = info.get("file") or info.get("external")
    if not file_info:
        return None
    url = file_info.get("url")
    if not url:
        return None
    p(f"  Downloading: {url[:80]}...")
    r = requests.get(url, verify=False, timeout=60)
    if r.status_code != 200:
        p(f"  [FAIL] Download failed: {r.status_code}")
        return None
    suffix = ".m4a"
    ct = r.headers.get("content-type", "")
    if "wav" in ct:
        suffix = ".wav"
    elif "mp3" in ct or "mpeg" in ct:
        suffix = ".mp3"
    elif "ogg" in ct:
        suffix = ".ogg"
    elif "webm" in ct:
        suffix = ".webm"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.close()
    p(f"  Saved: {tmp.name} ({len(r.content)//1024}KB)")
    return tmp.name


def transcribe(audio_path):
    try:
        import whisper
    except ImportError:
        p("  [WARN] whisper not installed. Run: pip install openai-whisper")
        return ""
    p("  Transcribing with Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="ja")
    text = result.get("text", "").strip()
    p(f"  Transcription done: {len(text)} chars")
    return text


def summarize(transcript):
    if not transcript:
        return "(Transcription was empty, cannot summarize)"
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
            "messages": [{"role": "user", "content": "以下の音声文字起こしを日本語で3〜5行に要約してください。重要なポイントと決定事項があれば箇条書きにしてください。\n\n" + transcript[:3000]}],
        },
        verify=False,
        timeout=30,
    )
    if r.status_code == 200:
        summary = r.json()["content"][0]["text"].strip()
        p(f"  Summary done: {len(summary)} chars")
        return summary
    else:
        p(f"  [WARN] Summary failed: {r.status_code}")
        return "(Summary generation failed)"


def create_notion_page(block_id, transcript, summary, block_created):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    title = f"Recording Note {timestamp}"

    def text_blocks(content, btype="paragraph"):
        lines = [content[i:i+1900] for i in range(0, len(content), 1900)]
        return [{"object": "block", "type": btype, btype: {"rich_text": [{"type": "text", "text": {"content": line}}]}} for line in lines]

    children = (
        [{"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Summary"}}]}}]
        + text_blocks(summary)
        + [{"object": "block", "type": "divider", "divider": {}}]
        + [{"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Full Transcription"}}]}}]
        + text_blocks(transcript if transcript else "(No transcription result)")
    )

    payload = {
        "parent": {"page_id": NOTION_PAGE_ID},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
        "children": children[:100],
    }
    r = notion_post("https://api.notion.com/v1/pages", payload)
    if r.status_code == 200:
        page_url = r.json().get("url", "")
        p(f"  [OK] Notion page created: {page_url}")
        return True
    else:
        p(f"  [FAIL] Page creation failed: {r.status_code} -- {r.text[:300]}")
        return False


def process_once():
    p(f"\n{'='*50}")
    p(f"Run time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p("="*50)
    processed = load_processed()
    blocks = get_audio_blocks()
    if not blocks:
        p("No audio blocks found")
        return
    new_count = 0
    for block in blocks:
        bid = block["id"]
        if bid in processed:
            continue
        p(f"\nNew audio block found: {bid}")
        audio_path = download_audio(block)
        if not audio_path:
            p("  [FAIL] Could not download audio (URL may have expired)")
            processed.add(bid)
            save_processed(processed)
            continue
        try:
            transcript = transcribe(audio_path)
            summary = summarize(transcript)
            create_notion_page(bid, transcript, summary, block.get("created_time", ""))
            processed.add(bid)
            save_processed(processed)
            new_count += 1
        finally:
            try:
                os.unlink(audio_path)
            except Exception:
                pass
    if new_count == 0:
        p("No new audio blocks to process")
    else:
        p(f"\n[OK] Processed {new_count} audio file(s)")


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
        p("\nWatch mode started (checking every 5 minutes). Press Ctrl+C to stop.")
        while True:
            process_once()
            p("\nWaiting 5 minutes until next check...")
            time.sleep(300)
    else:
        process_once()


if __name__ == "__main__":
    main()