# Emport AI アプリ ビルド・リリースガイド

## 開発環境の確認

- Node.js v24 ✅
- Expo SDK 54 ✅
- React Native 0.81.5 ✅

---

## Step 1: ローカル動作確認

```bash
cd apps/emport-ai-app

# Expo Goアプリで確認（最速）
npm start

# → QRコードをExpo GoアプリでスキャンするとiPhone/Androidで即確認できる
# Expo Go: https://expo.dev/go
```

---

## Step 2: Expo EAS でビルド（Google Play向けAAB）

### 2-1. EAS CLIをインストール
```bash
npm install -g eas-cli
eas login  # Expoアカウントでログイン
```

### 2-2. EAS設定を初期化
```bash
cd apps/emport-ai-app
eas build:configure
```

### 2-3. eas.json を作成（下記内容）
```json
{
  "cli": { "version": ">= 7.0.0" },
  "build": {
    "production": {
      "android": {
        "buildType": "app-bundle"
      }
    },
    "preview": {
      "android": {
        "buildType": "apk"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

### 2-4. Androidビルド実行
```bash
# テスト用APK（実機確認）
eas build --platform android --profile preview

# 本番AAB（Google Play提出用）
eas build --platform android --profile production
```

---

## Step 3: Google Play 提出

### 3-1. Google Play Console 準備
1. https://play.google.com/console にアクセス
2. デベロッパー登録（初回のみ$25）
3. 「アプリを作成」→ アプリ名「Emport AI」

### 3-2. ストア掲載情報を入力
- STORE_LISTING.md の内容を参照
- スクリーンショット5枚をアップロード
- フィーチャーグラフィック（1024×500px）をアップロード

### 3-3. AABをアップロード
1. 「リリース」→「製品版」→「新しいリリースを作成」
2. EASビルドで生成された .aab ファイルをアップロード
3. リリースノートを入力

### 3-4. 審査提出
- コンテンツレーティング: ビジネス
- ターゲット年齢: 全年齢
- データ安全: ネットワーク通信（Claude API）を申告

---

## Step 4: プライバシーポリシーの作成

Google Playへの提出には**プライバシーポリシーのURL**が必須です。

最低限の内容:
```
・収集するデータ: APIキー（端末内のみ保存）、チャット内容（Anthropic APIに送信）
・データの共有: Anthropicのみ（AI処理のため）
・データの保持: ユーザーがアプリを削除すると消去
・お問い合わせ: tsubeyou081@gmail.com
```

既存のウェブサイト (https://emport-ai.vercel.app/) にプライバシーポリシーページを追加することを推奨。

---

## Google Playランキング戦略（ASO）

### 高評価を得るための初期戦略

1. **知人・関係者に最初の評価をお願いする**（5つ星×10件が最初の目標）
2. **キーワード最適化**: タイトルと説明文に主要キーワードを含める
3. **更新頻度を上げる**: 月1回以上のアップデートがランキングに有利
4. **スクリーンショット品質**: 実際の使用シーンを鮮明に見せる

### 狙うキーワード（検索ボリューム高）
- 「補助金 アプリ」
- 「経営相談 AI」
- 「中小企業 AI」
- 「ものづくり補助金」

---

## トラブルシューティング

### ビルドエラー: gradle 関連
```bash
cd android && ./gradlew clean
```

### TypeScriptエラー
```bash
npx tsc --noEmit
```

### パッケージの競合
```bash
npm install --legacy-peer-deps
```
