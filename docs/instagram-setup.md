# Instagram自動投稿 セットアップ手順

**所要時間: 約20分（一度やれば60日間有効）**

---

## 前提条件チェック

- [x] Instagramアカウントが **クリエイターまたはビジネス** に切り替え済み
- [ ] InstagramをFacebookページに接続済み
- [x] Meta Developersアプリ「Emport AI Social」作成済み（App ID: 1942533017149464）

---

## Step 1: InstagramをFacebookページに接続する

Instagramの Graph API は **Facebookページとの接続が必須** です。

1. **Facebookページを作成**（未作成の場合）
   - https://www.facebook.com/pages/create にアクセス
   - 「ビジネスまたはブランド」を選択
   - ページ名: `Emport AI` で作成

2. **InstagramとFacebookページを接続**
   - Instagramアプリを開く
   - プロフィール → 設定 → アカウントの種類とツール
   - 「プロアカウントに切り替える」またはクリエイター設定
   - 「Facebookをリンク」→ 作成したページを選択

---

## Step 2: アクセストークンを取得する

### 2-1. Graph API Explorerにアクセス
https://developers.facebook.com/tools/explorer/?app_id=1942533017149464

### 2-2. アプリを確認
- 右上の「Metaアプリ」が **Emport AI Social** になっていることを確認

### 2-3. パーミッションを追加
「許可を追加」の入力欄に以下を**1つずつ**入力してEnter（またはクリックで選択）：

```
instagram_basic
instagram_content_publish
pages_show_list
pages_read_engagement
```

### 2-4. Generate Access Token をクリック
- ポップアップが開く
- 「Emport AI Social の利用を続ける」→「許可」をクリック
- トークンがコピーされる

### 2-5. 長期トークンに変換（60日有効）
短期トークンは1時間で失効するため、以下のコマンドで60日トークンに変換：

```bash
python tools/social-media/refresh_ig_token.py SHORT_LIVED_TOKEN
```

または手動でcurl:
```bash
curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=1942533017149464&client_secret=d2a265f0df24e2c7898a65d24daeb72e&fb_exchange_token=SHORT_LIVED_TOKEN_HERE"
```

レスポンス例：
```json
{"access_token": "EAAxxxxxx（長いトークン）", "token_type": "bearer"}
```

---

## Step 3: Instagram User IDを取得する

アクセストークンを取得後、以下のURLにアクセス（トークンを置き換えて）:

```
https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_TOKEN
```

または Graph API Explorer で `/me/accounts` を送信。

レスポンスから `instagram_business_account > id` を取得する。

---

## Step 4: imgbb APIキーを取得する

1. https://imgbb.com/signup で無料アカウント作成
2. https://api.imgbb.com/ からAPIキーを取得
3. 月50MB・無料・クレジットカード不要

---

## Step 5: GitHub Secretsに設定する

https://github.com/YOUR_REPO/settings/secrets/actions に以下を追加:

| Secret名 | 値 |
|----------|-----|
| `IG_USER_ID` | Step 3で取得したUser ID |
| `IG_ACCESS_TOKEN` | Step 2-5で取得した長期トークン |
| `IMGBB_API_KEY` | Step 4で取得したAPIキー |

---

## Step 6: 動作テスト

```bash
# ローカルでテスト（実際には投稿しない）
IG_USER_ID=xxx IG_ACCESS_TOKEN=xxx IMGBB_API_KEY=xxx \
  python tools/social-media/post_to_instagram.py --image test.jpg --caption "テスト" --dry-run
```

---

## トークン更新について

**60日ごとに更新が必要**。以下のコマンドで延長できます：

```bash
curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=1942533017149464&client_secret=d2a265f0df24e2c7898a65d24daeb72e&fb_exchange_token=CURRENT_LONG_TOKEN"
```

新しいトークンをGitHub Secretsの `IG_ACCESS_TOKEN` に更新してください。

---

*最終更新: 2026-05-19 / CEO アレン*
