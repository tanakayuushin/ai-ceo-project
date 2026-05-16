#!/usr/bin/env python3
"""
X API v2 でツイートのメトリクス（インプレッション・いいね等）を取得し、
パフォーマンス分析レポートを生成するスクリプト。

毎週日曜に GitHub Actions から自動実行される。
"""

import os
import sys
import json
import re
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


def pct(s):
    return urllib.parse.quote(str(s), safe='')


def build_oauth_header(method, url, ck, cs, at, ats, query_params=None):
    timestamp = str(int(time.time()))
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    oauth_params = {
        'oauth_consumer_key': ck,
        'oauth_nonce': nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': timestamp,
        'oauth_token': at,
        'oauth_version': '1.0',
    }

    all_params = dict(oauth_params)
    if query_params:
        all_params.update(query_params)

    param_str = '&'.join(
        pct(k) + '=' + pct(v) for k, v in sorted(all_params.items())
    )
    base_str = '&'.join([method.upper(), pct(url), pct(param_str)])
    signing_key = pct(cs) + '&' + pct(ats)

    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()

    oauth_params['oauth_signature'] = sig

    header_parts = [
        pct(k) + '="' + pct(v) + '"'
        for k, v in sorted(oauth_params.items())
    ]
    return 'OAuth ' + ', '.join(header_parts)


def fetch_tweet_metrics(tweet_ids, ck, cs, at, ats):
    if not tweet_ids:
        return []

    base_url = 'https://api.twitter.com/2/tweets'
    query_params = {
        'ids': ','.join(tweet_ids[:100]),
        'tweet.fields': 'public_metrics,created_at',
    }

    query_str = urllib.parse.urlencode(query_params)
    url = f'{base_url}?{query_str}'

    auth = build_oauth_header('GET', base_url, ck, cs, at, ats, query_params)

    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', auth)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx) as res:
            data = json.loads(res.read().decode())
            return data.get('data', [])
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f'HTTP Error {e.code}: {err}', file=sys.stderr)
        return []


def extract_posts_from_md_files(x_posts_dir):
    posts = {}
    for md_file in sorted(x_posts_dir.glob('*.md')):
        if md_file.name in ('post-log.md',):
            continue

        content = md_file.read_text(encoding='utf-8')

        id_match = re.search(r'投稿結果.*?ID[:\s（]+(\d{15,})', content)
        if not id_match:
            id_match = re.search(r'ID[:\s（]+(\d{15,})', content)
        if not id_match:
            continue

        tweet_id = id_match.group(1)

        topic_match = re.search(r'\*\*トピック\*\*[：:]\s*(.+)', content)
        topic = topic_match.group(1).strip() if topic_match else md_file.stem

        text_match = re.search(r'## 投稿文\s+(.+?)(?:\n---|\n\*\*)', content, re.DOTALL)
        text_preview = text_match.group(1).strip()[:40] if text_match else ''

        posts[tweet_id] = {
            'date': md_file.stem,
            'topic': topic,
            'text_preview': text_preview,
        }

    return posts


def categorize_topic(topic_str):
    t = topic_str.lower()
    if 'tips' in t or 'コツ' in t or 'プロンプト' in t:
        return 'tips'
    elif 'story' in t or 'ストーリー' in t:
        return 'story'
    elif 'case' in t or '事例' in t:
        return 'case_study'
    elif 'subsidy' in t or '補助金' in t:
        return 'subsidy'
    elif 'how' in t or '始め方' in t or '議事録' in t or '採用' in t:
        return 'how_to_start'
    elif 'encouragement' in t or '励まし' in t:
        return 'encouragement'
    elif 'misconception' in t or '誤解' in t:
        return 'misconception'
    elif 'cta' in t or '診断' in t:
        return 'cta'
    else:
        return 'other'


CAT_NAMES = {
    'tips':          '💡 Tips（活用のコツ）',
    'story':         '📖 Story（ストーリー）',
    'case_study':    '🏭 事例紹介',
    'subsidy':       '💰 補助金情報',
    'how_to_start':  '🚀 始め方',
    'encouragement': '💪 励まし',
    'misconception': '❌ 誤解解消',
    'cta':           '📣 CTA（診断案内）',
    'other':         'その他',
}


