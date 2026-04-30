#!/usr/bin/env python3
"""
X (Twitter) API v2 投稿スクリプト
標準ライブラリのみ使用（pip install 不要）

使い方:
  export X_CONSUMER_KEY="..."
  export X_CONSUMER_SECRET="..."
  export X_ACCESS_TOKEN="..."
  export X_ACCESS_TOKEN_SECRET="..."
  python tools/post_to_x.py "投稿したいテキスト"
"""

import sys
import os
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


def pct(s):
    return urllib.parse.quote(str(s), safe='')


def build_oauth_header(method, url, ck, cs, at, ats):
    timestamp = str(int(time.time()))
    nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    params = {
        'oauth_consumer_key':     ck,
        'oauth_nonce':            nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp':        timestamp,
        'oauth_token':            at,
        'oauth_version':          '1.0',
    }

    param_str = '&'.join(
        pct(k) + '=' + pct(v) for k, v in sorted(params.items())
    )
    base_str    = '&'.join([method.upper(), pct(url), pct(param_str)])
    signing_key = pct(cs) + '&' + pct(ats)

    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()
    ).decode()

    params['oauth_signature'] = sig

    header_parts = [
        pct(k) + '="' + pct(v) + '"'
        for k, v in sorted(params.items())
    ]
    return 'OAuth ' + ', '.join(header_parts)


def post_tweet(text):
    ck  = os.environ.get('X_CONSUMER_KEY', '')
    cs  = os.environ.get('X_CONSUMER_SECRET', '')
    at  = os.environ.get('X_ACCESS_TOKEN', '')
    ats = os.environ.get('X_ACCESS_TOKEN_SECRET', '')

    if not ck:
        print('Error: X_CONSUMER_KEY が設定されていません', file=sys.stderr)
        sys.exit(1)

    url  = 'https://api.twitter.com/2/tweets'
    body = json.dumps({'text': text}).encode('utf-8')
    auth = build_oauth_header('POST', url, ck, cs, at, ats)

    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Authorization', auth)
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read().decode())
            tweet_id = result.get('data', {}).get('id', '')
            print('投稿成功: ID = ' + tweet_id)
            return tweet_id
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print('HTTP Error ' + str(e.code) + ': ' + err, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '--file':
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            text = f.read().strip()
    elif len(sys.argv) >= 2:
        text = sys.argv[1]
    else:
        text = sys.stdin.read().strip()

    if not text:
        print('Error: 投稿テキストが空です', file=sys.stderr)
        sys.exit(1)

    tweet_id = post_tweet(text)
    sys.exit(0 if tweet_id else 1)
