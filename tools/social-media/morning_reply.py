"""
morning_reply.py - 朝のリプライワークフロー
target_accounts.yaml のアカウントの最新ツイートを取得し、
Claude Haiku で返信案を3パターン生成 → インタラクティブに選択して投稿。
"""

import os
import sys
import json
import time
import hmac
import hashlib
import urllib.parse
import urllib.request
import secrets
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── 定数 ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent.parent
ENV_PATH   = PROJECT_DIR / ".env"
YAML_PATH  = BASE_DIR / "target_accounts.yaml"
POST_DELAY = 5  # 投稿間隔（秒）

# ── .env 読み込み ──────────────────────────────────────────────────────────────
def load_env():
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    for k, v in env.items():
        os.environ.setdefault(k, v)

# ── OAuth 1.0a ────────────────────────────────────────────────────────────────
def _pct(s: str) -> str:
    return urllib.parse.quote(str(s), safe="")

def oauth_header(method: str, url: str, extra_params: dict = None) -> str:
    ck  = os.environ["X_CONSUMER_KEY"]
    cs  = os.environ["X_CONSUMER_SECRET"]
    at  = os.environ["X_ACCESS_TOKEN"]
    ats = os.environ["X_ACCESS_TOKEN_SECRET"]

    ts    = str(int(time.time()))
    nonce = secrets.token_hex(16)

    oauth_params = {
        "oauth_consumer_key":     ck,
        "oauth_nonce":            nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp":        ts,
        "oauth_token":            at,
        "oauth_version":          "1.0",
    }
    all_params = {**oauth_params, **(extra_params or {})}
    sorted_params = "&".join(
        f"{_pct(k)}={_pct(v)}" for k, v in sorted(all_params.items())
    )
    base = "&".join([_pct(method.upper()), _pct(url), _pct(sorted_params)])
    key  = f"{_pct(cs)}&{_pct(ats)}"
    sig  = hmac.new(key.encode(), base.encode(), hashlib.sha1)
    sig_b64 = __import__("base64").b64encode(sig.digest()).decode()

    oauth_params["oauth_signature"] = sig_b64
    header_value = "OAuth " + ", ".join(
        f'{_pct(k)}="{_pct(v)}"' for k, v in sorted(oauth_params.items())
    )
    return header_value

# ── X API ─────────────────────────────────────────────────────────────────────
def x_get(path: str, query: dict = None) -> dict:
    url = f"https://api.twitter.com/2/{path.lstrip('/')}"
    qs  = urllib.parse.urlencode(query) if query else ""
    full_url = f"{url}?{qs}" if qs else url
    auth = oauth_header("GET", url, query)
    req  = urllib.request.Request(full_url, headers={"Authorization": auth})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def get_user_id(username: str) -> str | None:
    try:
        data = x_get(f"users/by/username/{username}", {"user.fields": "id,name,public_metrics"})
        return data["data"]["id"]
    except Exception as e:
        print(f"  [WARN] {username} のユーザーID取得失敗: {e}")
        return None

def get_recent_tweets(user_id: str, hours: int = 24) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        data = x_get(f"users/{user_id}/tweets", {
            "max_results": "10",
            "start_time": since,
            "tweet.fields": "id,text,created_at,public_metrics",
            "exclude": "retweets,replies",
        })
        return data.get("data", [])
    except Exception as e:
        print(f"  [WARN] ツイート取得失敗: {e}")
        return []

