#!/usr/bin/env python3
"""
X (Twitter) エンゲージメント追跡スクリプト
投稿済みツイートのいいね・RT・返信数を取得してレポートに記録する

使い方:
  python tools/social-media/x_analytics.py

必要な環境変数（GitHub Secrets または Windows 環境変数）:
  X_CONSUMER_KEY, X_CONSUMER_SECRET
  X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
  X_USER_ID (自分のユーザーID — 数字。@ユーザー名ではない)
"""

import os
import re
import json
import hmac
import hashlib
import base64
import time
import random
import string
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

POSTS_DIR = Path(__file__).parent.parent.parent / "departments/marketing/x-posts"
REPORT_PATH = POSTS_DIR / "engagement-report.md"

JST = timezone(timedelta(hours=9))


def pct(s):
    return urllib.parse.quote(str(s), safe='')


def oauth1_header(method, url, params, consumer_key, consumer_secret, token, token_secret):
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    ts = str(int(time.time()))
    oauth_params = {
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': ts,
        'oauth_token': token,
        'oauth_version': '1.0',
    }
    all_params = {**params, **oauth_params}
    param_str = '&'.join(f'{pct(k)}={pct(v)}' for k, v in sorted(all_params.items()))
    base_str = f'{method}&{pct(url)}&{pct(param_str)}'
    signing_key = f'{pct(consumer_secret)}&{pct(token_secret)}'
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params['oauth_signature'] = sig
    header = 'OAuth ' + ', '.join(
        f'{pct(k)}="{pct(v)}"' for k, v in sorted(oauth_params.items())
    )
    return header


def get_tweet_metrics(tweet_id, credentials):
    """X API v2 でツイートのメトリクスを取得"""
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    params = {
        "tweet.fields": "public_metrics,created_at,text",
    }
    query_str = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_str}"

    auth = oauth1_header(
        'GET', url, params,
        credentials['consumer_key'], credentials['consumer_secret'],
        credentials['access_token'], credentials['access_token_secret']
    )
    req = urllib.request.Request(full_url, headers={
        'Authorization': auth,
        'Content-Type': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get('data', {})
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  APIエラー ({e.code}): {body[:100]}")
        return None
    except Exception as e:
        print(f"  エラー: {e}")
        return None


def collect_posted_ids():
    """投稿済み .md ファイルからツイートIDと日付を収集"""
    results = []
    for md_file in sorted(POSTS_DIR.glob("*.md")):
        text = md_file.read_text(encoding='utf-8')
        match = re.search(r'成功.*ID[:\s＝=]+(\d{15,20})', text)
        if match:
            tweet_id = match.group(1)
            date_str = md_file.stem  # e.g. 2026-05-17-12
            results.append({
                'file': md_file.name,
                'date': date_str,
                'tweet_id': tweet_id,
            })
    return results


def generate_report(entries):
    """エンゲージメントレポートをMarkdownで生成"""
    now = datetime.now(JST).strftime('%Y-%m-%d %H:%M JST')
    lines = [
        "# X エンゲージメントレポート",
        "",
        f"**最終更新**: {now}  ",
        f"**集計対象**: {len(entries)} 件の投稿済みツイート",
        "",
        "---",
        "",
        "## 投稿別パフォーマンス",
        "",
        "| 日時 | いいね | RT | 返信 | インプレッション | ツイートID |",
        "|------|--------|-----|------|-----------------|------------|",
    ]

    total_likes = total_rt = total_replies = total_imp = 0
    api_available = True

    for e in entries:
        metrics = e.get('metrics')
        if metrics is None:
            api_available = False
            row = f"| {e['date']} | - | - | - | - | {e['tweet_id']} |"
        else:
            pm = metrics.get('public_metrics', {})
            likes = pm.get('like_count', 0)
            rt = pm.get('retweet_count', 0)
            replies = pm.get('reply_count', 0)
            imp = pm.get('impression_count', 0)
            total_likes += likes
            total_rt += rt
            total_replies += replies
            total_imp += imp
            row = f"| {e['date']} | {likes} | {rt} | {replies} | {imp} | {e['tweet_id']} |"
        lines.append(row)

    lines += [
        "",
        "---",
        "",
        "## 累計サマリー",
        "",
    ]

    if api_available and entries:
        lines += [
            f"- **総いいね数**: {total_likes}",
            f"- **総RT数**: {total_rt}",
            f"- **総返信数**: {total_replies}",
            f"- **総インプレッション**: {total_imp}",
            f"- **平均いいね/投稿**: {total_likes / len(entries):.1f}",
            f"- **平均RT/投稿**: {total_rt / len(entries):.1f}",
        ]
    else:
        lines += [
            "> ⚠️ X API Free tierでは `public_metrics` の取得に制限があります。",
            "> X Developer Portal で Basic または Pro プランへのアップグレードが必要です。",
            "> 現在はツイートIDのみ記録。手動でX Analyticsを確認してください。",
            "",
            "**手動確認先**: https://analytics.twitter.com",
        ]

    lines += [
        "",
        "---",
        "",
        "## コンテンツ別傾向（手動記録欄）",
        "",
        "| カテゴリ | 平均いいね | 評価 | メモ |",
        "|----------|-----------|------|------|",
        "| 事例紹介 | - | - | |",
        "| 補助金情報 | - | - | |",
        "| AI活用Tips | - | - | |",
        "| 誤解シリーズ | - | - | |",
        "| 励まし系 | - | - | |",
        "| 質問・アンケート | - | - | |",
        "",
        "*毎週更新: GitHub Actionsで自動実行（要設定）*",
    ]

    return "\n".join(lines)


def main():
    creds = {
        'consumer_key': os.getenv('X_CONSUMER_KEY', ''),
        'consumer_secret': os.getenv('X_CONSUMER_SECRET', ''),
        'access_token': os.getenv('X_ACCESS_TOKEN', ''),
        'access_token_secret': os.getenv('X_ACCESS_TOKEN_SECRET', ''),
    }
    has_creds = all(creds.values())

    print("=== X エンゲージメント追跡 ===")
    posted = collect_posted_ids()
    print(f"投稿済みツイート: {len(posted)} 件")

    if has_creds:
        print("APIキー確認済み。メトリクスを取得中...")
        for entry in posted:
            print(f"  取得中: {entry['date']} (ID: {entry['tweet_id']})", end='')
            metrics = get_tweet_metrics(entry['tweet_id'], creds)
            entry['metrics'] = metrics
            if metrics:
                pm = metrics.get('public_metrics', {})
                print(f" → ❤️{pm.get('like_count',0)} 🔁{pm.get('retweet_count',0)}")
            else:
                print(" → 取得失敗")
            time.sleep(1)  # レート制限対策
    else:
        print("⚠️ APIキーが未設定。IDのみ記録します。")
        for entry in posted:
            entry['metrics'] = None

    report = generate_report(posted)
    REPORT_PATH.write_text(report, encoding='utf-8')
    print(f"\nレポート保存完了: {REPORT_PATH}")


if __name__ == '__main__':
    main()
