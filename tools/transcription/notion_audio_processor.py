# -*- coding: utf-8 -*-
"""
Soundcore Notion audio pipeline with weekly/monthly summaries.

Structure:
  AppSoundcore (main)
  └── 2026年5月 (monthly page, auto-created)
      └── 週まとめ 05/04〜05/10 (weekly page, created after week ends)
          Individual recording pages stay in AppSoundcore as-is.

Usage:
  python notion_audio_processor.py --test
  python notion_audio_processor.py
  python notion_audio_processor.py --watch
"""

import os
import sys
import ssl
import json
import time
import argparse
import tempfile
import datetime
import requests
import urllib3
from pathlib import Path
from dotenv import load_dotenv

ssl._create_default_https_context = ssl._create_unverified_context
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

STATE_FILE = Path(__file__).parent / ".notion_state.json"


def p(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "processed_pages": {},   # page_id -> {date, title, summary}
        "weekly_summaries": {},  # "YYYY-Www" -> notion_page_id
        "monthly_pages": {},     # "YYYY-MM"  -> notion_page_id
    }


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Notion helpers
# ---------------------------------------------------------------------------

def notion_get(url):
    return requests.get(url, headers=NOTION_HEADERS, verify=False)


def notion_patch(url, data):
    return requests.patch(url, headers=NOTION_HEADERS, json=data, verify=False)


def notion_post(url, data):
    return requests.post(url, headers=NOTION_HEADERS, json=data, verify=False)


def make_text_blocks(content, btype="paragraph"):
    lines = [content[i:i+1900] for i in range(0, len(content), 1900)]
    return [{"object": "block", "type": btype,
             btype: {"rich_text": [{"type": "text", "text": {"content": line}}]}}
            for line in lines]


def heading(text, level=2):
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {
        "rich_text": [{"type": "text", "text": {"content": text}}]}}


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


# ---------------------------------------------------------------------------
# Connection test
# ---------------------------------------------------------------------------

def test_connection():
    p(f"Notion connection check... (ID: {NOTION_PAGE_ID})")
    r = notion_get(f"https://api.notion.com/v1/pages/{NOTION_PAGE_ID}")
    if r.status_code == 200:
        arr = r.json().get("properties", {}).get("title", {}).get("title", [])
        name = arr[0].get("plain_text", "(no title)") if arr else "(no title)"
        p(f"[OK] Connected: {name}")
        return True
    p(f"[FAIL] {r.status_code} -- {r.text[:200]}")
    return False


# ---------------------------------------------------------------------------
# Recording processing
# ---------------------------------------------------------------------------

def get_child_pages():
    pages = []
    cursor = None
    while True:
        url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        r = notion_get(url)
        if r.status_code != 200:
            return []
        data = r.json()
        for block in data.get("results", []):
            if block.get("type") == "child_page":
                pages.append(block)
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return pages


