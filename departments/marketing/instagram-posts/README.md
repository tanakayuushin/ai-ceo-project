# Instagram投稿管理

## 使い方

### 1. 投稿を準備する
`pending/` フォルダに以下2ファイルをセットで置く：

```
pending/
  2026-05-20_ai-tip.jpg      ← 投稿する画像（1:1 正方形推奨）
  2026-05-20_ai-tip.txt      ← キャプション（ハッシュタグ含む）
```

### 2. キャプション例（.txt ファイル）
```
中小企業のAI活用、何から始めますか？

✅ まず「繰り返し作業」を洗い出す
✅ AI導入コストより「人件費削減効果」を計算する
✅ 小さく始めて、成果が出たら拡大する

Emport AIでは無料相談を受け付けています👇
プロフィールのリンクからどうぞ

#中小企業DX #AI活用 #山口県 #スタートアップ #EmportAI
```

### 3. 自動投稿のタイミング
GitHub Actions が以下の時間に自動投稿します（JST）：
- 7:00 / 10:00 / 13:00

## フォルダ構成

```
instagram-posts/
├── pending/     ← 投稿待ち（ここに画像+txtを置く）
├── posted/      ← 投稿済み（自動移動される）
└── YYYY-MM-DD.md ← 投稿ログ（自動生成）
```

## 必要なGitHub Secrets

| Secret名 | 説明 |
|----------|------|
| IG_USER_ID | Instagram Business User ID |
| IG_ACCESS_TOKEN | 長期アクセストークン（60日有効） |
| IMGBB_API_KEY | imgbb.com APIキー（画像ホスト用） |

## 初回セットアップ → docs/instagram-setup.md を参照
