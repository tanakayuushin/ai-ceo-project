#!/usr/bin/env python3
"""
X（Twitter）競合・バズ投稿分析スクリプト。

関連ハッシュタグで上位投稿を取得し、
・カテゴリ別エンゲージメント傾向
・バズっている投稿の文体・構成パターン
・注目アカウント
・自社コンテンツへの応用提言
を生成する。

毎週日曜に GitHub Actions から x_analytics.yml と合わせて自動実行。
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


OWN_AUTHOR_ID = "2046457694509502464"   # tanakayuushin のユーザーID

SEARCH_QUERIES = [
    ("#AI活用 #中小企業 -is:retweet",        "AI活用×中小企業"),
    ("#DX推進 #中小企業 -is:retweet",         "DX推進×中小企業"),
    ("AI 業務効率化 中小企業 -is:retweet",    "AI業務効率化"),
    ("#補助金 AI 中小企業 -is:retweet",        "補助金×AI"),
    ("AI 導入事例 中小企業 -is:retweet",       "AI導入事例"),
]

MAX_RESULTS = 10   # 1クエリあたり（Free/Basicは最大10〜100）


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
    base_str  = '&'.join(['GET', pct(url), pct(param_str)])
    signing   = pct(cs) + '&' + pct(ats)
    sig = base64.b64encode(
        hmac.new(signing.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()

    oauth['oauth_signature'] = sig
    return 'OAuth ' + ', '.join(
        pct(k) + '="' + pct(v) + '"' for k, v in sorted(oauth.items())
    )


def search_tweets(query, ck, cs, at, ats, max_results=10):
    base_url = 'https://api.twitter.com/2/tweets/search/recent'
    params = {
        'query':         query,
        'tweet.fields':  'public_metrics,author_id,created_at,text',
        'expansions':    'author_id',
        'user.fields':   'username,name,public_metrics',
        'max_results':   str(max_results),
    }

    url  = base_url + '?' + urllib.parse.urlencode(params)
    auth = build_oauth_header('GET', base_url, ck, cs, at, ats, params)

    req = urllib.request.Request(url)
    req.add_header('Authorization', auth)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f'  検索エラー {e.code}: {e.read().decode()[:200]}', file=sys.stderr)
        return {}
    except Exception as e:
        print(f'  エラー: {e}', file=sys.stderr)
        return {}


def extract_features(text):
    """投稿テキストの特徴を抽出"""
    features = {
        'length':       len(text),
        'has_number':   bool(re.search(r'\d+', text)),
        'has_percent':  bool(re.search(r'\d+%|％', text)),
        'has_arrow':    bool(re.search(r'→|⇒|▶', text)),
        'has_case':     bool(re.search(r'事例|導入|効率|削減|短縮', text)),
        'has_story':    bool(re.search(r'社長と話した|経営者.*話|先月|先週|先日', text)),
        'has_question': bool(re.search(r'[？?]', text)),
        'has_list':     bool(re.search(r'[①②③・\n・]', text)),
        'has_mistake':  bool(re.search(r'誤解|違います|実は', text)),
        'has_subsidy':  bool(re.search(r'補助金|助成金', text)),
        'has_cta':      bool(re.search(r'無料|診断|お問い|DM|連絡', text)),
        'hashtag_count': len(re.findall(r'#\S+', text)),
        'line_count':    text.count('\n') + 1,
    }
    return features


def classify_post(text, features):
    """投稿のカテゴリ分類"""
    if features['has_story']:
        return 'story'
    if features['has_case']:
        return 'case_study'
    if features['has_subsidy']:
        return 'subsidy'
    if features['has_mistake']:
        return 'misconception'
    if features['has_cta']:
        return 'cta'
    if features['has_question']:
        return 'tips_qa'
    return 'tips'


CAT_NAMES = {
    'story':        '📖 ストーリー型',
    'case_study':   '🏭 事例紹介型',
    'subsidy':      '💰 補助金情報型',
    'misconception':'❌ 誤解解消型',
    'cta':          '📣 CTA型',
    'tips_qa':      '❓ Tips QA型',
    'tips':         '💡 Tips型',
}


def generate_report(all_posts, user_map, output_path):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 自社投稿を除外
    competitor_posts = [p for p in all_posts if p.get('author_id') != OWN_AUTHOR_ID]

    if not competitor_posts:
        print('競合投稿が見つかりませんでした')
        return 0

    # エンゲージメント計算＋特徴抽出
    analyzed = []
    for p in competitor_posts:
        pm   = p.get('public_metrics', {})
        text = p.get('text', '')
        feat = extract_features(text)
        cat  = classify_post(text, feat)
        eng  = pm.get('like_count', 0) + pm.get('retweet_count', 0) * 2 + pm.get('reply_count', 0)
        user = user_map.get(p.get('author_id', ''), {})
        analyzed.append({
            'id':         p.get('id', ''),
            'author_id':  p.get('author_id', ''),
            'username':   user.get('username', ''),
            'name':       user.get('name', ''),
            'text':       text,
            'category':   cat,
            'features':   feat,
            'likes':      pm.get('like_count', 0),
            'retweets':   pm.get('retweet_count', 0),
            'replies':    pm.get('reply_count', 0),
            'engagement': eng,
            'created_at': p.get('created_at', ''),
        })

    analyzed.sort(key=lambda x: x['engagement'], reverse=True)

    # カテゴリ別集計
    cat_stats = defaultdict(lambda: {'count': 0, 'total_eng': 0, 'total_likes': 0})
    for a in analyzed:
        cat = a['category']
        cat_stats[cat]['count']       += 1
        cat_stats[cat]['total_eng']   += a['engagement']
        cat_stats[cat]['total_likes'] += a['likes']

    cat_summary = sorted(
        [
            {
                'category':   cat,
                'count':      s['count'],
                'avg_eng':    s['total_eng']  / s['count'],
                'avg_likes':  s['total_likes'] / s['count'],
            }
            for cat, s in cat_stats.items()
        ],
        key=lambda x: x['avg_eng'],
        reverse=True,
    )

    # 特徴相関分析（いいねが高い投稿の共通特徴）
    top_posts  = analyzed[:max(1, len(analyzed) // 3)]
    all_feats  = ['has_number', 'has_percent', 'has_arrow', 'has_story',
                  'has_question', 'has_list', 'has_case', 'has_subsidy']
    feat_score = {}
    for f in all_feats:
        rate = sum(1 for p in top_posts if p['features'].get(f)) / len(top_posts)
        feat_score[f] = rate

    feat_names = {
        'has_number':   '数字・数値あり',
        'has_percent':  '％・パーセントあり',
        'has_arrow':    '→や⇒の矢印あり',
        'has_story':    'ストーリー形式（社長と話した等）',
        'has_question': '問いかけ形式',
        'has_list':     '箇条書き形式',
        'has_case':     '事例・削減・効率などのキーワード',
        'has_subsidy':  '補助金・助成金キーワード',
    }

    avg_len      = sum(p['features']['length'] for p in top_posts) / len(top_posts)
    avg_hashtags = sum(p['features']['hashtag_count'] for p in top_posts) / len(top_posts)

    # 注目アカウント（エンゲージメント上位）
    author_eng = defaultdict(lambda: {'total': 0, 'count': 0, 'username': '', 'name': ''})
    for a in analyzed:
        aid = a['author_id']
        author_eng[aid]['total']    += a['engagement']
        author_eng[aid]['count']    += 1
        author_eng[aid]['username']  = a['username']
        author_eng[aid]['name']      = a['name']

    top_accounts = sorted(
        [
            {
                'username': v['username'],
                'name':     v['name'],
                'posts':    v['count'],
                'avg_eng':  v['total'] / v['count'],
            }
            for v in author_eng.values() if v['username']
        ],
        key=lambda x: x['avg_eng'],
        reverse=True,
    )[:5]

    # レポート生成
    lines = [
        '# X 競合・バズ投稿 分析レポート',
        '',
        f'**最終更新**: {now}  ',
        f'**分析投稿数**: {len(competitor_posts)}件（自社投稿除く）',
        '',
        '---',
        '',
        '## カテゴリ別エンゲージメント（高い順）',
        '',
        '| カテゴリ | 件数 | 平均エンゲージメント | 平均いいね |',
        '|---------|------|---------------------|-----------|',
    ]
    for cs in cat_summary:
        lines.append(
            f"| {CAT_NAMES.get(cs['category'], cs['category'])} | {cs['count']} "
            f"| {cs['avg_eng']:.1f} | {cs['avg_likes']:.1f} |"
        )

    # バズ投稿トップ10
    top10 = analyzed[:10]
    lines += [
        '',
        '## バズ投稿 トップ10',
        '',
        '| エンゲージ | いいね | RT | アカウント | 投稿内容（冒頭50字） |',
        '|-----------|-------|----|-----------|--------------------|',
    ]
    for p in top10:
        preview = p['text'].replace('\n', ' ').replace('|', '｜')[:50]
        uname   = f"@{p['username']}" if p['username'] else p['author_id']
        lines.append(
            f"| {p['engagement']} | {p['likes']} | {p['retweets']} | {uname} | {preview}… |"
        )

    # 注目アカウント
    if top_accounts:
        lines += [
            '',
            '## 注目アカウント（エンゲージメント上位）',
            '',
            '| アカウント | 投稿数（取得分） | 平均エンゲージメント |',
            '|-----------|----------------|---------------------|',
        ]
        for a in top_accounts:
            lines.append(
                f"| @{a['username']}（{a['name']}） | {a['posts']} | {a['avg_eng']:.1f} |"
            )

    # バズる投稿の特徴
    lines += [
        '',
        '## バズる投稿の共通特徴（上位1/3の投稿から抽出）',
        '',
        f'- **平均文字数**: {avg_len:.0f}字',
        f'- **平均ハッシュタグ数**: {avg_hashtags:.1f}個',
        '',
        '| 特徴 | 上位投稿での出現率 |',
        '|------|-----------------|',
    ]
    for f, rate in sorted(feat_score.items(), key=lambda x: x[1], reverse=True):
        bar = '█' * int(rate * 10) + '░' * (10 - int(rate * 10))
        lines.append(f"| {feat_names[f]} | {bar} {rate*100:.0f}% |")

    # 自社コンテンツへの応用提言
    best_cat  = cat_summary[0] if cat_summary else None
    top_feats = [f for f, r in feat_score.items() if r >= 0.6]

    lines += ['', '## 自社コンテンツへの応用提言', '']

    if best_cat:
        lines.append(
            f"1. **カテゴリ優先度**: `{CAT_NAMES.get(best_cat['category'])}` が最も高エンゲージメント。"
            f"週3本中2本はこの形式を優先する"
        )

    feat_advice = {
        'has_number':  '「〇名」「〇時間→〇分」など具体的な数字を必ず入れる',
        'has_percent': '「〇%削減」「最大〇%補助」など割合を使う',
        'has_arrow':   '変化を「→」で可視化する（Before/After形式）',
        'has_story':   '「先日、〇〇と話した」で始めるストーリー形式を増やす',
        'has_question': '問いかけで始める（「〜知っていますか？」）',
        'has_list':    '箇条書きで情報を整理する（①②③形式）',
    }
    count = 2
    for f in top_feats:
        if f in feat_advice:
            lines.append(f"{count}. **{feat_names[f]}**: {feat_advice[f]}")
            count += 1

    if top_accounts:
        accounts_str = ' / '.join([f"@{a['username']}" for a in top_accounts[:3]])
        lines.append(
            f"{count}. **参考アカウント**: {accounts_str} の投稿フォーマットを定期的に参照する"
        )

    lines += [
        '',
        '---',
        '',
        '*次回自動更新: 翌週日曜日 10:00 JST*',
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'競合分析レポート生成: {output_path} ({len(analyzed)}件)')
    return len(analyzed)


if __name__ == '__main__':
    ck  = os.environ.get('X_CONSUMER_KEY', '')
    cs  = os.environ.get('X_CONSUMER_SECRET', '')
    at  = os.environ.get('X_ACCESS_TOKEN', '')
    ats = os.environ.get('X_ACCESS_TOKEN_SECRET', '')

    if not ck:
        print('Error: X_CONSUMER_KEY が設定されていません', file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).parent.parent.parent
    output_path  = project_root / 'data' / 'reports' / 'x-competitor-analysis.md'

    all_posts = []
    user_map  = {}

    for query, label in SEARCH_QUERIES:
        print(f'検索中: {label}')
        time.sleep(1)   # レート制限対策
        result = search_tweets(query, ck, cs, at, ats, MAX_RESULTS)

        tweets = result.get('data', [])
        all_posts.extend(tweets)
        print(f'  → {len(tweets)}件取得')

        for user in result.get('includes', {}).get('users', []):
            user_map[user['id']] = user

    # 重複除去
    seen = set()
    unique_posts = []
    for p in all_posts:
        if p['id'] not in seen:
            seen.add(p['id'])
            unique_posts.append(p)

    print(f'合計 {len(unique_posts)}件（重複除去後）')

    count = generate_report(unique_posts, user_map, output_path)
    print(f'完了: {count}件分析')
