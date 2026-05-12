# -*- coding: utf-8 -*-
"""
Notion (SoundCore) → Knowledge Base sync + 自動統合

フロー:
  個別録音ファイル (daily)
    ↓ 週終了後
  週次まとめ (YYYY-Www.md)
    ↓ 月終了後
  月次まとめ (YYYY-MM.md)  ← 長期保存

個別・週次ファイルは統合後に自動削除してファイル数を削減する。
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

NOTION_TOKEN      = os.environ.get("NOTION_TOKEN")
NOTION_PAGE_ID    = os.environ.get("NOTION_PAGE_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

STATE_FILE = Path(__file__).parent / ".notion_knowledge_state.json"
NOTES_DIR  = Path(__file__).parent.parent.parent / "ceo" / "meeting-notes"


def p(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {
        "saved_pages":  {},  # pid -> {title, saved_at, last_edited, file, consolidated_to}
        "weekly_files": {},  # "2026-W20" -> filename
        "monthly_files": {}, # "2026-05"  -> filename
    }


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
# Block → Markdown
# ---------------------------------------------------------------------------

def rich_text_to_str(rt_list):
    return "".join(rt.get("plain_text", "") for rt in rt_list)


def block_to_markdown(block):
    btype = block.get("type", "")
    data  = block.get(btype, {})
    text  = rich_text_to_str(data.get("rich_text", []))

    if btype == "paragraph":
        return text
    elif btype == "heading_1":
        return f"# {text}"
    elif btype == "heading_2":
        return f"## {text}"
    elif btype == "heading_3":
        return f"### {text}"
    elif btype == "bulleted_list_item":
        return f"- {text}"
    elif btype == "numbered_list_item":
        return f"1. {text}"
    elif btype == "to_do":
        return f"- [{'x' if data.get('checked') else ' '}] {text}"
    elif btype == "quote":
        return f"> {text}"
    elif btype == "callout":
        return f"> {text}"
    elif btype == "divider":
        return "---"
    elif btype == "code":
        return f"```{data.get('language','')}\n{text}\n```"
    elif btype == "child_page":
        return f"### {data.get('title','')}"
    else:
        return text


def blocks_to_markdown(page_id):
    blocks = get_all_blocks(page_id)
    lines  = []
    for block in blocks:
        line = block_to_markdown(block)
        lines.append(line)
        if block.get("type") == "child_page":
            child_md = blocks_to_markdown(block["id"])
            if child_md:
                lines.append(child_md)
    return "\n".join(l for l in lines if l is not None)


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------

def call_claude(prompt, max_tokens=800):
    if not ANTHROPIC_API_KEY:
        return None
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
    p(f"  [WARN] Claude {r.status_code}")
    return None


def ai_summary(contents_list, period_label, period_type="week"):
    combined = "\n\n---\n\n".join(contents_list)[:6000]
    period_word = "週" if period_type == "week" else "月"
    result = call_claude(
        f"以下は{period_label}の録音メモ（文字起こし・要約）です。\n"
        f"この{period_word}全体を通じた主なテーマ・重要な決定事項・次のアクションを"
        f"日本語で箇条書きにまとめてください（500字以内）。\n\n"
        + combined,
        max_tokens=700,
    )
    return result or "(AI要約の生成に失敗しました)"


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def sanitize(title):
    for ch in r'\/:*?"<>|':
        title = title.replace(ch, "-")
    return title.strip()[:60]


def date_from_created(created_time):
    try:
        dt  = datetime.datetime.fromisoformat(created_time.replace("Z", "+00:00"))
        jst = dt + datetime.timedelta(hours=9)
        return jst.strftime("%Y-%m-%d")
    except Exception:
        return datetime.date.today().isoformat()


def week_bounds(date: datetime.date):
    monday = date - datetime.timedelta(days=date.weekday())
    return monday, monday + datetime.timedelta(days=6)


def parse_date_from_filename(filename):
    try:
        return datetime.date.fromisoformat(filename[:10])
    except Exception:
        return None


def first_of_next_month(year, month):
    if month == 12:
        return datetime.date(year + 1, 1, 1)
    return datetime.date(year, month + 1, 1)


# ---------------------------------------------------------------------------
# Save individual note
# ---------------------------------------------------------------------------

def has_meaningful_content(content):
    lines = [l for l in content.strip().split("\n") if l.strip() and not l.startswith("[")]
    return len(lines) >= 3


def save_daily_note(date_str, title, content):
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{date_str}_{sanitize(title)}.md"
    path     = NOTES_DIR / filename
    header   = f"# {title}\n\n**日付**: {date_str}  \n**取得元**: Notion (SoundCore)\n\n---\n\n"
    path.write_text(header + content, encoding="utf-8")
    p(f"  [OK] Saved: {filename}")
    return filename


# ---------------------------------------------------------------------------
# Weekly consolidation
# ---------------------------------------------------------------------------

def consolidate_weekly(state):
    today = datetime.date.today()

    # Group pending individual files by ISO week
    by_week: dict[str, list] = {}
    for pid, info in state["saved_pages"].items():
        if info.get("consolidated_to"):
            continue
        fname = info.get("file")
        if not fname:
            continue
        d = parse_date_from_filename(fname)
        if not d:
            continue
        monday, sunday = week_bounds(d)
        if today <= sunday:
            continue  # 週がまだ終わっていない
        iso    = d.isocalendar()
        wk     = f"{iso[0]}-W{iso[1]:02d}"
        by_week.setdefault(wk, []).append((pid, info, fname))

    for wk, entries in by_week.items():
        if wk in state["weekly_files"]:
            # ファイルは作済みだが個別ファイルが残っている場合だけ削除
            for pid, info, fname in entries:
                path = NOTES_DIR / fname
                if path.exists():
                    path.unlink()
                state["saved_pages"][pid]["consolidated_to"] = wk
            save_state(state)
            continue

        p(f"\n  [weekly] Consolidating {wk} ({len(entries)} recordings)...")

        entries_sorted = sorted(entries, key=lambda x: x[2])
        contents = []
        date_first = entries_sorted[0][2][:10]
        date_last  = entries_sorted[-1][2][:10]

        for pid, info, fname in entries_sorted:
            path = NOTES_DIR / fname
            if path.exists():
                contents.append(path.read_text(encoding="utf-8"))

        if not contents:
            continue

        label   = f"{wk} ({date_first} 〜 {date_last})"
        summary = ai_summary(contents, label, "week")

        lines = [
            f"# 週次まとめ {label}",
            "",
            f"**生成日**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## この週のまとめ（AI生成）",
            "",
            summary,
            "",
            "---",
            "",
            "## 各録音の内容",
            "",
        ]
        for pid, info, fname in entries_sorted:
            lines.append(f"### {info.get('title', fname)}")
            lines.append("")
            path = NOTES_DIR / fname
            if path.exists():
                body = path.read_text(encoding="utf-8")
                # ヘッダー部分をスキップして本文だけ追加
                body_lines = body.split("\n")
                skip = 0
                for i, bl in enumerate(body_lines):
                    if bl.strip() == "---":
                        skip = i + 1
                        break
                lines.extend(body_lines[skip:])
            lines.append("")

        weekly_filename = f"{wk}.md"
        (NOTES_DIR / weekly_filename).write_text("\n".join(lines), encoding="utf-8")
        p(f"  [OK] Weekly file: {weekly_filename}")

        for pid, info, fname in entries:
            path = NOTES_DIR / fname
            if path.exists():
                path.unlink()
            state["saved_pages"][pid]["consolidated_to"] = wk

        state["weekly_files"][wk] = weekly_filename
        save_state(state)
        p(f"  [OK] Deleted {len(entries)} individual file(s)")


# ---------------------------------------------------------------------------
# Monthly consolidation
# ---------------------------------------------------------------------------

def consolidate_monthly(state):
    today = datetime.date.today()

    # Group weekly files by month
    by_month: dict[str, list] = {}
    for wk, fname in state["weekly_files"].items():
        if any(wk in v.get("source_weeks", []) for v in state["monthly_files"].values()
               if isinstance(v, dict)):
            continue
        if fname in state["monthly_files"].values():
            continue
        # Parse year and week number
        try:
            yr, wnum = wk.split("-W")
            jan4    = datetime.date(int(yr), 1, 4)
            monday  = jan4 - datetime.timedelta(days=jan4.weekday()) + datetime.timedelta(weeks=int(wnum) - 1)
        except Exception:
            continue
        mk = monday.strftime("%Y-%m")
        yr_m, mo_m = int(mk[:4]), int(mk[5:7])
        if today < first_of_next_month(yr_m, mo_m):
            continue  # 月がまだ終わっていない
        by_month.setdefault(mk, []).append((wk, fname))

    for mk, entries in by_month.items():
        if mk in state["monthly_files"]:
            continue

        p(f"\n  [monthly] Consolidating {mk} ({len(entries)} weeks)...")

        entries_sorted = sorted(entries)
        contents = []
        for wk, fname in entries_sorted:
            path = NOTES_DIR / fname
            if path.exists():
                contents.append(path.read_text(encoding="utf-8"))

        if not contents:
            continue

        yr_m, mo_m = int(mk[:4]), int(mk[5:7])
        label   = f"{yr_m}年{mo_m}月"
        summary = ai_summary(contents, label, "month")

        lines = [
            f"# 月次まとめ {label}",
            "",
            f"**生成日**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**対象週**: {', '.join(wk for wk, _ in entries_sorted)}",
            "",
            "---",
            "",
            f"## {label}のまとめ（AI生成）",
            "",
            summary,
            "",
            "---",
            "",
            "## 各週の内容",
            "",
        ]
        for wk, fname in entries_sorted:
            lines.append(f"## {wk}")
            lines.append("")
            path = NOTES_DIR / fname
            if path.exists():
                body_lines = path.read_text(encoding="utf-8").split("\n")
                skip = 0
                for i, bl in enumerate(body_lines):
                    if bl.strip() == "---":
                        skip = i + 1
                        break
                lines.extend(body_lines[skip:])
            lines.append("")

        monthly_filename = f"{mk}.md"
        (NOTES_DIR / monthly_filename).write_text("\n".join(lines), encoding="utf-8")
        p(f"  [OK] Monthly file: {monthly_filename}")

        for wk, fname in entries:
            path = NOTES_DIR / fname
            if path.exists():
                path.unlink()

        state["monthly_files"][mk] = monthly_filename
        save_state(state)
        p(f"  [OK] Deleted {len(entries)} weekly file(s)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    p(f"\n=== Notion → Knowledge Base sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    state = load_state()
    saved_count = 0

    recording_pages = get_child_pages(NOTION_PAGE_ID)
    p(f"Found {len(recording_pages)} recording page(s)")

    for page_block in recording_pages:
        pid         = page_block["id"]
        title       = page_block.get("child_page", {}).get("title", pid)
        created     = page_block.get("created_time", "")
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

        date_str = date_from_created(created)
        filename = save_daily_note(date_str, title, content)

        state["saved_pages"][pid] = {
            "title":           title,
            "saved_at":        datetime.datetime.now().isoformat(),
            "last_edited":     last_edited,
            "file":            filename,
            "consolidated_to": None,
        }
        save_state(state)
        saved_count += 1

    if saved_count == 0:
        p("No new/updated recordings.")
    else:
        p(f"\n[OK] Saved {saved_count} note(s)")

    p("\nRunning consolidation...")
    consolidate_weekly(state)
    consolidate_monthly(state)
    p("Consolidation done.")


if __name__ == "__main__":
    if not NOTION_TOKEN or not NOTION_PAGE_ID:
        print("[ERROR] NOTION_TOKEN and NOTION_PAGE_ID must be set")
        exit(1)
    run()