def is_already_transcribed(page_id):
    """Check if page already has a divider (= transcription was appended)."""
    r = notion_get(f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100")
    if r.status_code != 200:
        return False
    for block in r.json().get("results", []):
        if block.get("type") == "divider":
            return True
    return False


def get_file_url_in_page(page_id):
    r = notion_get(f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100")
    if r.status_code != 200:
        return None
    for block in r.json().get("results", []):
        if block.get("type") == "file":
            info = block.get("file", {})
            fi = info.get("file") or info.get("external")
            if fi and fi.get("url"):
                return fi["url"]
    return None


def download_audio(url):
    p("  Downloading audio...")
    r = requests.get(url, verify=False, timeout=60)
    if r.status_code != 200:
        p(f"  [FAIL] {r.status_code}")
        return None
    suffix = ".ogg"
    ct = r.headers.get("content-type", "")
    if "wav" in ct: suffix = ".wav"
    elif "mp3" in ct or "mpeg" in ct: suffix = ".mp3"
    elif "m4a" in ct or "mp4" in ct: suffix = ".m4a"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.close()
    p(f"  Saved: {tmp.name} ({len(r.content)//1024}KB)")
    return tmp.name


def transcribe(audio_path):
    try:
        import whisper
    except ImportError:
        p("  [WARN] whisper not installed")
        return ""
    p("  Transcribing with Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="ja")
    text = result.get("text", "").strip()
    p(f"  Transcribed: {len(text)} chars")
    return text


def call_claude(prompt, max_tokens=500):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
        verify=False, timeout=30,
    )
    if r.status_code == 200:
        return r.json()["content"][0]["text"].strip()
    p(f"  [WARN] Claude API {r.status_code}")
    return None


def summarize(transcript):
    if not transcript:
        return "(文字起こし結果が空のため要約できませんでした)"
    p("  Summarizing with Claude Haiku...")
    result = call_claude(
        "以下の音声文字起こしを日本語で3〜5行に要約してください。"
        "重要なポイントと決定事項があれば箇条書きにしてください。\n\n" + transcript[:3000]
    )
    if result:
        p(f"  Summary: {len(result)} chars")
        return result
    return "(要約の生成に失敗しました)"


def append_transcription_to_page(page_id, transcript, summary):
    children = (
        [divider(), heading("要約")]
        + make_text_blocks(summary)
        + [heading("文字起こし（全文）")]
        + make_text_blocks(transcript or "(文字起こし結果なし)")
    )
    r = notion_patch(
        f"https://api.notion.com/v1/blocks/{page_id}/children",
        {"children": children[:50]}
    )
    if r.status_code == 200:
        p("  [OK] Appended to Notion page")
        return True
    p(f"  [FAIL] {r.status_code} -- {r.text[:200]}")
    return False


# ---------------------------------------------------------------------------
# Weekly / Monthly summaries
# ---------------------------------------------------------------------------

def to_jst_date(date_str):
    if not date_str:
        return None
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (dt + datetime.timedelta(hours=9)).date()
    except Exception:
        return None


def get_week_bounds(year, week):
    """Return (monday, sunday) for an ISO week."""
    jan4 = datetime.date(year, 1, 4)
    monday = jan4 - datetime.timedelta(days=jan4.weekday()) + datetime.timedelta(weeks=week - 1)
    return monday, monday + datetime.timedelta(days=6)


def get_or_create_monthly_page(month_key, state):
    if month_key in state["monthly_pages"]:
        return state["monthly_pages"][month_key]
    year, month = month_key.split("-")
    title = f"{year}年{int(month)}月"
    p(f"  Creating monthly page: {title}")
    payload = {
        "parent": {"page_id": NOTION_PAGE_ID},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
        "children": [
            {"object": "block", "type": "paragraph", "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"{title}の録音週次まとめ"}}]
            }}
        ],
    }
    r = notion_post("https://api.notion.com/v1/pages", payload)
    if r.status_code == 200:
        page_id = r.json()["id"]
        state["monthly_pages"][month_key] = page_id
        save_state(state)
        p(f"  [OK] Monthly page created: {title}")
        return page_id
    p(f"  [FAIL] Monthly page: {r.status_code}")
    return None


def create_weekly_summary_text(entries):
    if not entries:
        return "(この週の録音要約がありません)"
    combined = "\n\n".join(entries)
    p("  Generating weekly summary with Claude Haiku...")
    result = call_claude(
        "以下は1週間の音声メモの要約集です。"
        "週全体を通じた主なテーマ・重要な決定事項・次のアクションを"
        "日本語で箇条書きにまとめてください（400字以内）。\n\n" + combined[:4000],
        max_tokens=600,
    )
    return result or "(週次要約の生成に失敗しました)"


def save_weekly_report_locally(week_key, date_range, recordings, weekly_summary):
    """Save weekly summary as a markdown file for Allen to learn from."""
    reports_dir = Path(__file__).parent.parent.parent / "ceo" / "weekly-reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# 週次レポート {week_key} ({date_range})",
        f"",
        f"**生成日**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"---",
        f"",
        f"## 週全体のまとめ",
        f"",
        weekly_summary,
        f"",
        f"---",
        f"",
        f"## 各録音の要約",
        f"",
    ]
    for _, info in recordings:
        title = info.get("title", "")
        summary = info.get("summary", "")
        if title:
            lines.append(f"### {title}")
            lines.append("")
        lines.append(summary if summary else "(要約なし)")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*自動生成: Soundcore録音 → Whisper文字起こし → Claude Haiku要約*")

    report_path = reports_dir / f"{week_key}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    p(f"  [OK] Weekly report saved: {report_path}")