def generate_report(post_info, metrics_data, output_path):
    metrics_by_id = {m['id']: m for m in metrics_data}

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    records = []
    category_stats = {}

    for tweet_id, info in post_info.items():
        if tweet_id not in metrics_by_id:
            continue

        pm = metrics_by_id[tweet_id].get('public_metrics', {})
        impressions    = pm.get('impression_count', 0)
        likes          = pm.get('like_count', 0)
        retweets       = pm.get('retweet_count', 0)
        replies        = pm.get('reply_count', 0)
        engagement_rate = (likes + retweets + replies) / max(impressions, 1) * 100

        category = categorize_topic(info.get('topic', ''))

        records.append({
            'date':           info.get('date', ''),
            'topic':          info.get('topic', ''),
            'text_preview':   info.get('text_preview', ''),
            'category':       category,
            'tweet_id':       tweet_id,
            'impressions':    impressions,
            'likes':          likes,
            'retweets':       retweets,
            'replies':        replies,
            'engagement_rate': engagement_rate,
        })

        if category not in category_stats:
            category_stats[category] = {'impressions': [], 'likes': [], 'engagement': []}
        category_stats[category]['impressions'].append(impressions)
        category_stats[category]['likes'].append(likes)
        category_stats[category]['engagement'].append(engagement_rate)

    records.sort(key=lambda x: x['date'], reverse=True)

    cat_summary = sorted(
        [
            {
                'category':        cat,
                'count':           len(s['impressions']),
                'avg_impressions': sum(s['impressions']) / len(s['impressions']),
                'avg_likes':       sum(s['likes']) / len(s['likes']),
                'avg_engagement':  sum(s['engagement']) / len(s['engagement']),
            }
            for cat, s in category_stats.items()
        ],
        key=lambda x: x['avg_impressions'],
        reverse=True,
    )

    lines = [
        '# X投稿 パフォーマンス分析レポート',
        '',
        f'**最終更新**: {now}  ',
        f'**分析対象**: {len(records)}件の投稿',
        '',
        '---',
        '',
        '## カテゴリ別パフォーマンス（平均）',
        '',
        '| カテゴリ | 件数 | 平均インプレッション | 平均いいね | エンゲージメント率 |',
        '|---------|------|---------------------|-----------|------------------|',
    ]

    for cs in cat_summary:
        name = CAT_NAMES.get(cs['category'], cs['category'])
        lines.append(
            f"| {name} | {cs['count']} | {cs['avg_impressions']:.0f} | "
            f"{cs['avg_likes']:.1f} | {cs['avg_engagement']:.2f}% |"
        )

    top5 = sorted(records, key=lambda x: x['impressions'], reverse=True)[:5]

    lines += [
        '',
        '## トップ5投稿（インプレッション順）',
        '',
        '| 日付 | カテゴリ | 投稿内容（冒頭） | インプレッション | いいね | RT |',
        '|------|---------|----------------|----------------|-------|-----|',
    ]
    for r in top5:
        cat_name = CAT_NAMES.get(r['category'], r['category'])
        preview = r['text_preview'].replace('|', '｜')
        lines.append(
            f"| {r['date']} | {cat_name} | {preview}… | "
            f"{r['impressions']:,} | {r['likes']} | {r['retweets']} |"
        )

    lines += [
        '',
        '## 全投稿データ',
        '',
        '| 日付 | カテゴリ | インプレッション | いいね | RT | エンゲージメント率 |',
        '|------|---------|----------------|-------|----|--------------------|',
    ]
    for r in records:
        cat_name = CAT_NAMES.get(r['category'], r['category'])
        lines.append(
            f"| {r['date']} | {cat_name} | {r['impressions']:,} | "
            f"{r['likes']} | {r['retweets']} | {r['engagement_rate']:.2f}% |"
        )

    # 改善提言
    if cat_summary:
        best = cat_summary[0]
        worst = cat_summary[-1] if len(cat_summary) > 1 else None

        lines += [
            '',
            '## 改善提言',
            '',
            f"- **最高パフォーマンス**: {CAT_NAMES.get(best['category'])} "
            f"（平均 {best['avg_impressions']:.0f} imp / {best['avg_likes']:.1f} likes）",
        ]
        if worst:
            lines.append(
                f"- **改善余地あり**: {CAT_NAMES.get(worst['category'])} "
                f"（平均 {worst['avg_impressions']:.0f} imp / {worst['avg_likes']:.1f} likes）"
            )
        lines += [
            '',
            '### 次週コンテンツへの反映方針',
            '',
            f"1. **好調カテゴリを増やす**: `{CAT_NAMES.get(best['category'])}` 系を週3本中2本に",
            '2. **投稿時間の継続評価**: 9時・12時・18時の各スロットのエンゲージメントを追跡',
            '3. **ハッシュタグの改善**: トップ5投稿のハッシュタグパターンを次週に踏襲',
            '',
            '*次回自動更新: 翌週日曜日 10:00 JST*',
        ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'レポート生成完了: {output_path} ({len(records)}件)')
    return len(records)


if __name__ == '__main__':
    ck  = os.environ.get('X_CONSUMER_KEY', '')
    cs  = os.environ.get('X_CONSUMER_SECRET', '')
    at  = os.environ.get('X_ACCESS_TOKEN', '')
    ats = os.environ.get('X_ACCESS_TOKEN_SECRET', '')

    if not ck:
        print('Error: X_CONSUMER_KEY が設定されていません', file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).parent.parent.parent
    x_posts_dir  = project_root / 'departments' / 'marketing' / 'x-posts'
    output_path  = project_root / 'data' / 'reports' / 'x-analytics.md'

    post_info = extract_posts_from_md_files(x_posts_dir)
    print(f'投稿ファイルから {len(post_info)}件のツイートIDを取得')

    if not post_info:
        print('ツイートIDが見つかりません。終了します。')
        sys.exit(0)

    metrics = fetch_tweet_metrics(list(post_info.keys()), ck, cs, at, ats)
    print(f'X APIからメトリクス取得: {len(metrics)}件')

    if not metrics:
        print('メトリクスを取得できませんでした（APIアクセスレベルを確認してください）')
        sys.exit(1)

    count = generate_report(post_info, metrics, output_path)
    print(f'完了: {count}件のデータを処理しました')