def post_reply(text: str, reply_to_id: str) -> dict:
    url  = "https://api.twitter.com/2/tweets"
    body = json.dumps({"text": text, "reply": {"in_reply_to_tweet_id": reply_to_id}}).encode()
    auth = oauth_header("POST", url)
    req  = urllib.request.Request(
        url, data=body,
        headers={"Authorization": auth, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# ── Claude Haiku でリプライ案生成 ─────────────────────────────────────────────
def generate_replies(tweet_text: str, account_name: str, reply_angle: str) -> list[str]:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return ["（APIキー未設定のため自動生成不可）"]

    system = (
        "あなたはEmport AI CEO アレンのSNS運用アシスタントです。\n"
        "アレンは山口県で中小企業向けAI導入支援を行うスタートアップのCEOです。\n"
        "\n"
        "以下のルールでリプライ案を3パターン生成してください:\n"
        "- フォーマット: 感想(1行) + 経験/知識(1〜2行) + 質問(1行)\n"
        "- 130字以内（日本語の場合）\n"
        "- 宣伝・サービス誘導・エンゲベイトは絶対NG\n"
        "- パターン1: フォーマル（知識・データ重視）\n"
        "- パターン2: カジュアル（共感・親しみやすい）\n"
        "- パターン3: 質問特化（相手への興味・学び姿勢）\n"
        "- 各パターンは「===」で区切る\n"
        "- パターン番号ラベル不要、本文のみ\n"
    )
    user_msg = (
        f"リプライ先のアカウント: {account_name}\n"
        f"リプライ角度のヒント: {reply_angle}\n"
        f"\nツイート本文:\n{tweet_text}\n"
        "\n上記に対するリプライ案を3パターン生成してください。"
    )

    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 800,
        "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
            raw  = resp["content"][0]["text"].strip()
            parts = [p.strip() for p in raw.split("===") if p.strip()]
            return parts[:3] if parts else [raw]
    except Exception as e:
        return [f"（生成エラー: {e}）"]

# ── 文字数カウント（Twitter基準） ─────────────────────────────────────────────
def tweet_char_count(text: str) -> int:
    count = 0
    for ch in text:
        count += 2 if ord(ch) > 0x7F else 1
    return count

# ── メイン ────────────────────────────────────────────────────────────────────
def run():
    load_env()

    print("=" * 60)
    print("  朝のリプライワークフロー  Emport AI / アレン")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # YAML 読み込み
    if not YAML_PATH.exists():
        print(f"[ERROR] {YAML_PATH} が見つかりません")
        sys.exit(1)

    with open(YAML_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    accounts_data = config.get("accounts", {})
    all_accounts  = []
    for tier in ["tier_a", "tier_b"]:
        for acc in accounts_data.get(tier, []):
            acc["_tier"] = tier
            all_accounts.append(acc)

    total_replied = 0

    for acc in all_accounts:
        username    = acc.get("username", "")
        name        = acc.get("name", username)
        reply_angle = acc.get("reply_angle", "")
        tier        = acc.get("_tier", "")

        print(f"\n{'─' * 60}")
        print(f"  @{username}  ({name})  [{tier}]")
        print(f"  角度: {reply_angle}")
        print(f"{'─' * 60}")

        uid = get_user_id(username)
        if not uid:
            continue

        tweets = get_recent_tweets(uid)
        if not tweets:
            print("  直近24時間のツイートなし → スキップ")
            continue

        for tweet in tweets[:3]:  # 最大3件
            tweet_id   = tweet["id"]
            tweet_text = tweet["text"]
            created_at = tweet.get("created_at", "")

            print(f"\n  ツイート ({created_at[:16]}):")
            print(f"  {tweet_text[:200]}")
            tc = tweet_char_count(tweet_text)
            print(f"  https://x.com/{username}/status/{tweet_id}")

            print("\n  [リプライ案生成中...]")
            replies = generate_replies(tweet_text, name, reply_angle)

            for i, r in enumerate(replies, 1):
                cc = tweet_char_count(r)
                flag = "⚠️ 長すぎ" if cc > 280 else f"({cc}/280)"
                print(f"\n  [{i}] {flag}")
                print(f"  {r}")

            print("\n  操作: [1/2/3]=投稿  [e]=編集  [s]=スキップ  [q]=終了")
            choice = input("  > ").strip().lower()

            if choice == "q":
                print("\n終了します。")
                print(f"本日のリプライ数: {total_replied} 件")
                return

            if choice == "s" or choice == "":
                print("  スキップ")
                continue

            if choice == "e":
                text = input("  リプライ本文を入力 (Enter で確定):\n  > ").strip()
            elif choice in ("1", "2", "3"):
                idx  = int(choice) - 1
                text = replies[idx] if idx < len(replies) else ""
            else:
                print("  無効な入力 → スキップ")
                continue

            if not text:
                print("  テキストなし → スキップ")
                continue

            cc = tweet_char_count(text)
            if cc > 280:
                print(f"  ⚠️ {cc}/280 文字 — 長すぎます。編集してください。")
                text = input("  編集: ").strip()
                if not text:
                    continue

            print(f"\n  投稿します... ", end="", flush=True)
            try:
                result = post_reply(text, tweet_id)
                new_id = result.get("data", {}).get("id", "?")
                print(f"✅ 完了 (ID: {new_id})")
                total_replied += 1
                time.sleep(POST_DELAY)
            except Exception as e:
                print(f"❌ エラー: {e}")

    print(f"\n{'=' * 60}")
    print(f"  完了！本日のリプライ数: {total_replied} 件")
    print("=" * 60)


if __name__ == "__main__":
    run()
