#!/usr/bin/env python3
"""
X API v2 で山口県の中小企業・経営者アカウントを検索し、
フォロー候補リストを生成するスクリプト。
"""

import os
import sys
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
import ssl
from pathlib import Path
from datetime import datetime
from collections import defaultdict

OWN_AUTHOR_ID = "2046457694509502464"

SEARCH_QUERIES = [
    ("山口県 経営者 -is:retweet",                "山口県経営者"),
    ("山口県 中小企業 AI -is:retweet",           "山口県中小企業AI"),
    ("下関 OR 宇部 OR 山口市 経営 -is:retweet",  "山口市内経営"),
    ("山口県 DX 中小企業 -is:retweet",           "山口DX"),
    ("山口 社長 OR 代表 -is:retweet",            "山口社長"),
    ("#山口県 経営 -is:retweet",                  "山口県ハッシュタグ"),
    ("周南 OR 防府 OR 萩 経営者 -is:retweet",    "周南防府萩経営"),
]


def pct(s):
    return urllib.parse.quote(str(s), safe='')


def build_oauth_header(method, url, ck, cs, at, ats, query_params=None):
    timestamp = str(int(time.time()))
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    oauth = {
        'oauth_consumer_key':     ck,
        'oauth_nonce':            nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp':        timestamp,
        'oauth_token':            at,
        'oauth_version':          '1.0',
    }
    all_p = dict(oauth)
    if query_params:
        all_p.update(query_params)
    param_str = '&'.join(pct(k) + '=' + pct(v) for k, v in sorted(all_p.items()))
    base_str  = '&'.join([method.upper(), pct(url), pct(param_str)])
    signing   = pct(cs) + '&' + pct(ats)
    sig = base64.b64encode(
        hmac.new(signing.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()
    oauth['oauth_signature'] = sig
    return 'OAuth ' + ', '.join(
        pct(k) + '="' + pct(v) + '"' for k, v in sorted(oauth.items())
    )


def api_get(endpoint, params, ck, cs, at, ats):
    url  = endpoint + '?' + urllib.parse.urlencode(params)
    auth = build_oauth_header('GET', endpoint, ck, cs, at, ats, params)
    req  = urllib.request.Request(url)
    req.add_header('Authorization', auth)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'  HTTP {e.code}: {body[:150]}', file=sys.stderr)
        return {}
    except Exception as e:
        print(f'  Error: {e}', file=sys.stderr)
        return {}


def search_tweets(query, ck, cs, at, ats):
    return api_get(
        'https://api.twitter.com/2/tweets/search/recent',
        {
            'query':       query,
            'tweet.fields':'author_id,created_at,text',
            'expansions':  'author_id',
            'user.fields': 'username,name,description,location,public_metrics',
            'max_results': '10',
        },
        ck, cs, at, ats,
    )


def score_account(user):
    """山口県関連・中小企業経営者らしさをスコアリング"""
    score = 0
    bio   = (user.get('description') or '').lower()
    loc   = (user.get('location') or '').lower()
    name  = (user.get('name') or '').lower()
    pm    = user.get('public_metrics', {})
    followers = pm.get('followers_count', 0)
    following = pm.get('following_count', 0)

    # 山口県関連キーワード
    yamaguchi_words = ['山口', '下関', '宇部', '防府', '周南', '萩', '岩国', '光市', '柳井', '長門']
    for w in yamaguchi_words:
        if w in loc or w in bio or w in name:
            score += 3

    # 経営者・中小企業キーワード
    biz_words = ['社長', '代表', '経営', '創業', '起業', '中小企業', 'CEO', '取締役', '事業', '会社']
    for w in biz_words:
        if w in bio or w in name:
            score += 2

    # AI・DX関連
    tech_words = ['ai', 'dx', 'デジタル', '効率化', '自動化', 'it', 'システム']
    for w in tech_words:
        if w in bio:
            score += 1

    # フォロワー数ボーナス（地方中小企業として適切な範囲）
    if 100 <= followers <= 10000:
        score += 2
    elif followers > 10000:
        score += 1

    # フォロー比率（スパムアカウント除外）
    if following > 0 and followers / max(following, 1) > 0.1:
        score += 1

    return score


def generate_follow_list(candidates, output_path):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # スコア順にソート
    ranked = sorted(candidates.values(), key=lambda x: x['score'], reverse=True)

    # カテゴリ分類
    high_priority   = [u for u in ranked if u['score'] >= 6]
    medium_priority = [u for u in ranked if 3 <= u['score'] < 6]
    low_priority    = [u for u in ranked if u['score'] < 3]

    lines = [
        '# X フォロー候補リスト（山口県 中小企業・経営者）',
        '',
        f'**作成日**: {now}  ',
        f'**候補総数**: {len(ranked)}件',
        '',
        '> スコアリング基準: 山口県関連地名(+3) / 経営者キーワード(+2) / AI・DX(+1) / フォロワー数(+2) / フォロー比率(+1)',
        '',
        '---',
        '',
        f'## 🔴 優先フォロー（スコア6以上）: {len(high_priority)}件',
        '',
        '| アカウント | 名前 | フォロワー | 場所 | プロフィール（冒頭） | スコア |',
        '|-----------|------|-----------|------|---------------------|-------|',
    ]

    for u in high_priority:
        bio_short = (u.get('description') or '')[:30].replace('|', '｜').replace('\n', ' ')
        lines.append(
            f"| @{u['username']} | {u['name']} | "
            f"{u.get('public_metrics', {}).get('followers_count', 0):,} | "
            f"{u.get('location', '')} | {bio_short} | {u['score']} |"
        )

    lines += [
        '',
        f'## 🟡 通常フォロー（スコア3〜5）: {len(medium_priority)}件',
        '',
        '| アカウント | 名前 | フォロワー | 場所 | プロフィール（冒頭） | スコア |',
        '|-----------|------|-----------|------|---------------------|-------|',
    ]

    for u in medium_priority:
        bio_short = (u.get('description') or '')[:30].replace('|', '｜').replace('\n', ' ')
        lines.append(
            f"| @{u['username']} | {u['name']} | "
            f"{u.get('public_metrics', {}).get('followers_count', 0):,} | "
            f"{u.get('location', '')} | {bio_short} | {u['score']} |"
        )

    lines += [
        '',
        f'## ⚪ 低優先度（スコア2以下）: {len(low_priority)}件',
        '',
        '| アカウント | 名前 | フォロワー | スコア |',
        '|-----------|------|-----------|-------|',
    ]

    for u in low_priority[:20]:  # 上位20件のみ
        lines.append(
            f"| @{u['username']} | {u['name']} | "
            f"{u.get('public_metrics', {}).get('followers_count', 0):,} | {u['score']} |"
        )

    lines += [
        '',
        '---',
        '',
        '## フォロー実行メモ',
        '',
        '- **推奨ペース**: 1日30〜50件（スパム判定回避）',
        '- **優先順序**: 🔴 → 🟡 の順でフォロー',
        '- **フォロバ確認**: 1週間後にフォロバなしアカウントはフォロー解除を検討',
        '',
        f'*次回更新予定: 翌週（新規候補を追加）*',
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'フォローリスト生成: {output_path}')
    return len(ranked)


if __name__ == '__main__':
    ck  = os.environ.get('X_CONSUMER_KEY', '')
    cs  = os.environ.get('X_CONSUMER_SECRET', '')
    at  = os.environ.get('X_ACCESS_TOKEN', '')
    ats = os.environ.get('X_ACCESS_TOKEN_SECRET', '')

    if not ck:
        print('Error: X_CONSUMER_KEY が設定されていません', file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).parent.parent.parent
    output_path  = project_root / 'departments' / 'marketing' / 'x-follow-list.md'

    candidates = {}   # user_id → user dict + score

    for query, label in SEARCH_QUERIES:
        print(f'検索: {label}')
        time.sleep(1)
        result = search_tweets(query, ck, cs, at, ats)

        users = {u['id']: u for u in result.get('includes', {}).get('users', [])}

        for tweet in result.get('data', []):
            author_id = tweet.get('author_id', '')
            if author_id == OWN_AUTHOR_ID:
                continue
            if author_id not in users:
                continue
            user = users[author_id]
            if author_id not in candidates:
                user['score'] = score_account(user)
                user['queries'] = []
                candidates[author_id] = user
            candidates[author_id]['queries'].append(label)

        print(f'  → {len(users)}件のユーザー取得')

    # 重複除去後の件数
    print(f'合計候補: {len(candidates)}件')

    count = generate_follow_list(candidates, output_path)
    print(f'完了: {count}件のフォロー候補リストを生成')