def create_weekly_page(monthly_page_id, date_range, week_key, recordings, weekly_summary):
    title = f"週まとめ {date_range}"
    p(f"  Creating weekly page: {title}")
    children = (
        [heading("週全体のまとめ")]
        + make_text_blocks(weekly_summary)
        + [divider(), heading("各録音の要約")]
    )
    for _, info in recordings:
        rec_title = info.get("title", "")
        summary = info.get("summary", "")
        if rec_title:
            children.append(heading(rec_title, level=3))
        if summary:
            children += make_text_blocks(summary)
        else:
            children += make_text_blocks("(要約なし - 各録音ページを参照)")

    payload = {
        "parent": {"page_id": monthly_page_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
        "children": children[:100],
    }
    r = notion_post("https://api.notion.com/v1/pages", payload)
    if r.status_code == 200:
        page_id = r.json()["id"]
        p(f"  [OK] Weekly page created: {title}")
        # Also save locally for Allen to learn from
        save_weekly_report_locally(week_key, date_range, recordings, weekly_summary)
        return page_id
    p(f"  [FAIL] {r.status_code} -- {r.text[:200]}")
    return None


def run_weekly_summaries(state):
    today = datetime.date.today()

    # Group recordings by ISO week
    weeks = {}
    for page_id, info in state["processed_pages"].items():
        jst_date = to_jst_date(info.get("date"))
        if not jst_date:
            continue
        iso = jst_date.isocalendar()
        week_key = f"{iso[0]}-W{iso[1]:02d}"
        month_key = jst_date.strftime("%Y-%m")
        if week_key not in weeks:
            weeks[week_key] = {"recordings": [], "month_key": month_key, "year": iso[0], "week": iso[1]}
        weeks[week_key]["recordings"].append((page_id, info))

    for week_key, data in weeks.items():
        if week_key in state["weekly_summaries"]:
            continue  # Already done

        monday, sunday = get_week_bounds(data["year"], data["week"])
        if today <= sunday:
            p(f"  [skip weekly] {week_key} ends {sunday} (not over yet)")
            continue

        p(f"\nCreating weekly summary: {week_key}")

        # Compile summaries
        entries = []
        recordings_sorted = sorted(data["recordings"], key=lambda x: x[1].get("date", ""))
        for _, info in recordings_sorted:
            title = info.get("title", "")
            summary = info.get("summary", "")
            if summary and "失敗" not in summary and "空" not in summary:
                entries.append(f"【{title}】\n{summary}")

        weekly_summary = create_weekly_summary_text(entries)
        date_range = f"{monday.strftime('%m/%d')}〜{sunday.strftime('%m/%d')}"

        monthly_page_id = get_or_create_monthly_page(data["month_key"], state)
        if not monthly_page_id:
            continue

        week_page_id = create_weekly_page(
            monthly_page_id, date_range, week_key, recordings_sorted, weekly_summary
        )
        if week_page_id:
            state["weekly_summaries"][week_key] = week_page_id
            save_state(state)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def process_once(state):
    p(f"\n{'='*50}")
    p(f"Run: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p("="*50)

    child_pages = get_child_pages()
    p(f"Found {len(child_pages)} child page(s) in AppSoundcore")

    new_count = 0
    for page_block in child_pages:
        pid = page_block["id"]
        title = page_block.get("child_page", {}).get("title", "")
        created = page_block.get("created_time", "")

        if pid in state["processed_pages"]:
            p(f"  [skip] {title}")
            continue

        p(f"\nProcessing: {title}")

        # Check if already transcribed (e.g. from previous script version)
        if is_already_transcribed(pid):
            p("  Already transcribed - recording metadata only")
            state["processed_pages"][pid] = {
                "date": created,
                "title": title,
                "summary": "(既処理済み)",
            }
            save_state(state)
            continue

        audio_url = get_file_url_in_page(pid)
        if not audio_url:
            p("  No audio file found")
            state["processed_pages"][pid] = {"date": created, "title": title, "summary": ""}
            save_state(state)
            continue

        audio_path = download_audio(audio_url)
        if not audio_path:
            p("  [FAIL] Download failed (URL may be expired)")
            state["processed_pages"][pid] = {"date": created, "title": title, "summary": ""}
            save_state(state)
            continue

        try:
            transcript = transcribe(audio_path)
            summary = summarize(transcript)
            append_transcription_to_page(pid, transcript, summary)
            state["processed_pages"][pid] = {"date": created, "title": title, "summary": summary}
            save_state(state)
            new_count += 1
        finally:
            try:
                os.unlink(audio_path)
            except Exception:
                pass

    if new_count == 0:
        p("No new recordings processed")
    else:
        p(f"\n[OK] Processed {new_count} recording(s)")

    p("\nChecking weekly/monthly summaries...")
    run_weekly_summaries(state)


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

    state = load_state()

    if args.watch:
        p("\nWatch mode: checking every 5 minutes. Ctrl+C to stop.")
        while True:
            process_once(state)
            p("\nWaiting 5 minutes...")
            time.sleep(300)
    else:
        process_once(state)


if __name__ == "__main__":
    main()