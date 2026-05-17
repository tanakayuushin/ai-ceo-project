#!/usr/bin/env python3
"""
X プロフィール更新スクリプト
bio（自己紹介文）・location・website URL を X API v2 で更新する

使い方:
  python tools/social-media/x_update_profile.py

必要な環境変数:
  X_CONSUMER_KEY, X_CONSUMER_SECRET
  X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
"""

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


def oauth1_header(method, url, body_params, consumer_key, consumer_secret, token, token_secret):
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
    all_params = {**body_params, **oauth_params}
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


# ============================================================
# プロフィール設定（ここを編集）
# ============================================================
PROFILE = {
    "name": "アレン｜Emport AI CEO",
    "description": (
        "🤖 中小企業のAI導入を支援｜Emport AI CEO\n"
        "📋 補助金を使ったAI活用が専門（IT導入補助金・省力化補助金）\n"
        "🏭 製造・建設・飲食・小売業の経営者向け\n"
        "💬 無料AI相談受付中 → リンク先から予約"
    ),
    "location": "山口県",
    "url": "https://web-production-e1bc3.up.railway.app",
}
# ============================================================


def update_profile(creds):
    url = "https://api.twitter.com/1.1/account/update_profile.json"
    params = {
        'name': PROFILE['name'],
        'description': PROFILE['description'],
        'location': PROFILE['location'],
        'url': PROFILE['url'],
    }
    body = urllib.parse.urlencode(params).encode()
    auth = oauth1_header(
        'POST', url, params,
        creds['consumer_key'], creds['consumer_secret'],
        creds['access_token'], creds['access_token_secret']
    )
    req = urllib.request.Request(url, data=body, headers={
        'Authorization': auth,
        'Content-Type': 'application/x-www-form-urlencoded',
    }, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()
        print(f"APIエラー ({e.code}): {body_err}")
        return None


def main():
    creds = {
        'consumer_key': os.getenv('X_CONSUMER_KEY', ''),
        'consumer_secret': os.getenv('X_CONSUMER_SECRET', ''),
        'access_token': os.getenv('X_ACCESS_TOKEN', ''),
        'access_token_secret': os.getenv('X_ACCESS_TOKEN_SECRET', ''),
    }
    if not all(creds.values()):
        print("❌ 環境変数が未設定です。X_CONSUMER_KEY 等を設定してください。")
        return

    print("=== X プロフィール更新 ===")
    print(f"表示名: {PROFILE['name']}")
    print(f"bio  : {PROFILE['description'][:50]}...")
    print(f"場所  : {PROFILE['location']}")
    print(f"URL  : {PROFILE['url']}")
    print()

    result = update_profile(creds)
    if result:
        print(f"✅ 更新成功！@{result.get('screen_name')} のプロフィールを更新しました。")
    else:
        print("❌ 更新失敗。APIエラーを確認してください。")


if __name__ == '__main__':
    main()
