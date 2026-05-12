# -*- coding: utf-8 -*-
"""
Notion (SoundCore) → Knowledge Base sync

SoundCoreが録音ページに追加した文字起こし・要約を読み取り、
ceo/meeting-notes/ にmarkdownとして保存する。
"""

import os
import json
import datetime
import requests
import urllib3
from pathlib import Path
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

NOTION_TOKEN   = os.environ.get("NOTION_TOKEN")
NOTION_PAGE_ID = os.environ.get("NOTION_PAGE_ID")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

STATE_FILE   = Path(__file__).parent / ".notion_knowledge_state.json"
NOTES_DIR    = Path(__file__).parent.parent.parent / "ceo" / "meeting-notes"


def p(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"saved_pages": {}}  # page_id -> {"title", "saved_at", "file"}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Notion API
# ---------------------------------------------------------------------------

def notion_get(url):
    return requests.get(url, headers=NOTION_HEADERS, verify=False, timeout=30)


def get_child_pages(parent_id):
    pages = []
    cursor = None
    while True:
        url = f"https://api.notion.com/v1/blocks/{parent_id}/children?page_size=100"
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


def get_page_metadata(page_id):
    r = notion_get(f"https://api.notion.com/v1/pages/{page_id}")
    if r.status_code != 200:
        return None
    return r.json()


def get_all_blocks(page_id):
    blocks = []
    cursor = None
    while True:
        url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        r = notion_get(url)
        if r.status_code != 200:
            break
        data = r.json()
        blocks.extend(data.get("results", []))
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return blocks


# ---------------------------------------------------------------------------
# Block → Markdown conversion
# ---------------------------------------------------------------------------

def rich_text_to_str(rich_text_list):
    return "".join(rt.get("plain_text", "") for rt in rich_text_list)


def block_to_markdown(block, depth=0):
    btype = block.get("type", "")
    indent = "  " * depth
    data   = block.get(btype, {})
    rt     = data.get("rich_text", [])
    text   = rich_text_to_str(rt)

    if btype == "paragraph":
        return f"{indent}{text}" if text else ""
    elif btype == "heading_1":
        return f"# {text}"
    elif btype == "heading_2":
        return f"## {text}"
    elif btype == "heading_3":
        return f"### {text}"
    elif btype == "bulleted_list_item":
        return f"{indent}- {text}"
    elif btype == "numbered_list_item":
        return f"{indent}1. {text}"
    elif btype == "to_do":
        check = "x" if data.get("checked") else " "
        return f"{indent}- [{check}] {text}"
    elif btype == "quote":
        return f"> {text}"
    elif btype == "callout":
        return f"> {text}"
    elif btype == "divider":
        return "---"
    elif btype == "code":
        lang = data.get("language", "")
        return f"```{lang}\n{text}\n```"
    elif btype == "child_page":
        title = data.get("title", "")
        return f"### {title}"
    elif btype in ("file", "audio"):
        fi = data.get("file") or data.get("external") or {}
        url = fi.get("url", "")
        cap_rt = data.get("caption", [])
        cap = rich_text_to_str(cap_rt) or btype
        return f"[{cap}]({url})" if url else f"[{cap}]"
    elif btype == "image":
        fi = data.get("file") or data.get("external") or {}
        url = fi.get("url", "")
        cap_rt = data.get("caption", [])
        cap = rich_text_to_str(cap_rt) or "image"
        return f"![{cap}]({url})" if url else f"![{cap}]"
    else:
        return f"{indent}{text}" if text else ""


def blocks_to_markdown(page_id):
    blocks = get_all_blocks(page_id)
    lines  = []
    for block in blocks:
        line = block_to_markdown(block)
        lines.append(line)

        # child_page → recurse into it
        if block.get("type") == "child_page":
            child_id = block["id"]
            child_lines = blocks_to_markdown(child_id)
            if child_lines:
                lines.append(child_lines)

    return "\n".join(l for l in lines if l is not None)


# ---------------------------------------------------------------------------
# Save to markdown
# ---------------------------------------------------------------------------

def recording_date(page_id, title, created_time):
    try:
        dt = datetime.datetime.fromisoformat(created_time.replace("Z", "+00:00"))
        jst = dt + datetime.timedelta(hours=9)
        return jst.strftime("%Y-%m-%d")
    except Exception:
        return datetime.date.today().isoformat()


def sanitize_filename(title):
    for ch in r'\/:*?"<>|':
        title = title.replace(ch, "-")
    return title.strip()[:60]


def save_note(date_str, title, content):
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = sanitize_filename(title)
    filename   = f"{date_str}_{safe_title}.md"
    path       = NOTES_DIR / filename

    header = f"# {title}\n\n**日付**: {date_str}  \n**取得元**: Notion (SoundCore)\n\n---\n\n"
    path.write_text(header + content, encoding="utf-8")
    p(f"  [OK] Saved: {path.name}")
    return filename


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def has_meaningful_content(content):
    """ほぼ空のページをスキップする（audioブロックしかないなど）"""
    stripped = content.strip()
    lines    = [l for l in stripped.split("\n") if l.strip() and not l.startswith("[")]
    return len(lines) >= 3


def run():
    p(f"\n=== Notion → Knowledge Base sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    state = load_state()
    saved_count = 0

    recording_pages = get_child_pages(NOTION_PAGE_ID)
    p(f"Found {len(recording_pages)} recording page(s)")

    for page_block in recording_pages:
        pid        = page_block["id"]
        title      = page_block.get("child_page", {}).get("title", pid)
        created    = page_block.get("created_time", "")
        last_edited = page_block.get("last_edited_time", "")

        prev = state["saved_pages"].get(pid, {})
        if prev.get("last_edited") == last_edited:
            p(f"  [skip] {title} (unchanged)")
            continue

        p(f"\nReading: {title}")
        content = blocks_to_markdown(pid)

        if not has_meaningful_content(content):
            p("  [skip] Not enough content yet")
            continue

        date_str = recording_date(pid, title, created)
        filename = save_note(date_str, title, content)

        state["saved_pages"][pid] = {
            "title":       title,
            "saved_at":    datetime.datetime.now().isoformat(),
            "last_edited": last_edited,
            "file":        filename,
        }
        save_state(state)
        saved_count += 1

    if saved_count == 0:
        p("No new/updated recordings.")
    else:
        p(f"\n[OK] Saved {saved_count} note(s) to ceo/meeting-notes/")


if __name__ == "__main__":
    if not NOTION_TOKEN or not NOTION_PAGE_ID:
        print("[ERROR] NOTION_TOKEN and NOTION_PAGE_ID must be set")
        exit(1)
    run()
