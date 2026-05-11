#!/usr/bin/env python3
"""
X (Twitter) 自動投稿スクリプト
月曜・水曜・金曜の週3本を自動投稿する。

動作:
  - departments/marketing/x-posts/ の最新 *-week.md を読み込む
  - 今日が月曜→投稿1、水曜→投稿2、金曜→投稿3 を投稿
  - 投稿済みはスキップ（.x_post_state.json で管理）
  - 投稿後は post-log.md を更新する
"""

import sys
import os
import re
import json
import glob
import hmac
import hashlib
import base64
import time
import random
import string
import urllib.parse
import urllib.request
import urllib.error
from datetime import date, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parents[2]
POSTS_DIR = BASE_DIR / "departments" / "marketing" / "x-posts"
STATE_FILE = BASE_DIR / ".x_post_state.json"
LOG_FILE = POSTS_DIR / "post-log.md"


def load_env():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"posted": {}}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def find_week_file():
    files = sorted(POSTS_DIR.glob("*-week.md"), reverse=True)
    return files[0] if files else None


def extract_post(week_file: Path, post_num: int) -> str | None:
    text = week_file.read_text(encoding="utf-8")
    pattern = rf"## 投稿{post_num}[^\n]*\n.*?```\n(.*?)```"
    m = re.search(pattern, text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def update_week_file_status(week_file: Path, post_num: int, today_str: str):
    text = week_file.read_text(encoding="utf-8")
    day_map = {1: "月", 2: "水", 3: "金"}
    day_ja = day_map.get(post_num, str(post_num))
    text = re.sub(
        rf"(\| {today_str}[^|]*\|[^|]*\|) 下書き",
        r"\1 投稿済",
        text
    )
    # 曜日ベースでも更新を試みる
    text = re.sub(
        rf"(\| 2[0-9]{{3}}-[0-9]{{2}}-[0-9]{{2}}（{day_ja}）[^|]*\|[^|]*\|) 下書き",
        r"\1 投稿済",
        text
    )
    week_file.write_text(text, encoding="utf-8")


def append_post_log(today_str: str, tweet_text: str, tweet_id: str):
    snippet = tweet_text[:30].replace("\n", " ") + "…"
    result = f"投稿済（ID: {tweet_id}）" if tweet_id else "失敗"
    new_row = f"| {today_str} | auto | {snippet} | {result} |\n"
    if LOG_FILE.exists():
        log = LOG_FILE.read_text(encoding="utf-8")
        log += new_row
    else:
        log = "# X投稿ログ\n\n| 日付 | トピック | 投稿文（冒頭） | 結果 |\n|------|---------|--------------|------|\n" + new_row
    LOG_FILE.write_text(log, encoding="utf-8")


def pct(s):
    return urllib.parse.quote(str(s), safe="")


def build_oauth_header(method, url, ck, cs, at, ats):
    timestamp = str(int(time.time()))
    nonce = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    params = {
        "oauth_consumer_key":     ck,
        "oauth_nonce":            nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp":        timestamp,
        "oauth_token":            at,
        "oauth_version":          "1.0",
    }
    param_str = "&".join(pct(k) + "=" + pct(v) for k, v in sorted(params.items()))
    base_str = "&".join([method.upper(), pct(url), pct(param_str)])
    signing_key = pct(cs) + "&" + pct(ats)
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()
    params["oauth_signature"] = sig
    header_parts = [pct(k) + '="' + pct(v) + '"' for k, v in sorted(params.items())]
    return "OAuth " + ", ".join(header_parts)


def post_tweet(text: str) -> str:
    ck  = os.environ.get("X_CONSUMER_KEY", "")
    cs  = os.environ.get("X_CONSUMER_SECRET", "")
    at  = os.environ.get("X_ACCESS_TOKEN", "")
    ats = os.environ.get("X_ACCESS_TOKEN_SECRET", "")
    if not ck:
        print("[ERROR] X_CONSUMER_KEY が設定されていません")
        return ""
    url  = "https://api.twitter.com/2/tweets"
    body = json.dumps({"text": text}).encode("utf-8")
    auth = build_oauth_header("POST", url, ck, cs, at, ats)
    req  = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", auth)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read().decode())
            tweet_id = result.get("data", {}).get("id", "")
            print(f"[OK] 投稿成功: {tweet_id}")
            return tweet_id
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"[ERROR] HTTP {e.code}: {err}")
        return ""


def main():
    load_env()

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    weekday = today.weekday()  # 0=Mon, 2=Wed, 4=Fri

    day_to_post = {0: 1, 2: 2, 4: 3}
    if weekday not in day_to_post:
        print(f"[SKIP] 今日（{today_str}）は投稿日ではありません（月・水・金のみ）")
        return

    post_num = day_to_post[weekday]

    state = load_state()
    state_key = f"{today_str}-post{post_num}"
    if state["posted"].get(state_key):
        print(f"[SKIP] {state_key} はすでに投稿済みです")
        return

    week_file = find_week_file()
    if not week_file:
        print("[ERROR] 週次下書きファイルが見つかりません")
        sys.exit(1)

    print(f"[INFO] 下書きファイル: {week_file.name}")
    tweet_text = extract_post(week_file, post_num)
    if not tweet_text:
        print(f"[ERROR] 投稿{post_num} のテキストを抽出できませんでした")
        sys.exit(1)

    print(f"[INFO] 投稿{post_num} を送信します（{len(tweet_text)}文字）")
    print(f"---\n{tweet_text}\n---")

    tweet_id = post_tweet(tweet_text)

    state["posted"][state_key] = {
        "date": today_str,
        "tweet_id": tweet_id,
        "file": week_file.name,
    }
    save_state(state)

    update_week_file_status(week_file, post_num, today_str)
    append_post_log(today_str, tweet_text, tweet_id)

    if tweet_id:
        print(f"[DONE] 投稿完了: https://x.com/AI_chuusyou/status/{tweet_id}")
    else:
        print("[WARN] 投稿に失敗しました。post-log.md を確認してください")
        sys.exit(1)


if __name__ == "__main__":
    main()
