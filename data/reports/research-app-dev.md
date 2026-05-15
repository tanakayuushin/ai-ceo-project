# アプリ開発 調査レポート — 自律リサーチ

> 調査開始: 2026-05-14  
> 対象: Emport AI モバイルアプリ（React Native / Expo）の開発・リリース・最適化に関する技術情報

---

## 1. Expo SDK 53 & React Native 0.79 最新情報

**調査日時: 2026-05-14 (第1ラウンド)**

### Expo SDK 53 主要変更点（2026年最新）

| 機能 | 内容 | Emport AIへの影響 |
|---|---|---|
| **New Architecture デフォルト有効** | Fabric+TurboModules+JSIが全アプリで標準 | パフォーマンス大幅改善 |
| **React Native 0.79** | Hermes V1.0標準搭載 | 起動速度40%向上 |
| **React 19統合** | Suspense・エラー処理改善 | コード品質向上 |
| **Edge-to-Edge（Android）** | フルスクリーンUI標準化 | UIリデザイン必要 |
| **expo-audio（安定版）** | expo-avから移行推奨 | 音声機能使用時は移行 |
| **expo-maps（alpha）** | Google Maps/Apple Maps統合API | 将来の地図機能に活用 |
| **リモートビルドキャッシュ** | 同一ビルドを再コンパイルしない | EASビルド時間25%削減 |

### New Architecture のパフォーマンス実測データ

```
移行後の実測（業界平均）:
  冷起動時間: -40%（従来比）
  UIレンダリング速度: +35%
  メモリ使用量: -25%
  JS→Native呼び出しレイテンシ: -40倍（JSIによる直接呼び出し）
```

### Emport AIへの即時アクション

```bash
# SDK 53にアップグレード
npx expo install expo@latest

# New Architecture有効確認（SDK53以降はデフォルトON）
# app.json
{
  "expo": {
    "experiments": {
      "newArchEnabled": true
    }
  }
}
```

**情報源:**
- [Expo SDK 53 公式リリースノート](https://expo.dev/changelog/sdk-53)
- [React Native New Architecture ガイド](https://docs.expo.dev/guides/new-architecture/)
- [React Native Expo 2026 完全ガイド](https://farooxium.dev/blog/react-native-expo-2026-guide)

---

## 2. React Native パフォーマンス最適化 2026年版

**調査日時: 2026-05-14 (第1ラウンド)**

### 最重要最適化テクニック（優先順）

**【Priority 1】New Architecture 有効化（最大インパクト）**
```
効果: UIレンダリング+35%、起動-40%、メモリ-25%
方法: SDK53以降はデフォルトON → 何もしなくてよい
注意: サードパーティライブラリのNew Architecture対応を確認
```

**【Priority 2】FlashList（リスト最適化）**
```bash
npx expo install @shopify/flash-list

# FlatListの置き換え（チャット履歴等）
import { FlashList } from "@shopify/flash-list";

# 効果: FlatListの5〜10倍高速
# Emport AIのチャット履歴リストに最適
```

**【Priority 3】React.memo / useMemo / useCallback**
```typescript
// 子コンポーネントの不要な再レンダリングを防止
const ChatMessage = React.memo(({ message }: Props) => {
  return <Text>{message.content}</Text>;
});

// 計算コストが高い処理をキャッシュ
const sortedMessages = useMemo(
  () => messages.sort((a, b) => a.timestamp - b.timestamp),
  [messages]
);
```

**【Priority 4】アニメーション最適化**
```typescript
// ❌ NG: JSスレッドでアニメーション
Animated.timing(value, { toValue: 1 }).start();

// ✅ OK: Nativeドライバー使用
Animated.timing(value, {
  toValue: 1,
  useNativeDriver: true  // ← これ必須
}).start();

// ✅ さらに良い: Reanimated 3（ジェスチャー対応）
import Animated, { useSharedValue, withTiming } from 'react-native-reanimated';
```

**【Priority 5】画像最適化**
```bash
# expo-imageはReact Nativeの標準Imageより2〜3倍高速
npx expo install expo-image

# 使い方
import { Image } from 'expo-image';
<Image source={uri} contentFit="cover" transition={200} />
```

### Hermes エンジンの効果

```
Hermes 1.0（SDK53標準）:
  - ビルド時にJSをバイトコードにコンパイル
  - 起動速度: JSC比+40%
  - メモリ効率: 長時間セッションで-25%
  - JSIで bridge不要 → Native呼び出しが3倍速
```

**情報源:**
- [React Native Performance Optimization 2026 Playbook](https://www.rapidnative.com/blogs/react-native-performance-optimization-2026-playbook)
- [25 React Native Best Practices 2026](https://www.esparkinfo.com/blog/react-native-best-practices)

---

## 3. App Store / Google Play 提出チェックリスト 2026年版

**調査日時: 2026-05-14 (第1ラウンド)**

### iOS App Store 提出前チェックリスト

**コード・設定**
```
□ Bundle Identifier が Apple Developer と一致
□ App Version / Build Number を更新
□ 本番用APIキー・URLに切り替え済み
□ console.log を本番から削除（またはdisable）
□ Hermes有効
□ New Architecture有効
□ デバッグモード無効
□ Privacy Manifest（PrivacyInfo.xcprivacy）作成済み ← 2024年必須
```

**App Store Connect メタデータ**
```
□ アプリ名（30文字以内）
□ サブタイトル（30文字以内）
□ 説明文（4000文字以内）
□ キーワード（100文字以内）
□ カテゴリ選択（Business / Productivity）
□ スクリーンショット（iPhone 6.9"・6.5"・5.5"）
□ アプリアイコン（1024×1024px PNG）
□ プライバシーポリシーURL
□ サポートURL
□ データセーフティ宣言（NSF = Nutrition Safety Form）
```

**審査対策**
```
□ 「AIが最適な答えを保証する」等の断定表現を削除
□ 免責表示「AIの回答は参考情報です」を追加
□ テスト用アカウント・手順をReviewer Notesに記載
□ 実機でクラッシュなし確認
□ 全ネットワーク権限に理由を記載（Info.plist）
```

**審査時間**: 通常24〜48時間

### Android Google Play 提出前チェックリスト

**ビルド**
```
□ Android App Bundle（.aab）形式でビルド
□ リリース署名キー設定済み（keystore）
□ VersionCode と VersionName を更新
□ minSdkVersion: 24以上推奨
□ targetSdkVersion: 最新（34以上）
```

**Google Play Console メタデータ**
```
□ アプリ名（30文字以内）
□ 説明文（4000文字以内）
□ スクリーンショット（最低2枚）
□ フィーチャーグラフィック（1024×500px）
□ アイコン（512×512px）
□ プライバシーポリシーURL
□ データセーフティセクション記入
□ コンテンツレーティング（自己申告）
```

**新規デベロッパー向け追加要件（2024年〜）**
```
□ クローズドテスター12名以上を確保
□ 14日以上のクローズドテスト実施
□ テスト完了後に本番リリース申請
```

**審査時間**: 通常24時間

**情報源:**
- [App Store Submission Checklist 2026 (contextark.com)](https://contextark.com/blog/app-store-submission-checklist-2026)
- [Expo React Native App Store 提出ガイド](https://codebrahma.com/publish-expo-react-native-app-to-app-stores/)

---

## 4. Expo Router v4 ナビゲーション設計

**調査日時: 2026-05-14 (第1ラウンド)**

### ファイルベースルーティングの基本構造

```
apps/emport-ai-app/app/
├── _layout.tsx          ← ルートレイアウト（認証・テーマ等）
├── index.tsx            ← ホーム画面
├── (auth)/              ← 認証グループ
│   ├── _layout.tsx
│   ├── login.tsx
│   └── register.tsx
├── (tabs)/              ← メインタブ
│   ├── _layout.tsx      ← Tab Navigator
│   ├── chat.tsx         ← チャット（メイン）
│   ├── history.tsx      ← 相談履歴
│   ├── tools.tsx        ← ツール
│   └── settings.tsx     ← 設定
└── modal/               ← モーダル画面
    └── subscription.tsx ← サブスク購入
```

### Emport AIの推奨ナビゲーション設計

```typescript
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{
      tabBarStyle: { backgroundColor: '#1a1a2e' },
      tabBarActiveTintColor: '#6c63ff',
    }}>
      <Tabs.Screen name="chat" options={{ title: '相談', tabBarIcon: ... }} />
      <Tabs.Screen name="history" options={{ title: '履歴', tabBarIcon: ... }} />
      <Tabs.Screen name="tools" options={{ title: 'ツール', tabBarIcon: ... }} />
      <Tabs.Screen name="settings" options={{ title: '設定', tabBarIcon: ... }} />
    </Tabs>
  );
}
```

### 認証フロー設計（推奨パターン）

```typescript
// app/_layout.tsx
import { useAuth } from '@/hooks/useAuth';
import { Redirect } from 'expo-router';

export default function RootLayout() {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Redirect href="/(auth)/login" />;
  }
  
  return <Stack />;
}
```

**情報源:**
- [Expo Router ナビゲーションパターン（公式）](https://docs.expo.dev/router/basics/common-navigation-patterns/)
- [Expo Router 2026 完全ガイド](https://www.codesofphoenix.com/articles/expo/expo-router-nav)

---

## 5. 次のリサーチ課題（第1ラウンド終了）

第2ラウンドで調査予定：
1. **状態管理（Zustand vs Redux vs Jotai）** — 2026年最新の選択基準
2. **Expo EAS Build CI/CD設定** — 自動ビルド・デプロイパイプライン
3. **React Native テスト戦略** — Jest・Detox・Maestroの使い分け
4. **アプリのセキュリティ対策** — APIキー管理・証明書ピンニング
5. **オフライン対応・データキャッシュ** — AsyncStorage・MMKV・SQLite比較

---

*調査継続中。ユーザーが「いい」と言うまで次のトピックを調査して追記します。*

---

## 6. 状態管理ライブラリ 2026年比較 — Zustand vs Jotai vs Redux

**調査日時: 2026-05-14 (第2ラウンド)**

### 2026年の結論

```
Zustandが最もバランスが良く、ほぼ全プロジェクトで推奨
  バンドルサイズ: Zustand ~1KB / Jotai ~2.5KB / Redux ~15KB
  更新速度(1000コンポーネント): Zustand 12ms / Jotai 14ms / Redux 18ms
```

### 選択基準

| 状況 | 推奨 | 理由 |
|---|---|---|
| **小〜中規模（Emport AIに最適）** | **Zustand** | シンプルAPI・学習コスト低・バンドル小 |
| 複雑な依存関係の状態 | Jotai | アトム型・Suspense対応 |
| 大規模チーム・厳格な構造 | Redux Toolkit | パターン強制・デバッグツール充実 |

### Zustand 基本実装（Emport AI向け）

```typescript
// store/chatStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  industry: string;
  addMessage: (msg: Message) => void;
  setLoading: (loading: boolean) => void;
  setIndustry: (industry: string) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isLoading: false,
      industry: '汎用',
      addMessage: (msg) =>
        set((state) => ({ messages: [...state.messages, msg] })),
      setLoading: (loading) => set({ isLoading: loading }),
      setIndustry: (industry) => set({ industry }),
    }),
    {
      name: 'emport-ai-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

**情報源:**
- [React Native State Management 2026: Zustand vs Jotai vs Redux](https://www.oflight.co.jp/en/columns/react-native-state-management-2026)
- [State Management 2026 比較 (DEV Community)](https://dev.to/jsgurujobs/state-management-in-2026-zustand-vs-jotai-vs-redux-toolkit-vs-signals-2gge)

---

## 7. EAS Build × GitHub Actions — 自動ビルド・CI/CDパイプライン

**調査日時: 2026-05-14 (第2ラウンド)**

### EAS の全体像

```
EAS（Expo Application Services）:
  EAS Build   → クラウドでiOS/Androidを自動ビルド
  EAS Submit  → ビルド後にストアへ自動提出
  EAS Update  → OTA（Over-the-Air）でコード更新
  EAS Workflows → GitHub Actionsとの統合CI/CD
```

### GitHub Actions 設定

```yaml
# .github/workflows/eas-build.yml
name: EAS Build
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm install
        working-directory: ./apps/emport-ai-app
      - run: eas build --platform all --non-interactive
        working-directory: ./apps/emport-ai-app
```

### リモートビルドキャッシュ（SDK53新機能・25%高速化）

```json
// eas.json
{
  "build": {
    "production": {
      "experiments": { "remoteBuildCache": true }
    }
  }
}
```

**情報源:**
- [EAS Build CI 設定（Expo公式）](https://docs.expo.dev/build/building-on-ci/)
- [EAS Workflows × GitHub Actions](https://expo.dev/blog/how-to-integrate-eas-workflows-with-github-actions)

---

## 8. React Native テスト戦略 2026年版

**調査日時: 2026-05-14 (第2ラウンド)**

### テストピラミッド（推奨配分）

```
70% — Unit Tests（Jest）     → ロジック・API呼び出し
20% — Component Tests（RNTL）→ UIコンポーネントの振る舞い
10% — E2E Tests（Maestro）   → ユーザーフロー全体
```

### Maestro — 最も簡単なE2E（2026年推奨）

```yaml
# .maestro/chat_flow.yaml
appId: com.emportai.app
---
- launchApp
- tapOn: "相談を始める"
- inputText: "補助金について教えてください"
- tapOn: "送信"
- assertVisible: "補助金"
```

```bash
# インストール・実行
curl -Ls "https://get.maestro.mobile.dev" | bash
maestro test .maestro/chat_flow.yaml
```

### Emport AI向けテスト優先順位

```
Phase 1（最低限）:
  Jest:    APIクライアントのユニットテスト
  Maestro: チャット送信の基本フロー

Phase 2（安定化後）:
  RNTL:    主要コンポーネントのレンダリングテスト
  Maestro: オンボーディング・設定画面フロー
```

**情報源:**
- [React Native Testing 2026: Jest, Detox, Maestro比較](https://hashnode.com/posts/react-native-testing-in-2026-jest-detox-and-maestro-compared/69fb478e50ecad4533331c4f)
- [Maestro E2E Testing 2026](https://addjam.com/blog/2026-02-18/our-experience-adding-e2e-testing-react-native-maestro/)

---

## 9. ストレージ選択 2026年版 — MMKV vs AsyncStorage vs SQLite

**調査日時: 2026-05-14 (第2ラウンド)**

### 比較表

| ライブラリ | 速度 | 上限 | 暗号化 | 用途 |
|---|---|---|---|---|
| **MMKV** | **30倍高速（同期）** | 無制限 | AES対応 | 設定・状態保存 |
| AsyncStorage | 標準（非同期） | 6MB（Android） | なし | 簡単なデータ |
| expo-secure-store | 中速（非同期） | 2KB/item | OS Keychain | 認証トークン |
| expo-sqlite | 中速 | 無制限 | 別途設定 | 大量データ・検索 |

### Emport AI推奨ストレージ設計

```typescript
// 用途別ストレージ選択

// 1. 業種設定・UI状態 → MMKV（高速・同期）
import { MMKV } from 'react-native-mmkv';
const storage = new MMKV();
storage.set('industry', '飲食業');
const industry = storage.getString('industry'); // 同期・即座に取得

// 2. 認証トークン → expo-secure-store（OS暗号化）
import * as SecureStore from 'expo-secure-store';
await SecureStore.setItemAsync('auth_token', token);

// 3. チャット履歴 → expo-sqlite（大量データ対応）
import * as SQLite from 'expo-sqlite';
const db = SQLite.openDatabaseSync('emport.db');
```

```bash
# MMKV インストール（New Architecture対応）
npx expo install react-native-mmkv
```

**情報源:**
- [MMKV vs AsyncStorage 2026 (pkgpulse)](https://www.pkgpulse.com/guides/react-native-mmkv-vs-async-storage-vs-expo-secure-store-2026)
- [react-native-mmkv GitHub](https://github.com/mrousavy/react-native-mmkv)

---

## 10. セキュリティ実装 2026年版 — APIキー管理・SSL Pinning

**調査日時: 2026-05-14 (第2ラウンド)**

### 大原則：APIキーをクライアントに置かない

```
Emport AIの現在の設計（正解）:
  モバイルアプリ → Railwayバックエンド → Anthropic API
  
  APIキーはサーバー側環境変数のみ。
  クライアント（アプリ）は一切知らない設計。
```

### expo-secure-store で認証トークン保護

```typescript
import * as SecureStore from 'expo-secure-store';

// iOS: Keychain / Android: Keystore に暗号化保存
await SecureStore.setItemAsync('session_token', token);
const token = await SecureStore.getItemAsync('session_token');
await SecureStore.deleteItemAsync('session_token'); // ログアウト時
```

### SSL Certificate Pinning（中〜上級）

```bash
npx expo install react-native-ssl-public-key-pinning
```

```typescript
import { initializeSslPinning } from 'react-native-ssl-public-key-pinning';

await initializeSslPinning({
  'your-railway-domain.railway.app': {
    includeSubdomains: true,
    publicKeyHashes: [
      'sha256/プライマリキーハッシュ',
      'sha256/バックアップキーハッシュ', // ローテーション対応
    ],
  },
});
```

### Emport AIセキュリティチェックリスト

```
✅ 実装済み:
  - APIキーはサーバーサイド（Railway）のみ
  - HTTPS通信（Railway標準）

⚠️ 要実装:
  - expo-secure-store でセッショントークン保護
  - 入力値のサニタイズ（XSS対策）
  - プライバシーポリシーページ

🔜 将来的に:
  - SSL Certificate Pinning
  - 2要素認証（有料機能実装時）
```

**情報源:**
- [React Native セキュリティ公式ガイド](https://reactnative.dev/docs/security)
- [SSL Pinning in React Native](https://blog.logrocket.com/how-to-implement-ssl-certificate-pinning-react-native/)

---

## 11. 次のリサーチ課題（第2ラウンド終了）

第3ラウンドで調査予定：
1. **Expo OTA Updates（Over-the-Air更新）** — アプリ再提出せずにコードを更新する方法
2. **プッシュ通知実装（Expo Notifications）** — 完全な実装ガイド
3. **アプリ内課金 vs Stripe Web** — 手数料30%問題と最適な課金設計
4. **React Native ディープリンク** — URLスキームからアプリ画面を直接開く
5. **アプリアクセシビリティ対応** — App Store審査で問われるa11y要件

---

## 12. Expo OTA Update（Over-the-Air更新）— アプリ再申請なしで更新

**調査日時: 2026-05-14 (第3ラウンド)**

### OTAアップデートとは

```
通常のアプリ更新:
  コード変更 → EASビルド → App Store審査（24-48時間）→ ユーザーへ

OTA Update（EAS Update）:
  コード変更 → eas update コマンド → 即座にユーザーへ（数分）
  
→ バグ修正・テキスト変更・UI調整を審査なしで即時リリース可能！
```

### 制約（重要）

```
OTAで更新できる:
  ✅ JavaScriptコード
  ✅ 画像・フォント等のアセット
  ✅ スタイル・テキスト・ロジック
  ✅ APIエンドポイントURL

OTAで更新できない（ネイティブ変更は新ビルドが必要）:
  ❌ 新しいライブラリのインストール（native modules）
  ❌ app.json の変更
  ❌ Permissions の追加
  ❌ SDKバージョンアップ
```

### セットアップ手順

```bash
# 1. expo-updates インストール
npx expo install expo-updates

# 2. EAS設定
eas build:configure
eas update:configure

# 3. OTAアップデート送信
eas update --branch production --message "バグ修正: チャット送信の問題を修正"

# 4. 確認
eas update:list
```

### eas.json の channel設定

```json
{
  "build": {
    "production": {
      "channel": "production"
    },
    "staging": {
      "channel": "staging"
    }
  }
}
```

### Emport AIでの活用シナリオ

```
シナリオ1: 補助金情報の更新
  「今月から新しい補助金が始まった」
  → システムプロンプトの更新をOTAで即時配信

シナリオ2: バグ修正
  「チャット画面で特定条件でクラッシュ」
  → 審査なし・即日修正を全ユーザーに配信

シナリオ3: 業種特化モード追加
  → 建設業モードをOTAで追加（ネイティブ変更なし）
```

**情報源:**
- [EAS Update 公式ドキュメント](https://docs.expo.dev/eas-update/introduction/)
- [OTA Updates ベストプラクティス (pagepro)](https://pagepro.co/blog/ota-updates-with-expo/)

---

## 13. Expo Push Notifications 実装ガイド 2026年版

**調査日時: 2026-05-14 (第3ラウンド)**

### 重要な2026年変更点

```
⚠️ SDK 53以降の重大変更:
  Expo Go では Push通知が完全に動作しなくなった
  → Development Build が必須
```

### 実装手順

```bash
# 1. ライブラリインストール
npx expo install expo-notifications expo-device expo-constants

# 2. Development Build（Expo Go不可のため）
npx expo install expo-dev-client
eas build --profile development --platform ios
```

### クライアント実装

```typescript
// hooks/usePushNotifications.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.log('実機でのみ動作します');
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    return null; // 権限拒否 → 静かに失敗
  }

  const token = await Notifications.getExpoPushTokenAsync({
    projectId: Constants.expoConfig?.extra?.eas?.projectId,
  });

  return token.data;
}
```

### サーバー（Flask/Railway）からの送信

```python
# app.py に追加
import requests

def send_push_notification(expo_push_token: str, title: str, body: str):
    """Expo Push Notification送信"""
    requests.post(
        'https://exp.host/--/api/v2/push/send',
        json={
            'to': expo_push_token,
            'title': title,
            'body': body,
            'sound': 'default',
        },
        headers={'Content-Type': 'application/json'}
    )

# 例: 週次Tips配信
# send_push_notification(token, "今週の経営Tips", "飲食業のFL比率改善法3選")
```

### 通知パーミッション取得のベストプラクティス

```
✅ アプリの価値を体感した後（Step 4のチャット後）にPermission要求
✅ 「なぜ通知が必要か」を先に説明
✅ 拒否されても機能をブロックしない
❌ 起動直後にいきなりPermission要求しない
❌ 繰り返し何度も要求しない
```

**情報源:**
- [Expo Push Notifications 公式ガイド](https://docs.expo.dev/push-notifications/push-notifications-setup/)
- [Expo Push Notifications 2026 完全ガイド (devcom.com)](https://devcom.com/tech-blog/react-native-push-notifications/)

---

## 14. アプリ内課金 vs Stripe Web — 手数料30%問題と最適解

**調査日時: 2026-05-14 (第3ラウンド)**

### 手数料比較（2026年）

| 課金方式 | 手数料 | 月額4,980円での実収 |
|---|---|---|
| Apple IAP（App Store） | **30%**（1年後15%） | 3,486円 |
| Google Play IAP | **15〜30%** | 3,486〜4,233円 |
| Stripe（Web決済） | **2.9% + 30円** | 4,806円 |
| **差額（Stripe vs Apple）** | - | **+1,320円/ユーザー** |

### 2026年の法的変化（重要）

```
2025年4月 Epic v. Apple 判決:
  → 米国のiOSアプリはWebリンクから課金ページに誘導可能に
  → Stripeを使えば30%手数料を回避できる

EUデジタル市場法（DMA）:
  → EUでも外部決済が認められるが、5%の手数料をAppleに支払う必要あり

日本：
  → 2026年現在、Apple IAP強制ルールが撤廃される動きあり
  → ただし確定ではない（要最新確認）
```

### Emport AIの推奨課金設計（2026年）

```
戦略: 「Webを入口にして30%を回避する」

Phase 1（最安全・今すぐ）:
  → Stripeの Web決済（Stripe Checkout）のみ
  → アプリ内に課金ボタンなし
  → 「プランを見る」ボタン → ブラウザのStripeページへ
  → Apple/Google の審査リスクなし・手数料2.9%のみ

Phase 2（審査通過後）:
  → iOS/Android で「外部リンク」の課金ページへ誘導
  → Epic v. Apple判決を活用（米国ユーザー向け）

Phase 3（将来・スケール後）:
  → RevenueCat（サブスク管理ライブラリ）で
    IAP + Web課金をハイブリッド管理
```

### RevenueCat（サブスク管理ライブラリ）

```bash
npx expo install react-native-purchases

# 特徴:
# - iOS IAP・Android IAP・Web課金を統一管理
# - 分析ダッシュボード付き
# - チャーン追跡・パワーユーザー特定
# - 月$119まで無料プランあり
```

**情報源:**
- [Stripe for In-App Purchases 2026 (adapty.io)](https://adapty.io/blog/can-you-use-stripe-for-in-app-purchases/)
- [RevenueCat React Native 公式](https://www.revenuecat.com/docs/getting-started/installation/reactnative)

---

## 15. 次のリサーチ課題（第3ラウンド終了）

第4ラウンドで調査予定：
1. **React Native ディープリンク / ユニバーサルリンク** — 外部からアプリ画面を直接開く
2. **アプリのアクセシビリティ（a11y）** — App Store審査で求められる対応
3. **Expo Router × 認証フロー** — JWT・セッション管理・ログイン状態の永続化
4. **React Native アプリのSEO戦略** — ASO（App Store最適化）の具体的手法
5. **Emport AI特有の技術課題** — チャット履歴の管理・長いセッションのメモリ最適化

---

## 16. ディープリンク / ユニバーサルリンク — 外部からアプリ画面を直接開く

**調査日時: 2026-05-14 (第4ラウンド)**

### 2つのディープリンク方式の比較

```
❌ カスタムURLスキーム（myapp://）:
  - 設定が最も簡単
  - アプリ未インストール時: 失敗してアプリストアへ誘導できない
  - 別アプリがschemeを奪える（セキュリティリスク）
  - iOS 14以降では制限が増加

✅ ユニバーサルリンク（iOS） / App Links（Android）:
  - https://yourdomain.com/path → アプリで開く（未インストールならWebへ）
  - ドメイン所有者のみが設定可能（安全）
  - Firebase Dynamic Linksは2025年8月に廃止 → 自前実装が必要
```

### Firebase Dynamic Links廃止（2025年8月）後の代替

```
主要な代替サービス:
  Branch.io     — ディープリンク + アトリビューション統合、React Native SDK有り
  Adjust        — 広告アトリビューション + ディープリンク
  AppsFlyer     — エンタープライズ向け

自前実装（推奨・コスト最小）:
  Expo Router + Universal Links/App Links の組み合わせ
```

### Expo Router でのユニバーサルリンク設定

```typescript
// app.json
{
  "expo": {
    "scheme": "emport-ai",
    "ios": {
      "bundleIdentifier": "ai.emport.app",
      "associatedDomains": ["applinks:emport-ai.vercel.app"]
    },
    "android": {
      "package": "ai.emport.app",
      "intentFilters": [
        {
          "action": "VIEW",
          "autoVerify": true,
          "data": [
            {
              "scheme": "https",
              "host": "emport-ai.vercel.app",
              "pathPrefix": "/app"
            }
          ],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    }
  }
}
```

### サーバー側の設定（必須）

```json
// iOS: https://emport-ai.vercel.app/.well-known/apple-app-site-association
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "TEAMID.ai.emport.app",
        "paths": ["/app/*", "/chat/*"]
      }
    ]
  }
}

// Android: https://emport-ai.vercel.app/.well-known/assetlinks.json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "ai.emport.app",
    "sha256_cert_fingerprints": ["YOUR_SHA256_FINGERPRINT"]
  }
}]
```

### Expo Router でのディープリンク受信（コード）

```typescript
// app/app/chat/[id].tsx
// URL: https://emport-ai.vercel.app/app/chat/12345
// → このファイルが自動的に開かれる

import { useLocalSearchParams } from 'expo-router';

export default function ChatScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  // id = "12345"
  return <ChatView chatId={id} />;
}
```

### デファード・ディープリンク（未インストール→インストール後に指定画面）

```
Branch.io の「Deferred Deep Linking」機能:
  1. ユーザーがリンクをタップ → アプリ未インストール → App Storeへ
  2. インストール完了後、アプリを起動
  3. Branch SDKが「最初にどの画面を開くべきか」を記憶して自動遷移
  
用途: マーケティングリンク・紹介機能・キャンペーンLP
```

### Emport AIでの活用シナリオ

```
✅ 使うべきシーン:
  - メールでチャット共有リンク送付 → タップでそのチャット画面を直接開く
  - ランディングページ → 無料トライアル登録後、アプリを自動起動
  - プッシュ通知のディープリンク → 特定の業種ページへ直接遷移
  - QRコードキャンペーン → 店舗からアプリ特定機能へ誘導
```

**情報源:**
- [Expo ディープリンク公式ドキュメント](https://docs.expo.dev/linking/overview/)
- [Expo Router ディープリンク完全ガイド（2026）](https://reactnativerelay.com/article/deep-linking-react-native-expo-router-universal-links-app-links)

---

## 17. アプリアクセシビリティ（a11y）— App Store審査で求められる要件

**調査日時: 2026-05-14 (第4ラウンド)**

### なぜ重要か

```
法的要件:
  - Americans with Disabilities Act (ADA) — 米国
  - European Accessibility Act (EAA) — EU 2025年6月施行
  - 日本: 障害者差別解消法（努力義務だが審査で確認される）

App Store審査:
  - Apple: アクセシビリティ不備でリジェクトされるケースが増加
  - VoiceOver（iOS）/ TalkBack（Android）で操作不能だとリジェクト対象
```

### React Native の主要なアクセシビリティProps

```typescript
// スクリーンリーダー向けラベル
<TouchableOpacity
  accessible={true}
  accessibilityLabel="AIチャットを送信"
  accessibilityRole="button"
  accessibilityState={{ disabled: isLoading }}
  onPress={handleSend}
>
  <Text>送信</Text>
</TouchableOpacity>

// 画像の代替テキスト
<Image
  source={avatarUri}
  accessible={true}
  accessibilityLabel="AIアシスタントのアバター"
/>

// 動的な更新をスクリーンリーダーに通知
import { AccessibilityInfo } from 'react-native';
AccessibilityInfo.announceForAccessibility('メッセージを送信しました');
```

### accessibilityRole 一覧（重要なもの）

```
"button"    — タップ可能なボタン
"link"      — 外部リンク
"header"    — セクションの見出し
"image"     — 画像
"text"      — テキスト（デフォルト）
"switch"    — ON/OFFトグル
"adjustable" — スライダー等の調整可能要素
```

### テストツール

```
開発中:
  @react-native-ama/core   — レンダリング時に違反を検出・ログ出力
  eslint-plugin-react-native-a11y — コード書き時に警告

CI/自動テスト:
  jest + @testing-library/react-native — スクリーンリーダー動作をユニットテスト

定期的な手動テスト:
  iOS: VoiceOver（設定→アクセシビリティ→VoiceOver）
  Android: TalkBack（設定→ユーザー補助→TalkBack）
```

### Emport AI での最低限対応

```typescript
// チャット入力フィールド
<TextInput
  accessible={true}
  accessibilityLabel="業種・質問を入力"
  accessibilityHint="入力後に送信ボタンをタップしてください"
  placeholder="例: 建設業の見積もり作成について"
/>

// ローディング状態
<ActivityIndicator
  accessible={true}
  accessibilityLabel="AIが回答を生成中"
/>

// reducedMotion（動きに敏感なユーザー向け）
import { useReducedMotion } from 'react-native-reanimated';
const reducedMotion = useReducedMotion();
// reducedMotion が true の場合はアニメーションを無効化
```

### Emport AIの優先対応リスト

```
🔴 必須（審査リジェクト防止）:
  - 全ボタン/タップ要素に accessibilityLabel を設定
  - 画像に accessibilityLabel を設定
  - フォーム入力に accessibilityLabel + accessibilityHint

🟡 推奨（評価向上）:
  - VoiceOver/TalkBack での手動テスト
  - ローディング状態をスクリーンリーダーに通知
  - 色だけに頼らない情報伝達（色盲対応）

🟢 余裕があれば:
  - Dynamic Type（文字サイズ変更）対応
  - reducedMotion 対応
  - Focus Management（モーダル開閉時のフォーカス制御）
```

**情報源:**
- [React Native アクセシビリティ（公式）](https://reactnative.dev/docs/accessibility)
- [React Native Accessibility Guide 2026](https://reactnativerelay.com/article/react-native-accessibility-guide-building-inclusive-apps-expo)

---

## 18. Expo Router × 認証フロー — JWT・セッション管理・ログイン状態の永続化

**調査日時: 2026-05-14 (第4ラウンド)**

### 2026年の推奨アーキテクチャ

```
Expo Router v5 の Protected Routes が認証フローの標準:
  - Stack.Protected コンポーネントで画面を条件付き保護
  - クライアントサイドで即座にリダイレクト
  - ディープリンクからアクセスされても保護が機能する
```

### ディレクトリ構成

```
app/
├── _layout.tsx          ← RootNavigator（認証状態管理の中心）
├── (auth)/              ← 未認証ユーザー向け画面
│   ├── login.tsx
│   └── register.tsx
├── (app)/               ← 認証済みユーザー向け画面
│   ├── _layout.tsx
│   ├── index.tsx        ← チャット画面
│   └── settings.tsx
└── index.tsx            ← ルートリダイレクト
```

### Stack.Protected を使った認証実装

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router';
import { useSession } from '@/hooks/useSession';

export default function RootLayout() {
  const { session, isLoading } = useSession();

  if (isLoading) return <SplashScreen />;

  return (
    <Stack>
      {/* 認証済みユーザーのみアクセス可能 */}
      <Stack.Protected guard={!!session}>
        <Stack.Screen name="(app)" />
      </Stack.Protected>

      {/* 未認証ユーザーのみアクセス可能 */}
      <Stack.Protected guard={!session}>
        <Stack.Screen name="(auth)" />
      </Stack.Protected>
    </Stack>
  );
}
```

### セッション管理（expo-secure-store を使ったJWT保存）

```typescript
// hooks/useSession.ts
import * as SecureStore from 'expo-secure-store';
import { useState, useEffect } from 'react';

const TOKEN_KEY = 'emport_ai_token';

export function useSession() {
  const [session, setSession] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // アプリ起動時にトークンを読み込み
    SecureStore.getItemAsync(TOKEN_KEY).then((token) => {
      setSession(token);
      setIsLoading(false);
    });
  }, []);

  const signIn = async (token: string) => {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
    setSession(token);
  };

  const signOut = async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    setSession(null);
  };

  return { session, isLoading, signIn, signOut };
}
```

### バックエンド（Flask）でのJWT発行

```python
# app.py (Railway上のバックエンド)
import jwt
import datetime

JWT_SECRET = os.environ.get('JWT_SECRET')

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    access_code = data.get('access_code')
    
    if access_code != os.environ.get('ACCESS_CODE'):
        return jsonify({'error': '認証コードが違います'}), 401
    
    # JWTトークンを発行（24時間有効）
    payload = {
        'user': 'authenticated',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return jsonify({'token': token})

def verify_token(token: str) -> bool:
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
```

### 認証フロー全体像

```
1. アプリ起動
   → expo-secure-store からJWT取得試行
   → トークンあり: 認証済み画面へ（(app)/）
   → トークンなし: ログイン画面へ（(auth)/login）

2. ログイン
   → アクセスコード入力 → Railwayバックエンドへ POST
   → JWTが返ってくる → expo-secure-store に保存
   → Stack.Protected が session を検知 → 自動的に(app)/へ遷移

3. API呼び出し
   → SecureStoreからJWT取得
   → Authorization: Bearer <token> ヘッダーに付与
   → バックエンドでverify_token()で検証

4. ログアウト
   → SecureStore.deleteItemAsync()
   → session = null → Stack.Protected が(auth)/へリダイレクト
```

**情報源:**
- [Expo Router 認証（公式）](https://docs.expo.dev/router/advanced/authentication/)
- [Protected Routes（公式）](https://docs.expo.dev/router/advanced/protected/)

---

## 19. ASO（App Store最適化）— 日本市場でダウンロードを最大化する

**調査日時: 2026-05-14 (第4ラウンド)**

### ASOの基本原則

```
App Store（iOS）の特徴:
  - アプリ名（30文字）・サブタイトル（30文字）・キーワード欄（100文字）が検索インデックス
  - 説明文は検索インデックスされない → ユーザー説得用に書く
  - 検索が最大の流入経路（全流入の約65%）

Google Play（Android）の特徴:
  - タイトル・短い説明・長い説明 全てが検索インデックス
  - 説明文にキーワードを自然に入れることで上位表示可能
  - 1000文字ごとに同じキーワード1回が最適密度
```

### 2026年のASOトレンド

```
1. AIによるキーワード提案
   - Apple: AI生成の「App Store Tags」が2026年より導入
   - スクリーンショット・説明文からAIが自動でタグを生成

2. ロングテールキーワードの重要性上昇
   - 「AIアシスタント」より「中小企業向けAI業務改善アシスタント」が転換率高い
   - 競合の少ないロングテールで上位を狙う戦略が2026年主流

3. エンゲージメント指標の比重増加
   - 2026年はダウンロード数よりリテンション率（DAU/MAU）がランキングに影響
   - セッション頻度・評価数・評価スコアが重要
```

### 日本市場特有の注意点

```
検索キーワードの形式:
  - ひらがな・カタカナ・漢字 それぞれで検索される
  - ローマ字入力でも変換後の日本語で検索が届く
  - 例: "AI チャット" / "AIチャット" / "ai chat" 全て別キーワード

ひらがな/カタカナの両方を登録するのが必須:
  ✅ AIアシスタント（カタカナ）
  ✅ あいあしすたんと（ひらがな）← 意外と検索される
  ✅ 人工知能（漢字）
  ✅ 業務改善（業界キーワード）
```

### Emport AI の最適なキーワード戦略

```
アプリ名（30文字）:
  "Emport AI - 中小企業向けAIアシスタント"

サブタイトル（30文字）:
  "業務改善・見積・提案書を自動作成"

キーワード欄（100文字、カンマ区切り）:
  AI,業務効率化,中小企業,チャットGPT,見積書,提案書,
  コンサル,経営,自動化,AIアシスタント,ビジネス

説明文の冒頭（重要 — 最初の3行が展開前に表示される）:
  "中小企業の業務を最大80%効率化するAIアシスタント。
   建設業・製造業・小売業など業種に特化したAIが、
   見積もり・提案書・報告書を数秒で自動作成します。"
```

### ビジュアル最適化（インストール率への影響大）

```
スクリーンショット戦略:
  - 最初の3枚が最重要（プレビューで表示される）
  - キャプションテキストを入れる（画面だけでは伝わらない）
  - Before/After で効果を視覚化

App プレビュー動画（最大30秒）:
  - スクリーンショットより高いコンバージョンが期待できる
  - 実際の操作画面を見せる（AI回答生成の速さを見せる）
  - 最初の5秒が勝負（音なしで視聴される前提で作る）
```

### ASOツール

```
無料:
  AppFollow    — ランキング追跡・レビュー管理
  Store Maven  — スクリーンショットA/Bテスト

有料（効果高）:
  AppTweak     — 最も包括的なキーワード分析プラットフォーム
  MobileAction — 競合分析・市場シェア追跡
```

**情報源:**
- [ASO 2026 完全ガイド（ASOMobile）](https://asomobile.net/en/blog/aso-in-2026-the-complete-guide-to-app-optimization/)
- [日本市場のASO攻略（phiture）](https://phiture.com/asostack/how-to-crack-open-the-japanese-market-part-i-kwo-462bce02d69b/)

---

## 20. Emport AI特有の技術課題 — チャット履歴管理・長セッション最適化

**調査日時: 2026-05-14 (第4ラウンド)**

### チャット履歴管理の問題

```
AIチャットアプリ特有の課題:
  1. メッセージが増えるにつれてFlatListが重くなる
  2. Claude APIに送るcontext（履歴）が長くなるとトークン消費増
  3. 長セッション中のメモリリーク
  4. アプリ再起動後の履歴復元
```

### FlatList → FlashList 移行（メッセージリスト最適化）

```typescript
// Before: FlatList（重い）
<FlatList
  data={messages}
  renderItem={({ item }) => <MessageBubble message={item} />}
  keyExtractor={(item) => item.id}
  inverted  // チャットは下から上に表示
/>

// After: FlashList（5-10倍高速）
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={messages}
  renderItem={({ item }) => <MessageBubble message={item} />}
  estimatedItemSize={80}  // メッセージの推定高さ
  keyExtractor={(item) => item.id}
  inverted
/>
```

### React.memo でメッセージコンポーネントを最適化

```typescript
// MessageBubble.tsx
const MessageBubble = React.memo(({ message }: { message: Message }) => {
  return (
    <View style={styles.bubble}>
      <Text>{message.content}</Text>
      <Text style={styles.timestamp}>{message.timestamp}</Text>
    </View>
  );
}, (prevProps, nextProps) => {
  // メッセージIDが同じなら再レンダリングしない
  return prevProps.message.id === nextProps.message.id;
});
```

### Claude APIへ送るcontextの最適化

```typescript
// 全履歴をAPIに送らず最新N件に制限
const MAX_CONTEXT_MESSAGES = 20;

const buildApiMessages = (messages: Message[]) => {
  // 最新20件のみをコンテキストとして送る
  const contextMessages = messages.slice(-MAX_CONTEXT_MESSAGES);
  
  return contextMessages.map(msg => ({
    role: msg.role,  // 'user' | 'assistant'
    content: msg.content
  }));
};

// さらに最適化: 要約を使う
// 古い会話履歴を「これまでの会話の要約: ...」に置き換える
const summarizeOldMessages = async (messages: Message[]) => {
  const oldMessages = messages.slice(0, -10); // 最新10件以外
  const summary = await callClaudeAPI(
    `以下の会話を3行で要約してください: ${JSON.stringify(oldMessages)}`
  );
  return [
    { role: 'system', content: `これまでの会話の要約: ${summary}` },
    ...messages.slice(-10) // 最新10件はそのまま
  ];
};
```

### MMKV でチャット履歴を高速永続化

```typescript
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV();
const CHAT_KEY = 'chat_messages';

// 保存（AsyncStorageより30倍速い）
const saveMessages = (messages: Message[]) => {
  storage.set(CHAT_KEY, JSON.stringify(messages));
};

// 読み込み（同期的 → 画面遷移が速い）
const loadMessages = (): Message[] => {
  const data = storage.getString(CHAT_KEY);
  return data ? JSON.parse(data) : [];
};
```

### 長セッションのメモリリーク防止

```typescript
// useEffect のクリーンアップを必ず実装
useEffect(() => {
  const subscription = someEventEmitter.addListener('event', handler);
  return () => subscription.remove(); // ← クリーンアップ必須
}, []);

// 不要になったデータはnullをセット（GCを助ける）
useEffect(() => {
  return () => {
    setMessages([]); // コンポーネントアンマウント時にクリア
  };
}, []);
```

### Emport AI のチャット最適化ロードマップ

```
Phase 1（今すぐ）:
  ✅ FlashList に移行（estimatedItemSize=80）
  ✅ MessageBubble を React.memo 化
  ✅ APIに送るコンテキストを最新20件に制限

Phase 2（次のスプリント）:
  - MMKV でチャット履歴を永続化
  - セッション要約機能（古い会話を圧縮）
  - ページネーション（100件以上は遅延読み込み）

Phase 3（将来）:
  - サーバーサイドでのチャット履歴管理
  - ベクトル検索による関連過去会話の検索
  - Streaming API対応（逐次表示でUX向上）
```

**情報源:**
- [React Native Performance 2026 Playbook（RapidNative）](https://www.rapidnative.com/blogs/react-native-performance-optimization-2026-playbook)
- [Stream Chat SDK パフォーマンスガイド](https://getstream.io/chat/docs/sdk/react-native/v4/guides/performance-guide/)

---

## 21. 次のリサーチ課題（第4ラウンド終了）

第5ラウンドで調査予定：
1. **React Native アニメーション — Reanimated 4** — workletによるUI thread実行・60fps保証
2. **Expo ローカライズ（i18n）** — 多言語対応の実装方法
3. **モバイルアプリのCrash監視** — Sentry・Firebase Crashlytics設定
4. **Expo Dev Client / Development Build** — Expo Goを超えたカスタムビルド環境
5. **React Native Web対応** — 1つのコードベースでWeb+Mobile両対応

---

## 22. Reanimated 4 — workletでUIスレッド60fpsアニメーション

**調査日時: 2026-05-14 (第5ラウンド)**

### なぜ通常のアニメーションは遅いか

```
❌ JSスレッドのアニメーション（従来）:
  JS Thread → Bridge → UI Thread → 描画
  → JSスレッドが重い処理中はアニメーションが詰まる（フレームドロップ）

✅ Reanimated 4（worklet）:
  UI Thread で直接実行 → JSスレッドが何をしていても60fps維持
  New Architecture必須（Fabric対応）
```

### Reanimated 4のインストール

```bash
npx expo install react-native-reanimated
# app.json の experiments.newArchEnabled: true が前提
```

```typescript
// babel.config.js
module.exports = {
  presets: ['babel-preset-expo'],
  plugins: ['react-native-reanimated/plugin'], // 最後に追加必須
};
```

### workletの基本

```typescript
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring,
  withTiming 
} from 'react-native-reanimated';

export function AnimatedCard() {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  // useAnimatedStyle は自動的にUIスレッドで実行される
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  const handlePress = () => {
    // withSpring・withTiming もUIスレッドで動く
    scale.value = withSpring(0.95, {}, () => {
      scale.value = withSpring(1); // 押した→元に戻るアニメーション
    });
  };

  return (
    <Animated.View style={[styles.card, animatedStyle]}>
      <TouchableWithoutFeedback onPress={handlePress}>
        <View><Text>タップしてみて</Text></View>
      </TouchableWithoutFeedback>
    </Animated.View>
  );
}
```

### Reanimated 4の新機能: CSS Animations

```typescript
// Reanimated 4からCSSアニメーション構文が使えるようになった
import Animated from 'react-native-reanimated';

const styles = {
  loadingDot: {
    animationName: 'pulse',
    animationDuration: '1s',
    animationIterationCount: 'infinite',
  }
};

// CSSキーフレームをそのまま定義
// → Webのアニメーション知識がそのまま使える
```

### チャット送信アニメーション（Emport AI向け）

```typescript
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming,
  FadeInDown,
  FadeOutUp
} from 'react-native-reanimated';

// メッセージが追加される時のアニメーション
const MessageBubble = React.memo(({ message }) => {
  return (
    <Animated.View entering={FadeInDown.duration(300)}>
      <Text>{message.content}</Text>
    </Animated.View>
  );
});

// AIが考え中のドットアニメーション
export function ThinkingIndicator() {
  const dot1 = useSharedValue(0);
  const dot2 = useSharedValue(0);
  const dot3 = useSharedValue(0);

  // 各ドットを時差でバウンスさせる
  useEffect(() => {
    const bounce = (sv: SharedValue<number>, delay: number) => {
      setTimeout(() => {
        sv.value = withSpring(-8, {}, () => {
          sv.value = withSpring(0);
        });
        setInterval(() => {
          sv.value = withSpring(-8, {}, () => {
            sv.value = withSpring(0);
          });
        }, 900);
      }, delay);
    };
    bounce(dot1, 0);
    bounce(dot2, 300);
    bounce(dot3, 600);
  }, []);

  // 各ドットのスタイルをuseAnimatedStyleで制御
  // ...
}
```

### パフォーマンス比較

```
Animated API（旧）: JSスレッド依存 → 重い処理中はカクつく
Reanimated 4:      UIスレッド直接実行 → 常に60fps

推奨アニメーション手法:
  ✅ レイアウト変化: useAnimatedStyle + useSharedValue
  ✅ 画面遷移:      Expo Router の built-in transition
  ✅ ジェスチャー:  react-native-gesture-handler + Reanimated
  ❌ 非推奨:        Animated.timing（旧API・JSスレッド）
```

**情報源:**
- [Reanimated 公式ドキュメント](https://docs.swmansion.com/react-native-reanimated/docs/guides/worklets/)
- [Reanimated 4でCSSアニメーション（freeCodeCamp）](https://www.freecodecamp.org/news/how-to-create-fluid-animations-with-react-native-reanimated-v4/)

---

## 23. Expo ローカライズ（i18n）— 多言語対応

**調査日時: 2026-05-14 (第5ラウンド)**

### 2026年の推奨スタック

```
expo-localization  — デバイスの言語設定を取得
i18next            — 翻訳ランタイム（最も普及）
react-i18next      — Reactフック（useTranslation）
```

### セットアップ

```bash
npx expo install expo-localization
npm install i18next react-i18next
```

```typescript
// i18n.ts
import * as Localization from 'expo-localization';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  ja: {
    translation: {
      "welcome": "Emport AIへようこそ",
      "chat_placeholder": "業種や質問を入力してください",
      "send": "送信",
      "industry": {
        "construction": "建設業",
        "manufacturing": "製造業",
        "retail": "小売業"
      }
    }
  },
  en: {
    translation: {
      "welcome": "Welcome to Emport AI",
      "chat_placeholder": "Enter your industry or question",
      "send": "Send",
      "industry": {
        "construction": "Construction",
        "manufacturing": "Manufacturing",
        "retail": "Retail"
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    // デバイスの言語設定を自動取得
    lng: Localization.getLocales()[0].languageCode ?? 'ja',
    fallbackLng: 'ja',
    interpolation: { escapeValue: false }
  });

export default i18n;
```

```typescript
// コンポーネントでの使用
import { useTranslation } from 'react-i18next';

export function ChatScreen() {
  const { t } = useTranslation();

  return (
    <View>
      <Text>{t('welcome')}</Text>
      <TextInput placeholder={t('chat_placeholder')} />
      <Button title={t('send')} />
    </View>
  );
}
```

### Emport AIでのi18n方針

```
現状: 日本語のみ → 問題なし

将来対応が必要になる時:
  - 海外展開時（東南アジア・英語圏）
  - App Store の多言語メタデータ（ASO目的）

今すぐできる準備:
  - ハードコードされた文字列を全てi18nキーに置き換える
  - 翻訳ファイルを外部JSON化（後で追加しやすく）
```

**情報源:**
- [Expo Localization 公式](https://docs.expo.dev/versions/latest/sdk/localization/)
- [i18next + expo-localization 実装ガイド](https://medium.com/@kgkrool/implementing-internationalization-in-expo-react-native-i18next-expo-localization-8ed810ad4455)

---

## 24. Sentry — クラッシュ監視・エラートラッキング

**調査日時: 2026-05-14 (第5ラウンド)**

### Sentry vs Firebase Crashlytics 比較

```
Sentry:
  ✅ 無料: 月5,000イベントまで
  ✅ エラー詳細（スタックトレース・変数値）が見やすい
  ✅ OTA Update（EAS Update）のコンテキスト対応
  ✅ パフォーマンス監視も可能
  ✅ Expo公式に推奨されている

Firebase Crashlytics:
  ✅ 無料（制限なし）
  ✅ Androidクラッシュの詳細に強い
  ❌ React Native の詳細は少し劣る
  ❌ Expoとの統合が少し複雑

→ Emport AIには Sentry 推奨
```

### Sentry セットアップ（Expo SDK 53）

```bash
npx expo install @sentry/react-native
npx expo customize metro.config.js  # ソースマップ設定
```

```typescript
// app/_layout.tsx
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  // OTA Updateのバージョン追跡
  enableAutoSessionTracking: true,
  debug: __DEV__,
  tracesSampleRate: 0.2,  // パフォーマンス追跡（20%サンプリング）
});

export default Sentry.wrap(RootLayout);
```

```json
// app.json にSentryプラグインを追加
{
  "expo": {
    "plugins": [
      ["@sentry/react-native/expo", {
        "organization": "emport-ai",
        "project": "emport-ai-app"
      }]
    ]
  }
}
```

### エラーを手動でキャプチャ

```typescript
import * as Sentry from '@sentry/react-native';

// APIエラーをSentryに送信
try {
  const response = await fetch(API_URL);
} catch (error) {
  Sentry.captureException(error, {
    tags: { feature: 'chat', industry: currentIndustry },
    extra: { userId: user.id, messageCount: messages.length }
  });
}

// ユーザーコンテキストの設定（ログイン後）
Sentry.setUser({ id: userId });
```

### EAS Build でのソースマップ自動アップロード

```bash
# .env.local に設定
SENTRY_AUTH_TOKEN=your_auth_token

# EAS Build時に自動でソースマップがアップロードされる
# → 難読化されたコードでも読みやすいスタックトレースが取得可能
```

### 監視すべき主要指標（Emport AI）

```
Crash-Free Rate:
  目標: 99.5%以上
  警告: 99%を下回ったら即調査

主要エラー監視:
  - AIチャット応答エラー（Railway API障害）
  - 認証エラー（JWT期限切れ・ネットワーク）
  - 画面遷移エラー（Expo Routerのナビゲーション）
```

**情報源:**
- [Sentry + Expo 公式ガイド](https://docs.expo.dev/guides/using-sentry/)
- [Sentry React Native ドキュメント](https://docs.sentry.io/platforms/react-native/manual-setup/expo/)

---

## 25. Expo Dev Client (Development Build) — Expo Goを卒業する

**調査日時: 2026-05-14 (第5ラウンド)**

### Expo Go vs Development Build

```
Expo Go:
  - Expoが提供するサンドボックスアプリ
  - インストール不要でQRコードでテスト可能
  - 固定のネイティブモジュールしか使えない
  - SDK 53以降: プッシュ通知・一部決済ライブラリが使えない
  - 学習・プロトタイプに最適

Development Build:
  - 自分のアプリをDev環境用にビルドしたもの
  - 任意のネイティブモジュールが使える
  - expo-dev-client を含む（DevMenuでリロード等が可能）
  - プッシュ通知・IAP・カスタムSDKが使える
  - 本番に向けた開発に必須
```

### Development Buildの作成

```bash
# expo-dev-clientのインストール
npx expo install expo-dev-client

# EASでDevelopment Buildを作成（クラウドビルド）
eas build --profile development --platform ios
eas build --profile development --platform android

# または ローカルビルド（Mac + Xcodeが必要）
npx expo run:ios --configuration Debug
npx expo run:android
```

### eas.json の設定

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  }
}
```

### Emport AIの移行タイミング

```
Expo Goで開発継続できるうちはExpo Goで十分
以下の機能を実装し始めたらDevelopment Buildへ移行:
  ❌ プッシュ通知（SDK 53でExpo Go非対応）
  ❌ RevenueCat（ネイティブIAP）
  ❌ SSL Certificate Pinning
  ❌ カスタムネイティブモジュール

→ 現状: まだExpo Goで開発可能
→ プッシュ通知実装時にDevelopment Buildへ移行する
```

**情報源:**
- [Development Builds 公式ガイド](https://docs.expo.dev/develop/development-builds/introduction/)
- [Expo Go vs Development Builds（expo.dev）](https://expo.dev/blog/expo-go-vs-development-builds)

---

## 26. React Native Web — 1つのコードでiOS/Android/Web対応

**調査日時: 2026-05-14 (第5ラウンド)**

### Expo でWebに対応する

```bash
# Web対応は最初から含まれている（Expo managed workflow）
npx expo start --web  # ブラウザで確認

# デプロイ用ビルド
npx expo export --platform web
# → dist/ フォルダに静的ファイルが生成される
```

### 対応状況（2026年）

```
✅ 動作するもの:
  - 基本的なUIコンポーネント（View, Text, TouchableOpacity）
  - React Navigation / Expo Router
  - Expo SDK の多くのモジュール
  - Reanimated 4 (Web対応済み)
  - i18next

❌ Web非対応（モバイルのみ）:
  - expo-camera
  - react-native-mmkv（Web版は別途対応が必要）
  - プッシュ通知（Web Push Notificationsは別実装）
  - 生体認証
```

### Platform 別コード分岐

```typescript
import { Platform } from 'react-native';

// プラットフォームに応じて実装を切り替え
const saveToken = async (token: string) => {
  if (Platform.OS === 'web') {
    localStorage.setItem('token', token);
  } else {
    await SecureStore.setItemAsync('token', token);
  }
};

// Platform.select でスタイル分岐
const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.select({
      ios: 44,
      android: 24,
      web: 0,
    })
  }
});
```

### Emport AIでのWeb対応方針

```
現状の判断: モバイルファーストで開発・Web対応は後回し

理由:
  1. 中小企業向けはスマートフォンからの利用が主体
  2. Web対応で複雑さが増す（今は不要）
  3. PWA（Progressive Web App）で代替可能

将来の検討:
  - Web版ダッシュボード（管理画面）: Expo Webで実現可能
  - LP/プライバシーポリシー: 既存のVercel（静的HTML）で十分
```

**情報源:**
- [Expo Web開発ガイド（公式）](https://docs.expo.dev/workflow/web/)
- [React Native Web 2026: One Codebase, All Platforms](https://medium.com/react-native-journal/react-native-for-web-in-2025-one-codebase-all-platforms-b985d8f7db28)

---

## 27. 次のリサーチ課題（第5ラウンド終了）

第6ラウンドで調査予定：
1. **モバイルアプリのA/Bテスト** — Firebase Remote Config・機能フラグ
2. **React Native アプリのオフライン対応** — WatermelonDB・SQLite・データ同期
3. **Expo Camera / 画像認識** — OCR・名刺読み取り・業務書類デジタル化
4. **App Store レビュー管理戦略** — 良いレビューを増やす・悪いレビューへの対処
5. **React Native のデバッグ技法** — Flipper・Reactotron・新Architecture Debugger

---

## 28. A/Bテスト & 機能フラグ — Firebase Remote Config

**調査日時: 2026-05-14 (第6ラウンド)**

### 機能フラグとは

```
機能フラグ（Feature Flag）= コードを変えずにアプリの動作を変える仕組み

活用例:
  - 新UIを一部ユーザーのみに先行公開
  - A/Bテスト: タイトルAとタイトルBでどちらがCTR高いか計測
  - 問題のある機能を即座にOFFにする（リリース後のキルスイッチ）
  - 有料プランのユーザーだけに機能を見せる
```

### Firebase Remote Config セットアップ

```bash
# @react-native-firebase 全体インストール（Development Build必要）
npx expo install @react-native-firebase/app @react-native-firebase/remote-config

# または Expo公式フィーチャーフラグ（シンプル版）
# Expoドキュメント: docs.expo.dev/guides/using-feature-flags/
```

```typescript
// hooks/useRemoteConfig.ts
import remoteConfig from '@react-native-firebase/remote-config';

export async function initRemoteConfig() {
  await remoteConfig().setDefaults({
    new_chat_ui_enabled: false,      // 新しいチャットUI
    max_free_messages: 10,           // 無料メッセージ数
    show_industry_picker: true,      // 業種選択UI表示
    welcome_message: 'こんにちは！', // ウェルカムメッセージ
  });

  // 5分ごとに最新値を取得（本番環境）
  await remoteConfig().setConfigSettings({ minimumFetchIntervalMillis: 300000 });
  await remoteConfig().fetchAndActivate();
}

export function useFeatureFlag(key: string): boolean {
  return remoteConfig().getBoolean(key);
}

export function useRemoteValue(key: string): string {
  return remoteConfig().getString(key);
}
```

```typescript
// 使用例
export function ChatScreen() {
  const newUiEnabled = useFeatureFlag('new_chat_ui_enabled');
  const maxMessages = remoteConfig().getNumber('max_free_messages');

  return newUiEnabled ? <NewChatUI /> : <OldChatUI />;
}
```

### Firebase A/Bテスト設定

```
Firebaseコンソールでの設定:
  1. Remote Config → A/Bテスト作成
  2. テスト対象: 50%にnew_chat_ui_enabled=true、50%にfalse
  3. 計測指標: セッション継続時間・メッセージ送信数・有料転換率
  4. 統計的有意性が出るまで継続（通常2週間）

Emport AIでテストすべき項目:
  - ウェルカムメッセージの文章（転換率への影響）
  - 無料プランのメッセージ制限数（5件 vs 10件 vs 20件）
  - 業種選択UIの位置（最初 vs チャット中）
  - CTA（有料プランへの誘導）のコピー
```

### 軽量な代替: Expo公式フィーチャーフラグ

```typescript
// Firebase不要のシンプルな実装
// docs.expo.dev/guides/using-feature-flags/

const FEATURE_FLAGS = {
  newChatUI: process.env.EXPO_PUBLIC_FEATURE_NEW_CHAT === 'true',
  analyticsEnabled: process.env.EXPO_PUBLIC_ANALYTICS === 'true',
};

// .env.production
// EXPO_PUBLIC_FEATURE_NEW_CHAT=true
```

**情報源:**
- [React Native Feature Flags（Expo公式）](https://docs.expo.dev/guides/using-feature-flags/)
- [Firebase Remote Config（公式）](https://firebase.google.com/docs/remote-config)

---

## 29. オフライン対応 — WatermelonDB vs MMKV vs SQLite

**調査日時: 2026-05-14 (第6ラウンド)**

### 2026年のオフライン対応ライブラリ比較

```
用途別推奨:

軽量データ（設定・キャッシュ・トークン）:
  → MMKV（30倍速、同期読み書き、既に導入済み）

構造化データ（チャット履歴・顧客データ・大量レコード）:
  → WatermelonDB または expo-sqlite

リアルタイム同期が必要:
  → WatermelonDB + Supabase/バックエンド
  → RxDB（最も包括的、CouchDB/Supabase/Firestoreに対応）
```

### WatermelonDB の特徴

```
✅ パフォーマンス: 1,000件の一括挿入が10件と同じ速度（SQLiteトランザクション活用）
✅ Observable: データ変更が自動でUIに反映（RxJS的）
✅ 同期プロトコル内蔵: サーバーとのdiff同期（変更分だけ転送）
✅ 50,000件以上のレコードでも高速

❌ 複雑: セットアップが難しい（スキーマ定義が必要）
❌ Development Build必須（Expo Goでは動かない）
❌ Expo managedでは追加設定が必要
```

### expo-sqlite（シンプルなSQL）

```typescript
import * as SQLite from 'expo-sqlite';

const db = SQLite.openDatabaseSync('emport_ai.db');

// テーブル作成
db.execSync(`
  CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    role TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    session_id TEXT NOT NULL
  );
`);

// メッセージ保存
const saveMessage = (message: Message) => {
  db.runSync(
    'INSERT INTO messages (id, content, role, timestamp, session_id) VALUES (?, ?, ?, ?, ?)',
    [message.id, message.content, message.role, Date.now(), message.sessionId]
  );
};

// 特定セッションのメッセージ取得
const getSessionMessages = (sessionId: string): Message[] => {
  return db.getAllSync(
    'SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC',
    [sessionId]
  );
};
```

### Emport AI のオフライン戦略

```
現状の判断: 本格的なオフライン対応は後回し

理由:
  - Emport AIはAI回答がメイン → ネットなしでは機能しない
  - オフライン = キャッシュ程度で十分

段階的な実装:
Phase 1（今）: MMKV でチャット履歴を保存（既に設計済み）
Phase 2（将来）: expo-sqlite で複数セッション・検索対応
Phase 3（スケール後）: WatermelonDB + バックエンド同期

→ Phase 1から始めて、ユーザーのニーズに合わせて拡張する
```

**情報源:**
- [WatermelonDB 公式（GitHub）](https://github.com/nozbe/watermelondb)
- [TinyBase vs WatermelonDB vs RxDB 2026比較](https://www.pkgpulse.com/blog/tinybase-vs-watermelondb-vs-rxdb-offline-first-2026)

---

## 30. Expo Camera & OCR — 業務書類のデジタル化

**調査日時: 2026-05-14 (第6ラウンド)**

### OCRの実装方法（2026年）

```
方法1: MLKit（Google）— Android強み
  react-native-mlkit-ocr
  - Development Build必須
  - iOS/Android対応
  - オフラインでOCR可能

方法2: Vision Framework（Apple）— iOS強み
  expo-ocr
  - iOS専用（iPhone/iPad）
  - iOSの組み込みOCRエンジン使用
  - 高精度だがAndroid非対応

方法3: Google Vision API（クラウド）— 最高精度
  - サーバー経由で送信
  - ネット接続必要
  - 月1,000件まで無料
  - 日本語精度が最高

→ Emport AIには Google Vision API が最適（既にFlaskバックエンドあり）
```

### Google Vision API での OCR 実装

```typescript
// フロントエンド: 画像を撮影してサーバーへ送信
import { CameraView, useCameraPermissions } from 'expo-camera';

export function DocumentScanner() {
  const cameraRef = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();

  const scanDocument = async () => {
    const photo = await cameraRef.current.takePictureAsync({ base64: true });
    
    // バックエンドへ送信してOCR
    const response = await fetch(`${API_URL}/api/ocr`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: photo.base64 })
    });
    const { text } = await response.json();
    
    // 抽出したテキストをAIチャットに入力
    setInputText(`以下の書類の内容を整理してください:\n${text}`);
  };

  return (
    <CameraView ref={cameraRef} style={styles.camera}>
      <TouchableOpacity onPress={scanDocument} style={styles.button}>
        <Text>書類をスキャン</Text>
      </TouchableOpacity>
    </CameraView>
  );
}
```

```python
# バックエンド（Flask）: Google Vision API を呼び出す
import google.cloud.vision as vision
import base64

@app.route('/api/ocr', methods=['POST'])
def ocr():
    image_b64 = request.json['image']
    image_bytes = base64.b64decode(image_b64)
    
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    
    extracted_text = response.text_annotations[0].description if response.text_annotations else ''
    return jsonify({'text': extracted_text})
```

### Emport AIでのOCR活用シナリオ

```
✅ 実用的なユースケース:
  - 請求書・見積書をカメラで読み取り → AIで分析・要約
  - 名刺を読み取り → 顧客情報として整理
  - 工事現場の黒板を読み取り → 日報自動作成
  - 手書きメモを読み取り → テキスト化してAIに渡す

💡 Emport AIの差別化:
  「カメラで書類をスキャン → AI解析」の流れは
  中小企業にとって非常に価値が高い機能になりえる
```

**情報源:**
- [Expo Camera 公式ドキュメント](https://docs.expo.dev/versions/latest/sdk/camera/)
- [Google Vision API + React Native](https://medium.com/swlh/how-to-integrate-google-vision-api-with-react-native-and-expo-6af0db04b4e8)

---

## 31. App Store レビュー管理戦略

**調査日時: 2026-05-14 (第6ラウンド)**

### レビューがダウンロード数に与える影響

```
データ（2026年）:
  評価が★1上がる → ダウンロード数が25〜40%増加
  評価4.5以上 → 検索ランキング優遇
  評価3.5未満 → App Storeの特集から除外される可能性

→ App Storeレビューは最も費用対効果の高いASO施策
```

### In-App Review（アプリ内レビュー誘導）

```typescript
// expo-store-review: Expo公式のレビュー誘導API
import * as StoreReview from 'expo-store-review';

// 最適なタイミングでレビューを依頼
const requestReview = async () => {
  const isAvailable = await StoreReview.isAvailableAsync();
  if (isAvailable) {
    await StoreReview.requestReview();
    // → iOS/Androidのネイティブレビューダイアログが表示される
  }
};
```

### 最適なレビュー依頼タイミング

```
✅ 依頼すべきタイミング:
  - AI回答を「役に立った」と評価した直後
  - チャット10回目の節目
  - アプリ使用3日目（継続利用が確認できた時）
  - 有料プランに転換した直後

❌ 避けるべきタイミング:
  - アプリ初回起動時
  - エラー発生直後
  - 複雑な操作中
  - 同じユーザーに1週間以内に2回目

重要: iOS/Androidとも年間3回までしかダイアログを表示できない
→ タイミングを慎重に選ぶ
```

### 低評価レビューへの対応戦略

```
返信の基本:
  1. 感謝を述べる（批判でも）
  2. 問題を認める（言い訳しない）
  3. 解決策または改善予定を伝える
  4. 24時間以内に返信（素早さが重要）

返信テンプレート（日本語）:
  "ご意見をいただきありがとうございます。
   〇〇についてご不便をおかけして申し訳ございません。
   次回アップデートで改善予定です。
   引き続きよろしくお願いします。— Emport AIチーム"

低評価が増えたら:
  → Sentry でクラッシュログを確認
  → レビュー内容を機能改善のフィードバックとして活用
```

### レビュー管理ツール

```
AppFollow（無料プランあり）:
  - 複数ストアのレビューを一元管理
  - 返信テンプレート機能
  - レビュー感情分析

Appbot:
  - AIによるレビュー感情分析
  - Slackへの通知統合

→ 初期はAppFollowの無料プランで十分
```

**情報源:**
- [Expo StoreReview 公式](https://docs.expo.dev/versions/latest/sdk/storereview/)
- [App Store レビュー完全ガイド 2026（AppTweak）](https://www.apptweak.com/en/aso-blog/app-store-reviews)

---

## 32. React Native デバッグ技法 — 2026年最新ツール

**調査日時: 2026-05-14 (第6ラウンド)**

### 2026年のデバッグツール全体像

```
🟢 現在の標準（推奨）:
  React Native DevTools — RN 0.76以降の公式デバッガー
  Chromeプロトコル経由でHermes VMに直接接続
  → JS Thread を止めないので本番に近い動作でデバッグ可能

🟡 サードパーティ（補完的に使う）:
  Reactotron — ネットワーク・Redux状態の可視化（デバッグモード不要）
  
❌ 非推奨（過去の遺物）:
  Flipper — RN 0.74以降はデフォルト外（手動設定が必要）
  Chrome Remote Debugging — Hermes移行後は非推奨
```

### React Native DevTools の使い方

```bash
# アプリを起動してDevToolsを開く
npx expo start

# シミュレーターで: Cmd+D（iOS）/ Cmd+M（Android）→ "Open DevTools"
# または: ターミナルで 'j' を押す
```

```
DevToolsでできること:
  ✅ Console（console.log・エラー確認）
  ✅ Sources（ブレークポイント・ステップ実行）
  ✅ Memory（メモリ使用量・ヒープスナップショット）
  ✅ Performance Panel（0.83+）— フレームドロップ・JS実行時間を可視化
  ✅ Network Inspector（HTTPリクエスト確認）
  ✅ React DevTools（コンポーネントツリー・Propsの確認）
```

### Reactotron — デバッグモード不要の監視ツール

```bash
npm install --save-dev reactotron-react-native reactotron-redux
```

```typescript
// ReactotronConfig.ts（開発時のみ読み込む）
if (__DEV__) {
  const Reactotron = require('reactotron-react-native').default;
  Reactotron
    .configure({ host: 'localhost' })
    .useReactNative({
      networking: {
        ignoreUrls: /symbolicate/  // MetroBundlerの通信を無視
      }
    })
    .connect();
  
  console.tron = Reactotron;  // console.tron.log() で送信
}
```

```
Reactotronの特徴:
  ✅ JS ThreadをSTOPしないので本番に近い状態で監視できる
  ✅ APIのリクエスト・レスポンスをリアルタイム表示
  ✅ Zustand/Redux の状態変化をタイムライン表示
  ✅ カスタムコマンド（ボタン1つでテストデータを投入等）
  ✅ Desktop App（Mac/Windows）で確認
```

### よくあるバグと調査方法

```
バグ種別            | 調査ツール
--------------------|------------------------
クラッシュ          | Sentry（本番）/ DevTools（開発中）
パフォーマンス問題  | DevTools Performance Panel
APIエラー           | Reactotron / DevTools Network
状態管理バグ        | Reactotron（Zustand統合）
メモリリーク        | DevTools Memory タブ
レンダリング過多    | React DevTools Profiler
```

### 本番環境でのデバッグ（Sentry連携）

```typescript
// エラーの詳細コンテキストを添付
Sentry.withScope((scope) => {
  scope.setTag('screen', 'ChatScreen');
  scope.setExtra('messageCount', messages.length);
  scope.setExtra('industry', currentIndustry);
  Sentry.captureException(error);
});
```

**情報源:**
- [React Native Debugging Guide 2026（React Native Relay）](https://reactnativerelay.com/article/complete-guide-debugging-react-native-apps-2026-devtools-performance-panel-radon-ide-production-monitoring)
- [React Native DevTools vs Flipper（New Architecture）](https://metadesignsolutions.com/react-native-devtools-vs-flipper-the-ultimate-debugging-workflow-for-the-new-architecture/)

---

## 33. 次のリサーチ課題（第6ラウンド終了）

第7ラウンドで調査予定：
1. **React Native + AI統合パターン** — Streaming API・リアルタイムAI応答の実装
2. **Expo EAS Submit** — App Store / Google Play への自動提出
3. **モバイルアプリのマネタイズ最適化** — Paywall設計・転換率向上の心理学
4. **React Native パフォーマンス計測** — 具体的な数値目標と計測方法
5. **Claude API × モバイルアプリ最適化** — Promptキャッシング・コスト削減・レスポンス高速化

---

## 34. Claude API Streaming — リアルタイムAI応答の実装

**調査日時: 2026-05-14 (第7ラウンド)**

### なぜStreamingが重要か

```
❌ 通常のAPI呼び出し:
  ユーザーが送信 → 数秒待機（何も表示されない）→ 一気に全文表示
  → UXが悪い。ユーザーは「フリーズしたかも」と感じる

✅ Streaming:
  ユーザーが送信 → 即座に文字が1文字ずつ表示されていく（ChatGPTのあれ）
  → 即座のフィードバックがあり、待ち時間を感じにくい
  → 実際のレスポンス時間が同じでもUXが劇的に改善
```

### バックエンド（Flask）でのStreaming実装

```python
# app.py
import anthropic
from flask import Response, stream_with_context

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json
    messages = data.get('messages', [])
    industry = data.get('industry', '汎用')
    
    system_prompt = f"""あなたは{industry}に特化したAIアシスタントです。
    中小企業の経営者・従業員の業務効率化を支援します。"""
    
    def generate():
        with client.messages.stream(
            model='claude-sonnet-4-6',
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                # Server-Sent Events形式で送信
                yield f"data: {text}\n\n"
        yield "data: [DONE]\n\n"
    
    return Response(
        stream_with_context(generate()),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'  # Nginxのバッファリングを無効化
        }
    )
```

### フロントエンド（React Native）でのStreaming受信

```typescript
// hooks/useStreamingChat.ts
import { useState, useCallback } from 'react';

export function useStreamingChat() {
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = useCallback(async (
    messages: Message[],
    industry: string
  ) => {
    setIsStreaming(true);
    setStreamingText('');

    try {
      // fetch でSSEを受信
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ messages, industry })
      });

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setIsStreaming(false);
              return accumulated;
            }
            accumulated += data;
            setStreamingText(accumulated);  // リアルタイムで更新
          }
        }
      }
    } catch (error) {
      setIsStreaming(false);
      throw error;
    }
  }, []);

  return { streamingText, isStreaming, sendMessage };
}
```

```typescript
// コンポーネントでの使用
export function ChatScreen() {
  const { streamingText, isStreaming, sendMessage } = useStreamingChat();
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSend = async (text: string) => {
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);

    const response = await sendMessage(newMessages, industry);
    setMessages(prev => [...prev, { role: 'assistant', content: response }]);
  };

  return (
    <FlashList
      data={messages}
      renderItem={({ item }) => <MessageBubble message={item} />}
      ListFooterComponent={
        isStreaming ? (
          <MessageBubble
            message={{ role: 'assistant', content: streamingText + '▊' }}
          />
        ) : null
      }
    />
  );
}
```

**情報源:**
- [Claude API Streaming 公式ドキュメント](https://platform.claude.com/docs/en/api-reference/overview)
- [React Native + Claude AI（Design+Code）](https://designcode.io/react-native-ai/)

---

## 35. EAS Submit — App Store / Google Play 自動提出

**調査日時: 2026-05-14 (第7ラウンド)**

### EAS Submit の全体フロー

```
1. EAS Build でビルド作成
   eas build --platform ios --profile production
   
2. EAS Submit でストアへ自動送信
   eas submit --platform ios --latest
   
3. App Store Connect でメタデータ入力 → 審査提出
   （メタデータ入力は現状手動が必要）
```

### iOS（App Store）の設定

```json
// eas.json に submit 設定を追加
{
  "submit": {
    "production": {
      "ios": {
        "appleId": "tsubeyou081@gmail.com",
        "ascAppId": "XXXXXXXXXX",  // App Store Connect のApp ID
        "appleTeamId": "XXXXXXXXXX"
      }
    }
  }
}
```

```bash
# App Store Connectへ自動アップロード（TestFlightに送信）
eas submit --platform ios --profile production --latest

# ビルドと提出を一気に実行
eas build --platform ios --profile production --auto-submit
```

### Android（Google Play）の設定

```bash
# 初回のみ手動でAABをアップロードしてから、以降はAPI自動化
# Google Service Account Key が必要（Firebase Console で発行）

# eas.json
{
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "internal",  // internal → alpha → beta → production の順
        "releaseStatus": "draft"
      }
    }
  }
}
```

```bash
# Google Play内部テスターに自動提出
eas submit --platform android --profile production --latest
```

### GitHub Actions でCI/CD完結（ビルド→提出→通知）

```yaml
# .github/workflows/deploy.yml
name: Deploy to Stores

on:
  push:
    tags: ['v*']  # v1.0.0 のようなタグでトリガー

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      
      # ビルド + 自動提出
      - run: eas build --platform all --profile production --non-interactive --auto-submit
      
      # Slack/Discord通知（任意）
      - name: Notify
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text": "✅ App Store/Google Playへの提出完了"}'
```

### 提出から公開までの目安

```
App Store（iOS）:
  提出 → TestFlight: 10-15分
  審査: 24-48時間（初回は長い場合あり）
  承認後: 即座に公開 or 日時指定

Google Play（Android）:
  内部テスト: 即座
  クローズドテスト → オープンテスト → 本番: 各レビューに数時間
  本番公開: 審査なし（ポリシー違反のみ拒否）
```

**情報源:**
- [EAS Submit 公式ドキュメント](https://docs.expo.dev/submit/introduction/)
- [EAS Submit Android（公式）](https://docs.expo.dev/submit/android/)

---

## 36. Paywall設計 — 転換率を最大化する心理学

**調査日時: 2026-05-14 (第7ラウンド)**

### 2026年のPaywall最新データ

```
週次プランが2026年の主役:
  週次プラン = サブスク収益の55.6%（2026年）
  年次より週次の方がCVR 1〜7倍高い（カテゴリによる）
  → 「まず安く試させる」戦略が最も効果的

LTVの差:
  最良のPaywall構成 vs 最悪: LTVに636%の差
  A/Bテストする vs しない: 収益に最大40倍の差
```

### 転換率を上げる心理学的要素

```
1. 「いつでもキャンセル可能」の明記（最重要）
   - PaywallのCTAボタン近くに必ず表示
   - これがないと離脱率が大幅に上がる

2. アンカリング（価格の比較提示）
   - 月額プラン vs 年額プランを並べる
   - 年額を推奨として目立たせる（「最もお得」バッジ）
   - ユーザーに「年額の方が賢い」と感じさせる

3. 無料トライアルの透明性
   - 「〇日後に請求されます」を明確に表示
   - トライアル終了前のリマインダーを約束
   → CVRが最大46%向上（実績あり）

4. 社会的証明
   - 「1,000社以上が利用」
   - ★4.8 (234件のレビュー)
   - 具体的な業種・会社規模の声
```

### Emport AI の推奨Paywall設計

```
価格設計（A/Bテスト前の初期案）:
  
  🆓 無料プラン:
    月10回まで無料
    業種特化なし（汎用のみ）
  
  💰 スタンダードプラン（月額）:
    月額 ¥980/月
    無制限チャット + 全業種対応
  
  🏆 ビジネスプラン（年額 → 推奨として強調）:
    ¥7,800/年（¥650/月 = 34%割引）
    + 複数端末・チームメンバー追加
```

```typescript
// Paywall画面のベスト構成
export function PaywallScreen() {
  return (
    <View>
      {/* 価値提案を明確に */}
      <Text style={styles.headline}>
        AIが業務を自動化します
      </Text>
      <Text style={styles.subheadline}>
        1,200社以上の中小企業が活用中
      </Text>
      
      {/* 年額を強調 */}
      <PlanOption
        title="年間プラン"
        price="¥650/月"
        totalPrice="¥7,800/年"
        badge="最もお得・34%OFF"
        recommended={true}
      />
      <PlanOption
        title="月間プラン"
        price="¥980/月"
        recommended={false}
      />
      
      {/* CTAとキャンセル保証 */}
      <Button title="7日間無料で試す" onPress={handleSubscribe} />
      <Text style={styles.guarantee}>
        いつでもキャンセル可能 · 7日以内なら全額返金
      </Text>
      
      {/* 社会的証明 */}
      <TestimonialCard
        company="山田建設（従業員15名）"
        text="見積書作成時間が80%削減されました"
      />
    </View>
  );
}
```

### Superwall — Paywallのリアルタイムテスト

```
Superwallとは:
  - Paywallをリモートで変更・A/Bテストできるツール
  - アプリ再提出なしでPaywallデザイン・価格・コピーを変更
  - 実績: ある企業がSuperwallで収益48%増加（2026年事例）

→ スケール後に検討。初期はシンプルな実装で十分
```

**情報源:**
- [高転換率Paywallの設計（Adapty.io 2026）](https://adapty.io/blog/high-performing-paywall-2026/)
- [Paywall設計の心理学・10原則（4,500 A/Bテスト分析）](https://stormy.ai/blog/10-mobile-app-paywall-design-principles)

---

## 37. React Native パフォーマンス数値目標

**調査日時: 2026-05-14 (第7ラウンド)**

### 2026年の業界標準ターゲット値

```
指標             | 目標値          | 警告ライン
----------------|----------------|------------------
FPS（通常画面）  | 60fps          | 45fps以下でユーザーが体感
FPS（スクロール）| 58fps以上      | P99デバイスで計測
Cold Start（iOS）| 1.2秒以下      | 2.0秒超でユーザーが不満
Cold Start(Android)| 2.0秒以下  | 3.0秒超で離脱増
JSスレッド停止  | 100ms以下      | 100ms超で「フリーズ」感
メモリ使用量    | 150MB以下      | 300MB超でOSがkillする
Crash-Free率   | 99.5%以上      | 99%以下は即調査
```

### パフォーマンス計測ツール

```typescript
// react-native-performance-stats でリアルタイム計測
import PerformanceStats from 'react-native-performance-stats';

// 開発中にFPS・メモリ・CPU使用率を画面上に表示
PerformanceStats.start(); // FPSオーバーレイを表示

// DevToolsのPerformance Panelでの計測:
// 1. Metro起動: npx expo start
// 2. DevToolsを開く（j を押す）
// 3. Performance タブ → Record → 操作 → Stop
// 4. フレームドロップ・JS実行時間を可視化
```

### ボトルネック別の対処法

```
FPSが低い:
  → FlashList に移行（FlatList比10倍）
  → useAnimatedStyle（Reanimated4）でUIスレッドに移行
  → React.memoでメッセージコンポーネントを最適化

Cold Startが遅い:
  → New Architecture + Hermes 1.0 で40%改善
  → 起動時の不要な初期化処理を遅延（lazy import）
  → app.jsonのassets prebundlingを有効化

JSスレッド停止:
  → 重い計算処理をuseWorker（バックグラウンドスレッド）に移行
  → 大きなJSON処理は分割して処理

メモリ過多:
  → 画像はexpo-imageでキャッシュ管理
  → FlashList のコンポーネントリサイクル活用
  → 不要なEventListenerのクリーンアップ
```

### Emport AI の最優先パフォーマンス施策

```
優先度順:
  1. FlashList 導入（メッセージリスト）← 最大効果
  2. New Architecture 有効化（app.jsonで1行）
  3. MessageBubble React.memo 化
  4. Sentry でCrash-Free率監視
  5. 画像はすべてexpo-image に置き換え
```

**情報源:**
- [React Native Performance 2026 ガイド（RapidNative）](https://www.rapidnative.com/blogs/react-native-performance-optimization-2026-playbook)
- [React Native パフォーマンス監視（UXCam）](https://uxcam.com/blog/react-native-performance-monitoring/)

---

## 38. Claude API コスト最適化 — Prompt Caching で最大90%削減

**調査日時: 2026-05-14 (第7ラウンド)**

### Claude APIの価格（2026年）

```
モデル           | 入力          | 出力          | キャッシュ読み
----------------|--------------|--------------|---------------
claude-opus-4-7  | $15/MTok    | $75/MTok     | $1.5/MTok（90%OFF）
claude-sonnet-4-6| $3/MTok     | $15/MTok     | $0.3/MTok（90%OFF）
claude-haiku-4-5 | $0.8/MTok   | $4/MTok      | $0.08/MTok（90%OFF）

→ Emport AI: claude-sonnet-4-6 を使用（コスト・性能バランス最適）
→ Prompt Cachingで入力コストを90%削減できる
```

### Prompt Caching の仕組みと実装

```python
# バックエンド（Flask）でのPrompt Caching実装
import anthropic

client = anthropic.Anthropic()

INDUSTRY_PROMPTS = {
    '建設業': """あなたは建設業に特化したAIアシスタントです。
    以下の専門知識を持っています:
    - 建設業の工程管理・原価管理
    - 見積書・工事請負契約書の作成
    - 安全管理・品質管理の基礎知識
    ...(長い業種知識テキスト)...""",
    
    '製造業': """あなたは製造業に特化した..."""
}

def chat_with_caching(messages: list, industry: str) -> str:
    system_prompt = INDUSTRY_PROMPTS.get(industry, 'あなたは汎用AIアシスタントです。')
    
    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # ← これがキャッシュの設定
                # TTL: デフォルト5分（1.25x書き込みコスト）
                # 5分以内に同じsystem promptへのリクエストはキャッシュヒット
                # = 入力コストが1/10になる
            }
        ],
        messages=messages
    )
    return response.content[0].text
```

### コスト計算例

```
条件:
  - 業種プロンプト: 2,000トークン（キャッシュ対象）
  - 会話履歴: 平均500トークン
  - AI回答: 平均300トークン
  - 月間リクエスト: 10,000回

キャッシュなし:
  入力: (2,000 + 500) × 10,000 = 25M tokens × $3/MTok = $75/月

キャッシュあり（80%ヒット率と仮定）:
  キャッシュ書き込み: 2,000 × 10,000 × 20% = 4M tokens × $3.75/MTok = $15
  キャッシュ読み込み: 2,000 × 10,000 × 80% = 16M tokens × $0.3/MTok = $4.8
  非キャッシュ入力: 500 × 10,000 = 5M tokens × $3/MTok = $15
  合計: $34.8/月（54%削減）

→ リクエストが多いほどキャッシュ効果は増大
```

### コスト削減の全体戦略

```
1. Prompt Caching（最大90%削減）
   → 固定のsystem promptにキャッシュを設定

2. モデル選択（3〜10倍の差）
   → 単純なタスクはHaiku、複雑な業務相談はSonnet

3. Batch API（50%削減）
   → 急がない処理（レポート生成・夜間バッチ）に使用

4. max_tokens の最適化
   → 必要以上に大きな値を設定しない

5. 会話履歴の制限（第4ラウンドで設計済み）
   → 最新20件のみAPIに送信
```

**情報源:**
- [Claude API Prompt Caching（公式）](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic API Pricing 2026完全ガイド（finout.io）](https://www.finout.io/blog/anthropic-api-pricing)

---

## 39. 次のリサーチ課題（第7ラウンド終了）

第8ラウンドで調査予定：
1. **React Native + TypeScript 型安全設計** — APIレスポンスの型定義・Zod バリデーション
2. **Expo Router ファイルベースAPIルート** — バックエンドをアプリ内に統合する新手法
3. **モバイルアプリのユーザーオンボーディング設計** — チュートリアル・初回体験
4. **アプリのウィジェット対応（iOS/Android）** — ホーム画面ウィジェット
5. **React Native + Supabase** — Firebaseの代替・リアルタイムDB・認証

---

## 40. TypeScript + Zod — APIレスポンスの型安全バリデーション

**調査日時: 2026-05-14 (第8ラウンド)**

### なぜZodが必要か

```
TypeScriptの型は「コンパイル時」だけ保護する:
  const user: User = await fetchUser();  // 実行時はany

Zodは「実行時」にも保護する:
  const user = UserSchema.parse(await fetchUser());
  // APIが想定外のデータを返してもクラッシュしない

→ バックエンドのAPIが変更されても安全に検知できる
```

### Zodのインストールと基本実装

```bash
npm install zod
```

```typescript
// types/api.ts — APIレスポンスのスキーマ定義
import { z } from 'zod';

// メッセージのスキーマ
export const MessageSchema = z.object({
  id: z.string(),
  role: z.enum(['user', 'assistant']),
  content: z.string(),
  timestamp: z.number(),
});

// チャットレスポンスのスキーマ
export const ChatResponseSchema = z.object({
  message: z.string(),
  usage: z.object({
    input_tokens: z.number(),
    output_tokens: z.number(),
  }).optional(),
  error: z.string().optional(),
});

// 型を自動推論（TypeScriptの手書きinterfaceが不要になる）
export type Message = z.infer<typeof MessageSchema>;
export type ChatResponse = z.infer<typeof ChatResponseSchema>;
```

### APIコールでのZod使用

```typescript
// services/api.ts
import { ChatResponseSchema, ChatResponse } from '@/types/api';

export async function sendMessage(
  messages: Message[],
  industry: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, industry })
  });
  
  const rawData = await response.json();
  
  // safeParse: エラーでも例外を投げずに結果オブジェクトを返す
  const result = ChatResponseSchema.safeParse(rawData);
  
  if (!result.success) {
    // APIのレスポンス形式が変わった場合にSentryへ通知
    Sentry.captureException(result.error, {
      extra: { rawData, zodErrors: result.error.format() }
    });
    throw new Error('APIレスポンスの形式が不正です');
  }
  
  return result.data;  // 型安全なデータが返ってくる
}
```

### フォームバリデーション（Zod + React Hook Form）

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const LoginSchema = z.object({
  accessCode: z.string()
    .min(6, 'アクセスコードは6文字以上です')
    .max(20, 'アクセスコードは20文字以下です'),
});

type LoginForm = z.infer<typeof LoginSchema>;

export function LoginScreen() {
  const { control, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(LoginSchema),
  });

  return (
    <View>
      <Controller
        control={control}
        name="accessCode"
        render={({ field: { onChange, value } }) => (
          <TextInput
            value={value}
            onChangeText={onChange}
            placeholder="アクセスコードを入力"
          />
        )}
      />
      {errors.accessCode && (
        <Text style={styles.error}>{errors.accessCode.message}</Text>
      )}
    </View>
  );
}
```

**情報源:**
- [Zod 公式ドキュメント](https://zod.dev/)
- [React TypeScript + Zod API バリデーション（freeCodeCamp）](https://www.freecodecamp.org/news/how-to-use-zod-for-react-api-validation/)

---

## 41. Expo Router API Routes — バックエンドをアプリ内に統合

**調査日時: 2026-05-14 (第8ラウンド)**

### Expo Router API Routesとは

```
従来のアーキテクチャ:
  Reactアプリ → 別のFlaskサーバー → Claude API
  
Expo Router API Routes（新手法）:
  Expoアプリ内に +api.ts ファイルを置くだけでサーバーエンドポイントが作れる
  → Vercel/EAS にデプロイするだけでサーバーも動く
  → FlaskサーバーをExpoアプリ内に統合できる
```

### 基本的な実装

```typescript
// app/api/chat+api.ts  ← ファイル名に "+api" をつけるだけ
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function POST(request: Request) {
  const { messages, industry } = await request.json();
  
  const systemPrompt = `あなたは${industry}に特化したAIアシスタントです。`;
  
  const response = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 1024,
    system: systemPrompt,
    messages
  });
  
  return Response.json({
    message: response.content[0].text,
    usage: response.usage
  });
}
```

```typescript
// モバイルアプリ側からは通常のfetchで呼び出す
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ messages, industry })
});
```

### Expo Router API Routes vs Flask（比較）

```
Expo Router API Routes（新手法）:
  ✅ アプリと同じコードベースで管理
  ✅ TypeScriptで型安全
  ✅ EAS / Vercelへの統合が簡単
  ✅ APIキーをサーバーサイドで安全に管理
  ❌ SDK 55でまだalpha（本番利用は慎重に）
  ❌ Python特有の処理（pandas等）は使えない

Flaskサーバー（現在のEmport AI）:
  ✅ Python/Anthropic SDKで安定動作
  ✅ 複雑なビジネスロジックをPythonで書ける
  ✅ 本番実績あり（Railway上で動作中）
  ❌ 別リポジトリ/サーバーの管理コスト

→ Emport AIは現状のFlask構成を維持
  Expo Router API Routesは安定後に移行を検討
```

**情報源:**
- [Expo Router API Routes（公式）](https://docs.expo.dev/router/web/api-routes/)
- [RFC: API Routes in Expo Router](https://evanbacon.dev/blog/api-routes-rfc)

---

## 42. ユーザーオンボーディング設計 — 初回体験で離脱を防ぐ

**調査日時: 2026-05-14 (第8ラウンド)**

### なぜオンボーディングが最重要か

```
衝撃のデータ（2026年）:
  - インストール後3日以内に77%のユーザーが離脱
  - Day1 リテンション: Android 22.6% / iOS 25.6%
  
→ 初回体験で価値を感じさせないと捨てられる
→ オンボーディングは機能開発より先に投資すべき
```

### 2026年のベストプラクティス

```
1. 「逆順オンボーディング」（Duolingo方式）:
   ❌ 従来: 会員登録 → チュートリアル → 実際に使う
   ✅ 逆順: 実際に使う → 価値を感じる → 会員登録
   → 登録率が大幅に向上（価値を体験後なので意欲が高い）

2. パーソナライゼーション（業種選択をオンボーに組み込む）:
   - 最初に「どんな業種ですか？」と聞く
   - 業種に合わせたサンプル会話を見せる
   → ユーザーが「このアプリは自分向けだ」と感じる

3. スキップ可能にする:
   - 強制ステップを最小限にする
   - 必要のないユーザーは飛ばせるようにする

4. 社会的証明を早期に見せる:
   - 「1,200社が利用中」
   - 業種別の成功事例を早い段階で見せる
```

### Emport AI のオンボーディングフロー設計

```
ステップ1: 価値提案（1画面）
  「AIが業務を自動化します」
  + 具体的な効果（見積作成80%時間短縮 等）
  → [試してみる] ボタン（登録不要でサンプル会話へ）

ステップ2: 業種選択（1画面）
  「あなたの業種は何ですか？」
  ○ 建設業
  ○ 製造業
  ○ 小売業
  ○ その他
  → 業種を選ぶことでAIが最適化される

ステップ3: サンプル会話を体験（1画面）
  業種に応じた典型的な質問をデモ
  「見積書の項目を整理してください」
  → AIがリアルに回答（デモ用・実際のAI）

ステップ4: 登録・アクセスコード入力
  価値を体験した後に登録を求める
  → この順番だと登録完了率が高い

ステップ5: 最初の本物の会話
  「では、本当のご質問は何ですか？」
  → すぐに実際の業務で使えるように誘導
```

### 実装（Expo Router + Step管理）

```typescript
// app/(auth)/onboarding/_layout.tsx
const ONBOARDING_STEPS = [
  'value-proposition',
  'industry-select',
  'demo-chat',
  'register',
] as const;

export default function OnboardingLayout() {
  const [currentStep, setCurrentStep] = useState(0);
  const progress = (currentStep + 1) / ONBOARDING_STEPS.length;

  return (
    <View>
      {/* プログレスバー */}
      <View style={[styles.progressBar, { width: `${progress * 100}%` }]} />
      
      <Stack>
        <Stack.Screen name={ONBOARDING_STEPS[currentStep]} />
      </Stack>
      
      <Button
        title={currentStep < ONBOARDING_STEPS.length - 1 ? '次へ' : '始める'}
        onPress={() => setCurrentStep(prev => prev + 1)}
      />
    </View>
  );
}
```

**情報源:**
- [モバイルアプリオンボーディング完全ガイド 2026（VWO）](https://vwo.com/blog/mobile-app-onboarding-guide/)
- [最高のオンボーディング12例（UXCam）](https://uxcam.com/blog/10-apps-with-great-user-onboarding/)

---

## 43. React Native + Supabase — Firebase代替の決定版

**調査日時: 2026-05-14 (第8ラウンド)**

### Supabase vs Firebase（2026年決定版比較）

```
項目              | Supabase          | Firebase
-----------------|-------------------|------------------
データベース      | PostgreSQL（SQL）  | NoSQL（Firestore）
オープンソース    | ✅ 完全OSS         | ❌ Google独自
価格             | 無料枠太め・予測可能| 無料枠あり・従量課金複雑
リアルタイム      | ✅ テーブル変更監視 | ✅ ドキュメント変更監視
認証             | ✅ 豊富（MFA含む） | ✅ 豊富
ベクトル検索      | ✅ pgvector対応    | ❌ 別途設定必要
自己ホスト        | ✅ 可能（Docker）  | ❌ 不可
2026年シェア傾向  | 急成長中           | 安定・縮小傾向

→ 2026年: Supabase が「Firebase but better」として主流化
```

### Emport AI での Supabase 活用シナリオ

```
現在のEmport AI:
  - 認証: アクセスコード（超シンプル）
  - DB: なし（チャット履歴はMMKVでローカル保存）

将来的にSupabaseが必要になる時:
  - マルチユーザー対応（会社単位でログイン）
  - チャット履歴をクラウドに保存・デバイス間同期
  - 企業ごとのカスタム設定・履歴管理
  - チームメンバー機能（複数人が同じアカウントを使う）
```

### Expo + Supabase のセットアップ

```bash
npx expo install @supabase/supabase-js
npx expo install expo-secure-store
```

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js';
import * as SecureStore from 'expo-secure-store';

// トークン永続化アダプター（expo-secure-store使用）
const ExpoSecureStoreAdapter = {
  getItem: (key: string) => SecureStore.getItemAsync(key),
  setItem: (key: string, value: string) => SecureStore.setItemAsync(key, value),
  removeItem: (key: string) => SecureStore.deleteItemAsync(key),
};

export const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      storage: ExpoSecureStoreAdapter,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    }
  }
);
```

```typescript
// メール認証でのサインイン（認証情報は環境変数で管理）
const { data, error } = await supabase.auth.signInWithPassword({
  email: userEmail,    // ← ユーザー入力
  userCredential      // ← ユーザー入力（環境変数・SecureStore経由）
});

// チャット履歴をPostgreSQLに保存
const { error } = await supabase
  .from('chat_sessions')
  .insert({
    user_id: user.id,
    industry: currentIndustry,
    messages: JSON.stringify(messages),
    created_at: new Date().toISOString()
  });

// リアルタイム購読（別ユーザーのメッセージを即座に受信）
const channel = supabase
  .channel('chat-room')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'messages' },
    (payload) => setMessages(prev => [...prev, payload.new])
  )
  .subscribe();
```

### Emport AI のロードマップ

```
Phase 1（現在）:
  アクセスコード認証 + ローカルMMKV保存 → シンプルで十分

Phase 2（有料化後）:
  Supabase Auth → メール認証でログイン
  チャット履歴のクラウド保存 → デバイス移行時も履歴が残る

Phase 3（エンタープライズ化）:
  企業ごとのアカウント（Row Level Security）
  チームメンバー管理・権限設定
  カスタムプロンプト・社内ナレッジとの統合
```

**情報源:**
- [Expo + Supabase（公式ガイド）](https://docs.expo.dev/guides/using-supabase/)
- [Supabase 2026完全ガイド（DEV Community）](https://dev.to/ottoaria/supabase-in-2026-the-complete-developer-guide-to-the-open-source-firebase-alternative-357j)

---

## 44. 次のリサーチ課題（第8ラウンド終了）

第9ラウンドで調査予定：
1. **React Native テスト自動化の深堀り** — Maestro E2Eテストの実装例
2. **Expo SDK 55 新機能** — Server Rendering・React Server Components対応
3. **AIアプリの競合分析** — 日本市場の類似AIアプリ・差別化戦略
4. **モバイルアプリのSEO** — インデックス化・コンテンツ戦略とアプリ連携
5. **React Native パッケージ管理** — yarn vs pnpm vs bun の2026年比較

---

## 45. Maestro E2E テスト — YAMLで書けるE2Eテスト

**調査日時: 2026-05-14 (第9ラウンド)**

### Maestroの特徴

```
2026年のE2Eテストの標準:
  - テストをYAMLで記述（コードを書かなくていい）
  - アプリのコードに一切変更不要（外部から操作）
  - iOS/Android両対応
  - Expo Go / Development Build / EAS Workflows 全対応
  - CIへの組み込みが最も簡単
```

### インストール

```bash
# macOS
brew tap mobile-dev-inc/tap
brew install maestro

# Windows
iex "& {$(irm get.scoop.sh)} -RunAsNonInteractive"
scoop install maestro
```

### テストファイル（YAML）の書き方

```yaml
# tests/login.yaml — ログインフローのE2Eテスト
appId: ai.emport.app
---
- launchApp
- assertVisible: "Emport AI"        # スプラッシュ画面の確認
- tapOn: "ログイン"                  # ボタンをタップ
- inputText:
    text: "TEST-CODE-001"            # アクセスコードを入力
- tapOn: "確認"
- assertVisible: "チャット"          # ログイン成功後の画面を確認
- takeScreenshot: "after-login"      # スクリーンショット撮影
```

```yaml
# tests/chat-flow.yaml — チャット送信のE2Eテスト
appId: ai.emport.app
---
- launchApp
- tapOn: "建設業"                   # 業種を選択
- assertVisible: "建設業を選択しました"
- tapOn:
    id: "message-input"             # testID で要素を指定
- inputText:
    text: "見積書の作成方法を教えてください"
- tapOn: "送信"
- waitForAnimationToEnd             # AI応答を待機
- assertVisible:
    text: "見積書"                   # AI回答に「見積書」が含まれることを確認
    timeout: 10000                  # 10秒待機
```

### EAS Workflows での自動テスト

```yaml
# .eas/workflows/e2e-test.yml
name: E2E Test
on:
  push:
    branches: [main]

jobs:
  test:
    type: build
    steps:
      - name: Build for testing
        run: eas build --platform android --profile testing --non-interactive
      
      - name: Run Maestro tests
        run: maestro test tests/
```

### testID の設定（コンポーネント側）

```typescript
// テスト用IDをコンポーネントに設定
<TextInput
  testID="message-input"   // Maestroから testID で要素を特定できる
  placeholder="質問を入力"
/>

<TouchableOpacity testID="send-button" onPress={handleSend}>
  <Text>送信</Text>
</TouchableOpacity>
```

### Emport AI のテスト優先順位

```
E2Eテスト（Maestro）:
  1. ログインフロー（アクセスコード入力 → 認証成功）
  2. チャット送信（業種選択 → 送信 → AI応答表示）
  3. 業種切り替え（別業種への切り替え）

ユニットテスト（Jest）:
  - APIコールのモック・エラーハンドリング
  - Zodスキーマのバリデーション

→ まずE2Eで主要フローを保護、詳細はユニットテストで
```

**情報源:**
- [Maestro E2E on EAS Workflows（公式）](https://docs.expo.dev/eas/workflows/examples/e2e-tests/)
- [React Native E2E テスト Maestro 2026（addjam）](https://addjam.com/blog/2026-02-18/our-experience-adding-e2e-testing-react-native-maestro/)

---

## 46. Expo SDK 55 — 2026年最新の重大な変更点

**調査日時: 2026-05-14 (第9ラウンド)**

### SDK 55 の主要な変更

```
React Native 0.83 + React 19.2（最新）
New Architecture が強制（もはやオプションではない）
Legacy Architectureが削除済み
```

### 最重要: Bytecode Diffing で更新サイズが75%削減

```
従来のOTA Update:
  コード1行変更 → JSバンドル全体（数MB）をダウンロード
  → ユーザーの通信量を無駄に使う

SDK 55（Bytecode Diffing）:
  コード1行変更 → 変更された差分のみ（数KB）をダウンロード
  → 更新サイズが約25%まで削減（75%削減）
  → ユーザーはより速く最新版を取得できる
```

### Expo Router v7（SDK 55同梱）

```
主な新機能:
  - React Server Components（RSC）のモバイル対応（実験的）
  - Server-Side Rendering (SSR) のalpha版（Web）
  - データローダー（実験的）
  - Better static site generation

実用的な影響:
  - iOS/Android向けRSCは2026年時点でまだ実験的
  - Web向けSSRはVercelにデプロイすれば動作
  - Emport AIはモバイル中心なので今は様子見
```

### expo-widgets（iOS ウィジェット）

```typescript
// SDK 55から: iOSホーム画面ウィジェットをExpo UIで作成可能
// ネイティブコード不要！

// app/widget/index.tsx（ウィジェット専用ファイル）
import { Widget } from 'expo-widgets';

export default function ChatWidget() {
  return (
    <Widget>
      <Widget.Text style={{ fontSize: 16, fontWeight: 'bold' }}>
        Emport AI
      </Widget.Text>
      <Widget.Text>
        タップしてAIアシスタントを開く
      </Widget.Text>
    </Widget>
  );
}
```

### SDK 55 への移行注意点

```
❌ 非推奨 → 削除された:
  - Legacy Architecture（Bridge）— 使っていたら移行必須
  - Expo Go でのプッシュ通知（SDK 53から）

✅ 推奨される変更:
  - New Architecture: 強制になったので設定確認不要
  - app.json の experiments.newArchEnabled は削除可能

Emport AI の対応:
  - 現時点でSDK 53使用中 → SDK 55への移行計画が必要
  - Breaking Changesを確認してから移行する
```

**情報源:**
- [Expo SDK 55 公式ChangeLog](https://expo.dev/changelog/sdk-55)
- [What's New in Expo SDK 55（Medium）](https://medium.com/@onix_react/whats-new-in-expo-sdk-55-6eac1553cee8)

---

## 47. 日本市場の競合分析 — Emport AIの差別化戦略

**調査日時: 2026-05-14 (第9ラウンド)**

### 2026年日本の中小企業AI市場

```
市場規模:
  日本の対話型AI市場: 2034年に34億960万ドル（CAGR 16.63%）
  中小企業のAI導入率: 約4社に1社（25%程度）
  → まだ75%が未導入 = 巨大なブルーオーシャン

中小企業向け主要AI（競合）:
  ChatGPT    — 汎用性最高・最も知名度あり・月額$20
  Claude      — 長文処理・要約が得意・月額$20
  Microsoft Copilot — Office統合が強み・Microsoft 365に統合
  PKSHA      — 日本語AI・エンタープライズ向け・高価格
  Dify       — AIワークフロー構築・エンジニア向け
```

### Emport AIが持つ差別化優位性

```
1. 業種特化（最大の差別化）
   競合: 汎用AIアシスタント
   Emport AI: 建設業・製造業・小売業等の業種専門知識を組み込み
   → 「AIの回答が業界の常識を知っている」という体験

2. モバイルファースト
   競合: PCブラウザ中心（ChatGPT・Claude）
   Emport AI: スマートフォンで使えるネイティブアプリ
   → 現場でスマホを使う職人・営業職に刺さる

3. 超シンプルUI
   競合: 高機能だが複雑（AIに慣れていないと難しい）
   Emport AI: 業種を選んで話しかけるだけ
   → 「AIを使ったことがない」層へのハードルが最低

4. 低価格（月額980円）
   競合: ChatGPT ¥2,988/月・Claude ¥2,988/月
   Emport AI: ¥980/月（3分の1の価格）
   → 中小企業経営者が承認しやすい金額

5. IT導入補助金対象化（将来）
   → IT支援事業者登録後: 補助率50%（実質¥490/月）
   → 競合の汎用AIは補助金対象外が多い
```

### 弱点と対策

```
弱点:
  - ブランド認知度ゼロ（ChatGPTに対してほぼ無名）
  - 機能が少ない（汎用AIに比べて限定的）

対策:
  - ニッチを狙う（「建設業専門AI」で商工会議所経由）
  - 無料トライアルで価値を体験させてから有料化
  - 口コミ・紹介でスケール（実際に便利なら広がる）
```

**情報源:**
- [日本の中小企業向けAIツール比較 2026（sei-san-sei）](https://www.sei-san-sei.com/blog/blog-0090.html)
- [日本の対話型AI市場規模（NEWSCAST）](https://newscast.jp/smart/news/2793351)

---

## 48. パッケージマネージャー 2026年比較 — npm vs yarn vs pnpm vs bun

**調査日時: 2026-05-14 (第9ラウンド)**

### 2026年のパッケージマネージャー比較

```
速度比較（cold install、200依存関係）:
  Bun:   最速（10〜30倍速い、Zigで実装）
  pnpm:  速い（Node.jsベースの中では最速）
  Yarn Berry: 中程度
  npm:   最も遅い（デフォルトだが遅い）

ディスク使用量（10プロジェクト）:
  pnpm:  612MB（ハードリンクで重複排除）
  npm:   4.87GB（プロジェクトごとに全コピー）
  → pnpmは87%のディスク削減

React Native/Expo との互換性:
  npm:   ✅ 完全対応（デフォルト）
  yarn:  ✅ 完全対応（Expoで長年使われてきた）
  pnpm:  ✅ RN 0.76+ で公式サポート（Expoモノレポに推奨）
  bun:   ⚠️ 互換性が高まったが一部問題あり
```

### 2026年の推奨

```
React Native / Expo 単体プロジェクト:
  → npm または yarn（最も安全・ドキュメントが多い）
  
Expoモノレポ（複数アプリ管理）:
  → pnpm（ディスク効率・速度・RN 0.76+で公式サポート）
  
速度最優先の新プロジェクト:
  → Bun（ただしRNとの互換性を十分確認）
```

### Emport AI の現在の構成

```
現在: npm（デフォルト）→ 変更不要
理由:
  - 単体プロジェクト（モノレポではない）
  - npmで問題なく動作している
  - 変更のリスクより安定性を優先

将来: pnpmへの移行を検討
  - アプリが複数になった場合（iOS/Android/Web）
  - ディスク効率の改善が必要な場合
```

**情報源:**
- [pnpm vs npm vs yarn vs Bun 2026年比較（DEV Community）](https://dev.to/pockit_tools/pnpm-vs-npm-vs-yarn-vs-bun-the-2026-package-manager-showdown-51dc)
- [React Native パッケージマネージャー比較（reintech）](https://reintech.io/blog/npm-vs-yarn-vs-pnpm-vs-bun-2026-comparison)

---

## 49. 次のリサーチ課題（第9ラウンド終了）

第10ラウンドで調査予定：
1. **React Native のエラーハンドリング設計** — Error Boundary・グローバルエラー処理
2. **Expo アプリの CI/CD 完全自動化** — GitHub Actions + EAS + Sentry の連携
3. **モバイルアプリのアナリティクス** — Amplitude・Mixpanel・PostHog 比較
4. **React Native + LLM 次世代トレンド** — LLMをオンデバイスで動かす（llama.cpp等）
5. **Emport AI 開発ロードマップ最終整理** — 優先度・工数・技術スタックの統合

---

## 50. エラーハンドリング — Error Boundary + グローバルエラー処理

**調査日時: 2026-05-14 (第10ラウンド)**

### Error Boundary の限界

```
Error Boundary がキャッチできるもの:
  ✅ レンダリング中のエラー
  ✅ ライフサイクルメソッドのエラー
  ✅ コンストラクタのエラー

Error Boundary がキャッチできないもの:
  ❌ イベントハンドラ（onPress等）
  ❌ 非同期処理（setTimeout・Promise・fetch）
  ❌ ネイティブ側のエラー
  
→ 複数レイヤーでのエラーハンドリングが必要
```

### 完全なエラーハンドリング設計

```typescript
// app/_layout.tsx — アプリ全体のエラーハンドリング

// 1. Sentry の GlobalErrorBoundary（最外層）
import * as Sentry from '@sentry/react-native';

export default Sentry.wrap(function RootLayout() {
  return (
    // 2. カスタム Error Boundary（UI フォールバック用）
    <ErrorBoundary fallback={<ErrorScreen />}>
      <SessionProvider>
        <Stack />
      </SessionProvider>
    </ErrorBoundary>
  );
});
```

```typescript
// components/ErrorBoundary.tsx
import React, { Component, ErrorInfo } from 'react';

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  State
> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    Sentry.captureException(error, { extra: info });
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}
```

```typescript
// 3. 非同期エラーのグローバルキャプチャ
// index.js（エントリーポイント）

// Unhandled Promiseエラーをキャッチ
global.ErrorUtils.setGlobalHandler((error: Error, isFatal: boolean) => {
  Sentry.captureException(error, {
    tags: { fatal: isFatal ? 'true' : 'false' }
  });
  
  if (isFatal) {
    // 致命的エラー: ユーザーにメッセージを表示してアプリを再起動
    Alert.alert(
      'エラーが発生しました',
      'アプリを再起動してください。',
      [{ text: 'OK' }]
    );
  }
});
```

```typescript
// 4. API呼び出しの共通エラーハンドリング
const apiCall = async <T>(
  fn: () => Promise<T>,
  errorMessage = 'エラーが発生しました'
): Promise<T | null> => {
  try {
    return await fn();
  } catch (error) {
    Sentry.captureException(error);
    Alert.alert('エラー', errorMessage);
    return null;
  }
};

// 使用例
const result = await apiCall(
  () => sendMessage(messages, industry),
  'AI応答の取得に失敗しました。再度お試しください。'
);
```

**情報源:**
- [React Native Error Boundary（Sentry）](https://docs.sentry.io/platforms/react-native/integrations/error-boundary/)
- [React Native Error Handling 完全ガイド（dzone）](https://dzone.com/articles/react-native-error-handling-guide)

---

## 51. モバイルアプリアナリティクス — PostHog vs Mixpanel vs Amplitude

**調査日時: 2026-05-14 (第10ラウンド)**

### 2026年の3大アナリティクスツール比較

```
                | PostHog      | Mixpanel     | Amplitude
----------------|--------------|--------------|------------------
無料枠          | 100万イベント/月 | 100万イベント/月 | 1万MTU/月
オープンソース   | ✅ セルフホスト可 | ❌           | ❌
機能統合        | Analytics + Feature Flags + A/Bテスト + Session Replay | Analytics + Session Replay | Analytics
React Native SDK | ✅           | ✅           | ✅
日本語サポート  | △            | △            | △
Emport AI推奨   | ✅ 最適       | 中規模〜     | エンタープライズ〜
```

### PostHog — Emport AIに最適な理由

```
1. 無料枠が最も太い:
   月100万イベント + Feature Flags + A/Bテスト + Session Replay
   → 複数ツールを契約しなくていい（コスト削減）

2. エンジニア向け設計:
   アレン（Claude Code）が設定・管理しやすい
   セルフホストも可能（プライバシー重視の場合）

3. React Native対応:
   ネイティブSDK + オフライン時のイベントキュー
   ジェスチャー追跡・モバイルSession Replay
```

### PostHog の実装

```bash
npm install posthog-react-native
```

```typescript
// app/_layout.tsx
import PostHog, { PostHogProvider } from 'posthog-react-native';

const client = new PostHog(process.env.EXPO_PUBLIC_POSTHOG_API_KEY!, {
  host: 'https://eu.i.posthog.com',
  disabled: __DEV__,  // 開発中は計測しない
});

export default function RootLayout() {
  return (
    <PostHogProvider client={client}>
      <Stack />
    </PostHogProvider>
  );
}
```

```typescript
// イベントの計測
import { usePostHog } from 'posthog-react-native';

export function ChatScreen() {
  const posthog = usePostHog();

  const handleSend = async (message: string) => {
    // チャット送信イベントを計測
    posthog.capture('message_sent', {
      industry: currentIndustry,
      message_length: message.length,
      session_message_count: messages.length,
    });
    
    await sendMessage(message);
  };

  const handleUpgrade = () => {
    // 有料転換イベントを計測
    posthog.capture('upgrade_clicked', {
      plan: 'annual',
      source: 'chat_limit_reached',
    });
  };
}
```

### 計測すべき主要イベント（Emport AI）

```
ユーザー行動:
  app_opened         — アプリ起動
  industry_selected  — 業種選択
  message_sent       — メッセージ送信（conversions の分母）
  ai_response_viewed — AI回答表示

転換指標:
  paywall_shown      — ペイウォール表示
  upgrade_clicked    — 有料プラン選択
  subscription_started — 課金開始

離脱分析:
  onboarding_dropped — どのステップで離脱したか
  session_ended      — セッション長さ・最後の操作
```

**情報源:**
- [アナリティクスツール無料枠比較 2026（agentdeals）](https://agentdeals.dev/analytics-free-tier-comparison-2026)
- [モバイルアプリアナリティクス最良ツール（PostHog）](https://posthog.com/blog/best-mobile-app-analytics-tools)

---

## 52. オンデバイスLLM — インターネット不要のAI（次世代トレンド）

**調査日時: 2026-05-14 (第10ラウンド)**

### オンデバイスLLMとは

```
従来のアプリ:
  ユーザー → インターネット → Claude API → ユーザー
  
オンデバイスLLM:
  ユーザー → スマートフォン内のAIモデル → ユーザー
  → インターネット不要・プライバシー完全保護・レイテンシゼロ
```

### 主要ライブラリ（2026年）

```
llama.rn（最も普及）:
  - llama.cppのReact Nativeバインディング
  - New Architecture必須（v0.10+）
  - 1〜3Bパラメータのモデルに最適

react-native-executorch（SoftwareMansion製）:
  - Meta ExecuTorchを使ったオンデバイス推論
  - LLM・画像認識・音声認識に対応
  - より高精度・幅広いモデルに対応

対応モデル（小型・高速）:
  Llama 3.2 1B Instruct  — Meta製・日本語対応
  SmolLM2 1.7B          — 超軽量
  Qwen 2 0.5B           — 中国AI・多言語対応
```

### llama.rn の実装例

```bash
npm install llama.rn
# Development Build必須（Expo Goでは動かない）
```

```typescript
import { initLlama, LlamaContext } from 'llama.rn';

export function useOnDeviceAI() {
  const [context, setContext] = useState<LlamaContext | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadModel = async () => {
    setIsLoading(true);
    // モデルファイル（GGUF形式）をバンドルまたはダウンロード
    const ctx = await initLlama({
      model: 'file:///data/user/0/ai.emport.app/models/llama-3.2-1b.gguf',
      n_ctx: 2048,   // コンテキストサイズ
      n_threads: 4,  // CPUスレッド数
    });
    setContext(ctx);
    setIsLoading(false);
  };

  const chat = async (message: string): Promise<string> => {
    if (!context) return '';
    
    const result = await context.completion({
      prompt: `あなたはAIアシスタントです。\nUser: ${message}\nAssistant:`,
      n_predict: 512,
      temperature: 0.7,
    }, (data) => {
      // Streaming対応
      console.log(data.token); // 1トークンずつ受信
    });
    
    return result.text;
  };

  return { loadModel, chat, isLoading, isReady: !!context };
}
```

### Emport AIでの活用可能性

```
現状の判断: クラウドAI（Claude）を使い続ける

理由:
  - Claude Sonnetの品質に遠く及ばない（1Bモデルは賢くない）
  - モデルファイル（1〜4GB）をダウンロードさせる体験が悪い
  - オフライン対応はEmport AIのコア価値ではない

将来的に検討するタイミング:
  - モデルが進化して小型でも十分な精度になった場合
  - プライバシー重視の医療・法律業種への展開時
  - Claude APIのコストが大きな課題になった時

→ 2026年時点では「知っておく技術」として研究するのみ
```

**情報源:**
- [llama.rn GitHub](https://github.com/mybigday/llama.rn)
- [React Native オンデバイスAI 2026ガイド（Medium）](https://medium.com/@arslannaz195/react-native-on-device-ai-run-llms-without-internet-2026-guide-5bc95fc27bdb)

---

## 53. Emport AI 技術スタック & 開発ロードマップ 総整理

**調査日時: 2026-05-14 (第10ラウンド)**

### 確定技術スタック（今すぐ使うべき）

```
フロントエンド（モバイルアプリ）:
  Framework:  Expo SDK 53（→ 55に移行予定）
  Router:     Expo Router v3
  言語:       TypeScript
  状態管理:   Zustand + persist middleware
  リスト:     FlashList（FlatListから移行）
  ストレージ: MMKV（高速）+ expo-secure-store（機密）
  アニメーション: Reanimated 4（New Architecture）
  型安全:     Zod（APIレスポンス検証）

バックエンド:
  Server:     Flask（Python）on Railway Hobby Plan
  AI:         Claude claude-sonnet-4-6（Prompt Caching有効）
  Auth:       JWT（アクセスコード → JWT発行）

CI/CD:
  Build:      EAS Build（GitHub Actions連携）
  OTA:        EAS Update（バグ修正の即時配布）
  Submit:     EAS Submit（ストア提出自動化）

監視・分析:
  Error:      Sentry（Crash-Free率 99.5%目標）
  Analytics:  PostHog（無料100万イベント/月）
  
テスト:
  Unit:       Jest + React Native Testing Library
  E2E:        Maestro（YAMLで主要フローを自動化）
```

### 開発優先度マトリクス

```
🔴 今すぐ対応（リリース前必須）:
  1. FlashList 導入（パフォーマンス改善）
  2. accessibilityLabel 追加（審査リジェクト防止）
  3. Sentry 設定（エラー監視）
  4. Zod でAPIレスポンス検証
  5. プライバシーポリシー・利用規約ページ作成

🟡 リリース後 Sprint 1（1〜2週間）:
  6. Streaming API（AI応答の逐次表示）
  7. PostHog 設定（アナリティクス）
  8. Maestro でE2Eテスト（ログイン・チャット）
  9. オンボーディングフロー実装（業種選択）
  10. Paywall設計（7日間無料トライアル）

🟢 Sprint 2（1ヶ月後）:
  11. EAS Submit で自動ストア提出設定
  12. Firebase Remote Config（A/Bテスト）
  13. In-App Review（レビュー誘導）
  14. ASO（キーワード最適化・スクリーンショット）
  15. OCR機能（書類スキャン → AI解析）

🔵 将来（3〜6ヶ月後）:
  16. Supabase 移行（マルチユーザー対応）
  17. Development Build移行（プッシュ通知実装）
  18. SDK 55 アップグレード
  19. Expo Router API Routes移行（Flask廃止）
  20. オンデバイスLLM研究（llama.rn）
```

### コスト試算（月次）

```
現在の運用コスト:
  Railway Hobby:       $5/月
  Claude API:          $30〜50/月（利用量による）
  Sentry:              無料（5,000イベント/月）
  PostHog:             無料（100万イベント/月）
  EAS（Expo）:         無料〜$99/月
  合計:                約$35〜55/月

収益目標:
  Phase 1: 100ユーザー × ¥980/月 = ¥98,000/月（黒字化）
  Phase 2: 1,000ユーザー × ¥980/月 = ¥980,000/月
  Phase 3: 10,000ユーザー × ¥650/月（年額換算）= ¥6,500,000/月
```

### 競合との戦い方（最終戦略）

```
「業種特化 × スマートフォン × 低価格 × IT補助金対象」

武器:
  ChatGPTより安い（¥980 vs ¥2,988）
  ChatGPTより業種に詳しい（建設業・製造業の専門知識）
  ChatGPTよりモバイルで使いやすい
  IT導入補助金で実質半額（登録後）

突破口:
  商工会議所経由で中小企業経営者に直接リーチ
  「無料で使ってみてください」から始める
  使った人が口コミで広める
```

**情報源:**
- 第1〜9ラウンドの全調査結果を統合した総括

---

*アプリ開発調査完了（第1〜10ラウンド）。「いい」と言われるまで随時追加継続。*

---

## 54. React Native Flexbox レイアウト 2026年ベストプラクティス

**調査日時: 2026-05-15 (第11ラウンド)**

### Flexboxの基本原則（2026年版）

React Nativeは**Webとほぼ同じFlexbox**を採用しているが、デフォルト値が異なる：

| プロパティ | React Native デフォルト | Web デフォルト |
|-----------|----------------------|--------------|
| `flexDirection` | `column` | `row` |
| `alignContent` | `flex-start` | `normal` |
| `flexShrink` | `0` | `1` |

### 2026年推奨レイアウトパターン

```tsx
// ✅ 推奨：flex:1 で画面全体を使う
export default function Screen() {
  return (
    <View style={{ flex: 1 }}>           {/* 画面全体 */}
      <View style={{ flex: 0.3 }}>       {/* 上部30% */}
        <Header />
      </View>
      <View style={{ flex: 0.7 }}>       {/* 下部70% */}
        <Content />
      </View>
    </View>
  );
}

// ✅ レスポンシブ：useWindowDimensions でデバイス対応
import { useWindowDimensions } from 'react-native';

export function ResponsiveLayout() {
  const { width, height } = useWindowDimensions();
  const isTablet = width >= 768;

  return (
    <View style={{
      flexDirection: isTablet ? 'row' : 'column',
      padding: width * 0.04,  // 画面幅の4%をパディングに
    }}>
      <Card style={{ flex: isTablet ? 0.4 : 1 }} />
      <Card style={{ flex: isTablet ? 0.6 : 1 }} />
    </View>
  );
}
```

### よく使うレイアウトパターン

```tsx
// カード中央配置
const centerStyle = {
  flex: 1,
  justifyContent: 'center',  // 縦方向中央
  alignItems: 'center',      // 横方向中央
};

// ヘッダー＋スクロールコンテンツ
const screenStyle = {
  flex: 1,
  // headerは固定高さ、contentはflex:1で残りを埋める
};

// グリッドレイアウト（2列）
const gridItem = {
  width: '48%',
  margin: '1%',
};

// スペース均等分割
const spaceBetween = {
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
};
```

### Pressable（2026年推奨のタップ処理）

```tsx
// ❌ 非推奨（古い）
<TouchableOpacity onPress={handlePress}>

// ✅ 推奨（2026年）
<Pressable
  onPress={handlePress}
  style={({ pressed }) => ({
    opacity: pressed ? 0.7 : 1,
    transform: [{ scale: pressed ? 0.97 : 1 }],
  })}
>
```

### パーセンテージ vs flex の使い分け

- **flex**: 親の残余スペースを比率で分割 → 動的レイアウトに最適
- **%**: 親要素の幅/高さの割合 → グリッドやカード幅に最適
- **固定値**: ヘッダー高さ・アイコンサイズ等の変えてはいけない値に使う

### Emport AIへの応用

```
現状のEmport AIアプリ（5タブ構成）への適用：
  - BottomTabBar: 高さ固定（60px）、残りをflex:1のコンテンツエリアへ
  - ChatScreen: メッセージリストをflex:1、入力欄を固定高さ
  - レスポンシブ: useWindowDimensionsでiPad対応を将来追加
  - カード一覧: 横2列グリッド（width:'48%'）でAIメニューを表示
```

**情報源:**
- [Layout with Flexbox - React Native公式](https://reactnative.dev/docs/flexbox)
- [Responsive Layouts in React Native 2026](https://oneuptime.com/blog/post/2026-01-15-react-native-responsive-layouts/view)
- [Understanding Flexbox in React Native - Medium](https://medium.com/codetodeploy/understanding-layout-and-flexbox-in-react-native-9a6a5b759d42)

---

## 55. Reanimated 4 アニメーション — CSSトランジション & Worklet

**調査日時: 2026-05-15 (第11ラウンド)**

### Reanimated 4の2大アプローチ

```
1. CSS Transitions API（新機能）
   → Webの書き心地でアニメーション
   → 状態変化に自動追随
   → 初心者向け・シンプル

2. Worklet（従来の強力な機能）
   → UIスレッド上で直接実行
   → 60fps保証（JSスレッド詰まっても無関係）
   → ジェスチャー連動の複雑なアニメーションに最適
```

**前提条件**: React Native 0.76以上 + New Architecture（Fabric）必須

### CSS Transitions API（Reanimated 4の新機能）

```tsx
import Animated, { useAnimatedStyle, withTiming } from 'react-native-reanimated';

// ✅ CSSトランジション風（シンプル）
function FadeButton({ visible }: { visible: boolean }) {
  const animatedStyle = useAnimatedStyle(() => ({
    opacity: withTiming(visible ? 1 : 0, { duration: 300 }),
    transform: [{ scale: withTiming(visible ? 1 : 0.8, { duration: 300 }) }],
  }));

  return <Animated.View style={[styles.button, animatedStyle]} />;
}
```

### Workletでジェスチャー連動アニメーション

```tsx
import { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

function DraggableCard() {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  const panGesture = Gesture.Pan()
    .onUpdate((event) => {
      // UIスレッドで直接実行 → 60fps保証
      translateX.value = event.translationX;
      translateY.value = event.translationY;
    })
    .onEnd(() => {
      // 指を離したらバネで元の位置に戻る
      translateX.value = withSpring(0);
      translateY.value = withSpring(0);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
    ],
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={[styles.card, animatedStyle]} />
    </GestureDetector>
  );
}
```

### よく使うアニメーション関数

| 関数 | 挙動 | 用途 |
|------|------|------|
| `withTiming(value, { duration })` | 線形・イージング | フェード、スライド |
| `withSpring(value)` | バネ物理演算 | ドラッグ後の戻り |
| `withDelay(ms, animation)` | 遅延実行 | 連続アニメーション |
| `withSequence(...animations)` | 順番実行 | テキスト入力アニメ |
| `withRepeat(animation, n)` | 繰り返し | ローディング、点滅 |

### Emport AIへの応用

```
チャット画面:
  - メッセージ出現: withTiming(opacity 0→1, duration: 200)
  - 送信ボタン: withSpring(scale 1→1.1→1) でタップフィードバック
  - ローディング: withRepeat(withTiming) でパルスアニメーション

AI応答ストリーミング:
  - テキスト出現時にfadeIn（0.1秒）
  - 完了時にチェックマークをwithSpringでポップ

ホーム画面:
  - カード切り替え: withTiming(translateX) でスライド
```

**情報源:**
- [Reanimated 4公式ドキュメント](https://docs.swmansion.com/react-native-reanimated/)
- [How to Create Fluid Animations - FreeCodeCamp](https://www.freecodecamp.org/news/how-to-create-fluid-animations-with-react-native-reanimated-v4/)
- [Reanimated 4 Tutorial - React Native Relay](https://reactnativerelay.com/article/mastering-react-native-reanimated-4-css-animations-transitions-worklets)

---

## 56. Expo Router v4 ナビゲーション & 画面遷移

**調査日時: 2026-05-15 (第11ラウンド)**

### Expo Router v4の変更点（重要）

```
⚠️ 破壊的変更（v3→v4）:
  router.navigate() が router.push() と同じ挙動になった
  → 旧: navigate()はスタックを賢く管理
  → 新: navigate()は常にスタックにpush
  → 対策: router.replace() を使ってスタックを置き換える
```

### ファイルベースルーティング構造

```
app/
├── (tabs)/           ← タブグループ
│   ├── _layout.tsx   ← タブ設定
│   ├── index.tsx     ← ホームタブ
│   ├── chat.tsx      ← AIチャットタブ
│   └── settings.tsx  ← 設定タブ
├── (auth)/           ← 認証グループ
│   ├── login.tsx
│   └── register.tsx
├── _layout.tsx       ← ルートレイアウト（認証状態管理）
└── +not-found.tsx    ← 404ページ
```

### スクリーン遷移の実装

```tsx
import { router } from 'expo-router';

// 基本的なナビゲーション
router.push('/chat');           // スタックにpush
router.replace('/home');        // 現在のスクリーンを置き換え
router.back();                  // 戻る
router.canGoBack();             // 戻れるか確認

// パラメータ付きナビゲーション
router.push({
  pathname: '/chat/[id]',
  params: { id: 'session-123' }
});

// 型安全なルーティング（TypeScript）
import { Link } from 'expo-router';
<Link href="/chat" asChild>
  <Pressable><Text>チャットへ</Text></Pressable>
</Link>
```

### アニメーション付き画面遷移

```tsx
// _layout.tsx でスタックアニメーションを設定
import { Stack } from 'expo-router';

export default function Layout() {
  return (
    <Stack
      screenOptions={{
        animation: 'slide_from_right',    // iOS標準スライド
        // animation: 'fade',             // フェード
        // animation: 'flip',             // フリップ
        // animation: 'zoom',             // ズーム（新機能）
        headerShown: false,
      }}
    />
  );
}
```

### Zoom Transition（Expo Router独自機能）

```tsx
// 要素から画面へのズームトランジション
import { ZoomTransition } from 'expo-router';

// リスト項目をタップしたら詳細画面にズームで遷移
function ListItem({ item }) {
  return (
    <ZoomTransition sharedTransitionTag={`item-${item.id}`}>
      <Pressable onPress={() => router.push(`/detail/${item.id}`)}>
        <Image style={{ width: 100, height: 100 }} source={{ uri: item.image }} />
      </Pressable>
    </ZoomTransition>
  );
}
```

### モーダル画面の実装

```tsx
// app/_layout.tsx
<Stack>
  <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
  <Stack.Screen
    name="modal"
    options={{
      presentation: 'modal',        // iOS: カードモーダル
      // presentation: 'transparentModal',  // 透明背景モーダル
      animation: 'slide_from_bottom',
    }}
  />
</Stack>
```

### Emport AIへの応用

```
現在の5タブ構成に加えて:
  - AI相談 → 詳細セッション: slide_from_right
  - 設定モーダル: presentation:'modal'でボトムシート風
  - エラー画面: presentation:'transparentModal'でオーバーレイ
  - オンボーディング: replace()で戻れないフロー設計

重要: v4での router.navigate()→router.replace() の移行を確認
```

**情報源:**
- [Expo Router公式ドキュメント](https://docs.expo.dev/router/introduction/)
- [React Navigation with Expo Router 2026](https://www.codesofphoenix.com/articles/expo/expo-router-nav)
- [Zoom Transition - Expo Documentation](https://docs.expo.dev/router/advanced/zoom-transition/)

---

## 57. UIコンポーネントライブラリ比較 — NativeWind vs Tamagui vs Gluestack

**調査日時: 2026-05-15 (第11ラウンド)**

### 2026年の主要3ライブラリ比較

| ライブラリ | 週次DL | 特徴 | 推奨ユースケース |
|-----------|--------|------|----------------|
| **NativeWind 4.x** | 約40万 | TailwindCSS構文をネイティブで使用 | Webから移行・速い開発 |
| **Tamagui** | 約7.5万 | 最適化コンパイラで最高パフォーマンス | パフォーマンス最優先 |
| **Gluestack UI v2** | 約3万 | RSC・Expo対応・アクセシビリティ優秀 | 本格的デザインシステム |

### NativeWind 4.x（最もシェアが高い）

```tsx
// インストール
npm install nativewind
npm install --save-dev tailwindcss

// 使い方：TailwindCSSと全く同じ構文
import { View, Text, Pressable } from 'react-native';

export function ChatBubble({ message, isUser }) {
  return (
    <View className={`
      max-w-[80%] rounded-2xl px-4 py-3 mb-2
      ${isUser ? 'bg-blue-600 self-end' : 'bg-gray-100 self-start'}
    `}>
      <Text className={isUser ? 'text-white' : 'text-gray-900'}>
        {message.content}
      </Text>
    </View>
  );
}

// Container Queries（v4新機能）
<View className="@container">
  <Text className="@sm:text-lg @md:text-xl">レスポンシブテキスト</Text>
</View>
```

### Tamagui（最高パフォーマンス）

```tsx
import { Button, Card, Text, XStack, YStack } from 'tamagui';

export function AICard({ title, description }) {
  return (
    <Card elevate bordered padding="$4">
      <YStack gap="$2">
        <Text fontSize="$6" fontWeight="bold">{title}</Text>
        <Text fontSize="$4" color="$gray10">{description}</Text>
        <XStack gap="$2" justifyContent="flex-end">
          <Button size="$3" variant="outlined">詳細</Button>
          <Button size="$3" theme="active">使う</Button>
        </XStack>
      </YStack>
    </Card>
  );
}
// ↑ コンパイル時に最適化 → 実行時オーバーヘッドなし
```

### Gluestack UI v2（アクセシビリティ特化）

```tsx
import { Button, ButtonText, Input, InputField, VStack } from '@gluestack-ui/themed';

export function LoginForm() {
  return (
    <VStack space="md">
      <Input>
        <InputField placeholder="メールアドレス" />
      </Input>
      <Button>
        <ButtonText>ログイン</ButtonText>
      </Button>
    </VStack>
  );
}
// アクセシビリティ属性が自動付与（WAI-ARIA準拠）
```

### Emport AIへの推奨選択

```
【推奨: NativeWind 4.x】

理由:
  1. 開発速度が最も速い（TailwindCSSの知識が転用できる）
  2. 週40万DL・コミュニティが最大 → StackOverflow回答が豊富
  3. Expo SDKと相性良好
  4. 既存コードへの段階的導入が容易

移行手順:
  1. npx expo install nativewind tailwindcss
  2. tailwind.config.js を設定
  3. babel.config.js に nativewind/babel を追加
  4. 既存のStyleSheet.create()を徐々にclassName=""に移行
```

**情報源:**
- [The 10 best React Native UI libraries 2026 - LogRocket](https://blog.logrocket.com/best-react-native-ui-component-libraries/)
- [Best React Native libraries with Tailwind 2026 - DEV Community](https://dev.to/ninarao/best-react-native-component-libraries-with-tailwind-support-for-fast-ui-development-in-2026-2fe4)
- [Tamagui公式](https://tamagui.dev/)
- [Gluestack UI公式](https://gluestack.io/)

---

## 58. モバイルUX/UIデザイントレンド 2026

**調査日時: 2026-05-15 (第11ラウンド)**

### 2026年の主要UIトレンド

#### 1. ボトムシートUIの覇権

```
ボトムシートが2026年のメインUIパターン:
  - Appleがios15でボトムシートを標準化
  - Googleも Material Design 3でボトムシートを推奨
  - 適用場面: 詳細情報・フィルター・アクションメニュー・設定
  
日本アプリでの活用例:
  - LINEのメンションピッカー
  - メルカリの商品詳細シート
  - PayPayの送金確認
```

#### 2. グラスモーフィズム（選択的活用）

```tsx
// 2026年のグラスモーフィズムは「場所を選んで」使う
const glassStyle = {
  backgroundColor: 'rgba(255, 255, 255, 0.15)',
  backdropFilter: 'blur(20px)',  // iOS: BlurViewで代替
  borderWidth: 1,
  borderColor: 'rgba(255, 255, 255, 0.3)',
  borderRadius: 16,
};

// 適用場面: 通知カード・メディアコントロール・コンテキストメニュー
// 非適用場面: メインコンテンツ・テキスト読みやすさが必要な箇所
```

#### 3. マイクロインタラクション（UX差別化の鍵）

```tsx
// いいね！ボタンのマイクロインタラクション
function LikeButton() {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePress = () => {
    scale.value = withSequence(
      withTiming(1.3, { duration: 100 }),  // 大きく
      withSpring(1)                         // バネで戻る
    );
    // + ハプティックフィードバック（触覚）
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  return (
    <Animated.View style={animatedStyle}>
      <Pressable onPress={handlePress}>
        <Icon name="heart" />
      </Pressable>
    </Animated.View>
  );
}
```

#### 4. AIによるパーソナライズUI（2026年最先端）

```
AIがUIそのものを変える:
  - 使用頻度の高い機能を上位に自動配置
  - 時間帯・場所・利用状況でメニューを変化
  - ユーザーの行動パターンからレイアウトを最適化

Emport AIへの応用:
  - 朝: ニュースブリーフィング機能を前面に
  - 商談後: 議事録整理・メール作成を提案
  - 夜: SNS投稿スケジューリングを前面に
```

#### 5. ミニマリズム ≠ シンプル（2026年解釈）

```
2026年のミニマリズムの定義:
  - 情報密度を下げる × 機能を減らす
  - 意図的な余白: 最小margin 16dp（Material Design推奨）
  - フォーカス: 1画面に1つのプライマリアクション
  - タイポグラフィ: 見出し/本文の明確な階層（3段階まで）

日本のアプリに特有の注意点:
  - iOS シェアが高い（日本はiOS優位）→ iOS Human Interface Guidelinesを優先
  - 日本語フォントはサイズを1-2pt大きめに設定（可読性確保）
  - 情報量を多く表示する傾向 → スクロール可能なリストより展開式UIを好む
```

### UIカラーパレット設計（2026年版）

```tsx
// Emport AI向け推奨カラーシステム
const colors = {
  // プライマリ（信頼・テクノロジー）
  primary: '#1A3B8C',       // ネイビーブルー（ピッチ書と同色系）
  primaryLight: '#EBF0FF',  // 薄青（背景・カード）

  // セマンティック
  success: '#22C55E',       // 緑（完了・成功）
  warning: '#F59E0B',       // 黄（注意・処理中）
  error: '#EF4444',         // 赤（エラー）

  // ニュートラル（テキスト・背景）
  textPrimary: '#111827',   // ほぼ黒
  textSecondary: '#6B7280', // グレー
  background: '#F9FAFB',    // ほぼ白
  surface: '#FFFFFF',       // 純白（カード）
  border: '#E5E7EB',        // 薄いグレー

  // ダークモード対応
  dark: {
    background: '#111827',
    surface: '#1F2937',
    border: '#374151',
  }
};
```

### Emport AIへの応用

```
実装優先度:
  🔴 即時: ボトムシートUI（AI相談の入力欄をボトムシート化）
  🔴 即時: マイクロインタラクション（送信ボタン・いいね系）
  🟡 次期: グラスモーフィズム（通知カードに適用）
  🟡 次期: AIパーソナライズ（時間帯でホーム画面変更）
  🟢 将来: ダークモード対応
```

**情報源:**
- [9 Mobile App Design Trends for 2026 - UXPilot](https://uxpilot.ai/blogs/mobile-app-design-trends)
- [UI Patterns That Matter in 2026 - Muzli](https://muz.li/blog/whats-changing-in-mobile-app-design-ui-patterns-that-matter-in-2026/)
- [Mobile UI/UX Design Trends 2026 - UIStudioZ](https://uistudioz.com/blog/mobile-ui-ux-the-design-trends/)

---

## 59. ジェスチャーハンドリング — スワイプ・ドラッグ＆ドロップ

**調査日時: 2026-05-15 (第11ラウンド)**

### react-native-gesture-handler v3 の主要ジェスチャー

```tsx
import { GestureDetector, Gesture } from 'react-native-gesture-handler';

// ① タップ
const tap = Gesture.Tap()
  .numberOfTaps(1)               // シングルタップ
  .onStart(() => console.log('タップ'));

// ② ダブルタップ（いいね！など）
const doubleTap = Gesture.Tap()
  .numberOfTaps(2)
  .onStart(() => toggleLike());

// ③ 長押し
const longPress = Gesture.LongPress()
  .minDuration(500)
  .onStart(() => showContextMenu());

// ④ パン（ドラッグ）
const pan = Gesture.Pan()
  .onUpdate((e) => {
    translateX.value = e.translationX;
  })
  .onEnd(() => {
    translateX.value = withSpring(0);
  });

// 複数ジェスチャーの組み合わせ
const combined = Gesture.Simultaneous(pan, tap);  // 同時認識
const exclusive = Gesture.Exclusive(doubleTap, tap); // 優先順位付き

return (
  <GestureDetector gesture={combined}>
    <Animated.View style={animatedStyle} />
  </GestureDetector>
);
```

### スワイプで削除（メッセージ・リストアイテム）

```tsx
import { Swipeable } from 'react-native-gesture-handler';

function SwipeableMessage({ message, onDelete }) {
  const renderRightActions = () => (
    <Pressable
      style={styles.deleteAction}
      onPress={() => onDelete(message.id)}
    >
      <Text style={{ color: 'white' }}>削除</Text>
    </Pressable>
  );

  return (
    <Swipeable
      renderRightActions={renderRightActions}
      friction={2}              // スワイプの重さ（1=軽い、2=標準）
      overshootRight={false}   // 右端を超えてスワイプしない
    >
      <MessageBubble message={message} />
    </Swipeable>
  );
}
```

### ドラッグ＆ドロップ（リスト並び替え）

```tsx
// react-native-draggable-flatlist を使用
import DraggableFlatList from 'react-native-draggable-flatlist';

function ReorderableList({ items, onReorder }) {
  return (
    <DraggableFlatList
      data={items}
      keyExtractor={(item) => item.id}
      renderItem={({ item, drag, isActive }) => (
        <Pressable
          onLongPress={drag}       // 長押しでドラッグ開始
          style={{
            backgroundColor: isActive ? '#E5E7EB' : 'white',
            transform: [{ scale: isActive ? 1.05 : 1 }],
          }}
        >
          <Text>{item.title}</Text>
        </Pressable>
      )}
      onDragEnd={({ data }) => onReorder(data)}
    />
  );
}
```

### ハプティックフィードバック（触覚）

```tsx
import * as Haptics from 'expo-haptics';

// ジェスチャーに触覚フィードバックを追加
const handleSwipeDelete = () => {
  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
};

const handleLongPress = () => {
  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
};

const handleSuccess = () => {
  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
};
```

### Emport AIへの応用

```
チャット画面:
  - メッセージを左スワイプ → コピー/引用アクション表示
  - 送信ボタン長押し → 録音モード（将来機能）
  - プルダウン → チャット履歴リフレッシュ

ホーム画面:
  - AIカードを長押し → ドラッグで並び替え
  - 横スワイプ → 業種カテゴリ切り替え

設定画面:
  - リスト項目スワイプ → 削除オプション表示
```

**情報源:**
- [React Native Gesture Handler with Expo 2026](https://www.codesofphoenix.com/articles/expo/react-native-gesture-handler)
- [Add gestures - Expo Documentation](https://docs.expo.dev/tutorial/gestures/)
- [Reanimated Swipeable](https://docs.swmansion.com/react-native-gesture-handler/docs/components/reanimated_swipeable/)

---

## 60. ボトムシート & モーダル設計

**調査日時: 2026-05-15 (第11ラウンド)**

### @gorhom/bottom-sheet（2026年デファクトスタンダード）

```bash
npx expo install @gorhom/bottom-sheet react-native-reanimated react-native-gesture-handler
```

```tsx
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';
import { useRef, useMemo, useCallback } from 'react';

function ChatScreen() {
  const bottomSheetRef = useRef<BottomSheet>(null);

  // スナップポイント: 25%, 50%, 90%の高さで止まる
  const snapPoints = useMemo(() => ['25%', '50%', '90%'], []);

  const handleOpen = useCallback(() => {
    bottomSheetRef.current?.expand();
  }, []);

  const handleClose = useCallback(() => {
    bottomSheetRef.current?.close();
  }, []);

  return (
    <>
      <MainContent onAIButton={handleOpen} />

      <BottomSheet
        ref={bottomSheetRef}
        index={-1}              // -1 = 初期非表示
        snapPoints={snapPoints}
        enablePanDownToClose   // 下スワイプで閉じる
        backgroundStyle={{ borderRadius: 24 }}
        handleIndicatorStyle={{ backgroundColor: '#ccc', width: 40 }}
      >
        <BottomSheetView style={styles.contentContainer}>
          <AIInputPanel />
        </BottomSheetView>
      </BottomSheet>
    </>
  );
}
```

### BottomSheetModal（スタック対応）

```tsx
import { BottomSheetModal, BottomSheetModalProvider } from '@gorhom/bottom-sheet';

// Apple Maps風のスタック可能なモーダル
function App() {
  const modalRef = useRef<BottomSheetModal>(null);

  const handlePresent = () => modalRef.current?.present();
  const handleDismiss = () => modalRef.current?.dismiss();

  return (
    <BottomSheetModalProvider>
      <View>
        <Button onPress={handlePresent} title="AI相談を開く" />

        <BottomSheetModal
          ref={modalRef}
          index={1}
          snapPoints={['50%', '90%']}
          onDismiss={() => console.log('閉じた')}
        >
          <BottomSheetView>
            <AIConsultPanel />
          </BottomSheetView>
        </BottomSheetModal>
      </View>
    </BottomSheetModalProvider>
  );
}
```

### FlatList/ScrollView対応

```tsx
import { BottomSheetFlatList } from '@gorhom/bottom-sheet';

// ✅ 通常のFlatListではなくBottomSheetFlatListを使う
// → ボトムシート内でスクロールとジェスチャーが競合しない
function ChatHistorySheet() {
  return (
    <BottomSheet snapPoints={['50%', '90%']}>
      <BottomSheetFlatList
        data={chatHistory}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <ChatItem item={item} />}
        contentContainerStyle={{ paddingHorizontal: 16 }}
      />
    </BottomSheet>
  );
}
```

### カスタムドラッグハンドル

```tsx
const CustomHandle = () => (
  <View style={styles.handleContainer}>
    <View style={styles.handle} />
    <Text style={styles.title}>AI相談</Text>
  </View>
);

<BottomSheet handleComponent={CustomHandle}>
```

### Emport AIへの具体的な実装案

```
AI相談タブ（現在: 全画面）→ ボトムシート化のメリット:

Before（現在）:
  AIチャット → 別画面に遷移 → 他の機能を見ながら使えない

After（ボトムシート化）:
  ホーム画面を見ながら → ボトムシートでAI相談
  →「今日のニュース」を見ながらAIに質問できる
  → UXが大幅改善

実装手順:
  1. @gorhom/bottom-sheet をインストール
  2. 現在のChatScreen.tsx をBottomSheetView内に移動
  3. ホームのFABボタン（フローティングボタン）でシート展開
  4. snapPoints = ['60%', '95%'] で2段階展開

補助金情報モーダル:
  - BottomSheetModal でプレゼンテーション
  - FlatListで補助金一覧をスクロール
```

**情報源:**
- [@gorhom/bottom-sheet GitHub](https://github.com/gorhom/react-native-bottom-sheet)
- [React Native Bottom Sheet公式](https://gorhom.github.io/react-native-bottom-sheet/)
- [Bottom Sheet - Reanimated Examples](https://docs.swmansion.com/react-native-reanimated/examples/bottomsheet/)

---

*第11ラウンド完了（2026-05-15）: セクション54〜60 — レイアウト・アニメーション・ナビゲーション・UIライブラリ・UXトレンド・ジェスチャー・ボトムシート*

---

## 61. タイポグラフィ & フォントシステム — Expo Google Fonts・可変フォント

**調査日時: 2026-05-15 (第12ラウンド)**

### 2つのフォント読み込み方法

| 方法 | 特徴 | 推奨場面 |
|------|------|----------|
| **Config Plugin（埋め込み）** | アプリ起動と同時に利用可能・非同期待ち不要 | 本番アプリ |
| **useFonts Hook（動的読込）** | iOS/Android/Web全対応・コード変更不要 | プロトタイプ |

### Google Fontsの使い方（最速）

```bash
# Noto Sans JP（日本語対応）をインストール
npx expo install @expo-google-fonts/noto-sans-jp expo-font expo-splash-screen
```

```tsx
import { useFonts, NotoSansJP_400Regular, NotoSansJP_700Bold } from '@expo-google-fonts/noto-sans-jp';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    NotoSansJP_400Regular,
    NotoSansJP_700Bold,
  });

  useEffect(() => {
    if (fontsLoaded) SplashScreen.hideAsync();
  }, [fontsLoaded]);

  if (!fontsLoaded) return null;

  return <App />;
}

// 使い方
<Text style={{ fontFamily: 'NotoSansJP_400Regular', fontSize: 16 }}>
  日本語テキスト
</Text>
```

### タイポグラフィスケール（Emport AI推奨）

```tsx
// constants/Typography.ts
export const Typography = {
  // フォントファミリー
  fontFamily: {
    regular: 'NotoSansJP_400Regular',
    bold: 'NotoSansJP_700Bold',
    mono: 'SpaceMono_400Regular',
  },

  // サイズスケール（Material Design 3準拠）
  fontSize: {
    xs: 11,   // ラベル・バッジ
    sm: 13,   // キャプション・補足
    base: 15, // 本文（日本語は+1〜2pt推奨）
    md: 17,   // 強調本文
    lg: 20,   // サブタイトル
    xl: 24,   // タイトル
    '2xl': 30, // 大見出し
    '3xl': 38, // ヒーロー
  },

  // 行間（line height）
  lineHeight: {
    tight: 1.2,   // 見出し
    normal: 1.5,  // 本文（日本語は1.7推奨）
    loose: 1.8,   // 長文・説明文
  },

  // 字間
  letterSpacing: {
    tight: -0.5,
    normal: 0,
    wide: 0.5,    // 日本語の見出しに効果的
  },
};
```

### 可変フォント（2026年最新）

```
Variable Fonts のメリット:
  - 1ファイルで全ウェイト（100〜900）が使える
  - バンドルサイズ最大80%削減（静的フォント複数 vs 可変フォント1つ）
  - React Native 0.79 + Fabric が可変フォントをサポート

使用例:
  Inter Variable → Webに最適（英語メイン）
  Noto Sans JP → 日本語対応の信頼性No.1
```

### 日本語フォント特有の注意点

```
1. サイズを英語より1〜2pt大きめに → 可読性確保
2. 行間は1.7〜1.8倍 → 漢字の複雑さを補う
3. letterSpacingは0〜+0.5pt → きつすぎる字間は読みにくい
4. ボールドはweight:700のみ使用（中間ウェイトは日本語で崩れやすい）
5. フォント未ロード時はシステムフォント（ヒラギノ/Noto）でフォールバック
```

**情報源:**
- [Fonts - Expo Documentation](https://docs.expo.dev/develop/user-interface/fonts/)
- [expo/google-fonts GitHub](https://github.com/expo/google-fonts)
- [Add Custom Fonts in Expo 2026](https://javascript.plainenglish.io/add-custom-fonts-in-expo-2025-guide-3611083cddf1)

---

## 62. ダークモード & カラーシステム設計

**調査日時: 2026-05-15 (第12ラウンド)**

### Expoでのダークモード実装（3ステップ）

```tsx
// Step 1: app.json でダークモード宣言
{
  "expo": {
    "userInterfaceStyle": "automatic"  // "light" | "dark" | "automatic"
  }
}

// Step 2: カラー定数ファイル
// constants/Colors.ts
const Colors = {
  light: {
    text: '#111827',
    background: '#F9FAFB',
    surface: '#FFFFFF',
    primary: '#1A3B8C',
    border: '#E5E7EB',
    tint: '#1A3B8C',
  },
  dark: {
    text: '#F9FAFB',
    background: '#111827',
    surface: '#1F2937',
    primary: '#4F7FFF',
    border: '#374151',
    tint: '#4F7FFF',
  },
};

export default Colors;

// Step 3: useColorScheme で切り替え
import { useColorScheme } from 'react-native';
import Colors from '@/constants/Colors';

export function ThemedCard({ children }) {
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];

  return (
    <View style={{
      backgroundColor: colors.surface,
      borderColor: colors.border,
      borderWidth: 1,
      borderRadius: 12,
      padding: 16,
    }}>
      {children}
    </View>
  );
}
```

### NativeWindでのダークモード（最もシンプル）

```tsx
// tailwind.config.js
module.exports = {
  darkMode: 'class',  // または 'media'（システム追従）
};

// コンポーネント
<View className="bg-white dark:bg-gray-900">
  <Text className="text-gray-900 dark:text-white">
    テキスト
  </Text>
</View>

// 手動切り替え
import { colorScheme } from 'nativewind';
colorScheme.set('dark');    // ダークに固定
colorScheme.set('light');   // ライトに固定
colorScheme.set('system');  // システム追従に戻す
```

### カスタムテーマ Context（手動切り替え＋永続化）

```tsx
// context/ThemeContext.tsx
import { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

type Theme = 'light' | 'dark' | 'system';

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (t: Theme) => void;
  colors: typeof Colors.light;
}>({ theme: 'system', setTheme: () => {}, colors: Colors.light });

export function ThemeProvider({ children }) {
  const systemScheme = useColorScheme();
  const [theme, setThemeState] = useState<Theme>('system');

  const activeScheme = theme === 'system' ? (systemScheme ?? 'light') : theme;
  const colors = Colors[activeScheme];

  const setTheme = async (t: Theme) => {
    setThemeState(t);
    await AsyncStorage.setItem('app_theme', t);  // 永続化
  };

  useEffect(() => {
    AsyncStorage.getItem('app_theme').then((saved) => {
      if (saved) setThemeState(saved as Theme);
    });
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
```

### Emport AIへの応用

```
実装優先度:
  🔴 即時: NativeWindの dark: クラスをカード・背景に適用
  🟡 次期: ThemeContext + AsyncStorage で設定画面から切り替え
  🟢 将来: テーマ設定をバックエンドに同期（デバイス間共有）

ポイント:
  - 日本の中小企業経営者ターゲット → ダークモードより「見やすいライトモード」を優先
  - チャート・グラフを使う場合はダークモードで映えるように設計
```

**情報源:**
- [Color themes - Expo Documentation](https://docs.expo.dev/develop/user-interface/color-themes/)
- [Dark Mode - NativeWind](https://www.nativewind.dev/docs/core-concepts/dark-mode)
- [Implementing Dark/Light Mode with Expo Router](https://medium.com/@vipinnation/implementing-dark-and-light-mode-in-react-native-with-expo-router-a-complete-guide-bf26f32aba31)

---

## 63. React Native Skia — GPU描画・カスタムグラフィックス

**調査日時: 2026-05-15 (第12ラウンド)**

### Skiaとは

```
@shopify/react-native-skia:
  - Google Chrome・Flutter・Androidと同じSkiaグラフィックスエンジン
  - GPU直接描画 → 120fps対応デバイスでも滑らか
  - 最新: v2.6.x (2026年4月) → React Native 0.79 + React 19 + Expo SDK 55
  - Canvas・Path・テキスト・グラデーション・シェーダー・フィルター全対応
```

### 基本的な使い方

```bash
npx expo install @shopify/react-native-skia
```

```tsx
import { Canvas, Circle, Paint, Path, LinearGradient, vec } from '@shopify/react-native-skia';

// 円グラフ（AIスコア表示に使える）
export function ScoreGauge({ score }: { score: number }) {
  const size = 200;
  const strokeWidth = 20;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;

  return (
    <Canvas style={{ width: size, height: size }}>
      {/* 背景円 */}
      <Circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        style="stroke"
        strokeWidth={strokeWidth}
        color="#E5E7EB"
      />
      {/* 進捗円（パスで描画） */}
      <Path
        path={`M ${size/2} ${strokeWidth/2} A ${radius} ${radius} 0 ${score > 50 ? 1 : 0} 1 ${size/2 + radius * Math.sin(2 * Math.PI * score/100)} ${size/2 - radius * Math.cos(2 * Math.PI * score/100)}`}
        style="stroke"
        strokeWidth={strokeWidth}
        strokeCap="round"
        color="#1A3B8C"
      />
    </Canvas>
  );
}

// グラデーション背景
export function GradientCard() {
  return (
    <Canvas style={{ width: 300, height: 200 }}>
      <Paint>
        <LinearGradient
          start={vec(0, 0)}
          end={vec(300, 200)}
          colors={['#1A3B8C', '#4F7FFF']}
        />
      </Paint>
      <RoundedRect x={0} y={0} width={300} height={200} r={16} />
    </Canvas>
  );
}
```

### Reaniatedとの連携（60fpsアニメーション）

```tsx
import { useSharedValue, withTiming } from 'react-native-reanimated';
import { useAnimatedProps } from '@shopify/react-native-skia';

function AnimatedProgress({ target }: { target: number }) {
  const progress = useSharedValue(0);

  useEffect(() => {
    progress.value = withTiming(target, { duration: 1000 });
  }, [target]);

  // Skia + Reanimated → GPUで60fps保証
  const animatedProps = useAnimatedProps(() => ({
    strokeDashoffset: circumference * (1 - progress.value),
  }));
}
```

### Emport AIへの応用

```
使用場面:
  ① AIスコアゲージ（業務効率化率を円グラフで表示）
  ② 月次売上チャート（棒グラフ・折れ線グラフ）
  ③ 補助金申請ステータス（ステップ表示）
  ④ ローディングアニメーション（ブランドカラーのカスタムスピナー）
  ⑤ ホーム画面のヒーロービジュアル（グラデーション+アニメーション）

優先度: 🟠 中（基本UIが完成してから追加）
理由: Skiaは強力だが実装コストが高い。まず標準コンポーネントで形を作り、
     差別化が必要な画面から順にSkiaへ移行する戦略が最善。
```

**情報源:**
- [Skia Game Changer for React Native 2026 - Medium](https://medium.com/@expertappdevs/skia-game-changer-for-react-native-in-2026-f23cb9b85841)
- [React Native Skia Tutorial 2026 - React Native Relay](https://reactnativerelay.com/article/react-native-skia-tutorial-gpu-graphics-shaders-animations-expo)
- [@shopify/react-native-skia - Expo Documentation](https://docs.expo.dev/versions/latest/sdk/skia/)

---

## 64. Figma → React Native ワークフロー & デザイントークン

**調査日時: 2026-05-15 (第12ラウンド)**

### 2026年の推奨ワークフロー

```
Figma Variables（デザイントークン）
  ↓ Tokens Studio プラグインでJSON出力
  ↓ Style Dictionary で変換（JSON → TypeScript/NativeWind設定）
  ↓ CI/CDでGitHubへPR自動作成
  ↓ React Nativeで直接使用
```

### Figma Variables → コード変換

```json
// Figma から出力されるトークンJSON（例）
{
  "color": {
    "primary": { "value": "#1A3B8C", "type": "color" },
    "primary-light": { "value": "#EBF0FF", "type": "color" },
    "text-primary": { "value": "#111827", "type": "color" }
  },
  "spacing": {
    "xs": { "value": "4", "type": "spacing" },
    "sm": { "value": "8", "type": "spacing" },
    "md": { "value": "16", "type": "spacing" },
    "lg": { "value": "24", "type": "spacing" }
  },
  "borderRadius": {
    "sm": { "value": "4", "type": "borderRadius" },
    "md": { "value": "8", "type": "borderRadius" },
    "lg": { "value": "16", "type": "borderRadius" },
    "full": { "value": "9999", "type": "borderRadius" }
  }
}
```

```ts
// Style Dictionary が変換した TypeScript (constants/tokens.ts)
export const tokens = {
  color: {
    primary: '#1A3B8C',
    primaryLight: '#EBF0FF',
    textPrimary: '#111827',
  },
  spacing: { xs: 4, sm: 8, md: 16, lg: 24 },
  borderRadius: { sm: 4, md: 8, lg: 16, full: 9999 },
} as const;
```

### Figma Community Plugin（即座に使える）

```
「Figma to React Native」プラグイン:
  - FigmaのフレームをReact Nativeコードに変換
  - StyleSheet.create()形式で出力
  - 自動で色・フォント・余白を抽出

使い方:
  1. Figmaでフレームを選択
  2. Plugin → Figma to React Native
  3. コードをコピー → コンポーネントファイルに貼り付け
  4. 細部を手動調整（80%は使えるコードが生成される）
```

### Emport AI推奨ワークフロー

```
現在（コードファースト）:
  コードで直接デザイン → ファイルに保存 → Figmaなし

推奨（デザインシステム確立後）:
  Figmaでデザインシステム構築（色・スペーシング・コンポーネント）
  → tokens.ts にエクスポート
  → NativeWindの tailwind.config.js と連携
  → コンポーネント実装

今すぐできること:
  1. constants/tokens.ts を作成（上記のデザイントークン）
  2. NativeWindのextend.colorsにtokensを登録
  3. 全コンポーネントでハードコードされた色をtokensに置き換え
```

**情報源:**
- [Figma to React Native - RapidNative](https://www.rapidnative.com/blogs/figma-to-react-native)
- [Figma to Code: Design Tokens 2026](https://inhaq.com/blog/figma-to-code-design-engineer-workflow)
- [Automating Figma to React Token Pipeline - Medium](https://medium.com/@alexdev82/automating-the-figma-to-react-design-token-pipeline-3d3cf35c5a19)

---

## 65. スケルトンローディング & シマー効果

**調査日時: 2026-05-15 (第12ラウンド)**

### なぜスケルトンが重要か

```
研究結果:
  - スケルトン表示 vs スピナー → ユーザーが「50%速く感じる」
  - 実際の読み込み時間は同じでも体感が大幅改善
  - Facebook・LinkedIn・YouTube全てスケルトンを採用

原則:
  - 実際のコンテンツと同じ形・サイズのプレースホルダーを表示
  - レイアウトシフトを防ぐ（コンテンツ表示後にガクッとなる問題を解決）
```

### 推奨ライブラリ（2026年）

```bash
# react-native-auto-skeleton（ゼロ設定・自動生成）
npm install react-native-auto-skeleton

# またはカスタム実装（Reanimated使用）
```

### カスタムスケルトン実装（Reanimated）

```tsx
import { useEffect } from 'react';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withTiming, interpolate
} from 'react-native-reanimated';

function SkeletonBox({ width, height, borderRadius = 8 }) {
  const shimmer = useSharedValue(0);

  useEffect(() => {
    shimmer.value = withRepeat(
      withTiming(1, { duration: 1000 }),
      -1,    // 無限繰り返し
      false  // 往復なし
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: interpolate(shimmer.value, [0, 0.5, 1], [0.4, 0.8, 0.4]),
  }));

  return (
    <Animated.View
      style={[
        {
          width,
          height,
          borderRadius,
          backgroundColor: '#E5E7EB',
        },
        animatedStyle,
      ]}
    />
  );
}

// チャットリストのスケルトン
export function ChatListSkeleton() {
  return (
    <View style={{ padding: 16, gap: 12 }}>
      {[1, 2, 3, 4, 5].map((i) => (
        <View key={i} style={{ flexDirection: 'row', gap: 12, alignItems: 'center' }}>
          <SkeletonBox width={48} height={48} borderRadius={24} />  {/* アバター */}
          <View style={{ flex: 1, gap: 6 }}>
            <SkeletonBox width="60%" height={14} />   {/* 名前 */}
            <SkeletonBox width="90%" height={12} />   {/* メッセージ */}
          </View>
        </View>
      ))}
    </View>
  );
}
```

### react-native-auto-skeleton（ゼロ設定）

```tsx
import Skeleton from 'react-native-auto-skeleton';

// 本番コンポーネント
function UserCard({ user }) {
  return (
    <View>
      <Image source={{ uri: user.avatar }} />
      <Text>{user.name}</Text>
    </View>
  );
}

// スケルトン版（構造をそのまま使う）
<Skeleton loading={isLoading} animation="shimmer">
  <UserCard user={placeholderUser} />
</Skeleton>
// → ローディング中は自動でスケルトンに変換
```

### Emport AIへの適用箇所

```
チャット履歴一覧:
  ロード中 → ChatListSkeleton（上記コード）
  完了後 → 実際の履歴リスト

AIレスポンス生成中:
  テキスト領域に3行のSkeletonBox
  → テキストが届き始めたら順次実際のテキストに切り替え

ホーム画面カード:
  データ取得中 → カード形のSkeletonBox×4
  → コンテンツ読み込み後にフェードイン切り替え
```

**情報源:**
- [React Native Skeleton Loaders - Medium](https://medium.com/@andrew.chester/react-native-skeleton-loaders-elevate-your-apps-ux-with-shimmering-placeholders-5003b9507117)
- [react-native-auto-skeleton GitHub](https://github.com/pioner92/react-native-auto-skeleton)
- [Fast Shimmer Effects - Callstack](https://www.callstack.com/blog/performant-and-cross-platform-shimmers-in-react-native-apps)

---

## 66. アクセシビリティ実装（VoiceOver / TalkBack）

**調査日時: 2026-05-15 (第12ラウンド)**

### アクセシビリティが重要な理由

```
日本における数字:
  - 視覚障害者: 約31万人（2023年）
  - 高齢者（65歳以上）: 約3,500万人 → 文字が見えにくい
  - 中小企業経営者の平均年齢: 60.3歳（2023年中小企業白書）

→ Emport AIのターゲット（中高年経営者）にとってアクセシビリティは必須
```

### 基本的なアクセシビリティprops

```tsx
// ❌ スクリーンリーダーに伝わらない
<Pressable onPress={handleDelete}>
  <Icon name="trash" />
</Pressable>

// ✅ スクリーンリーダーが「削除ボタン」と読み上げる
<Pressable
  onPress={handleDelete}
  accessible={true}
  accessibilityLabel="このメッセージを削除"
  accessibilityRole="button"
  accessibilityHint="タップするとメッセージが削除されます"
>
  <Icon name="trash" />
</Pressable>
```

### accessibilityRole の主要値

| Role | 用途 | 読み上げ |
|------|------|----------|
| `button` | タップ可能な要素 | 「〇〇、ボタン」 |
| `link` | 外部リンク | 「〇〇、リンク」 |
| `header` | 画面タイトル | 「〇〇、見出し」 |
| `image` | 画像 | 「〇〇、画像」 |
| `checkbox` | チェックボックス | 「〇〇、チェックボックス、オン/オフ」 |
| `tab` | タブ | 「〇〇、タブ、X/Nのタブ」 |
| `search` | 検索欄 | 「〇〇、検索フィールド」 |

### フォームのアクセシビリティ

```tsx
// 入力欄のアクセシビリティ
<View>
  <Text nativeID="emailLabel">メールアドレス</Text>
  <TextInput
    accessibilityLabelledBy="emailLabel"  // ラベルと入力欄を紐付け
    accessibilityRequired={true}           // 必須フィールド
    autoCapitalize="none"
    keyboardType="email-address"
    returnKeyType="next"
  />
</View>

// エラーメッセージ
<TextInput
  accessibilityInvalid={hasError}          // エラー状態を伝える
  accessibilityErrorMessage={errorMessage}
/>
```

### ダイナミックコンテンツの通知

```tsx
import { AccessibilityInfo } from 'react-native';

// AIがレスポンスを生成完了した時に通知
const handleAIResponseComplete = (response: string) => {
  AccessibilityInfo.announceForAccessibility(
    `AIが回答しました。${response.slice(0, 50)}...`
  );
};

// 画面変更の通知
AccessibilityInfo.setAccessibilityFocus(elementRef.current);
```

### テスト方法

```
iOS: 設定 → アクセシビリティ → VoiceOver → ON
Android: 設定 → ユーザー補助 → TalkBack → ON

チェックリスト:
  ☐ 全ボタンに accessibilityLabel がある
  ☐ 画像に代替テキスト (accessibilityLabel) がある
  ☐ タップ領域が44×44dp以上（Apple HIG基準）
  ☐ カラーコントラスト比 4.5:1以上（WCAG AA）
  ☐ フォームにラベルが紐付いている
  ☐ エラーメッセージが読み上げられる
```

**情報源:**
- [Accessibility - React Native公式](https://reactnative.dev/docs/accessibility)
- [React Native Accessibility Guide 2026 - React Native Relay](https://reactnativerelay.com/article/react-native-accessibility-guide-building-inclusive-apps-expo)
- [React Native Accessibility - Callstack](https://www.callstack.com/blog/react-native-accessibility)

---

## 67. 画像最適化 — expo-image & BlurHash

**調査日時: 2026-05-15 (第12ラウンド)**

### expo-image vs 標準Image

| 比較項目 | 標準 `<Image>` | `expo-image` |
|----------|--------------|--------------|
| キャッシュ | 基本的 | 高度（SDWebImage/Glide） |
| フォーマット | JPEG/PNG | AVIF/WebP/JPEG/PNG |
| BlurHash | なし | **内蔵** |
| フェード遷移 | なし | **内蔵** |
| パフォーマンス | 標準 | 2〜3倍高速 |

### 基本実装

```bash
npx expo install expo-image
```

```tsx
import { Image } from 'expo-image';

// ✅ 2026年推奨
<Image
  source={{ uri: 'https://example.com/photo.jpg' }}
  placeholder={{ blurhash: 'L6PZfSi_.AyE_3t7t7R**0o#DgR4' }}  // ロード中のぼかし画像
  contentFit="cover"           // objectFit と同じ概念
  transition={200}             // フェードイン時間（ms）
  cachePolicy="memory-disk"   // メモリ+ディスクキャッシュ
  style={{ width: 200, height: 200, borderRadius: 12 }}
/>
```

### BlurHashの生成

```tsx
// サーバー側（Node.js）でBlurHashを生成してDBに保存
import { encode } from 'blurhash';

// または純粋なJS実装（クライアントでも可）
import * as FileSystem from 'expo-file-system';

// Emport AIの場合: ユーザーアイコンや記事サムネイルのBlurHashを
// バックエンド（Railway）で事前生成してAPIレスポンスに含める

// APIレスポンス例
{
  "user": {
    "avatar": "https://cdn.example.com/avatar.jpg",
    "avatarBlurhash": "L6PZfSi_.AyE_3t7t7R**0o#DgR4"
  }
}
```

### 画像プリフェッチ（一覧表示の高速化）

```tsx
import { Image } from 'expo-image';

// 次の画面の画像を事前に読み込む
await Image.prefetch([
  'https://example.com/image1.jpg',
  'https://example.com/image2.jpg',
]);

// キャッシュをクリア
await Image.clearDiskCache();
await Image.clearMemoryCache();
```

### SVGアイコンの最適化

```bash
npx expo install react-native-svg
```

```tsx
import Svg, { Path, Circle, G } from 'react-native-svg';

// カスタムアイコンコンポーネント
function AIIcon({ size = 24, color = '#1A3B8C' }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24">
      <Path
        d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"
        fill={color}
      />
    </Svg>
  );
}

// アイコンセットの管理
// @expo/vector-icons（Ionicons, MaterialIcons等を内包）
import { Ionicons } from '@expo/vector-icons';
<Ionicons name="chatbubble-outline" size={24} color="#1A3B8C" />
```

### Emport AIへの画像最適化戦略

```
1. ユーザーアイコン:
   - expo-image + BlurhashでUX改善
   - contentFit="cover" + borderRadius で丸いアバター

2. 業種選択画面の画像:
   - prefetch() で次の画面の画像を先読み
   - AVIF形式で50%サイズ削減

3. チャット内の画像送信（将来機能）:
   - expo-image-picker で選択
   - アップロード前に圧縮（quality: 0.7）
   - サーバー側でBlurHash生成→レスポンスに含める

4. SVGアイコン統一:
   - react-native-svg + @expo/vector-icons
   - カスタムアイコンはSVGで作成（ピクセルフリー）
```

**情報源:**
- [Image - Expo Documentation](https://docs.expo.dev/versions/latest/sdk/image/)
- [react-native-blurhash GitHub](https://github.com/mrousavy/react-native-blurhash)
- [React Native Image Optimization - Medium](https://medium.com/@engin.bolat/react-native-image-optimization-performance-essentials-9e8ce6a1193e)

---

*第12ラウンド完了（2026-05-15）: セクション61〜67 — タイポグラフィ・ダークモード・Skia・Figma連携・スケルトンUI・アクセシビリティ・画像最適化*


---

## 第13ラウンド調査（2026-05-15）: 状態管理・データフェッチ・カスタムフック・アーキテクチャ・最適化

### 調査テーマ
- Zustand グローバル状態管理
- TanStack Query v5 データフェッチング
- カスタムフック設計パターン
- フィーチャーベースフォルダ構造
- MMKV vs AsyncStorage オフライン対応
- エラーバウンダリ
- FlatList・メモ化パフォーマンス最適化

---

## 68. Zustand グローバル状態管理 ベストプラクティス 2026

### Zustand が2026年のデファクトスタンダードになった理由

| 比較軸 | Redux | Context API | Zustand |
|--------|-------|------------|---------|
| ボイラープレート | 多大 | 少 | 最小 |
| Provider不要 | x | x | o |
| TypeScript | 複雑 | 普通 | 優秀 |
| パフォーマンス | 良 | 問題あり | 優秀 |
| バンドルサイズ | 大きい | 0 | 1KB |

**2026年の選択基準:**
- **Zustand**: グローバル状態の8割をカバー（推奨）
- **Jotai**: アトミック状態（細粒度更新が必要な場合）
- **Redux**: 大規模エンタープライズのみ

### 基本パターン

```typescript
// stores/auth.store.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV({ id: 'auth-store' });

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => ({
        getItem: (key) => storage.getString(key) ?? null,
        setItem: (key, value) => storage.set(key, value),
        removeItem: (key) => storage.delete(key),
      })),
    }
  )
);
```

### セレクターパターン（不要な再レンダリングを防ぐ）

```typescript
// NG: ストア全体を取得 → 何かが変わるたびに再レンダリング
const { user, token, logout } = useAuthStore();

// OK: 必要なものだけ取得 → 関係する状態が変わったときだけ再レンダリング
const user = useAuthStore((state) => state.user);
const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
const logout = useAuthStore((state) => state.logout);
```

### フィーチャーごとにストアを分割

```
stores/
├── auth.store.ts       // 認証状態
├── chat.store.ts       // チャット画面状態
├── industry.store.ts   // 業種選択状態
└── ui.store.ts         // ローディング・モーダル等のUI状態
```

### devtools ミドルウェア

```typescript
import { devtools } from 'zustand/middleware';

export const useChatStore = create<ChatState>()(
  devtools(
    (set) => ({
      messages: [],
      addMessage: (msg) => set(
        (state) => ({ messages: [...state.messages, msg] }),
        false,
        'chat/addMessage'
      ),
    }),
    { name: 'ChatStore' }
  )
);
```

### Emport AI への応用

```
useAuthStore     → APIキー・ユーザー情報管理
useIndustryStore → 選択した業種・プロンプト設定
useChatStore     → 各チャットセッションのメッセージ履歴
useUIStore       → サイドメニュー開閉・ローディング状態
```

**情報源:**
- [Zustand GitHub](https://github.com/pmndrs/zustand)
- [State Management 2026: Redux vs Zustand](https://medium.com/@abdurrehman1/state-management-in-2026-redux-vs-zustand-vs-context-api-ad5760bfab0b)
- [Zustand in React Native](https://dev.to/ajmal_hasan/simplifying-state-management-in-react-native-with-zustand-41f2)

---

## 69. TanStack Query v5 データフェッチングパターン

### なぜ TanStack Query か

サーバー状態（APIレスポンス）はZustandで管理してはいけない。TanStack Queryが正解。— 2026年のベストプラクティス

| 機能 | axios単体 | Zustand+axios | TanStack Query |
|------|-----------|--------------|----------------|
| キャッシュ | x | 手動 | o自動 |
| ローディング状態 | 手動 | 手動 | o自動 |
| バックグラウンド更新 | x | x | o |
| 楽観的更新 | x | 難しい | o簡単 |
| 無限スクロール | 手動 | 手動 | o組み込み |
| オフライン対応 | x | x | o |

### セットアップ

```tsx
// app/_layout.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 30,
      retry: 2,
    },
  },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <Stack />
    </QueryClientProvider>
  );
}
```

### クエリキーファクトリーパターン

```typescript
export const chatKeys = {
  all: ['chat'] as const,
  lists: () => [...chatKeys.all, 'list'] as const,
  history: (sessionId: string) => [...chatKeys.all, 'history', sessionId] as const,
};

// 無効化
queryClient.invalidateQueries({ queryKey: chatKeys.lists() });
```

### React Native 画面フォーカス連動

```typescript
import { useIsFocused } from '@react-navigation/native';

function ChatHistoryScreen() {
  const isFocused = useIsFocused();
  const { data, isLoading } = useQuery({
    queryKey: chatKeys.lists(),
    queryFn: api.getChatSessions,
    subscribed: isFocused, // 画面表示中のみフェッチ
  });
}
```

### ミューテーション + 楽観的更新

```typescript
const sendMessage = useMutation({
  mutationFn: (message: string) => api.sendChat({ message, industry }),
  onMutate: async (message) => {
    await queryClient.cancelQueries({ queryKey: chatKeys.history(sessionId) });
    const previous = queryClient.getQueryData(chatKeys.history(sessionId));
    queryClient.setQueryData(chatKeys.history(sessionId), (old: Message[]) => [
      ...old,
      { id: Date.now(), role: 'user', content: message, pending: true },
    ]);
    return { previous };
  },
  onError: (_err, _message, context) => {
    queryClient.setQueryData(chatKeys.history(sessionId), context?.previous);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: chatKeys.history(sessionId) });
  },
});
```

### 無限スクロールパターン

```typescript
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: chatKeys.lists(),
  queryFn: ({ pageParam = 0 }) => api.getChatSessions({ offset: pageParam, limit: 20 }),
  getNextPageParam: (lastPage) => lastPage.hasMore ? lastPage.nextOffset : undefined,
  initialPageParam: 0,
});

<FlatList
  data={data?.pages.flatMap(page => page.items)}
  onEndReached={() => hasNextPage && fetchNextPage()}
/>
```

### Emport AI への応用

```
チャット履歴         → useQuery + キャッシュ
メッセージ送信       → useMutation + 楽観的更新
セッション一覧       → useInfiniteQuery
```

**情報源:**
- [TanStack Query React Native Docs](https://tanstack.com/query/v5/docs/framework/react/react-native)
- [TanStack Query v5 Complete Guide](https://medium.com/@pratikjadhav6632/tanstack-query-react-query-v5-the-complete-guide-for-building-smarter-react-applications-8fdf482212e5)

---

## 70. カスタムフック設計パターン 2026

### 設計原則

1. **単一責任**: 1つのフックは1つのことだけやる
2. **戻り値はオブジェクト**: 2つ以上の値はオブジェクトで返す（配列は避ける）
3. **型安全**: TypeScriptジェネリクスを活用
4. **テスト可能**: 副作用を外部から注入できる設計

### 主要パターン集

```typescript
// パターン1: データフェッチカスタムフック
function useChatHistory(sessionId: string) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: chatKeys.history(sessionId),
    queryFn: () => api.getChatHistory(sessionId),
    enabled: !!sessionId,
  });
  return { messages: data ?? [], isLoading, error, refetch };
}

// パターン2: デバウンスフック
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
}

// パターン3: MMKV永続化フック
function useMMKVState<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(() => {
    const stored = storage.getString(key);
    return stored ? JSON.parse(stored) : defaultValue;
  });
  const set = useCallback((newValue: T) => {
    setValue(newValue);
    storage.set(key, JSON.stringify(newValue));
  }, [key]);
  return [value, set] as const;
}

// パターン4: ネットワーク状態フック
function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState(true);
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      setIsConnected(state.isConnected ?? true);
    });
    return unsubscribe;
  }, []);
  return { isConnected, isOffline: !isConnected };
}
```

### Emport AI への応用

```
useChatSession(id)      → チャット管理（送信・履歴・状態）
useIndustrySelector()   → 業種選択と保存
useSubscription()       → サブスクリプション状態確認
useNetworkStatus()      → オフライン時のUI分岐
useDebounce(query, 500) → 検索入力のデバウンス
```

**情報源:**
- [React Custom Hooks 2026 - TheLinuxCode](https://thelinuxcode.com/react-custom-hooks-in-2026-a-practical-guide-to-cleaner-components-fewer-bugs-and-faster-product-delivery/)
- [React Design Patterns - TurboDocx](https://www.turbodocx.com/blog/react-design-patterns)

---

## 71. フィーチャーベースフォルダ構造（Expo推奨）

### Expo公式推奨構造（2026年）

```
app/                        ← Expo Router（ファイルベースルーティング）
├── (auth)/
│   ├── login.tsx
│   └── register.tsx
├── (main)/
│   ├── index.tsx
│   ├── chat/
│   │   ├── index.tsx
│   │   └── [sessionId].tsx
│   └── settings.tsx
└── _layout.tsx

src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   └── store.ts
│   ├── chat/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   └── store.ts
│   └── industry/
│       ├── components/
│       ├── hooks/
│       └── constants.ts
│
├── shared/
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── ErrorMessage.tsx
│   ├── hooks/
│   │   ├── useDebounce.ts
│   │   └── useNetworkStatus.ts
│   └── utils/
│       ├── api-client.ts
│       └── storage.ts
│
└── constants/
    ├── colors.ts
    └── config.ts
```

### 命名規則

```
コンポーネント:  PascalCase     → MessageBubble.tsx
フック:         camelCase      → useChatHistory.ts
ストア:         use-*-store.ts → use-chat-store.ts
スクリーン:     kebab-case     → chat-history-screen.tsx
```

### Emport AI フォルダ設計

```
features/
├── auth/        → サインイン・プラン確認
├── chat/        → AIチャット機能（メイン）
├── industry/    → 業種選択
├── history/     → チャット履歴管理
└── settings/    → アカウント・通知設定
```

**情報源:**
- [Expo Folder Structure Best Practices](https://expo.dev/blog/expo-app-folder-structure-best-practices)
- [React Folder Structure 2026 - Robin Wieruch](https://www.robinwieruch.de/react-folder-structure/)
- [React Native Project Structure - Tricentis](https://www.tricentis.com/learn/react-native-project-structure)

---

## 72. オフライン対応ストレージ（MMKV vs AsyncStorage vs SecureStore）

### 2026年の選択基準

| ライブラリ | 速度 | 暗号化 | 同期API | 用途 |
|-----------|------|--------|---------|------|
| MMKV | 30倍速 | o AES | o | ユーザー設定・アプリ状態 |
| AsyncStorage | 遅い | x | x | 非推奨（Expo Goで非対応化） |
| expo-secure-store | 普通 | o iOS Keychain | x | APIトークン・パスワード |
| SQLite (Drizzle) | 速い | オプション | o | 複雑なデータ・全文検索 |

### MMKV セットアップ

```typescript
// utils/storage.ts
import { MMKV } from 'react-native-mmkv';

export const appStorage = new MMKV({ id: 'app-preferences' });

export function getStorageItem<T>(key: string): T | null {
  const value = appStorage.getString(key);
  return value ? JSON.parse(value) : null;
}

export function setStorageItem<T>(key: string, value: T): void {
  appStorage.set(key, JSON.stringify(value));
}
```

### Zustand + MMKV 永続化（推奨パターン）

```typescript
export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'system',
      language: 'ja',
      selectedIndustry: null,
      setTheme: (theme) => set({ theme }),
      setIndustry: (industry) => set({ selectedIndustry: industry }),
    }),
    {
      name: 'settings',
      storage: createJSONStorage(() => ({
        getItem: (key) => appStorage.getString(key) ?? null,
        setItem: (key, value) => appStorage.set(key, value),
        removeItem: (key) => appStorage.delete(key),
      })),
    }
  )
);
```

### セキュリティ分類

```
MMKV（平文）:              テーマ・言語設定、業種選択状態
expo-secure-store（Keychain）: JWTトークン、ユーザーID
SQLite（Drizzle ORM）:     チャットメッセージ全文（検索対応）
```

**情報源:**
- [MMKV vs AsyncStorage vs SecureStore 2026 - PkgPulse](https://www.pkgpulse.com/guides/react-native-mmkv-vs-async-storage-vs-expo-secure-store-2026)
- [react-native-mmkv GitHub](https://github.com/mrousavy/react-native-mmkv)

---

## 73. エラーバウンダリとクラッシュハンドリング

### Expo Router のネイティブエラーバウンダリ

```tsx
// app/chat/[sessionId].tsx
export function ErrorBoundary({ error, retry }: { error: Error; retry: () => void }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>問題が発生しました</Text>
      <Text style={styles.message}>{error.message}</Text>
      <Button title="もう一度試す" onPress={retry} />
    </View>
  );
}
```

### 部分的エラーバウンダリ（機能単位で局所化）

```tsx
class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  retry = () => this.setState({ hasError: false, error: null });

  render() {
    const { hasError, error } = this.state;
    if (hasError && error) {
      return this.props.fallback?.(error, this.retry) ?? <Text>エラーが発生しました</Text>;
    }
    return this.props.children;
  }
}

// 使い方
<ErrorBoundary fallback={(err, retry) => (
  <ErrorCard message={err.message} onRetry={retry} />
)}>
  <ChatHistoryList />
</ErrorBoundary>
```

### イベントハンドラのエラーハンドリング

```typescript
// エラーバウンダリは onPress 等イベントをキャッチしない
// try/catch が必要
const handleSendMessage = async () => {
  try {
    await sendMessage.mutateAsync(inputText);
    setInputText('');
  } catch (error) {
    if (error instanceof APIError && error.status === 429) {
      Alert.alert('使用制限', 'しばらく時間をおいて再度お試しください');
    } else {
      Alert.alert('エラー', 'メッセージの送信に失敗しました');
    }
  }
};
```

### Emport AI エラー設計

```
画面レベル:  Expo Router ErrorBoundary（致命的エラー）
機能レベル:  部分的ErrorBoundary（チャットリスト・設定画面等）
API通信:    useMutation onError + Alert通知
監視:       Sentry（本番クラッシュ追跡、無料プランで十分）
```

**情報源:**
- [Expo Router Error Handling](https://docs.expo.dev/router/error-handling/)
- [React Native Error Boundaries](https://www.reactnative.university/blog/react-native-error-boundaries)

---

## 74. FlatList・メモ化によるパフォーマンス最適化

### FlatList 最適化チェックリスト

```tsx
const keyExtractor = useCallback((item: Message) => item.id, []);
const getItemLayout = useCallback((_: any, index: number) => ({
  length: MESSAGE_HEIGHT,
  offset: MESSAGE_HEIGHT * index,
  index,
}), []);

<FlatList
  data={messages}
  renderItem={renderMessage}
  keyExtractor={keyExtractor}
  getItemLayout={getItemLayout}  // 最大インパクトの最適化（固定高さの場合）
  maxToRenderPerBatch={10}
  windowSize={5}
  initialNumToRender={15}
  removeClippedSubviews
/>
```

### アイテムコンポーネントのメモ化

```tsx
const MessageBubble = React.memo(({ message }: { message: Message }) => {
  return (
    <View style={[styles.bubble, message.role === 'user' ? styles.userBubble : styles.aiBubble]}>
      <Text>{message.content}</Text>
    </View>
  );
}, (prev, next) => prev.message.id === next.message.id);

const renderMessage = useCallback(({ item }: { item: Message }) => (
  <MessageBubble message={item} />
), []);
```

### FlashList: FlatList の置き換え（Shopify製）

```tsx
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={messages}
  renderItem={renderMessage}
  estimatedItemSize={70}
  keyExtractor={keyExtractor}
/>
```

**FlashList vs FlatList 比較:**
| 指標 | FlatList | FlashList |
|------|----------|-----------|
| 10,000件スクロール | フレームドロップ | 60fps維持 |
| 移行コスト | — | estimatedItemSizeのみ追加 |
| API互換性 | 基準 | ほぼ同一 |

### useMemo・useCallback の正しい使い方

```tsx
// useMemo: 計算コストが高い値にのみ
const filteredMessages = useMemo(
  () => messages.filter(m => m.role !== 'system'),
  [messages]
);

// useCallback: 子コンポーネントに渡す関数にのみ
const handleDelete = useCallback((id: string) => {
  deleteMessage(id);
}, [deleteMessage]);

// 不要な最適化は避ける（コスト > 効果になる）
// 単純な文字列結合や、親が再レンダリングしない関数には使わない
```

### Emport AI パフォーマンス設計

```
チャット画面:     FlashList + MessageBubble(React.memo)
業種選択グリッド: FlatList(固定高さ) + getItemLayout
履歴一覧:        FlashList + TanStack Query無限スクロール
全体:            Zustand セレクター最適化でProvider不要
```

**情報源:**
- [FlatList Optimization Guide - obytes](https://www.obytes.com/blog/a-guide-to-optimizing-flatlists-in-react-native)
- [React Native Performance Optimization 2026](https://www.agilesoftlabs.com/blog/2026/03/react-native-performance-optimization)
- [Boosting RN Performance: FlatList, Memo & useCallback](https://medium.com/@chandangupta86/boosting-react-native-performance-flatlist-memo-usecallback-b6cea3471711)

---

*第13ラウンド完了（2026-05-15）: セクション68〜74 — Zustand・TanStack Query v5・カスタムフック・フォルダ構造・MMKV・エラーバウンダリ・FlatList最適化*


---

## 第14ラウンド調査（2026-05-15）: CI/CD・プッシュ通知・テスト・リリース・i18n・ディープリンク・OTA更新

### 調査テーマ
- EAS Build CI/CD（GitHub Actions連携）
- Expo プッシュ通知
- テスト戦略（Jest・Testing Library・Maestro）
- App Store / Google Play 提出（EAS Submit）
- 国際化（i18n）
- ディープリンク・ユニバーサルリンク
- OTA更新（EAS Update）本番運用

---

## 75. EAS Build CI/CD（GitHub Actions連携）

### EAS Workflows の位置づけ

EAS Workflows = GitHub Actions のモバイル拡張版。React Native のビルドで最も面倒な部分（証明書管理・署名・ストア提出）を80%削減。

### GitHub Actions 基本設定

```yaml
# .github/workflows/eas-build.yml
name: EAS Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    name: Install and build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20.x
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Setup Expo and EAS
        uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - name: Build on EAS (preview)
        run: eas build --platform all --profile preview --non-interactive
```

### EAS Workflows（Expo ネイティブ形式）

```yaml
# .eas/workflows/create-production-builds.yml
name: Production Release

on:
  push:
    branches: [main]

jobs:
  build-android:
    type: build
    params:
      platform: android
      profile: production

  build-ios:
    type: build
    params:
      platform: ios
      profile: production

  submit:
    needs: [build-android, build-ios]
    type: submit
    params:
      android:
        build_id: ${{ needs.build-android.outputs.build_id }}
      ios:
        build_id: ${{ needs.build-ios.outputs.build_id }}
```

### eas.json ビルドプロファイル設定

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development"
    },
    "preview": {
      "distribution": "internal",
      "channel": "preview",
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true,
      "channel": "production"
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./service-account.json",
        "track": "internal"
      },
      "ios": {
        "appleId": "tsubeyou081@gmail.com",
        "ascAppId": "YOUR_APP_ID"
      }
    }
  }
}
```

### Emport AI CI/CD パイプライン設計

```
PRマージ   → preview ビルド自動作成 → 内部テスター配布
mainプッシュ → production ビルド → ストア Internal Track へ自動提出
OTA更新    → eas update --channel production（JSのみ変更時）
```

**情報源:**
- [EAS Workflows - Expo Documentation](https://docs.expo.dev/eas/workflows/get-started/)
- [expo-github-action GitHub](https://github.com/expo/expo-github-action)
- [EAS Workflows Blog](https://expo.dev/blog/expo-workflows-automate-your-release-process)

---

## 76. プッシュ通知（Expo Notifications）

### 2026年の重要変更点

**SDK 53からExpo GoでAndroidプッシュ通知が廃止** — 必ずDevelopment Buildを使用すること。

### セットアップ

```bash
npx expo install expo-notifications expo-device expo-constants
```

### トークン取得と管理

```typescript
// hooks/usePushNotifications.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) return null; // 実機のみ

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return null;

  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const token = (await Notifications.getExpoPushTokenAsync({ projectId })).data;

  // バックエンドに保存（ユーザーIDと紐付け）
  await api.savePushToken(token);

  return token;
}
```

### 通知ハンドラー（コンポーネント）

```tsx
// app/_layout.tsx
export default function RootLayout() {
  const notificationListener = useRef<Notifications.EventSubscription>();
  const responseListener = useRef<Notifications.EventSubscription>();

  useEffect(() => {
    registerForPushNotifications();

    // 通知受信時（フォアグラウンド）
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('受信:', notification);
      }
    );

    // 通知タップ時
    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        const data = response.notification.request.content.data;
        // ディープリンクで対応する画面へ遷移
        router.push(data.url ?? '/');
      }
    );

    return () => {
      notificationListener.current?.remove();
      responseListener.current?.remove();
    };
  }, []);
}
```

### バックエンドからの送信（Node.js）

```typescript
// バックエンド側
import { Expo } from 'expo-server-sdk';

const expo = new Expo();

async function sendPushNotification(expoPushToken: string, title: string, body: string) {
  if (!Expo.isExpoPushToken(expoPushToken)) return;

  const messages = [{
    to: expoPushToken,
    sound: 'default',
    title,
    body,
    data: { url: '/chat' }, // ディープリンク先
  }];

  const chunks = expo.chunkPushNotifications(messages);
  for (const chunk of chunks) {
    await expo.sendPushNotificationsAsync(chunk);
  }
}
```

### UXベストプラクティス

```
許可を求るタイミング:
  x アプリ起動直後（拒否率最高）
  o ポジティブな体験後（初回チャット完了後など）

頻度の目安:
  - 週2〜5回が限界（それ以上でオプトアウト率急増）
  - Emport AI: 新機能リリース・重要アップデートのみ推奨

許可拒否時:
  - 機能をブロックしない
  - 設定画面で後から有効化できるUIを提供
```

**情報源:**
- [Expo Push Notifications Setup](https://docs.expo.dev/push-notifications/push-notifications-setup/)
- [Expo Push Notifications Guide 2026](https://reactnativerelay.com/article/react-native-push-notifications-expo-complete-guide-2026)

---

## 77. テスト戦略（Jest・Testing Library・Maestro E2E）

### 2026年の推奨テストスタック

| ツール | 役割 | 比率 |
|--------|------|------|
| Jest 30 + RNTL | ユニット・コンポーネントテスト | 70% |
| Jest + カスタムフックテスト | フックロジック検証 | 20% |
| Maestro | E2Eテスト（実機・シミュレーター） | 10% |

### Jest + React Native Testing Library

```bash
npm install --save-dev @testing-library/react-native jest-expo
```

```typescript
// __tests__/MessageBubble.test.tsx
import { render, screen } from '@testing-library/react-native';
import { MessageBubble } from '../components/MessageBubble';

describe('MessageBubble', () => {
  it('ユーザーメッセージを正しく表示する', () => {
    render(<MessageBubble message={{ role: 'user', content: 'こんにちは' }} />);
    expect(screen.getByText('こんにちは')).toBeTruthy();
  });

  it('AIメッセージで異なるスタイルが適用される', () => {
    const { getByTestId } = render(
      <MessageBubble message={{ role: 'assistant', content: '回答です' }} />
    );
    const bubble = getByTestId('bubble');
    expect(bubble.props.style).toMatchObject({ backgroundColor: '#F0F4FF' });
  });
});
```

### カスタムフックのテスト

```typescript
// __tests__/useDebounce.test.ts
import { renderHook, act } from '@testing-library/react-native';
import { useDebounce } from '../hooks/useDebounce';

jest.useFakeTimers();

test('300ms後にデバウンスされた値を返す', () => {
  const { result, rerender } = renderHook(
    ({ value }) => useDebounce(value, 300),
    { initialProps: { value: 'initial' } }
  );

  rerender({ value: 'updated' });
  expect(result.current).toBe('initial'); // まだ更新されていない

  act(() => jest.advanceTimersByTime(300));
  expect(result.current).toBe('updated');
});
```

### Maestro E2E テスト（YAML形式）

```yaml
# .maestro/flows/chat_flow.yaml
appId: com.emportai.app
---
- launchApp
- assertVisible: "業種を選択してください"
- tapOn: "建設業"
- tapOn: "チャットを開始"
- assertVisible: "AIアシスタント"
- inputText:
    id: "chat-input"
    text: "現場の安全管理で大変なことは？"
- tapOn: "送信"
- waitForAnimationToEnd
- assertVisible: "安全管理"  # AIが安全管理に言及するか確認
```

```bash
# 実行コマンド
maestro test .maestro/flows/chat_flow.yaml

# EAS Maestro Cloud（CI統合）
eas build:version:get && maestro cloud --apiKey $MAESTRO_CLOUD_KEY .maestro/
```

### jest.config.js 設定

```javascript
// jest.config.js
module.exports = {
  preset: 'jest-expo',
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)',
  ],
  setupFilesAfterFramework: ['@testing-library/react-native/extend-expect'],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
    },
  },
};
```

### Emport AI テスト設計

```
ユニットテスト:
  - useDebounce, useNetworkStatus 等のカスタムフック
  - Zustandストアのアクション
  - 日付・価格フォーマット関数

コンポーネントテスト:
  - MessageBubble（ユーザー/AI の表示切り替え）
  - IndustryCard（選択状態）
  - SubscriptionBadge（プラン表示）

E2E テスト（Maestro）:
  - ログイン → 業種選択 → チャット送信
  - サブスクリプション購入フロー
  - チャット履歴閲覧
```

**情報源:**
- [React Native Testing Guide 2026](https://reactnativerelay.com/article/complete-guide-testing-react-native-apps-2026-unit-tests-e2e-maestro)
- [Maestro React Native Docs](https://docs.maestro.dev/platform-support/react-native)
- [React Native Testing 2026: Jest, Detox, Maestro](https://hashnode.com/posts/react-native-testing-in-2026-jest-detox-and-maestro-compared/69fb478e50ecad4533331c4f)

---

## 78. App Store / Google Play 提出（EAS Submit）

### EAS Submit の全体フロー

```
1. eas build --profile production  → .ipa / .aab ファイル生成
2. eas submit --platform all       → ストアへ自動アップロード
3. ストア審査                       → iOS: 1〜2日、Android: 数時間〜1日
4. リリース                         → 段階的ロールアウト推奨
```

### 提出前チェックリスト

```
app.json / app.config.ts:
  o name: "Emport AI"
  o slug: "emport-ai"
  o version: "1.0.0"
  o android.package: "com.emportai.app"
  o ios.bundleIdentifier: "com.emportai.app"
  o ios.buildNumber と android.versionCode
  o icon: 1024x1024 PNG（透過なし）
  o splash: 1284x2778 PNG

App Store Connect（iOS）:
  o Apple Developer Program 加入（年$99）
  o App Store Connect でアプリ作成
  o プライバシーポリシーURL
  o スクリーンショット（各デバイスサイズ）

Google Play Console（Android）:
  o Developer アカウント（$25 初回のみ）
  o Service Account Key 取得
  o 初回は手動アップロード（APIの制限）
  o コンテンツレーティング設定
```

### eas submit コマンド

```bash
# iOS
eas submit --platform ios --profile production

# Android
eas submit --platform android --profile production

# 両方同時（ビルドIDを指定）
eas submit --platform all \
  --ios-build-id <ios-build-id> \
  --android-build-id <android-build-id>
```

### app.config.ts（本番設定）

```typescript
import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: 'Emport AI',
  slug: 'emport-ai',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  splash: { image: './assets/splash.png', resizeMode: 'contain', backgroundColor: '#0A1628' },
  ios: {
    bundleIdentifier: 'com.emportai.app',
    buildNumber: '1',
    supportsTablet: false,
    infoPlist: {
      NSMicrophoneUsageDescription: '音声入力に使用します',
    },
  },
  android: {
    package: 'com.emportai.app',
    versionCode: 1,
    adaptiveIcon: {
      foregroundImage: './assets/adaptive-icon.png',
      backgroundColor: '#0A1628',
    },
    permissions: ['INTERNET', 'CAMERA'],
  },
  extra: {
    eas: { projectId: 'YOUR_EAS_PROJECT_ID' },
  },
});
```

**情報源:**
- [EAS Submit - Expo Documentation](https://docs.expo.dev/submit/introduction/)
- [Submit to App Stores](https://docs.expo.dev/deploy/submit-to-app-stores/)

---

## 79. 国際化（i18n）expo-localization + i18next

### 推奨スタック（2026年）

```bash
npx expo install expo-localization
npm install i18next react-i18next
```

### セットアップ

```typescript
// i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';

import ja from './locales/ja.json';
import en from './locales/en.json';

i18n.use(initReactI18next).init({
  resources: { ja: { translation: ja }, en: { translation: en } },
  lng: Localization.getLocales()[0]?.languageCode ?? 'ja',
  fallbackLng: 'ja',
  interpolation: { escapeValue: false },
});

export default i18n;
```

### 翻訳ファイル

```json
// i18n/locales/ja.json
{
  "common": {
    "loading": "読み込み中...",
    "error": "エラーが発生しました",
    "retry": "もう一度試す"
  },
  "chat": {
    "placeholder": "メッセージを入力...",
    "send": "送信",
    "title": "AIアシスタント"
  },
  "industry": {
    "select": "業種を選択してください",
    "construction": "建設業",
    "fishery": "水産業",
    "manufacturing": "製造業"
  }
}
```

### コンポーネントでの使用

```tsx
import { useTranslation } from 'react-i18next';

function ChatScreen() {
  const { t } = useTranslation();

  return (
    <View>
      <Text>{t('chat.title')}</Text>
      <TextInput placeholder={t('chat.placeholder')} />
      <Button title={t('chat.send')} onPress={handleSend} />
    </View>
  );
}
```

### 言語切り替え（設定画面）

```typescript
import i18n from '../i18n';
import { setStorageItem } from '../utils/storage';

function changeLanguage(lng: 'ja' | 'en') {
  i18n.changeLanguage(lng);
  setStorageItem('language', lng); // 次回起動時に復元
}
```

### Emport AI の方針

```
初期リリース: 日本語のみ（ja.json）
第2フェーズ: 英語追加（海外展開時）
端末の言語設定を自動検出し、日本語以外はenにフォールバック
```

**情報源:**
- [Expo Localization Documentation](https://docs.expo.dev/versions/latest/sdk/localization/)
- [i18n in React Native with Expo - Intlayer](https://intlayer.org/doc/environment/react-native-and-expo)
- [react-i18next GitHub](https://github.com/i18next/react-i18next)

---

## 80. ディープリンク・ユニバーサルリンク（Expo Router）

### 2026年の重要変更

Firebase Dynamic Links が2025年8月で廃止。代替:
- **Expo Router** 自動ディープリンク（カスタムスキーム）
- **Universal Links（iOS）+ App Links（Android）** → https:// リンク推奨
- **Branch.io** → 高度な計測・遅延ディープリンクが必要な場合

### Expo Router の自動ディープリンク

```typescript
// app.json
{
  "expo": {
    "scheme": "emportai",
    "web": { "bundler": "metro" }
  }
}

// Expo Routerでは全ルートが自動的にディープリンク対応
// app/chat/[sessionId].tsx → emportai://chat/abc123
// app/(main)/settings.tsx  → emportai://settings
```

### ユニバーサルリンク設定（iOS）

```json
// ios/EmportAI/emportai-associated-domain.json (Apple CDNに配置)
{
  "applinks": {
    "details": [{
      "appIDs": ["TEAM_ID.com.emportai.app"],
      "components": [
        { "/": "/chat/*", "comment": "チャット画面" },
        { "/": "/invite/*", "comment": "招待リンク" }
      ]
    }]
  }
}
```

### 認証アウェアなリダイレクト

```tsx
// app/(main)/_layout.tsx
import { Redirect, useSegments } from 'expo-router';

export default function MainLayout() {
  const { isAuthenticated } = useAuthStore();
  const segments = useSegments();

  if (!isAuthenticated) {
    // ログイン後に元の画面に戻れるようにパスを保存
    const returnPath = segments.join('/');
    return <Redirect href={`/login?return=${returnPath}`} />;
  }

  return <Stack />;
}
```

### Emport AI ディープリンク設計

```
emportai://           → ホーム
emportai://chat/{id}  → 特定チャットセッション
emportai://invite/{code} → 紹介コード付き招待
https://emport-ai.vercel.app/chat/{id} → ユニバーサルリンク
```

**情報源:**
- [Expo Linking Documentation](https://docs.expo.dev/linking/into-your-app/)
- [Expo Router Deep Linking Guide 2026](https://reactnativerelay.com/article/deep-linking-react-native-expo-router-universal-links-app-links)

---

## 81. OTA更新（EAS Update）本番運用戦略

### OTA更新の原則

OTA（Over The Air）更新はJavaScript・アセットの変更のみ対象。ネイティブコード変更はフルビルドが必要。

```
OTA更新で可能:
  - UIの変更・バグ修正
  - APIエンドポイントの変更
  - テキスト・コピーの修正
  - 新しいJSロジック

フルビルドが必要:
  - 新しいネイティブモジュール追加
  - Expo SDK バージョンアップ
  - app.json の変更（アイコン等）
```

### EAS Update セットアップ

```bash
npx expo install expo-updates
eas update:configure
```

```json
// eas.json
{
  "build": {
    "production": {
      "channel": "production"
    },
    "preview": {
      "channel": "preview"
    }
  }
}
```

### 段階的ロールアウト（本番ベストプラクティス）

```bash
# ステップ1: 10%のユーザーに配信
eas update --channel production --message "バグ修正" --rollout-percentage 10

# ステップ2: 問題なければ50%へ
eas update:rollout --channel production --rollout-percentage 50

# ステップ3: 全体へ
eas update:rollout --channel production --rollout-percentage 100

# 問題発生時はロールバック（1コマンド）
eas update:rollback --channel production
```

### 自動更新設定

```typescript
// app/_layout.tsx
import * as Updates from 'expo-updates';

async function checkForUpdates() {
  if (!__DEV__) {
    try {
      const update = await Updates.checkForUpdateAsync();
      if (update.isAvailable) {
        await Updates.fetchUpdateAsync();
        // ユーザーに通知してからリロード
        Alert.alert(
          'アップデートあり',
          'アプリを再起動して最新版を適用しますか？',
          [{ text: '後で' }, { text: '今すぐ', onPress: Updates.reloadAsync }]
        );
      }
    } catch (e) {
      console.error('Update check failed:', e);
    }
  }
}

useEffect(() => {
  checkForUpdates();
}, []);
```

### ブランチ戦略

```
main       → production チャンネル（本番ユーザー）
develop    → preview チャンネル（社内テスター）
feature/*  → development チャンネル（開発者のみ）
```

### コード署名（セキュリティ）

```bash
# 署名キーの生成
expo-updates codesigning:generate --key-output-directory ./.certs

# ビルドに署名を埋め込む
eas build --profile production
```

### Emport AI OTA 運用方針

```
リリース頻度:    週1〜2回（小さな改善を継続）
段階ロールアウト: 10% → 50% → 100%（各24時間待機）
監視:           Sentry でクラッシュ率監視
ロールバック条件: クラッシュ率が0.5%を超えた場合
```

**情報源:**
- [EAS Update Production Playbook](https://expo.dev/blog/the-production-playbook-for-ota-updates)
- [EAS Update Guide 2026](https://reactnativerelay.com/article/react-native-ota-updates-eas-update-rollouts-rollbacks-cicd)
- [Zero-Downtime OTA Deployment](https://dev.to/jocanola/zero-downtime-deployment-master-over-the-air-ota-updates-in-expo-react-native-4p8a)

---

*第14ラウンド完了（2026-05-15）: セクション75〜81 — EAS Build CI/CD・プッシュ通知・テスト戦略・EAS Submit・i18n・ディープリンク・OTA更新*


---

## 第15ラウンド調査（2026-05-15）: 収益化・決済・アナリティクス・A/Bテスト・セキュリティ

### 調査テーマ
- RevenueCat サブスクリプション・IAP
- ペイウォールデザインパターン
- Stripe 決済統合
- プロダクトアナリティクス（PostHog・Mixpanel・Amplitude）
- A/Bテスト・フィーチャーフラグ
- 生体認証（expo-local-authentication）
- アプリセキュリティ設計

---

## 82. RevenueCat サブスクリプション・IAP（In-App Purchase）

### なぜ RevenueCat か

| 比較項目 | 自前実装 | RevenueCat | Adapty |
|--------|---------|-----------|-------|
| iOS/Android クロスプラットフォーム | 複雑 | o | o |
| レシート検証 | サーバー必要 | o自動 | o自動 |
| チャーン分析 | x | o | o |
| 無料枠 | — | 月250万ドル収益まで無料 | 月10万ドル |
| Expo対応 | — | o | o |

### セットアップ

```bash
npx expo install react-native-purchases react-native-purchases-ui
```

```typescript
// app/_layout.tsx
import Purchases, { LOG_LEVEL } from 'react-native-purchases';
import { Platform } from 'react-native';

const REVENUECAT_API_KEY = Platform.select({
  ios: process.env.EXPO_PUBLIC_RC_IOS_KEY,
  android: process.env.EXPO_PUBLIC_RC_ANDROID_KEY,
});

useEffect(() => {
  Purchases.setLogLevel(LOG_LEVEL.DEBUG);
  Purchases.configure({ apiKey: REVENUECAT_API_KEY! });
}, []);
```

### プランの取得と購入

```typescript
// hooks/useSubscription.ts
import Purchases, { PurchasesPackage } from 'react-native-purchases';

export function useSubscription() {
  const [packages, setPackages] = useState<PurchasesPackage[]>([]);
  const [customerInfo, setCustomerInfo] = useState<CustomerInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const offerings = await Purchases.getOfferings();
        if (offerings.current) {
          setPackages(offerings.current.availablePackages);
        }
        const info = await Purchases.getCustomerInfo();
        setCustomerInfo(info);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  // サブスクリプション状態確認
  const isPremium = customerInfo?.entitlements.active['premium'] !== undefined;

  const purchasePackage = async (pkg: PurchasesPackage) => {
    const { customerInfo } = await Purchases.purchasePackage(pkg);
    setCustomerInfo(customerInfo);
  };

  return { packages, isPremium, isLoading, purchasePackage };
}
```

### RevenueCat Paywalls UI（ノーコードペイウォール）

```tsx
import { RevenueCatUI, PAYWALL_RESULT } from 'react-native-purchases-ui';

async function showPaywall() {
  const result = await RevenueCatUI.presentPaywallIfNeeded({
    requiredEntitlementIdentifier: 'premium',
  });

  switch (result) {
    case PAYWALL_RESULT.PURCHASED:
    case PAYWALL_RESULT.RESTORED:
      console.log('購入完了');
      break;
    case PAYWALL_RESULT.NOT_PRESENTED:
    case PAYWALL_RESULT.CANCELLED:
      console.log('キャンセル');
      break;
  }
}
```

### Emport AI サブスクリプション設計

```
プラン:
  Free  → 月5回まで（無料）
  Pro   → 月額980円（iOS/Android IAP）
  Team  → 月額3,000円/人（法人向け）

エンタイトルメント:
  'free_limit' → 無料ユーザーの使用回数制御
  'premium'    → Pro以上のフルアクセス

収益目標:
  パイロット3社 → 月額3万円×3社 = 月9万円（第1フェーズ）
```

**情報源:**
- [RevenueCat Expo Documentation](https://www.revenuecat.com/docs/getting-started/installation/expo)
- [Expo + RevenueCat Tutorial](https://expo.dev/blog/expo-revenuecat-in-app-purchase-tutorial)
- [RevenueCat React Native GitHub](https://github.com/RevenueCat/react-native-purchases)

---

## 83. ペイウォールデザインパターン

### ペイウォールの種類

| タイプ | 説明 | 適用場面 |
|--------|------|---------|
| Hard Paywall | 機能をすべてロック、購入必須 | 高価値機能・コア機能 |
| Soft Paywall | 無料プレビュー後に購入促進 | コンテンツ型アプリ |
| Freemium | 基本無料・上位機能で課金 | Emport AI に最適 |
| Time-limited Trial | 7日間無料トライアル | 法人向け |

### 高コンバージョンペイウォールの要素

```tsx
function PaywallScreen() {
  const { packages, purchasePackage } = useSubscription();
  const proPackage = packages.find(p => p.identifier === 'pro_monthly');

  return (
    <ScrollView style={styles.container}>
      {/* ヘッドライン: ベネフィット訴求 */}
      <Text style={styles.headline}>AIが、あなたの経営チームになる</Text>

      {/* 価値提案リスト */}
      <FeatureList features={[
        { icon: '✓', text: '業種特化AIが無制限に回答' },
        { icon: '✓', text: '過去の会話履歴を完全保存' },
        { icon: '✓', text: '優先サポート（営業日24時間以内）' },
      ]} />

      {/* 社会的証明 */}
      <TestimonialCard
        quote="導入初月で提案書作成時間が70%減りました"
        author="建設会社 田中社長"
      />

      {/* 価格表示（年払いの方がお得感を演出）*/}
      <PricingToggle
        monthly={{ price: '¥980/月', label: '月払い' }}
        yearly={{ price: '¥7,800/年', label: '年払い（2ヶ月分お得）', badge: 'おすすめ' }}
      />

      {/* CTA ボタン */}
      <Button
        title={`${proPackage?.product.priceString ?? '¥980'}/月で始める`}
        onPress={() => purchasePackage(proPackage!)}
        style={styles.ctaButton}
      />

      {/* 信頼シグナル */}
      <Text style={styles.trust}>
        いつでもキャンセル可能・7日間無料トライアル
      </Text>
      <Text style={styles.restore} onPress={Purchases.restorePurchases}>
        購入を復元する
      </Text>
    </ScrollView>
  );
}
```

### コンバージョン率を上げるタイミング設計

```
最適なペイウォール表示タイミング:
  1. 無料制限到達時（5回目の質問後）
  2. 高価値アクション後（AI回答に「すごい」と反応した直後）
  3. セッション開始から3分後（エンゲージメント確認後）

避けるべきタイミング:
  x アプリ起動直後（まだ価値を理解していない）
  x エラー発生時
  x ユーザーが操作を中断した直後
```

**情報源:**
- [RevenueCat Paywall Displays](https://www.revenuecat.com/docs/tools/paywalls/displaying-paywalls)
- [RevenueCat vs Adapty vs Superwall 2026](https://www.pkgpulse.com/guides/revenuecat-vs-adapty-vs-superwall-mobile-in-app-2026)
- [Paywall Design Inspiration](https://nativelaunch.dev/articles/paywall-screen)

---

## 84. Stripe 決済統合（Web・コンサル向け）

### IAP vs Stripe の使い分け

```
App Store / Google Play IAP (RevenueCat):
  → モバイルアプリ内の購入（Appleが30%手数料）
  → ユーザーがアプリ内で決済する場合は必須

Stripe:
  → Webサイト・コンサル請求（手数料2.9%+30円）
  → 法人への請求書発行
  → 手動サブスクリプション管理
  → RevenueCat Web Billing のバックエンド
```

### Expo Stripe 統合

```bash
npx expo install @stripe/stripe-react-native
```

```tsx
// app.json
{
  "plugins": [
    ["@stripe/stripe-react-native", {
      "merchantIdentifier": "merchant.com.emportai",
      "enableGooglePay": true
    }]
  ]
}
```

```tsx
// コンポーネント
import { StripeProvider, PaymentSheet, useStripe } from '@stripe/stripe-react-native';

function ConsultingPaymentScreen() {
  const { initPaymentSheet, presentPaymentSheet } = useStripe();

  const initializePayment = async () => {
    // バックエンドからPaymentIntent取得
    const { paymentIntentClientSecret } = await api.createPaymentIntent({
      amount: 50000, // 5万円（コンサル初回料金）
      currency: 'jpy',
    });

    await initPaymentSheet({
      merchantDisplayName: 'Emport AI',
      paymentIntentClientSecret,
      defaultBillingDetails: { name: '田中社長' },
      applePay: { merchantCountryCode: 'JP' },
      googlePay: { merchantCountryCode: 'JP', testEnv: __DEV__ },
    });
  };

  const handlePayment = async () => {
    const { error } = await presentPaymentSheet();
    if (!error) {
      Alert.alert('決済完了', 'ありがとうございました');
    }
  };
}
```

### Emport AI の決済設計

```
フェーズ1（コンサル）:
  Stripe → 初回30〜100万円の請求書・カード決済

フェーズ2（アプリ）:
  iOS/Android → RevenueCat（月額980円 IAP）
  Web版      → Stripe（RevenueCat Web Billing）

フェーズ3（法人SaaS）:
  Stripe Billing → 月額3〜15万円/社の自動請求
```

**情報源:**
- [Stripe React Native SDK](https://docs.stripe.com/sdks/react-native)
- [Expo Stripe Documentation](https://docs.expo.dev/versions/latest/sdk/stripe/)
- [Stripe PaymentSheet React Native](https://blog.logrocket.com/mastering-stripe-paymentsheet-react-native-expo/)

---

## 85. プロダクトアナリティクス（PostHog・Mixpanel・Amplitude）

### 2026年の無料枠比較

| ツール | 無料枠 | 特徴 |
|--------|--------|------|
| PostHog | 月100万イベント + 5K session replay | オールインワン（推奨） |
| Mixpanel | 月100万イベント | イベント分析に強い |
| Amplitude | 月1万MAU | MAU課金（高エンゲージメントに有利） |

**2026年推奨: PostHog（アナリティクス + フィーチャーフラグ + A/Bテストが無料で1セット）**

### PostHog React Native セットアップ

```bash
npm install posthog-react-native
npx expo install expo-file-system expo-application expo-device
```

```tsx
// app/_layout.tsx
import { PostHogProvider } from 'posthog-react-native';

export default function RootLayout() {
  return (
    <PostHogProvider
      apiKey={process.env.EXPO_PUBLIC_POSTHOG_KEY}
      options={{ host: 'https://app.posthog.com' }}
    >
      <Stack />
    </PostHogProvider>
  );
}
```

### イベント計測

```typescript
import { usePostHog } from 'posthog-react-native';

function ChatScreen() {
  const posthog = usePostHog();

  const handleSendMessage = async () => {
    await sendMessage(inputText);

    // イベント送信
    posthog.capture('message_sent', {
      industry: selectedIndustry,
      message_length: inputText.length,
      session_id: sessionId,
    });
  };

  const handleUpgradeView = () => {
    posthog.capture('paywall_viewed', {
      trigger: 'limit_reached',
      current_plan: 'free',
    });
  };
}
```

### ユーザー識別

```typescript
// ログイン後
posthog.identify(userId, {
  email: user.email,
  industry: user.industry,
  plan: user.subscriptionPlan,
  company_size: user.companySize,
});

// ログアウト時
posthog.reset();
```

### Emport AI 計測すべき重要イベント

```
ファネル:
  app_opened → industry_selected → first_message_sent → paywall_viewed → purchase_completed

エンゲージメント:
  message_sent (industry, length)
  session_started / session_ended (duration)
  history_viewed (session_count)

収益:
  paywall_viewed (trigger)
  purchase_completed (plan, price)
  purchase_cancelled (step)
  subscription_renewed / churned
```

**情報源:**
- [Expo Analytics Guide](https://docs.expo.dev/guides/using-analytics/)
- [PostHog React Native Docs](https://posthog.com/docs/libraries/react-native)
- [Analytics Free Tier Comparison 2026](https://agentdeals.dev/analytics-free-tier-comparison-2026)

---

## 86. A/Bテスト・フィーチャーフラグ（PostHog）

### フィーチャーフラグの活用

```typescript
import { useFeatureFlag } from 'posthog-react-native';

function PaywallScreen() {
  // A/B テスト: ペイウォールのCTAボタンテキスト
  const ctaVariant = useFeatureFlag('paywall-cta-text');
  // 'control' → '今すぐ始める'
  // 'variant_b' → '7日間無料で試す'
  // 'variant_c' → '月980円で全機能開放'

  const ctaText = {
    control: '今すぐ始める',
    variant_b: '7日間無料で試す',
    variant_c: '月980円で全機能開放',
  }[ctaVariant ?? 'control'];

  return <Button title={ctaText} />;
}
```

### フィーチャーフラグ（段階的リリース）

```typescript
// 特定業種ユーザーのみ新機能を先行リリース
const showNewDashboard = useFeatureFlag('new-dashboard-v2');

// OTA更新と組み合わせて安全にデプロイ
if (showNewDashboard) {
  return <NewDashboard />;
}
return <LegacyDashboard />;
```

### GrowthBook（データウェアハウス連携が必要な場合）

```typescript
// 自社データウェアハウスとの統合
import { GrowthBook, GrowthBookProvider, useFeature } from '@growthbook/growthbook-react';

const gb = new GrowthBook({
  apiHost: 'https://cdn.growthbook.io',
  clientKey: process.env.EXPO_PUBLIC_GROWTHBOOK_KEY,
});

function App() {
  return (
    <GrowthBookProvider growthbook={gb}>
      <Stack />
    </GrowthBookProvider>
  );
}
```

### Emport AI A/Bテスト計画

```
テスト1: オンボーディング業種選択画面
  Control: リスト表示
  Variant B: グリッドカード表示
  指標: 業種選択率・初回メッセージ送信率

テスト2: ペイウォールCTAテキスト
  Control: '今すぐProにアップグレード'
  Variant B: '7日間無料でお試し'
  指標: コンバージョン率

テスト3: 無料制限の閾値
  Control: 月5回
  Variant B: 月3回
  指標: コンバージョン率・チャーン率
```

**情報源:**
- [PostHog A/B Tests React Native](https://posthog.com/tutorials/react-native-ab-tests)
- [Expo Feature Flags Guide](https://docs.expo.dev/guides/using-feature-flags/)
- [GrowthBook Feature Flags](https://www.growthbook.io/products/feature-flags)

---

## 87. 生体認証（expo-local-authentication）

### Face ID / Touch ID の実装

```bash
npx expo install expo-local-authentication
```

```typescript
// hooks/useBiometricAuth.ts
import * as LocalAuthentication from 'expo-local-authentication';

export function useBiometricAuth() {
  const [isAvailable, setIsAvailable] = useState(false);
  const [biometricType, setBiometricType] = useState<string>('');

  useEffect(() => {
    async function checkBiometrics() {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      setIsAvailable(compatible && enrolled);

      const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
      if (types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
        setBiometricType('Face ID');
      } else if (types.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
        setBiometricType('指紋認証');
      }
    }
    checkBiometrics();
  }, []);

  const authenticate = async (): Promise<boolean> => {
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'Emport AIにログイン',
      cancelLabel: 'キャンセル',
      disableDeviceFallback: false, // PINフォールバックを許可
    });
    return result.success;
  };

  return { isAvailable, biometricType, authenticate };
}
```

### セキュアなトークン管理との組み合わせ

```typescript
// 生体認証後にSecureStoreからトークンを取得
import * as SecureStore from 'expo-secure-store';

async function biometricLogin() {
  const { isAvailable, authenticate } = useBiometricAuth();

  if (isAvailable) {
    const success = await authenticate();
    if (success) {
      // 生体認証成功後にのみSecureStoreへアクセス
      const token = await SecureStore.getItemAsync('jwt_token');
      if (token) {
        useAuthStore.getState().login(token);
      }
    }
  }
}
```

### セキュリティレベルの確認

```typescript
// Class 3（Strong）の生体認証を優先
const level = await LocalAuthentication.getEnrolledLevelAsync();
if (level === LocalAuthentication.SecurityLevel.BIOMETRIC_STRONG) {
  // 強力な生体認証 → センシティブなデータにアクセス可
} else if (level === LocalAuthentication.SecurityLevel.BIOMETRIC_WEAK) {
  // 弱い認証 → PINで補完を要求
}
```

### Emport AI への応用

```
起動時: 生体認証でパスワードレスログイン
設定変更: 生体認証で本人確認
決済: 購入前に生体認証（追加セキュリティ層）
```

**情報源:**
- [Expo Local Authentication](https://docs.expo.dev/versions/latest/sdk/local-authentication/)
- [Biometric Auth Best Practices 2026](https://medium.com/@christosdemetriou93/best-practice-implementing-biometric-authentication-in-react-native-0e4a746543e6)

---

## 88. アプリセキュリティ設計（総合）

### セキュリティ層の設計

```
Layer 1: ネットワーク
  - HTTPS 必須（HTTP はブロック）
  - Certificate Pinning（高セキュリティの場合）
  - APIキーはサーバーサイドに（クライアントに埋め込まない）

Layer 2: ストレージ
  - 機密情報 → expo-secure-store（iOS Keychain）
  - 設定・キャッシュ → MMKV（平文、機密なし）
  - 絶対に AsyncStorage に機密を保存しない

Layer 3: 認証
  - JWT + Refresh Token パターン
  - 生体認証でパスワードレス化
  - トークン有効期限: アクセストークン15分、リフレッシュ7日

Layer 4: アプリ保護
  - expo-secure-store でコードサイニング
  - EAS Update の署名検証
  - Jailbreak/Root 検出（react-native-device-info）
```

### 環境変数の管理（.env セキュリティ）

```typescript
// app.config.ts でビルド時に埋め込む
export default {
  expo: {
    extra: {
      apiUrl: process.env.API_URL,  // 非機密
      // APIキーはクライアントに入れない！
    },
  },
};

// EXPO_PUBLIC_ プレフィックスはクライアントで読める
// → 機密情報には使わない（パブリックに読める）
process.env.EXPO_PUBLIC_API_URL      // OK（パブリックURL）
process.env.EXPO_PUBLIC_STRIPE_KEY   // OK（公開鍵は問題なし）
// process.env.SECRET_KEY           // NG（クライアントには入れない）
```

### Jailbreak / Root 検出

```typescript
import DeviceInfo from 'react-native-device-info';

async function checkDeviceIntegrity() {
  const isJailbroken = await DeviceInfo.isEmulator() ||
    await DeviceInfo.hasSystemFeature('android.hardware.device');

  if (isJailbroken) {
    Alert.alert(
      'セキュリティ警告',
      'このデバイスではセキュアな機能が制限されます',
    );
  }
}
```

### Emport AI セキュリティチェックリスト

```
リリース前:
  o HTTPS のみ（ATS有効化）
  o APIキーをクライアントに埋め込んでいない
  o expo-secure-store でトークン保存
  o プロダクションビルドでデバッグログ無効
  o EAS Update コード署名設定

運用時:
  o Sentry でクラッシュ監視
  o PostHog で異常なAPIコール検出
  o 定期的な依存パッケージの脆弱性チェック（npm audit）
  o RevenueCat でサブスクリプション詐欺検出
```

**情報源:**
- [Expo Security Best Practices](https://docs.expo.dev/develop/authentication/)
- [Building Secure React Native Apps 2026](https://johal.in/building-secure-mobile-applications-with-react-native-and-expo-for-cross-platform-development-2026/)
- [Expo Secure Store Documentation](https://docs.expo.dev/versions/latest/sdk/securestore/)

---

*第15ラウンド完了（2026-05-15）: セクション82〜88 — RevenueCat・ペイウォールデザイン・Stripe・アナリティクス・A/Bテスト・生体認証・セキュリティ設計*


---

## 第16ラウンド調査（2026-05-15）: AI/LLM統合・ストリーミングチャット・音声・オンデバイスAI

### 調査テーマ
- Anthropic Claude API ストリーミングチャット
- Vercel AI SDK React Native 対応
- ストリーミングUI・タイプライター効果
- マークダウンレンダリング（AIレスポンス）
- 音声入出力（expo-speech）
- オンデバイスLLM（llama.rn・ExecuTorch）
- AIアプリのバックエンド設計

---

## 89. Anthropic Claude API ストリーミングチャット統合

### なぜストリーミングが重要か

最初のトークンが200ms以内に画面に届くと、ユーザーは「速い」と感じる。
全部届いてから表示する場合と比べて体感レスポンス速度が3〜5倍向上する。

### アーキテクチャ設計

```
Emport AI アーキテクチャ（推奨）:

[React Native App]
       |
       | HTTPS POST /api/chat
       v
[バックエンド API（Railway / Vercel Edge）]
  APIキーをサーバーサイドで管理
       |
       | Anthropic API stream
       v
[Claude claude-sonnet-4-5]
       |
       | Server-Sent Events (SSE) / chunked transfer
       v
[React Native App]
  トークン受信 → リアルタイム描画
```

**重要**: APIキーは絶対にクライアント（アプリ）に入れない。バックエンド経由が必須。

### バックエンド（Next.js / Hono）

```typescript
// app/api/chat/route.ts（Next.js App Router）
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY, // サーバーサイドのみ
});

export async function POST(req: Request) {
  const { messages, industry } = await req.json();

  const stream = await client.messages.stream({
    model: 'claude-sonnet-4-5',
    max_tokens: 1024,
    system: `あなたは${industry}専門のAI経営アドバイザーです。
    簡潔で実践的なアドバイスを日本語で提供してください。`,
    messages,
  });

  // SSEストリームとして返す
  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      for await (const chunk of stream) {
        if (chunk.type === 'content_block_delta' &&
            chunk.delta.type === 'text_delta') {
          const data = JSON.stringify({ text: chunk.delta.text });
          controller.enqueue(encoder.encode(`data: ${data}\n\n`));
        }
      }
      controller.enqueue(encoder.encode('data: [DONE]\n\n'));
      controller.close();
    },
  });

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

### React Native クライアント（SSEストリーミング受信）

```typescript
// hooks/useStreamingChat.ts
import { useState, useCallback } from 'react';

export function useStreamingChat(industry: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = useCallback(async (userText: string) => {
    const userMsg: Message = { role: 'user', content: userText };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setIsStreaming(true);

    // アシスタントのプレースホルダーを追加
    const assistantMsg: Message = { role: 'assistant', content: '' };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: updatedMessages, industry }),
      });

      // React Native: fetchでストリームを直接読む
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;

            const { text } = JSON.parse(data);
            // アシスタントの最後のメッセージにトークンを追記
            setMessages(prev => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                content: updated[updated.length - 1].content + text,
              };
              return updated;
            });
          }
        }
      }
    } finally {
      setIsStreaming(false);
    }
  }, [messages, industry]);

  return { messages, isStreaming, sendMessage };
}
```

### Emport AI の業種プロンプト設計

```typescript
const INDUSTRY_PROMPTS: Record<string, string> = {
  construction: '建設・工事業に特化したAI経営アドバイザー。現場管理・安全・原価・下請け管理を熟知。',
  fishery: '水産業に特化したAIアドバイザー。漁獲量管理・鮮度保持・流通・補助金申請を支援。',
  manufacturing: '製造業専門AIアドバイザー。品質管理・在庫・設備保全・カイゼンを専門とする。',
  retail: '小売業AIアドバイザー。在庫回転・季節変動・POSデータ活用・接客改善を支援。',
};
```

**情報源:**
- [Building AI Chat in React Native - DEV Community](https://dev.to/famitha_ma_b9c13ab1d324e/building-an-ai-chat-interface-in-react-native-with-streaming-responses-1b8g)
- [Anthropic React Native Client](https://github.com/backmesh/anthropic-react-native)
- [Building AI Apps 2026: Claude + React](https://www.nucamp.co/blog/building-ai-powered-apps-in-2026-integrating-openai-and-claude-apis-with-react-and-node)

---

## 90. Vercel AI SDK React Native 対応

### Vercel AI SDK の React Native 課題

React Nativeには `EventSource` がないため、デフォルトのVercel AI SDKの
ストリーミングが動作しない。解決策は2つ:

```
1. react-native-vercel-ai（ポリフィル）
   → EventSourceをポリフィルして useChat/useCompletion をそのまま使う

2. カスタムFetchストリーミング（推奨）
   → 自分でfetch + ReadableStreamを実装（依存を減らせる）
```

### react-native-vercel-ai セットアップ

```bash
npm install react-native-vercel-ai ai
npx expo install expo-application
```

```typescript
// app/_layout.tsx - ポリフィルを最初にインポート
import 'react-native-vercel-ai';

// チャット画面
import { useChat } from 'ai/react';

function ChatScreen() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: `${process.env.EXPO_PUBLIC_API_URL}/api/chat`,
    body: { industry: selectedIndustry },
  });

  return (
    <View>
      <FlashList
        data={messages}
        renderItem={({ item }) => (
          <MessageBubble message={item} />
        )}
        estimatedItemSize={70}
      />
      <ChatInput
        value={input}
        onChangeText={(text) => handleInputChange({ target: { value: text } } as any)}
        onSend={() => handleSubmit()}
        isLoading={isLoading}
      />
    </View>
  );
}
```

### callstack/ai（オンデバイスLLM + Vercel AI SDK互換）

```typescript
// オンデバイスLLMをVercel AI SDKと同じインターフェースで使う
import { useChat } from '@callstack/ai/react';
import { getLlama, LlamaModel } from 'llama.rn';

// ローカルLLMとクラウドLLMを同じフックで切り替え可能
const { messages, sendMessage } = useChat({
  backend: isOffline ? 'local' : 'cloud',
});
```

**情報源:**
- [react-native-vercel-ai GitHub](https://github.com/bidah/react-native-vercel-ai)
- [callstack/ai GitHub](https://github.com/callstackincubator/ai)
- [Vercel AI SDK](https://vercel.com/docs/ai-sdk)

---

## 91. ストリーミングUI・タイプライター効果・マークダウンレンダリング

### タイプライター効果（ストリーミングAI応答）

```tsx
// components/StreamingText.tsx
import { useEffect, useRef } from 'react';
import { Animated, Text } from 'react-native';

function StreamingText({ content, isStreaming }: Props) {
  const blinkAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (isStreaming) {
      // カーソル点滅
      Animated.loop(
        Animated.sequence([
          Animated.timing(blinkAnim, { toValue: 0, duration: 500, useNativeDriver: true }),
          Animated.timing(blinkAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
        ])
      ).start();
    } else {
      blinkAnim.stopAnimation();
      blinkAnim.setValue(0);
    }
  }, [isStreaming]);

  return (
    <Text>
      {content}
      {isStreaming && (
        <Animated.Text style={{ opacity: blinkAnim }}>▋</Animated.Text>
      )}
    </Text>
  );
}
```

### マークダウンレンダリング（react-native-markdown-display）

```bash
npm install react-native-markdown-display
```

```tsx
import Markdown from 'react-native-markdown-display';

const markdownStyles = {
  body: { color: '#1A1A2E', fontSize: 15, lineHeight: 22 },
  code_inline: {
    backgroundColor: '#F0F4FF',
    fontFamily: 'monospace',
    borderRadius: 4,
    paddingHorizontal: 4,
  },
  fence: {
    backgroundColor: '#1E1E3F',
    borderRadius: 8,
    padding: 12,
  },
  code_block: { color: '#E8EAF6', fontFamily: 'monospace' },
  heading1: { fontSize: 20, fontWeight: 'bold', color: '#1A3B8C' },
  heading2: { fontSize: 18, fontWeight: '600', color: '#1A3B8C' },
  table: { borderWidth: 1, borderColor: '#E0E0E0' },
  th: { backgroundColor: '#1A3B8C', padding: 8 },
};

function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'assistant') {
    return (
      <View style={styles.aiBubble}>
        <Markdown style={markdownStyles}>{message.content}</Markdown>
      </View>
    );
  }
  return (
    <View style={styles.userBubble}>
      <Text style={styles.userText}>{message.content}</Text>
    </View>
  );
}
```

### ストリーミング中のパフォーマンス最適化

```tsx
// ストリーミング中は軽量テキスト、完了後にMarkdownレンダリング
function MessageBubble({ message, isStreaming }: Props) {
  return (
    <View style={styles.bubble}>
      {message.role === 'assistant' ? (
        isStreaming && message.pending ? (
          // ストリーミング中: プレーンテキストで高速更新
          <StreamingText content={message.content} isStreaming />
        ) : (
          // 完了後: マークダウンでリッチ表示
          <Markdown style={markdownStyles}>{message.content}</Markdown>
        )
      ) : (
        <Text>{message.content}</Text>
      )}
    </View>
  );
}
```

**情報源:**
- [Stream Chat React Native AI](https://getstream.io/chat/docs/sdk/react-native/guides/ai-integrations/)
- [react-native-markdown-display npm](https://www.npmjs.com/package/react-native-markdown-display)
- [react-native-typewriter-effect](https://github.com/7nohe/react-native-typewriter-effect)

---

## 92. 音声入出力（expo-speech + expo-speech-recognition）

### Text-to-Speech（expo-speech）

```bash
npx expo install expo-speech
```

```typescript
import * as Speech from 'expo-speech';

// AIの回答を読み上げ
async function speakResponse(text: string) {
  const isSpeaking = await Speech.isSpeakingAsync();
  if (isSpeaking) await Speech.stop();

  Speech.speak(text, {
    language: 'ja-JP',
    pitch: 1.0,
    rate: 1.1, // 少し速め
    onStart: () => setIsSpeaking(true),
    onDone: () => setIsSpeaking(false),
    onError: () => setIsSpeaking(false),
  });
}
```

### Speech-to-Text（expo-speech-recognition）

```bash
npx expo install expo-speech-recognition
```

```typescript
import {
  ExpoSpeechRecognitionModule,
  useSpeechRecognitionEvent,
} from 'expo-speech-recognition';

function VoiceInputButton() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');

  useSpeechRecognitionEvent('result', (event) => {
    if (event.results[0]) {
      setTranscript(event.results[0].transcript);
    }
  });

  useSpeechRecognitionEvent('end', () => {
    setIsListening(false);
    if (transcript) {
      // 音声入力完了後にメッセージ送信
      sendMessage(transcript);
    }
  });

  const startListening = async () => {
    const result = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
    if (!result.granted) return;

    ExpoSpeechRecognitionModule.start({
      lang: 'ja-JP',
      interimResults: true,  // リアルタイム表示
      continuous: false,
    });
    setIsListening(true);
  };

  return (
    <TouchableOpacity onPress={isListening ? ExpoSpeechRecognitionModule.stop : startListening}>
      <Ionicons name={isListening ? 'mic' : 'mic-outline'} size={24}
        color={isListening ? '#FF4444' : '#1A3B8C'} />
    </TouchableOpacity>
  );
}
```

### Emport AI 音声UX設計

```
音声入力:
  マイクボタン長押し → 音声認識開始
  離す → 認識終了・自動送信
  リアルタイムで文字起こしをプレビュー表示

音声出力:
  AIの回答の右上にスピーカーアイコン
  タップで読み上げ開始/停止
  日本語 TTS（じっくり・ゆっくり選択可）

注意: Android 13+のみon-device音声認識対応
      それ以前はGoogle Cloud Speech-to-Text API（バックエンド経由）
```

**情報源:**
- [Expo Speech Documentation](https://docs.expo.dev/versions/latest/sdk/speech/)
- [expo-speech-recognition GitHub](https://github.com/jamsch/expo-speech-recognition)
- [React Native Speech Recognition 2026](https://picovoice.ai/blog/react-native-speech-recognition/)

---

## 93. オンデバイスLLM（llama.rn・React Native ExecuTorch）

### オンデバイスLLMの現状（2026年）

| ライブラリ | モデル対応 | 速度 | メモリ | 主な用途 |
|-----------|----------|------|--------|---------|
| llama.rn | Llama 3.x, Qwen, Phi | 速い | 2〜8GB | テキスト生成 |
| react-native-executorch | ExecuTorch全モデル | 最速 | 可変 | 画像・音声含む |
| whisper.rn | Whisper音声認識のみ | 速い | 1〜3GB | 高精度STT |

### llama.rn セットアップ

```bash
npm install llama.rn
```

```typescript
import { initLlama, LlamaContext } from 'llama.rn';
import RNFS from 'react-native-fs';

async function loadLocalModel() {
  const modelPath = `${RNFS.DocumentDirectoryPath}/llama-3.2-1b.gguf`;

  const context: LlamaContext = await initLlama({
    model: modelPath,
    use_mlock: true,
    n_ctx: 2048,
    n_threads: 4,
  });

  return context;
}

// 推論実行
async function generateLocally(context: LlamaContext, prompt: string) {
  const result = await context.completion({
    prompt,
    n_predict: 256,
    temperature: 0.7,
    stop: ['<|eot_id|>', '</s>'],
  }, (token) => {
    // ストリーミングコールバック
    console.log(token.token); // トークンを受信
  });
  return result.text;
}
```

### React Native ExecuTorch（Software Mansion製）

```bash
npm install react-native-executorch
```

```typescript
import { useLLM } from 'react-native-executorch';

function OfflineChatScreen() {
  const llm = useLLM({
    modelSource: require('./assets/llama3.2-1b.pte'),
  });

  const [response, setResponse] = useState('');

  const ask = async (question: string) => {
    setResponse('');
    await llm.generate(question, (token) => {
      setResponse(prev => prev + token); // リアルタイムストリーミング
    });
  };
}
```

### 実用上の制約と判断基準

```
オンデバイスLLMを採用すべき場面:
  o プライバシーが最重要（医療・金融・機密情報）
  o オフライン環境（農村・工事現場・船上）
  o APIコストを徹底的に削減したい

採用を見送る場面:
  x モデルサイズ: 1〜2Bモデルでも1〜3GBのストレージ増加
  x 品質: Claude比で大幅に劣る（2026年時点）
  x 開発コスト: ネイティブ連携のデバッグが複雑

Emport AI の推奨:
  フェーズ1〜2: Claude API（クラウド）を使用
  フェーズ3（オフライン向け）: whisper.rn（音声認識）のみオンデバイス
```

**情報源:**
- [llama.rn GitHub](https://github.com/mybigday/llama.rn)
- [React Native ExecuTorch](https://docs.swmansion.com/react-native-executorch/)
- [On-device AI React Native 2026](https://medium.com/@arslannaz195/react-native-on-device-ai-run-llms-without-internet-2026-guide-5bc95fc27bdb)

---

## 94. AIアプリのバックエンド設計（APIキーセキュリティ）

### セキュリティの鉄則

```
絶対にやってはいけない:
  x EXPO_PUBLIC_ANTHROPIC_API_KEY をアプリに入れる
    → クライアントバンドルを展開すれば誰でも抽出できる
    → APIキーを不正利用される → 高額請求

正しいアーキテクチャ:
  React Native App → バックエンドAPI → Anthropic API
                          ↑
                   ここでAPIキーを管理
```

### 軽量バックエンドオプション

```typescript
// Option A: Hono on Cloudflare Workers（最速・無料）
import { Hono } from 'hono';
import Anthropic from '@anthropic-ai/sdk';

const app = new Hono();

app.post('/api/chat', async (c) => {
  const { messages, industry } = await c.req.json();
  const user = c.get('user'); // 認証済みユーザー

  // レート制限チェック
  const usage = await checkUsageLimit(user.id);
  if (usage.exceeded) {
    return c.json({ error: 'Usage limit exceeded' }, 429);
  }

  const client = new Anthropic({ apiKey: c.env.ANTHROPIC_API_KEY });
  // ...ストリーミング実装
});

// Option B: Next.js API Routes on Vercel（フロントと同居）
// Option C: Railway（Pythonバックエンドが既にある場合）
```

### ユーザー認証とレート制限

```typescript
// レート制限: 無料ユーザーは月5回まで
async function checkUsageLimit(userId: string): Promise<{ exceeded: boolean; count: number }> {
  const key = `usage:${userId}:${new Date().toISOString().slice(0, 7)}`; // 月ごと
  const count = await redis.incr(key);

  if (count === 1) {
    await redis.expire(key, 60 * 60 * 24 * 31); // 31日後に期限切れ
  }

  const limit = await getUserPlan(userId) === 'premium' ? Infinity : 5;
  return { exceeded: count > limit, count };
}
```

### Emport AI バックエンド構成

```
既存: Railway（Python/Flask app.py）
  → /api/chat エンドポイントを追加

新規追加:
  POST /api/chat          → Claudeチャット（ストリーミング）
  GET  /api/usage         → 利用回数確認
  POST /api/subscription  → RevenueCatと連携してサブスク確認

環境変数（Railway）:
  ANTHROPIC_API_KEY
  REVENUECAT_WEBHOOK_SECRET
  JWT_SECRET
```

**情報源:**
- [Why Your AI React Native App Needs a Backend](https://blog.codeminer42.com/thinking-about-adding-ai-to-your-expo-react-native-app-read-this-first/)
- [React + AI Stack 2026](https://www.builder.io/blog/react-ai-stack-2026)

---

## 95. Emport AI AI機能 統合アーキテクチャ（総合設計）

### 全体アーキテクチャ図

```
[Emport AI モバイルアプリ]
        |
        +-- 認証 (expo-secure-store + JWT)
        |
        +-- 業種選択 (Zustand + MMKV永続化)
        |
        +-- チャット画面
        |     |
        |     +-- useStreamingChat() → POST /api/chat
        |     +-- FlashList (メッセージ一覧)
        |     +-- StreamingText + Markdown (AIレスポンス)
        |     +-- VoiceInputButton (expo-speech-recognition)
        |     +-- SpeakButton (expo-speech)
        |
        +-- サブスク管理 (RevenueCat)
        |
        +-- アナリティクス (PostHog)
        |
[バックエンド API (Railway/Python + Flask)]
        |
        +-- JWT認証ミドルウェア
        +-- レート制限 (Redis)
        +-- POST /api/chat → Anthropic ストリーミング
        |
[Anthropic Claude claude-sonnet-4-5]
```

### 技術スタック まとめ

```
フロントエンド:
  Framework:  Expo SDK 53 / React Native 0.79
  ルーティング: Expo Router v4
  状態管理:    Zustand + MMKV (ローカル), TanStack Query (サーバー)
  UI:         NativeWind 4.x (TailwindCSS)
  アニメーション: Reanimated 4
  リスト:      FlashList (@shopify/flash-list)
  AI表示:     react-native-markdown-display + カスタムStreamingText

バックエンド:
  サーバー:    Railway (既存Python/Flask)
  AI:         Anthropic Claude API (ストリーミング)
  認証:        JWT + expo-secure-store
  DB/Cache:   PostgreSQL + Redis (Upstash)

収益:
  モバイルIAP: RevenueCat (react-native-purchases)
  Web決済:    Stripe

アナリティクス/実験:
  Analytics:  PostHog (イベント + セッション録画 + A/B)
  クラッシュ:  Sentry

デプロイ:
  ビルド:     EAS Build
  OTA更新:    EAS Update (段階ロールアウト)
  CI/CD:     GitHub Actions + EAS Workflows
```

**Emport AIアプリの差別化ポイント:**
1. 業種特化プロンプト（建設・水産・製造等）
2. ストリーミングで即座に回答が届く体験
3. 月額980円（ChatGPT Plusの3分の1）
4. 音声入力対応で入力の手間を省く
5. IT補助金で導入コスト最大450万円まで補助

---

*第16ラウンド完了（2026-05-15）: セクション89〜95 — Anthropic API統合・Vercel AI SDK・ストリーミングUI・音声入出力・オンデバイスLLM・バックエンド設計・Emport AI統合アーキテクチャ*


---

## 第17ラウンド調査（2026-05-15）: リアルタイム・オフラインDB・バックグラウンド・カメラ・ウィジェット

### 調査テーマ
- Supabase Realtime（リアルタイムデータ同期）
- SQLite + Drizzle ORM（オフラインファースト）
- バックグラウンドタスク
- カメラ・画像ピッカー・ファイルアップロード
- iOS ウィジェット・Live Activities
- ホームスクリーンショートカット・Share Extension

---

## 96. Supabase Realtime（リアルタイムデータ同期）

### Supabase の位置づけ

Supabase = オープンソースの Firebase 代替。Emport AI バックエンドとして考えた場合:

```
既存のRailway(Python/Flask) vs Supabase:
  Railway: 自前コントロール可能・Anthropic API連携済み → 維持推奨
  Supabase: 認証・DB・Realtime・Storage がオールインワン → 第2フェーズで検討
```

### セットアップ

```bash
npx expo install @supabase/supabase-js @react-native-async-storage/async-storage react-native-url-polyfill
```

```typescript
// utils/supabase.ts
import 'react-native-url-polyfill/auto';
import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!, // 公開キー（行レベルセキュリティで保護）
  {
    auth: {
      storage: AsyncStorage,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    },
  }
);
```

### Supabase Auth（メール・ソーシャルログイン）

```typescript
// ログイン（パスワードはユーザーが入力する変数を使う）
const { data, error } = await supabase.auth.signInWithPassword({
  email: userEmail,      // フォームから取得
  userInputPassword, // フォームから取得（ハードコードしない）
});

// サインアップ
const { data, error } = await supabase.auth.signUp({
  email: userEmail,
  password: userInputPassword, // ユーザー入力値
  options: {
    data: { industry: 'construction', full_name: userName }
  }
});

// セッション監視
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') {
    useAuthStore.getState().login(session!.access_token, session!.user);
  } else if (event === 'SIGNED_OUT') {
    useAuthStore.getState().logout();
  }
});
```

### Supabase Realtime（チャット履歴のリアルタイム同期）

```typescript
// チャット履歴をリアルタイムで監視
useEffect(() => {
  const channel = supabase
    .channel('chat-history')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'messages',
        filter: `session_id=eq.${sessionId}`,
      },
      (payload) => {
        setMessages(prev => [...prev, payload.new as Message]);
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}, [sessionId]);
```

### Expo SDK 53 での注意点

```
Supabase-js v2.x が ws モジュールに依存 → React Native では polyfill 必要
解決策:
  1. react-native-url-polyfill を最初にインポート
  2. Supabase クライアントで realtime を最小設定に

const supabase = createClient(url, key, {
  realtime: { params: { eventsPerSecond: 10 } },
});

2026年末に旧APIキーが廃止予定:
  旧: anon / service_role キー
  新: sb_publishable_[key] / sb_secret_[key] 形式に移行推奨
```

**情報源:**
- [Supabase with Expo React Native](https://supabase.com/docs/guides/getting-started/quickstarts/expo-react-native)
- [Expo Supabase Guide](https://docs.expo.dev/guides/using-supabase/)

---

## 97. SQLite + Drizzle ORM（オフラインファースト）

### なぜ SQLite + Drizzle ORM か

```
MMKV         → シンプルなKV（設定・状態）
SQLite+Drizzle → 複雑なリレーショナルデータ（チャット履歴・検索対応）

Drizzle の強み:
  - TypeScript で型安全なSQLクエリ
  - expo-sqlite と公式統合
  - useLiveQuery でデータ変更時に自動再レンダリング
  - マイグレーション管理が容易
```

### セットアップ

```bash
npx expo install expo-sqlite
npm install drizzle-orm
npm install --save-dev drizzle-kit
```

### スキーマ定義

```typescript
// db/schema.ts
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
import { relations } from 'drizzle-orm';

export const chatSessions = sqliteTable('chat_sessions', {
  id: text('id').primaryKey(),
  industry: text('industry').notNull(),
  title: text('title').notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull(),
});

export const messages = sqliteTable('messages', {
  id: text('id').primaryKey(),
  sessionId: text('session_id').references(() => chatSessions.id).notNull(),
  role: text('role', { enum: ['user', 'assistant'] }).notNull(),
  content: text('content').notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull(),
});

export const sessionRelations = relations(chatSessions, ({ many }) => ({
  messages: many(messages),
}));
```

### データベース初期化とマイグレーション

```typescript
// db/index.ts
import { drizzle } from 'drizzle-orm/expo-sqlite';
import { openDatabaseSync } from 'expo-sqlite';
import { useMigrations } from 'drizzle-orm/expo-sqlite/migrator';
import migrations from './migrations';

const expo = openDatabaseSync('emport-ai.db', { enableChangeListener: true });
export const db = drizzle(expo);

export function DatabaseProvider({ children }: { children: React.ReactNode }) {
  const { success, error } = useMigrations(db, migrations);
  if (error) return <ErrorScreen message="DB初期化エラー" />;
  if (!success) return <LoadingScreen />;
  return children;
}
```

### useLiveQuery（リアルタイムDB更新）

```typescript
import { useLiveQuery } from 'drizzle-orm/expo-sqlite';
import { desc } from 'drizzle-orm';

function ChatHistoryScreen() {
  // DBが変更されると自動的に再レンダリング
  const { data: sessions } = useLiveQuery(
    db.select()
      .from(chatSessions)
      .orderBy(desc(chatSessions.updatedAt))
      .limit(50)
  );

  return (
    <FlashList
      data={sessions}
      renderItem={({ item }) => <SessionCard session={item} />}
      estimatedItemSize={70}
    />
  );
}
```

### オフラインファースト + バックグラウンド同期

```typescript
// 書き込みはSQLiteに即座に → バックグラウンドでサーバーに同期
async function saveMessageLocally(message: Message) {
  // 1. ローカルに即保存（UI即座に更新）
  await db.insert(messages).values(message);

  // 2. バックグラウンドでサーバーに同期（失敗してもOK）
  syncQueue.add(() => api.saveMessage(message));
}
```

**情報源:**
- [Drizzle ORM Expo SQLite](https://orm.drizzle.team/docs/connect-expo-sqlite)
- [Modern SQLite for React Native](https://expo.dev/blog/modern-sqlite-for-react-native-apps)
- [Offline-First with Drizzle + Expo](https://medium.com/@detl/building-an-offline-first-production-ready-expo-app-with-drizzle-orm-and-sqlite-f156968547a2)

---

## 98. バックグラウンドタスク（expo-background-task）

### 2026年の変更点

expo-background-fetch が**非推奨**になり、`expo-background-task` に移行。

```bash
npx expo install expo-background-task expo-task-manager
```

### バックグラウンドタスク実装

```typescript
import * as BackgroundTask from 'expo-background-task';
import * as TaskManager from 'expo-task-manager';

const SYNC_TASK = 'emport-ai-sync';

// タスク定義（アプリ起動前にグローバルで登録）
TaskManager.defineTask(SYNC_TASK, async () => {
  try {
    await syncUnsentMessages();
    await refreshSubscriptionStatus();
    return BackgroundTask.BackgroundTaskResult.Success;
  } catch {
    return BackgroundTask.BackgroundTaskResult.Failed;
  }
});

// タスク登録（アプリ起動時）
async function registerBackgroundSync() {
  const status = await BackgroundTask.getStatusAsync();
  if (status === BackgroundTask.BackgroundTaskStatus.Available) {
    await BackgroundTask.registerTaskAsync(SYNC_TASK, {
      minimumInterval: 15 * 60, // 最小15分（OSが遅延させる場合あり）
    });
  }
}
```

### バックグラウンドの制約（重要）

```
iOS の制限:
  - 最小インターバル15分（実際には1〜2時間に1回程度）
  - Low Power Mode 中は停止
  - アプリを最近使っていないと頻度が減る

できること:
  o 未送信メッセージの同期
  o サブスクリプション状態の確認
  o 軽量なAPIポーリング

できないこと:
  x 30秒以上の処理
  x UI の更新
  x 大量データの転送
```

### Emport AI バックグラウンド設計

```
バックグラウンドで実行:
  - オフライン中に作成したチャットをサーバーに同期
  - RevenueCatのサブスクリプション状態をキャッシュ更新

フォアグラウンドで実行:
  - Claude APIへのリクエスト（ストリーミング）
  - ファイルのアップロード
```

**情報源:**
- [Expo Background Task](https://docs.expo.dev/versions/latest/sdk/background-task/)
- [Background Tasks React Native 2026](https://dev.to/eira-wexford/run-react-native-background-tasks-2026-for-optimal-performance-d26)

---

## 99. カメラ・画像ピッカー・ファイルアップロード

### expo-image-picker セットアップ

```bash
npx expo install expo-image-picker
```

```tsx
import * as ImagePicker from 'expo-image-picker';

function DocumentUploadButton() {
  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') return;

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.7,
      allowsMultipleSelection: true,
      selectionLimit: 5,
    });

    if (!result.canceled) {
      await uploadFiles(result.assets);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') return;

    const result = await ImagePicker.launchCameraAsync({
      quality: 0.8,
      allowsEditing: true,
    });

    if (!result.canceled) {
      await uploadFiles([result.assets[0]]);
    }
  };
}
```

### サーバーへのアップロード（FormData）

```typescript
import { fetch } from 'expo/fetch'; // React Native の fetch より高機能

async function uploadFiles(assets: ImagePicker.ImagePickerAsset[]) {
  const formData = new FormData();

  for (const asset of assets) {
    const file = {
      uri: asset.uri,
      type: asset.mimeType ?? 'image/jpeg',
      name: asset.fileName ?? `upload_${Date.now()}.jpg`,
    } as any;
    formData.append('files', file);
  }

  const response = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData,
  });

  const { urls } = await response.json();
  return urls;
}
```

### ドキュメントピッカー（PDF・Word等）

```typescript
import * as DocumentPicker from 'expo-document-picker';

async function pickDocument() {
  const result = await DocumentPicker.getDocumentAsync({
    type: ['application/pdf',
           'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    multiple: false,
    copyToCacheDirectory: true,
  });

  if (!result.canceled) {
    const doc = result.assets[0];
    await uploadFiles([doc as any]);
  }
}
```

### Emport AI への応用

```
名刺・契約書スキャン（将来機能）:
  カメラで名刺を撮影 → Claude Vision APIで名前・会社名を抽出

注意: 現フェーズはテキストチャットのみ。画像対応は第2フェーズ以降。
```

**情報源:**
- [Expo ImagePicker Documentation](https://docs.expo.dev/versions/latest/sdk/imagepicker/)
- [Expo image-upload-example GitHub](https://github.com/expo/image-upload-example)

---

## 100. iOS ウィジェット・Live Activities

### iOS ウィジェット実装（2026年）

iOSウィジェット（WidgetKit）はSwiftで書く必要あり。以下のツールで統合:

```
expo-widgets        : Expo UIコンポーネントでウィジェット作成
react-native-widget-extension: Swift + Expo の組み合わせ
```

### expo-widgets セットアップ

```typescript
// widget/index.tsx
import { Text, View } from 'expo-widgets/components';

export default function EmportAIWidget() {
  return (
    <View style={{ padding: 12, flex: 1, justifyContent: 'center' }}>
      <Text style={{ fontSize: 14, color: '#8888AA' }}>今日の業務ヒント</Text>
      <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#1A3B8C' }}>
        AIが今日もサポート
      </Text>
    </View>
  );
}
```

### App Groups（ウィジェット-アプリ間データ共有）

```typescript
import * as SharedGroupPreferences from 'react-native-shared-group-preferences';

const GROUP_ID = 'group.com.emportai.app';

// アプリ側: ウィジェット用データを書き込む
await SharedGroupPreferences.setItem('lastTip', JSON.stringify({
  text: '建設現場の安全管理で最も重要なのは...',
  industry: 'construction',
  updatedAt: new Date().toISOString(),
}), GROUP_ID);
```

### Live Activities（Dynamic Island対応）

```typescript
import { startActivity, updateActivity, endActivity } from 'expo-widgets/live-activity';

// チャット処理中のLive Activity
const activityId = await startActivity({
  attributes: { sessionId: currentSessionId },
  contentState: {
    status: 'AIが回答を生成中...',
    progress: 0.0,
  },
});

await updateActivity(activityId, {
  contentState: { status: '回答完了', progress: 1.0 },
});

await endActivity(activityId);
```

### Emport AI ウィジェット設計

```
Small ウィジェット: 今日のAIヒント（業種別）
Medium ウィジェット: 最新の業務アドバイス + 「今すぐ相談」ボタン
Live Activity: Claude回答生成中のプログレス表示（将来機能）
```

**情報源:**
- [Expo Widgets Documentation](https://docs.expo.dev/versions/latest/sdk/widgets/)
- [iOS Widgets in Expo Blog](https://expo.dev/blog/how-to-implement-ios-widgets-in-expo-apps)
- [react-native-widget-extension GitHub](https://github.com/bndkt/react-native-widget-extension)

---

## 101. ホームスクリーンショートカット・Share Extension

### ホームスクリーン長押しショートカット（expo-quick-actions）

```bash
npx expo install expo-quick-actions
```

```typescript
import * as QuickActions from 'expo-quick-actions';
import { useQuickActionCallback } from 'expo-quick-actions/hooks';

useEffect(() => {
  QuickActions.setItems([
    {
      title: '新しい相談を始める',
      subtitle: 'AIに相談する',
      id: 'new_chat',
      icon: 'compose',
    },
    {
      title: '建設業AIを開く',
      id: 'construction_chat',
      icon: 'building',
    },
  ]);
}, []);

useQuickActionCallback((action) => {
  switch (action.id) {
    case 'new_chat':
      router.push('/chat/new');
      break;
    case 'construction_chat':
      router.push('/chat/new?industry=construction');
      break;
  }
});
```

### Emport AI ショートカット設計

```
ホームスクリーン長押しメニュー:
  1. 「新しい相談」→ /chat/new
  2. 「建設業AIチャット」→ /chat/new?industry=construction
  3. 「相談履歴を見る」→ /history

Share Extension（将来機能）:
  Webページ・ニュース記事を共有 → AIが内容を要約・解説
```

**情報源:**
- [expo-quick-actions GitHub](https://github.com/EvanBacon/expo-quick-actions)
- [Home Screen Shortcuts in Expo](https://dev.to/zuluana/home-screen-shortcuts-in-react-native-with-expo-a5b)
- [expo-share-extension GitHub](https://github.com/MaxAst/expo-share-extension)

---

## 102. Emport AI 実装ロードマップ（17ラウンド調査総括）

### フェーズ別実装計画

```
フェーズ1（2026年6月リリース）: MVP
  技術スタック:
    - Expo SDK 53 / React Native 0.79
    - Expo Router v4
    - NativeWind 4.x（TailwindCSS）
    - Zustand + MMKV（状態管理）
    - TanStack Query v5（APIデータ）
    - FlashList（高速リスト）
    - Reanimated 4（アニメーション）
    - RevenueCat（月額980円 IAP）
    - Anthropic Claude Streaming（Railway バックエンド）
    - PostHog（アナリティクス + A/B）
    - EAS Build + EAS Submit

  機能:
    - 業種選択（建設・水産・製造・小売）
    - テキストチャット（ストリーミング）
    - 月5回無料・Pro無制限
    - 生体認証（Touch ID / Face ID）

フェーズ2（2026年9〜11月）: 機能強化
  追加技術:
    - SQLite + Drizzle ORM（オフラインファースト）
    - expo-speech-recognition（音声入力）
    - expo-speech（音声読み上げ）
    - expo-widgets（ホームスクリーンウィジェット）
    - expo-quick-actions（ショートカット）
    - Sentry（クラッシュ監視）
    - Maestro（E2Eテスト）

  機能:
    - 音声チャット
    - オフライン対応
    - ウィジェット（今日のヒント）
    - 画像添付（名刺・資料スキャン）

フェーズ3（2027年〜）: スケール
  追加技術:
    - Supabase（認証・DB・Realtime）
    - Stripe（Web決済）
    - チームプラン（マルチユーザー）
    - バーティカルSaaS化（建設AI・水産AI等の専門版）
```

### 学習した主要技術一覧（17ラウンド・セクション1〜102）

```
レイアウト:    Flexbox, Yoga, SafeAreaView, KeyboardAvoidingView
アニメーション: Reanimated 4, CSS Transitions, Shared Elements
ナビゲーション: Expo Router v4, Stack, Tabs, Bottom Sheet
UIライブラリ:  NativeWind, Gluestack UI v2, Tamagui
状態管理:     Zustand, TanStack Query v5
ストレージ:   MMKV, expo-secure-store, SQLite+Drizzle
ネットワーク: fetch streaming, Supabase Realtime
AI統合:       Anthropic Claude API, Vercel AI SDK, llama.rn
決済:         RevenueCat, Stripe
テスト:       Jest, RNTL, Maestro E2E
デプロイ:     EAS Build, EAS Submit, EAS Update(OTA)
CI/CD:       GitHub Actions + EAS Workflows
アナリティクス: PostHog (A/B + Feature Flags + Analytics)
セキュリティ:  生体認証, SecureStore, JWT, HTTPS
パフォーマンス: FlashList, React.memo, useCallback, getItemLayout
プラットフォーム: iOS Widgets, Live Activities, Quick Actions
```

---

*第17ラウンド完了（2026-05-15）: セクション96〜102 — Supabase Realtime・SQLite Drizzle・バックグラウンド・カメラ・ウィジェット・ショートカット・実装ロードマップ総括*

---

## 調査完了サマリー（2026-05-15）

**総調査ラウンド数**: 17ラウンド
**総セクション数**: 102セクション
**ファイル**: data/reports/research-app-dev.md

Emport AIアプリ開発に必要な技術知識を体系的に網羅。
MVP実装からスケールまでの全技術スタックを調査・文書化完了。

---

## Round 18 — アクセシビリティ・i18n・フォーム・ディープリンク・パフォーマンス・通知・テスト
調査日時: 2026-05-15

---

## 103. React Native アクセシビリティ（a11y）完全ガイド

### 調査日時
2026-05-15

### 概要
アクセシビリティ（a11y）は、VoiceOver（iOS）・TalkBack（Android）などのスクリーンリーダーを使うユーザーでも快適にアプリを使えるようにするための実装。2026年はアクセシビリティ対応がApp Store審査の評価項目にも組み込まれ始めている。

### 主要プロパティ

```tsx
// 基本的なアクセシビリティprops
<TouchableOpacity
  accessible={true}
  accessibilityRole="button"
  accessibilityLabel="AIに質問する"
  accessibilityHint="タップするとAIが回答を生成します"
  accessibilityState={{ disabled: isLoading }}
  onPress={handlePress}
>
  <Text>質問する</Text>
</TouchableOpacity>

// フォーム要素
<TextInput
  accessible={true}
  accessibilityRole="search"
  accessibilityLabel="業種を入力"
  accessibilityRequired={true}
  placeholder="例：建設業"
/>

// 動的アナウンス（ローディング完了通知など）
import { AccessibilityInfo } from 'react-native';

const announceResult = (text: string) => {
  AccessibilityInfo.announceForAccessibility(text);
};

// 回答生成後にスクリーンリーダーへ通知
useEffect(() => {
  if (response) {
    announceResult(`AIの回答が生成されました: ${response.slice(0, 50)}`);
  }
}, [response]);
```

### Reduced Motion 対応

```tsx
import { AccessibilityInfo } from 'react-native';
import { useEffect, useState } from 'react';

export function useReducedMotion() {
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotion);
    const sub = AccessibilityInfo.addEventListener(
      'reduceMotionChanged',
      setReduceMotion
    );
    return () => sub.remove();
  }, []);

  return reduceMotion;
}

// アニメーション制御
const reduceMotion = useReducedMotion();
const animStyle = useAnimatedStyle(() => ({
  opacity: withTiming(visible ? 1 : 0, {
    duration: reduceMotion ? 0 : 300,
  }),
}));
```

### accessibilityRole 一覧（主要）

| Role | 用途 |
|------|------|
| button | タップ可能なボタン |
| link | 外部リンク |
| header | セクション見出し |
| image | 画像（decorativeなら accessibilityElementsHidden={true}） |
| search | 検索入力欄 |
| tab | タブナビゲーション |
| checkbox | チェックボックス |
| combobox | ドロップダウン選択 |

### Emport AIへの応用
- AIチャット送信ボタン・業種選択ドロップダウンに accessibilityLabel を必ず付与
- ストリーミング完了時に `AccessibilityInfo.announceForAccessibility()` で通知
- アニメーション（タイピングエフェクト）は `useReducedMotion()` でスキップ対応
- 将来的なApp Store審査での差別化ポイントになる

---

## 104. 国際化（i18n）— expo-localization + react-i18next

### 調査日時
2026-05-15

### 概要
expo-localization でデバイスのロケール（言語・地域）を取得し、react-i18next で翻訳テキストを管理する組み合わせが2026年の標準。Emport AIは日本語主体だが、将来的な英語・中国語対応の基盤として今から設計しておく価値がある。

### インストール

```bash
npx expo install expo-localization
npm install i18next react-i18next
```

### セットアップ

```typescript
// i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';

import ja from './locales/ja.json';
import en from './locales/en.json';

const deviceLocale = Localization.getLocales()[0]?.languageCode ?? 'ja';

i18n.use(initReactI18next).init({
  resources: {
    ja: { translation: ja },
    en: { translation: en },
  },
  lng: deviceLocale,
  fallbackLng: 'ja',
  interpolation: { escapeValue: false },
  compatibilityJSON: 'v4',
});

export default i18n;
```

```json
// i18n/locales/ja.json
{
  "chat": {
    "placeholder": "業種・悩みを入力してください",
    "send": "送信",
    "thinking": "考え中...",
    "error": "エラーが発生しました"
  },
  "onboarding": {
    "title": "AI経営アドバイザー",
    "subtitle": "あなたの業種に特化したAIが回答します",
    "selectIndustry": "業種を選択"
  },
  "subscription": {
    "upgrade": "プレミアムにアップグレード",
    "perMonth": "月額 {{price}}円"
  }
}
```

### 使い方

```tsx
// コンポーネント内
import { useTranslation } from 'react-i18next';

export function ChatScreen() {
  const { t } = useTranslation();

  return (
    <TextInput
      placeholder={t('chat.placeholder')}
    />
    <Button title={t('chat.send')} onPress={handleSend} />
    // 補間（変数埋め込み）
    <Text>{t('subscription.perMonth', { price: 980 })}</Text>
  );
}

// 言語切り替え
import i18n from '../i18n/config';
const switchLanguage = (lang: 'ja' | 'en') => i18n.changeLanguage(lang);
```

### Emport AIへの応用
- 日本語のみでも今から i18n 構造で書いておく → 英語版リリース時にコスト激減
- `Localization.getLocales()[0]?.languageCode` でデバイス言語を自動検出
- 将来の海外展開（ASEAN中小企業向け）の礎になる

---

## 105. React Hook Form + Zod — 型安全フォームバリデーション

### 調査日時
2026-05-15

### 概要
React Hook Form（RHF）は非制御コンポーネントベースで再レンダリングを最小化し、Zodは TypeScript-first のスキーマバリデーションライブラリ。両者の組み合わせが2026年のRNフォームのデファクトスタンダード。

### インストール

```bash
npm install react-hook-form zod @hookform/resolvers
```

### 実装パターン（ログイン画面）

```tsx
import { useForm, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { View, TextInput, Text, TouchableOpacity, StyleSheet } from 'react-native';

// スキーマ定義（型推論も自動）
const loginSchema = z.object({
  email: z.string().email('有効なメールアドレスを入力してください'),
  userPassword: z.string().min(8, 'パスワードは8文字以上必要です'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', userPassword: '' },
  });

  const onSubmit = async (data: LoginFormValues) => {
    await signIn(data.email, data.userPassword);
  };

  return (
    <View>
      <Controller
        name="email"
        control={control}
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            onChangeText={onChange}
            onBlur={onBlur}
            value={value}
            placeholder="メールアドレス"
            keyboardType="email-address"
            autoCapitalize="none"
            style={[styles.input, errors.email && styles.inputError]}
          />
        )}
      />
      {errors.email && (
        <Text style={styles.errorText}>{errors.email.message}</Text>
      )}

      <Controller
        name="userPassword"
        control={control}
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            onChangeText={onChange}
            onBlur={onBlur}
            value={value}
            placeholder="パスワード（8文字以上）"
            secureTextEntry
            style={[styles.input, errors.userPassword && styles.inputError]}
          />
        )}
      />
      {errors.userPassword && (
        <Text style={styles.errorText}>{errors.userPassword.message}</Text>
      )}

      <TouchableOpacity
        onPress={handleSubmit(onSubmit)}
        disabled={isSubmitting}
        style={styles.button}
      >
        <Text>{isSubmitting ? '送信中...' : 'ログイン'}</Text>
      </TouchableOpacity>
    </View>
  );
}
```

### 業種登録フォーム（Emport AI向け）

```tsx
const onboardingSchema = z.object({
  companyName: z.string().min(1, '会社名を入力してください').max(50),
  industry: z.enum(['construction', 'fishery', 'retail', 'manufacturing', 'hospitality'], {
    errorMap: () => ({ message: '業種を選択してください' }),
  }),
  employeeCount: z.coerce.number().min(1).max(999),
  concern: z.string().max(200, '200文字以内で入力してください').optional(),
});

type OnboardingValues = z.infer<typeof onboardingSchema>;
```

### Emport AIへの応用
- 会社登録・業種選択・プロフィール編集に RHF + Zod を使用
- Zodスキーマをバックエンド（API）とフロントエンドで共有してバリデーション一元管理
- `z.infer<typeof schema>` で TypeScript型が自動生成されるため型定義の重複なし

---

## 106. ディープリンク・ユニバーサルリンク（Expo Router）

### 調査日時
2026-05-15

### 概要
ディープリンクはアプリの特定画面を外部から直接開く仕組み。Expo Router v4 ではファイルシステムベースのルーティングがそのままディープリンクに対応し、設定不要で全ルートが自動的にリンク可能になる。

### 3種類のリンキング方式

| 方式 | URL形式 | 特徴 |
|------|---------|------|
| カスタムスキーム | `emportai://chat` | アプリインストール済み前提。未インストールは失敗 |
| Universal Links (iOS) | `https://emport-ai.vercel.app/chat` | ウェブとアプリ両対応。未インストール時はWebへ |
| App Links (Android) | `https://emport-ai.vercel.app/chat` | iOS Universal LinksのAndroid版 |

### Expo Router での設定

```json
// app.json
{
  "expo": {
    "scheme": "emportai",
    "ios": {
      "associatedDomains": ["applinks:emport-ai.vercel.app"]
    },
    "android": {
      "intentFilters": [
        {
          "action": "VIEW",
          "autoVerify": true,
          "data": [
            { "scheme": "https", "host": "emport-ai.vercel.app" }
          ],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    }
  }
}
```

```typescript
// app/(tabs)/chat/[sessionId].tsx
// このファイル = emportai://chat/12345 で自動的に開く
import { useLocalSearchParams } from 'expo-router';

export default function ChatSessionScreen() {
  const { sessionId } = useLocalSearchParams<{ sessionId: string }>();
  // ...
}

// リンク生成（共有ボタンなど）
import { Linking } from 'react-native';
import * as Sharing from 'expo-sharing';

const shareConversation = async (sessionId: string) => {
  const url = `https://emport-ai.vercel.app/chat/${sessionId}`;
  await Sharing.shareAsync(url);
};

// プログラム的な画面遷移
import { router } from 'expo-router';
router.push('/chat/12345');
```

### assetlinks.json（Webサイト側設定）

```json
// vercel.app/.well-known/assetlinks.json (Android App Links用)
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.emportai.app",
    "sha256_cert_fingerprints": ["YOUR_SHA256_FINGERPRINT"]
  }
}]
```

### Firebase Dynamic Links廃止への対応（2025年8月終了）
2026年の代替ソリューション：
- **Branch.io**: 最も機能豊富。遅延ディープリンク（アプリ未インストールでも動作）、アトリビューション付き
- **Adjust**: モバイルアトリビューション特化
- **シンプルなケース**: Universal Links + カスタムスキームの組み合わせで十分

### Emport AIへの応用
- プッシュ通知からチャット履歴へのディープリンク（`emportai://history/sessionId`）
- 顧客紹介キャンペーン用の共有リンク（`https://emport-ai.vercel.app/invite/CODE`）
- Universal Links設定でWebとアプリの両方に対応

---

## 107. React Native パフォーマンスプロファイリング

### 調査日時
2026-05-15

### 概要
2026年のRNパフォーマンス最適化の目標は「99パーセンタイルデバイスで58fps以上の維持」。New Architecture（Fabric + JSI）がデフォルトになり、Hermes V1.0でJS実行速度が大幅向上した。それでもコンポーネントの過剰再レンダリングはボトルネックになる。

### プロファイリングツール

| ツール | 用途 | 対応 |
|--------|------|------|
| React DevTools Profiler | コンポーネント再レンダリング分析 | iOS/Android |
| Flipper | フレームレート・ネットワーク・ログ | iOS/Android |
| Flashlight | ベンチマーク数値化（CIに組み込める） | Android |
| react-native-performance | カスタムマーク計測 | iOS/Android |

### 再レンダリング削減

```tsx
import React, { memo, useCallback, useMemo } from 'react';

// memo: propsが変わらない限り再レンダリングしない
const ChatMessage = memo(({ message, onLongPress }: Props) => {
  return (
    <View>
      <Text>{message.content}</Text>
    </View>
  );
});

// useCallback: 関数の参照を固定
const handleLongPress = useCallback((messageId: string) => {
  setSelectedMessage(messageId);
}, []);

// useMemo: 計算結果をキャッシュ
const sortedMessages = useMemo(
  () => [...messages].sort((a, b) => b.timestamp - a.timestamp),
  [messages]
);
```

### FlashList + getItemLayout（60fps維持）

```tsx
import { FlashList } from '@shopify/flash-list';

// 固定高さの場合は getItemLayout 相当の overrideItemLayout が使える
<FlashList
  data={messages}
  renderItem={({ item }) => <ChatMessage message={item} />}
  estimatedItemSize={72}       // 平均アイテム高さ
  initialNumToRender={15}
  drawDistance={400}
  keyExtractor={(item) => item.id}
  // ヘビーな処理は removeClippedSubviews で画面外を非アクティブ化
/>
```

### Hermes Bundle最適化

```bash
# バンドルサイズ確認
npx expo export --platform android
npx react-native-bundle-visualizer

# 不要なimportを検出
npx depcheck
```

### パフォーマンス計測（カスタム）

```typescript
import * as Performance from 'react-native-performance';

// 画面初期表示時間の計測
Performance.mark('ChatScreen.mount.start');
// ...コンポーネントマウント...
Performance.mark('ChatScreen.mount.end');
Performance.measure('ChatScreen.TTI', 'ChatScreen.mount.start', 'ChatScreen.mount.end');
```

### 2026年の目標値

| 指標 | 目標値 |
|------|--------|
| スクロールFPS | 58fps以上（99パーセンタイル） |
| 初回表示（TTI） | 2秒以内 |
| JS Bundle Size | 5MB以下（gzip後） |
| メモリ使用量 | 150MB以下（ミッドレンジ端末） |

### Emport AIへの応用
- チャット画面の FlashList で長い会話履歴でも60fps維持
- `memo` + `useCallback` でメッセージコンポーネントの不要再レンダリングを排除
- Flashlight をCIに組み込み、パフォーマンス劣化をコミット単位で検出

---

## 108. プッシュ通知（expo-notifications）高度な設定

### 調査日時
2026-05-15

### 概要
expo-notifications は FCM（Android）・APNs（iOS）の複雑さを抽象化し、統一APIで通知を送受信できる。Expo Push Service経由とFCM/APNs直接送信の両方に対応。

### インストール・設定

```bash
npx expo install expo-notifications expo-device
```

```json
// app.json
{
  "expo": {
    "plugins": [
      [
        "expo-notifications",
        {
          "icon": "./assets/notification-icon.png",
          "color": "#1428C8",
          "sounds": ["./assets/notification.wav"],
          "androidMode": "default"
        }
      ]
    ]
  }
}
```

### プッシュトークン取得と送信

```typescript
// hooks/usePushNotifications.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
import { useEffect, useRef } from 'react';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export function usePushNotifications() {
  const notificationListener = useRef<Notifications.EventSubscription>();
  const responseListener = useRef<Notifications.EventSubscription>();

  const registerForPushNotifications = async () => {
    if (!Device.isDevice) return null;

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') return null;

    const projectId = Constants.expoConfig?.extra?.eas?.projectId;
    const token = await Notifications.getExpoPushTokenAsync({ projectId });
    return token.data;
  };

  useEffect(() => {
    registerForPushNotifications().then((token) => {
      if (token) {
        // バックエンドにトークンを送信して保存
        api.savePushToken(token);
      }
    });

    // フォアグラウンド通知受信
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('通知受信:', notification);
      }
    );

    // 通知タップ時の処理
    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        const data = response.notification.request.content.data;
        if (data.screen === 'chat') {
          router.push(`/chat/${data.sessionId}`);
        }
      }
    );

    return () => {
      notificationListener.current?.remove();
      responseListener.current?.remove();
    };
  }, []);
}
```

### スケジュール通知（リマインダー）

```typescript
// 翌日9時のリマインダー通知
const scheduleReminder = async () => {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: 'AIアドバイスの時間です',
      body: '今日の経営課題をEmport AIに相談しましょう',
      data: { screen: 'chat' },
      sound: true,
    },
    trigger: {
      type: Notifications.SchedulableTriggerInputTypes.CALENDAR,
      hour: 9,
      minute: 0,
      repeats: true,        // 毎日繰り返し
    },
  });
};

// Android 12+: 正確なアラームの許可が必要
import { Platform } from 'react-native';
if (Platform.OS === 'android' && Platform.Version >= 31) {
  await Notifications.requestPermissionsAsync({
    android: { allowAlarms: true },
  });
}
```

### バックエンドからの送信（Expo Push Service）

```typescript
// backend/notifications.ts
import Expo from 'expo-server-sdk';

const expo = new Expo();

export async function sendPushNotification(
  pushTokens: string[],
  title: string,
  body: string,
  data?: Record<string, unknown>
) {
  const messages = pushTokens
    .filter((token) => Expo.isExpoPushToken(token))
    .map((token) => ({
      to: token,
      sound: 'default' as const,
      title,
      body,
      data,
      badge: 1,
    }));

  const chunks = expo.chunkPushNotifications(messages);
  for (const chunk of chunks) {
    await expo.sendPushNotificationsAsync(chunk);
  }
}

// 使用例
await sendPushNotification(
  userTokens,
  'AIが回答を生成しました',
  '建設業の資金繰りについての回答が届きました',
  { screen: 'chat', sessionId: 'abc123' }
);
```

### Emport AIへの応用
- AIの回答生成完了通知（バックグラウンド処理後）
- 毎朝9時の「経営チェック」リマインダー通知
- 補助金申請締切リマインダー（例：5/22山口県DX補助金）
- 通知タップでチャット画面にディープリンク

---

## 109. テスト戦略（Jest + React Native Testing Library + Maestro）

### 調査日時
2026-05-15

### 概要
2026年のRN推奨テスト構成は「Jest（単体）+ React Native Testing Library RNTL（コンポーネント）+ Maestro（E2E）」の3層。react-test-renderer は React 19以降非推奨。

### セットアップ

```bash
# jest-expo は Expoの Jest プリセット（設定の大部分を自動化）
npx expo install jest-expo @testing-library/react-native @testing-library/jest-native
```

```json
// package.json
{
  "jest": {
    "preset": "jest-expo",
    "setupFilesAfterFramework": ["@testing-library/jest-native/extend-expect"],
    "transformIgnorePatterns": [
      "node_modules/(?!((jest-)?react-native|@react-native|expo|@expo|@unimodules|react-native-reanimated)/)"
    ]
  }
}
```

### カスタムフックのテスト

```typescript
// hooks/__tests__/useIndustry.test.ts
import { renderHook, act } from '@testing-library/react-native';
import { useIndustryStore } from '../useIndustryStore';

describe('useIndustryStore', () => {
  beforeEach(() => {
    useIndustryStore.setState({ industry: null });
  });

  it('業種を設定できる', () => {
    const { result } = renderHook(() => useIndustryStore());
    act(() => {
      result.current.setIndustry('construction');
    });
    expect(result.current.industry).toBe('construction');
  });

  it('業種をリセットできる', () => {
    const { result } = renderHook(() => useIndustryStore());
    act(() => {
      result.current.setIndustry('fishery');
      result.current.resetIndustry();
    });
    expect(result.current.industry).toBeNull();
  });
});
```

### コンポーネントテスト

```tsx
// components/__tests__/ChatBubble.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { ChatBubble } from '../ChatBubble';

describe('ChatBubble', () => {
  const userMessage = { role: 'user' as const, content: 'テスト質問', id: '1' };
  const aiMessage = { role: 'assistant' as const, content: 'テスト回答', id: '2' };

  it('ユーザーメッセージが右側に表示される', () => {
    render(<ChatBubble message={userMessage} />);
    const bubble = screen.getByTestId('chat-bubble');
    expect(bubble).toHaveStyle({ alignSelf: 'flex-end' });
  });

  it('AIメッセージが左側に表示される', () => {
    render(<ChatBubble message={aiMessage} />);
    const bubble = screen.getByTestId('chat-bubble');
    expect(bubble).toHaveStyle({ alignSelf: 'flex-start' });
  });

  it('長押しでコピーメニューが表示される', () => {
    const onLongPress = jest.fn();
    render(<ChatBubble message={aiMessage} onLongPress={onLongPress} />);
    fireEvent.longPress(screen.getByTestId('chat-bubble'));
    expect(onLongPress).toHaveBeenCalledTimes(1);
  });
});
```

### API モック（MSW）

```typescript
// __mocks__/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('/api/chat', async ({ request }) => {
    const { message } = await request.json();
    return HttpResponse.json({
      content: `「${message}」についてのAI回答です`,
      usage: { tokens: 50 },
    });
  }),
];

// __mocks__/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';
export const server = setupServer(...handlers);
```

### Maestro E2E テスト

```yaml
# maestro/flows/chat_flow.yaml
appId: com.emportai.app
---
- launchApp
- tapOn: "建設業"        # 業種選択
- tapOn: "AIに相談する"
- inputText: "資金繰りが厳しいです"
- tapOn:
    id: "send-button"
- assertVisible:          # AIの回答が表示されるまで待つ
    text: ".*回答.*"
    timeout: 10000
- takeScreenshot: chat_response
```

### テストカバレッジ目標（2026年推奨）

| 層 | 目標カバレッジ | ツール |
|----|---------------|--------|
| ユーティリティ関数 | 90%+ | Jest |
| カスタムフック | 85%+ | Jest + RNTL |
| コンポーネント | 70%+ | RNTL |
| E2E（クリティカルパス） | 主要フロー全て | Maestro |

### Emport AIへの応用
- チャット送信フロー・業種選択・サブスク課金の3フローは必ず E2E テスト
- Zustandストアのロジックは単体テストで100%カバー
- MSW でバックエンドAPIをモックし、ネットワーク不要なテスト環境を構築

---

## Round 19 — ASO・生体認証・OTA・オフライン・収益化・エラー監視・CI/CD
調査日時: 2026-05-15

---

## 110. App Store Optimization（ASO）完全ガイド

### 調査日時
2026-05-15

### 概要
ASOはApp Store・Google Playでの検索順位を上げ、ダウンロード数を有機的に増やす最適化施策。65%以上のアプリダウンロードはストア検索経由。ユーザー獲得コストを下げる最も費用対効果の高い施策。

### メタデータ最適化

| 要素 | iOS制限 | Google Play制限 | 重要度 |
|------|---------|----------------|--------|
| アプリタイトル | 30文字 | 50文字 | ★★★★★ |
| サブタイトル/短い説明 | 30文字 | 80文字 | ★★★★ |
| キーワードフィールド（iOS） | 100文字（非表示） | N/A | ★★★★ |
| 詳細説明 | 4000文字 | 4000文字 | ★★★ |
| スクリーンショット | 最大10枚 | 最大8枚 | ★★★★★ |

### Emport AI向けASO設計

```
【アプリタイトル案】
iOS:   "Emport AI - 中小企業AI経営アドバイザー"（29文字）
Play:  "Emport AI: 建設・製造業向けAI経営アシスタント"（25文字）

【iOSキーワード（100文字以内）】
AI,経営,中小企業,建設業,製造業,水産業,アドバイス,業務効率化,補助金,会計,経営相談

【スクリーンショット戦略（最初の3枚が最重要）】
1枚目: チャット画面 + "建設業30年の悩みをAIが即解決" キャプション
2枚目: 業種選択画面 + "あなたの業種に特化したAIアドバイザー" キャプション
3枚目: 料金表 + "月額980円・ChatGPTの3分の1" キャプション
```

### バンドルサイズ最適化（ASOにも影響）

```bash
# Atlas でバンドル分析（Expo SDK 53+）
npx expo export --platform android
npx react-native-bundle-visualizer

# tree-shaking で不要コード削除
# babel.config.js に "transform-remove-console" を production 時に追加

# 画像最適化
npx expo-optimize
# WebP変換で PNG比30-70%削減
```

### レーティング維持（4.0以上が必須）

```typescript
// 適切なタイミングでレビュー依頼（expo-store-review）
import * as StoreReview from 'expo-store-review';

const requestReview = async () => {
  if (await StoreReview.isAvailableAsync()) {
    // 良い体験の直後に依頼（AI回答完了後、3回目の使用時など）
    await StoreReview.requestReview();
  }
};

// 条件: 3回以上使用、5日以上経過、直近でエラーなし
const shouldRequestReview = sessionCount >= 3 && daysSinceInstall >= 5 && !recentError;
if (shouldRequestReview) requestReview();
```

### 更新頻度（上位アプリは月1-4回更新）
- バグ修正: 即時リリース（EAS OTA更新で対応）
- 機能追加: 2-4週に1回
- リリースノートに「ユーザーの声から改善」を明記してレーティング上昇を狙う

### Emport AIへの応用
- リリース前にASO設計を完了させる（後付けは効果半減）
- 日本語キーワードの競合調査: AppFollow・Sensor Tower（無料枠）を使用
- 初期レビュー: 最初の20件のレビューがアルゴリズム的に特に重要

---

## 111. 生体認証・セキュアストレージ（expo-local-authentication + expo-secure-store）

### 調査日時
2026-05-15

### 概要
expo-local-authentication で Face ID・Touch ID・指紋認証を実装し、expo-secure-store で機密データ（JWTトークン、APIキーなど）をOS管理の暗号化ストレージに保存する。KeyChain（iOS）・EncryptedSharedPreferences（Android）を利用するため、アプリが解析されても平文は取得できない。

### インストール

```bash
npx expo install expo-local-authentication expo-secure-store
```

### 生体認証実装

```typescript
// hooks/useBiometricAuth.ts
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'auth_token';
const BIOMETRIC_ENABLED_KEY = 'biometric_enabled';

export function useBiometricAuth() {
  // 生体認証の利用可能確認
  const checkBiometricSupport = async () => {
    const compatible = await LocalAuthentication.hasHardwareAsync();
    const enrolled = await LocalAuthentication.isEnrolledAsync();
    const level = await LocalAuthentication.getEnrolledLevelAsync();
    // level: NONE=0, WEAK=1 (顔認証など), STRONG=2 (指紋・Face ID)
    return { compatible, enrolled, isStrong: level === LocalAuthentication.SecurityLevel.STRONG };
  };

  // 生体認証でトークンを取得
  const authenticateWithBiometric = async (): Promise<string | null> => {
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'Emport AIにログイン',
      fallbackLabel: 'パスワードを使用',
      cancelLabel: 'キャンセル',
      disableDeviceFallback: false, // Falseでデバイスパスコードへフォールバック
    });

    if (!result.success) return null;

    // 認証成功後にセキュアストレージからトークン取得
    return await SecureStore.getItemAsync(TOKEN_KEY);
  };

  // ログイン後にトークンを安全に保存
  const saveTokenSecurely = async (token: string) => {
    await SecureStore.setItemAsync(TOKEN_KEY, token, {
      keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    });
    await SecureStore.setItemAsync(BIOMETRIC_ENABLED_KEY, 'true');
  };

  // ログアウト時にクリア
  const clearSecureData = async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(BIOMETRIC_ENABLED_KEY);
  };

  return { checkBiometricSupport, authenticateWithBiometric, saveTokenSecurely, clearSecureData };
}
```

### セキュアストレージ アクセスレベル

| オプション | タイミング | 用途 |
|-----------|-----------|------|
| WHEN_UNLOCKED | デバイスロック解除時 | デフォルト。一般的なトークン |
| WHEN_UNLOCKED_THIS_DEVICE_ONLY | 同上+このデバイスのみ | バックアップ不可。機密データ |
| AFTER_FIRST_UNLOCK | 再起動後1回解除後 | バックグラウンド処理が必要なデータ |
| ALWAYS | 常時 | 非推奨（ロック中もアクセス可能） |

### 生体認証フロー（UI）

```tsx
// screens/BiometricLoginScreen.tsx
export function BiometricLoginScreen() {
  const { checkBiometricSupport, authenticateWithBiometric } = useBiometricAuth();
  const [supportInfo, setSupportInfo] = useState<any>(null);

  useEffect(() => {
    checkBiometricSupport().then(setSupportInfo);
  }, []);

  const handleBiometricLogin = async () => {
    const token = await authenticateWithBiometric();
    if (token) {
      // Zustandストアにトークンをセット
      useAuthStore.getState().login(token);
      router.replace('/(tabs)');
    } else {
      Alert.alert('認証失敗', 'パスワードでログインしてください');
    }
  };

  if (!supportInfo?.enrolled) {
    // 生体認証未設定 → 通常ログイン画面へ
    return <LoginForm />;
  }

  return (
    <TouchableOpacity onPress={handleBiometricLogin}>
      <Ionicons name={supportInfo.isStrong ? 'finger-print' : 'scan'} size={64} />
      <Text>Touch ID / Face IDでログイン</Text>
    </TouchableOpacity>
  );
}
```

### Emport AIへの応用
- 毎日使うアプリだからこそ生体認証で素早いログインを提供
- JWTトークンは必ずSecureStoreに保存（MMKV・AsyncStorageは暗号化なし）
- 生体認証オプトイン設定をプロフィール画面に追加

---

## 112. EAS Update — OTA戦略（段階的ロールアウト・自動ロールバック）

### 調査日時
2026-05-15

### 概要
EAS Update（Over-The-Air更新）は、App Store審査なしでJavaScriptバンドルとアセットを即座に更新できる仕組み。Expo SDK 55（2026年2月）ではHermesバイトコード差分で更新ファイルサイズが大幅縮小。Microsoft App Center（旧CodePush）は2025年3月終了。

### チャネル戦略

```
main branch → preview チャネル（内部テスト）
      ↓
release branch → production チャネル（段階的ロールアウト）
```

```bash
# チャネルの作成
eas channel:create preview
eas channel:create production

# アップデート公開（全ユーザーへ）
eas update --channel production --message "AIレスポンス速度改善"

# 段階的ロールアウト（最初は10%のユーザーへ）
eas update --channel production --rollout-percentage 10

# ロールアウト拡大
eas update:roll-out --channel production --id UPDATE_ID --percentage 50
eas update:roll-out --channel production --id UPDATE_ID --percentage 100

# 即時ロールバック
eas update --channel production --republish --group PREVIOUS_GROUP_ID
```

### アプリ内更新チェック

```typescript
// hooks/useOTAUpdate.ts
import * as Updates from 'expo-updates';

export function useOTAUpdate() {
  const checkAndApplyUpdate = async () => {
    if (__DEV__) return; // 開発中はスキップ

    try {
      const update = await Updates.checkForUpdateAsync();
      if (update.isAvailable) {
        await Updates.fetchUpdateAsync();
        // ユーザーに確認してから再起動（UXに配慮）
        Alert.alert(
          'アップデートあり',
          'アプリを最新版に更新しますか？',
          [
            { text: 'あとで', style: 'cancel' },
            { text: '今すぐ更新', onPress: () => Updates.reloadAsync() },
          ]
        );
      }
    } catch (error) {
      // ネットワークエラー等は無視（アップデートなしで続行）
      console.warn('OTA check failed:', error);
    }
  };

  return { checkAndApplyUpdate };
}

// _layout.tsx で起動時に確認
useEffect(() => {
  checkAndApplyUpdate();
}, []);
```

### Fingerprint（ネイティブ変更検出）

```bash
# JS変更かネイティブ変更かを自動判定
npx expo-updates fingerprint:compare --platform ios

# OTAで済むか、フルビルドが必要かを判定
# → expo-modules-core, native依存の変更はOTA不可
```

### ネイティブ変更が必要なケース（OTA不可）
- 新しいExpoプラグインの追加
- ネイティブモジュール（expo-camera等）の新規導入
- `app.json`のpermissions変更
- iOS Info.plist / Android AndroidManifest.xml の変更

### Emport AIへの応用
- AI回答品質改善・UI調整はOTAで即座に反映（審査不要）
- 本番リリースは常に10%→50%→100%の3段階ロールアウト
- クラッシュ率が前版比1.5倍超えたら即ロールバック

---

## 113. オフラインファースト + 同期キュー + 競合解決

### 調査日時
2026-05-15

### 概要
オフライン対応はSaaS系アプリの競合差別化要因。地方の中小企業ユーザーは電波が不安定な環境（現場・山間部）でも使うため、Emport AIはオフラインでも操作できる設計が重要。

### 基本構成

```
ユーザー操作 → SQLite（ローカル）→ 同期キュー → バックエンド
                ↑                              ↓
             useLiveQuery                  競合解決
```

### 同期キュー実装

```typescript
// services/syncQueue.ts
import * as SQLite from 'expo-sqlite';

interface SyncOperation {
  id: string;
  type: 'create' | 'update' | 'delete';
  resource: string;
  payload: Record<string, unknown>;
  timestamp: number;
  retryCount: number;
  status: 'pending' | 'syncing' | 'failed';
}

const db = SQLite.openDatabaseSync('emport.db');

// キューに追加（オフライン時でも即座に返す）
export function enqueue(operation: Omit<SyncOperation, 'id' | 'retryCount' | 'status'>) {
  const id = crypto.randomUUID();
  db.runSync(
    `INSERT INTO sync_queue VALUES (?, ?, ?, ?, ?, 0, 'pending')`,
    [id, operation.type, operation.resource, JSON.stringify(operation.payload), operation.timestamp]
  );
  return id;
}

// バックエンドと同期（バックグラウンドタスクから呼ぶ）
export async function flushQueue() {
  const pending = db.getAllSync<SyncOperation>(
    `SELECT * FROM sync_queue WHERE status='pending' ORDER BY timestamp ASC LIMIT 50`
  );

  for (const op of pending) {
    try {
      db.runSync(`UPDATE sync_queue SET status='syncing' WHERE id=?`, [op.id]);
      await api.sync(op.type, op.resource, op.payload);
      db.runSync(`DELETE FROM sync_queue WHERE id=?`, [op.id]);
    } catch (error) {
      const newRetry = op.retryCount + 1;
      if (newRetry >= 5) {
        db.runSync(`UPDATE sync_queue SET status='failed', retryCount=? WHERE id=?`, [newRetry, op.id]);
      } else {
        // 指数バックオフ: 1, 2, 4, 8, 16分
        db.runSync(`UPDATE sync_queue SET status='pending', retryCount=? WHERE id=?`, [newRetry, op.id]);
      }
    }
  }
}
```

### 競合解決戦略

```typescript
// 競合解決ポリシー
type ConflictPolicy = 'local_wins' | 'remote_wins' | 'latest_wins' | 'merge';

const resolveConflict = (local: Record<string, unknown>, remote: Record<string, unknown>, policy: ConflictPolicy) => {
  switch (policy) {
    case 'latest_wins':
      // タイムスタンプが新しい方が勝つ
      return (local.updatedAt as number) > (remote.updatedAt as number) ? local : remote;
    case 'merge':
      // フィールドレベルのマージ（最後に更新されたフィールドが勝つ）
      return { ...remote, ...local };
    case 'remote_wins':
      return remote;
    case 'local_wins':
    default:
      return local;
  }
};
```

### ネットワーク状態監視

```typescript
import NetInfo from '@react-native-community/netinfo';
import { useEffect } from 'react';

export function useNetworkSync() {
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      if (state.isConnected && state.isInternetReachable) {
        // オンライン復帰 → キューをフラッシュ
        flushQueue().catch(console.warn);
      }
    });
    return unsubscribe;
  }, []);
}
```

### Emport AIへの応用
- チャット履歴・業種設定はオフラインでも閲覧・入力可能にする
- AIへの質問はキューに入れ、オンライン時に自動送信
- 同期状態をUI上部に「同期中...」「同期完了」で表示（不安感を減らす）

---

## 114. アプリ収益化戦略（2026年版）

### 調査日時
2026-05-15

### 概要
2026年のモバイル収益化はハイブリッドモデルが主流（60%以上のトップアプリが複数モデルを組み合わせ）。サブスクリプション市場は2025年に1,200億ドルを達成し、IAP市場は2,570億ドル規模に成長。

### 収益モデル比較

| モデル | 変換率 | ARPU（月） | 向いているアプリ |
|--------|--------|-----------|----------------|
| フリーミアム | 2-5% | $5-15 | ユーティリティ、B2B |
| サブスク（トライアル付き） | 10-30% | $10-30 | プレミアムツール |
| IAP（消費型） | 2-10% | 不定 | ゲーム、コンテンツ |
| 広告 | - | $1-3 | 高頻度・無料アプリ |

### Emport AIの推奨モデル（ハイブリッド）

```
【フェーズ1: 初期（0-6ヶ月）】
全機能無料 → ユーザー獲得最優先

【フェーズ2: 収益化開始（6ヶ月〜）】
Free tier: 月10回のAI質問
Premium: 月額980円（無制限 + 業種特化プロンプト + 履歴保存無制限）

【フェーズ3: B2B展開（1年〜）】
法人プラン: 月額3,000-15,000円/社（複数アカウント + 管理画面 + API）
```

### RevenueCat実装（サブスク管理）

```typescript
// services/revenue.ts
import Purchases, { PurchasesPackage } from 'react-native-purchases';

const PREMIUM_ENTITLEMENT = 'premium';

export async function initRevenueCat() {
  Purchases.configure({
    apiKey: Platform.OS === 'ios'
      ? process.env.EXPO_PUBLIC_RC_IOS_KEY!
      : process.env.EXPO_PUBLIC_RC_ANDROID_KEY!,
  });
}

// プレミアムステータス確認
export async function isPremiumUser(): Promise<boolean> {
  const info = await Purchases.getCustomerInfo();
  return info.entitlements.active[PREMIUM_ENTITLEMENT] !== undefined;
}

// サブスクリプション購入
export async function purchasePremium(pkg: PurchasesPackage): Promise<boolean> {
  try {
    const { customerInfo } = await Purchases.purchasePackage(pkg);
    return customerInfo.entitlements.active[PREMIUM_ENTITLEMENT] !== undefined;
  } catch (error: any) {
    if (error.userCancelled) return false;
    throw error;
  }
}

// ペイウォール表示（いつどこに表示するかが最重要）
// 最適タイミング: 10回目の質問後、またはエクスポート機能タップ時
```

### 価値の壁（ペイウォール設計）

```tsx
// components/PaywallGate.tsx
export function PaywallGate({ children, feature }: { children: ReactNode; feature: string }) {
  const { isPremium } = useSubscription();

  if (isPremium) return <>{children}</>;

  return (
    <>
      {children}
      <BlurView intensity={20} style={StyleSheet.absoluteFillObject}>
        <View style={styles.overlay}>
          <Text style={styles.title}>プレミアム機能</Text>
          <Text style={styles.subtitle}>{feature}を使うには月額980円のプランが必要です</Text>
          <TouchableOpacity onPress={() => router.push('/paywall')} style={styles.button}>
            <Text>7日間無料トライアルを始める</Text>
          </TouchableOpacity>
        </View>
      </BlurView>
    </>
  );
}
```

### Emport AIへの応用
- 初期は「10回/月無料」でハードルを下げ、使用実感を作ってから課金
- 980円はChatGPTの1/3価格 → 価格比較を前面に出す
- 7日間無料トライアルで変換率10-30%を狙う

---

## 115. Sentry — エラー監視・クラッシュ報告

### 調査日時
2026-05-15

### 概要
Sentryはリアルタイムのクラッシュレポート・エラートラッキング・パフォーマンス監視を提供。EAS Buildとネイティブに統合され、ソースマップのアップロードで難読化されたスタックトレースを人間が読める形に変換できる。

### インストール・設定

```bash
npx expo install @sentry/react-native
npx @sentry/react-native/sentry-wizard -i reactNative -p ios android
```

```json
// app.json
{
  "expo": {
    "plugins": [
      [
        "@sentry/react-native/expo",
        {
          "url": "https://sentry.io/",
          "project": "emport-ai",
          "organization": "emport-ai-org"
        }
      ]
    ]
  }
}
```

### 初期化

```typescript
// app/_layout.tsx
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  environment: __DEV__ ? 'development' : 'production',
  // パフォーマンス監視
  tracesSampleRate: __DEV__ ? 1.0 : 0.2,
  // セッションリプレイ（クラッシュ前の操作を記録）
  replaysSessionSampleRate: 0.05,
  replaysOnErrorSampleRate: 1.0,
  // PII保護（個人情報をマスク）
  sendDefaultPii: false,
  beforeSend(event) {
    // 機密情報をフィルタリング
    if (event.user) {
      delete event.user.email;
    }
    return event;
  },
});

export default Sentry.wrap(function RootLayout() {
  return <Stack />;
});
```

### エラー境界（React Error Boundary）

```tsx
// components/ErrorBoundary.tsx
import * as Sentry from '@sentry/react-native';

export const ErrorBoundary = Sentry.withErrorBoundary(
  function FallbackScreen({ error, resetError }: { error: Error; resetError: () => void }) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>エラーが発生しました</Text>
        <Text style={styles.message}>{error.message}</Text>
        <TouchableOpacity onPress={resetError} style={styles.button}>
          <Text>再試行</Text>
        </TouchableOpacity>
      </View>
    );
  },
  { showDialog: false }
);
```

### カスタムエラーキャプチャ

```typescript
// AI API エラーをSentryに記録
const sendMessage = async (text: string) => {
  try {
    return await api.chat(text);
  } catch (error) {
    Sentry.captureException(error, {
      tags: { feature: 'ai-chat', industry: selectedIndustry },
      extra: { messageLength: text.length },
      level: 'error',
    });
    throw error;
  }
};

// ユーザーコンテキスト（クラッシュ時にユーザーIDと紐付け）
Sentry.setUser({ id: userId });

// パフォーマンストランザクション
const transaction = Sentry.startTransaction({ name: 'AI Chat Response' });
const aiResponse = await api.chat(message);
transaction.finish();
```

### EAS Secrets（本番環境の認証情報管理）

```bash
# EASシークレットに設定（.envには書かない）
eas secret:create --scope project --name SENTRY_AUTH_TOKEN --value sentry_token_here
eas secret:create --scope project --name EXPO_PUBLIC_SENTRY_DSN --value dsn_here
```

### Emport AIへの応用
- リリース前にSentryを必ず設定（後から追加は手間が増える）
- AIストリーミングのエラー率を監視（目標: 0.1%以下）
- クラッシュフリーセッション率95%以上を維持目標

---

## 116. CI/CD — GitHub Actions + EAS Build 自動化

### 調査日時
2026-05-15

### 概要
GitHub ActionsとEAS Buildを連携し、プッシュ→テスト→ビルド→配布の全パイプラインを自動化する。EAS Workflows（2026年）はReact Native専用CI/CDソリューションとして成熟し、従来のGitHub Actionsより設定が大幅に簡略化された。

### GitHub Actions ワークフロー

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # 1. テスト・型チェック
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm test -- --coverage --watchAll=false
      - run: npm run lint

  # 2. EAS Build (本番リリース)
  build-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm ci
      - run: eas build --platform all --non-interactive --auto-submit

  # 3. OTA Update (developブランチ → preview チャネル)
  ota-preview:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm ci
      - run: eas update --channel preview --message "Preview: ${{ github.sha }}"
```

### EAS Workflows（eas.json）

```json
// eas.json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "channel": "preview"
    },
    "production": {
      "channel": "production",
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "tsubeyou081@gmail.com",
        "ascAppId": "APP_STORE_APP_ID"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "production"
      }
    }
  }
}
```

### 必要なGitHub Secrets

```bash
# EAS認証トークン（expo.dev → Settings → Access Tokens）
EXPO_TOKEN=your_expo_token

# Sentry（ソースマップ自動アップロード）
SENTRY_AUTH_TOKEN=your_sentry_token

# Apple Developer / Google Play（EAS Submit用）
# → eas.json の submit セクションで設定（EASシークレット経由）
```

### ブランチ戦略

```
feature/* → develop → [OTA preview更新] → 内部テスト
develop   → main    → [EAS Build + App Store提出] → 本番
```

### Emport AIへの応用
- `main`ブランチへのマージ = 自動的にApp Store提出（週1回リリースサイクル）
- `develop`への日常的なコミット = OTA preview更新（チーム内テスト）
- テスト失敗・型エラー時はビルドをブロック（品質ゲート）

---

## Round 20 — ナビゲーション高度パターン・画像最適化・デザインシステム・スケルトン・ハプティクス・オンボーディング
調査日時: 2026-05-15

---

## 117. Expo Router v4 高度なナビゲーションパターン

### 調査日時
2026-05-15

### 概要
Expo Router v4 はファイルシステムベースのルーティングが進化し、型付きルート・ネストレイアウト・共有ルート・モーダルパターンが標準化。React Navigation を内部エンジンとして使いながら、ファイル構造だけで複雑なナビゲーションを表現できる。

### ファイル構造と対応するナビゲーション

```
app/
├── _layout.tsx           # ルートレイアウト（Provider類）
├── (auth)/               # ルートグループ（URLに影響しない）
│   ├── _layout.tsx       # 認証なしユーザー向けスタック
│   ├── login.tsx         # /login
│   └── register.tsx      # /register
├── (tabs)/               # タブナビゲーション
│   ├── _layout.tsx       # Tabs定義
│   ├── index.tsx         # /(tabs)/  → タブ1: ホーム
│   ├── chat.tsx          # /(tabs)/chat → タブ2: チャット
│   ├── history.tsx       # /(tabs)/history → タブ3: 履歴
│   └── profile.tsx       # /(tabs)/profile → タブ4: プロフィール
├── chat/
│   └── [sessionId].tsx   # /chat/12345 (動的ルート)
└── +not-found.tsx        # 404画面
```

### 型付きルート（TypeScript自動生成）

```typescript
// expo-router の型付きルートを有効化（app.json）
// { "expo": { "experiments": { "typedRoutes": true } } }

// 型安全なナビゲーション
import { router, Link } from 'expo-router';

// ✅ 型チェックあり - 存在しないルートはコンパイルエラー
router.push('/chat/12345');
router.push({ pathname: '/chat/[sessionId]', params: { sessionId: '12345' } });

// ✅ Link コンポーネントも型付き
<Link href="/chat/12345">チャット開く</Link>
<Link href={{ pathname: '/chat/[sessionId]', params: { sessionId: id } }}>開く</Link>

// パラメータの型安全な取得
import { useLocalSearchParams } from 'expo-router';
const { sessionId } = useLocalSearchParams<{ sessionId: string }>();
```

### 認証ガード（route guard）

```tsx
// app/(tabs)/_layout.tsx
import { useAuthStore } from '@/stores/authStore';
import { Redirect } from 'expo-router';

export default function TabLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  // 未認証 → ログイン画面へリダイレクト
  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#1428C8' }}>
      <Tabs.Screen name="index" options={{ title: 'ホーム' }} />
      <Tabs.Screen name="chat" options={{ title: 'AIチャット' }} />
      <Tabs.Screen name="history" options={{ title: '履歴' }} />
      <Tabs.Screen name="profile" options={{ title: 'プロフィール' }} />
    </Tabs>
  );
}
```

### モーダルパターン

```tsx
// app/paywall.tsx - モーダルとして表示
import { router } from 'expo-router';

// _layout.tsx で presentation="modal" を指定
// <Stack.Screen name="paywall" options={{ presentation: 'modal' }} />

export default function PaywallModal() {
  return (
    <View>
      <Text>プレミアムプラン</Text>
      <TouchableOpacity onPress={() => router.back()}>
        <Text>閉じる</Text>
      </TouchableOpacity>
    </View>
  );
}

// 任意の画面からモーダルを開く
router.push('/paywall');
```

### ネスト内部からの上位ナビゲーション

```typescript
// タブ内スタック → タブレベルのナビゲーションにアクセス
import { useNavigation } from 'expo-router';

// セカンダリ引数でレイアウトルートを指定
const tabsNav = useNavigation('/(tabs)');
```

### Emport AIへの応用
- `(auth)` グループでログイン前後を完全分離
- `chat/[sessionId]` でAI会話の共有URLを生成
- `paywall` をモーダルで表示 → コンテキストを維持したままペイウォール表示

---

## 118. 画像最適化（expo-image）

### 調査日時
2026-05-15

### 概要
expo-image は React Native 標準の `<Image>` の完全な代替。Glide（Android）・SDWebImage（iOS）ベースのネイティブキャッシュ、BlurHash/ThumbHash プレースホルダー、WebP自動変換、遅延ロードをサポート。2026年はこれがデファクトスタンダード。

### インストール

```bash
npx expo install expo-image
```

### 基本使用法

```tsx
import { Image } from 'expo-image';

// シンプルな使用
<Image
  source="https://example.com/photo.jpg"
  style={{ width: 200, height: 200 }}
  contentFit="cover"
  transition={300}       // フェードイン（ミリ秒）
  placeholder={{ blurhash: 'L6PZfSi_.AyE_3t7t7R**0o#DgR4' }}
/>

// 優先度制御
<Image
  source={heroImageUrl}
  priority="high"        // 'low' | 'normal' | 'high'
  contentFit="cover"
  style={styles.hero}
/>
```

### BlurHash プレースホルダー

```typescript
// BlurHashの生成（バックエンド側で事前計算して保存）
// npm install blurhash (サーバーサイド)
import { encode } from 'blurhash';

// 画像アップロード時にBlurHashを計算して DBに保存
const blurhash = encode(pixels, width, height, 4, 4);
// → "L6PZfSi_.AyE_3t7t7R**0o#DgR4"

// アプリ側：APIレスポンスにblurhashを含める
// { url: "...", blurhash: "L6PZfSi_..." }
```

### 事前キャッシュ（プリロード）

```typescript
import { Image } from 'expo-image';

// アプリ起動時に重要な画像をプリロード
const prefetchImages = async () => {
  await Image.prefetch([
    'https://cdn.emport-ai.com/icons/construction.webp',
    'https://cdn.emport-ai.com/icons/fishery.webp',
    'https://cdn.emport-ai.com/icons/retail.webp',
  ]);
};

// キャッシュクリア（必要時）
await Image.clearMemoryCache();
await Image.clearDiskCache();
```

### Expo Optimize（バンドル内画像圧縮）

```bash
# 全画像を自動最適化（PNG → WebP変換）
npx expo-optimize

# 品質調整（デフォルト80%）
npx expo-optimize --quality 85
```

### 最適化チェックリスト

| 対策 | 効果 |
|------|------|
| WebP使用 | PNG比25-35%サイズ削減 |
| BlurHash placeholder | レイアウトシフト防止、UX改善 |
| priority="high" （ヒーロー画像） | LCP最適化 |
| prefetch（よく使う画像） | 次画面表示を高速化 |
| CDNリサイズ（URLパラメータ） | デバイスサイズに合わせた配信 |

### Emport AIへの応用
- 業種アイコン（建設・水産・製造）はプリロードしてタブ切替を瞬時に
- ユーザーアバターに BlurHash プレースホルダーで読み込み待ちのガタつき防止
- `contentFit="contain"` でアスペクト比を保った画像表示

---

## 119. デザインシステム（NativeWind v4 + デザイントークン + ダークモード）

### 調査日時
2026-05-15

### 概要
NativeWind v4はCSSカスタムプロパティ（CSS変数）によるデザイントークンをサポートし、ダークモード・ライトモードの切替がゼロコード追加で実現できる。Emport AIのブランドカラーをトークンとして定義し、全コンポーネントで一貫したデザインを維持する。

### セットアップ

```bash
npm install nativewind
npm install --save-dev tailwindcss
npx tailwindcss init
```

### デザイントークン定義

```css
/* global.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Emport AI ブランドカラー */
    --color-primary: 20 40 200;          /* #1428C8 */
    --color-primary-light: 100 120 255;
    --color-primary-dark: 10 20 120;

    /* セマンティックカラー（ライトモード） */
    --color-background: 255 255 255;
    --color-surface: 245 247 255;
    --color-text: 17 17 17;
    --color-text-secondary: 100 100 100;
    --color-border: 229 231 235;
    --color-success: 34 197 94;
    --color-error: 239 68 68;
  }

  .dark {
    /* ダークモード */
    --color-background: 15 15 20;
    --color-surface: 25 28 40;
    --color-text: 240 240 245;
    --color-text-secondary: 160 165 180;
    --color-border: 50 55 70;
  }
}
```

```javascript
// tailwind.config.js
module.exports = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        'primary-light': 'rgb(var(--color-primary-light) / <alpha-value>)',
        background: 'rgb(var(--color-background) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        'text-primary': 'rgb(var(--color-text) / <alpha-value>)',
        'text-secondary': 'rgb(var(--color-text-secondary) / <alpha-value>)',
        border: 'rgb(var(--color-border) / <alpha-value>)',
        success: 'rgb(var(--color-success) / <alpha-value>)',
        error: 'rgb(var(--color-error) / <alpha-value>)',
      },
    },
  },
};
```

### コンポーネントでの使用

```tsx
// components/ui/Button.tsx
import { TouchableOpacity, Text } from 'react-native';

interface ButtonProps {
  title: string;
  variant?: 'primary' | 'secondary' | 'ghost';
  onPress: () => void;
}

export function Button({ title, variant = 'primary', onPress }: ButtonProps) {
  const variants = {
    primary: 'bg-primary active:bg-primary-dark',
    secondary: 'bg-surface border border-border',
    ghost: 'bg-transparent',
  };

  const textVariants = {
    primary: 'text-white font-bold',
    secondary: 'text-text-primary font-medium',
    ghost: 'text-primary font-medium',
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      className={`px-6 py-3 rounded-xl ${variants[variant]}`}
    >
      <Text className={`text-center text-base ${textVariants[variant]}`}>
        {title}
      </Text>
    </TouchableOpacity>
  );
}
```

### ダークモード切替

```typescript
// hooks/useTheme.ts
import { useColorScheme } from 'nativewind';

export function useTheme() {
  const { colorScheme, setColorScheme, toggleColorScheme } = useColorScheme();

  return {
    isDark: colorScheme === 'dark',
    toggleTheme: toggleColorScheme,
    setTheme: setColorScheme,
  };
}

// _layout.tsx でシステムテーマに追従
const systemScheme = Appearance.getColorScheme();
setColorScheme(systemScheme ?? 'light');
```

### Emport AIへの応用
- ブランドカラー `#1428C8`（プライマリブルー）をトークン化して全体に一貫適用
- ダークモード対応で夜間使用ユーザーのUXを向上（ASO評価にもプラス）
- `Button`・`Card`・`Input` などの基本UIコンポーネントをシステム化

---

## 120. スケルトンローディング・シマーエフェクト

### 調査日時
2026-05-15

### 概要
スケルトンローダーはコンテンツが読み込まれる間に表示するシマー（光の流れる）プレースホルダー。YouTube・Twitter・Notionが採用するUXパターンで、ユーザーが「待たされている感」を軽減し、体感速度を改善する。

### 実装（Reanimated + LinearGradient）

```tsx
// components/ui/Skeleton.tsx
import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
  interpolateColor,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

interface SkeletonProps {
  width?: number | `${number}%`;
  height?: number;
  borderRadius?: number;
  style?: object;
}

export function Skeleton({ width = '100%', height = 20, borderRadius = 8, style }: SkeletonProps) {
  const translateX = useSharedValue(-1);

  useEffect(() => {
    translateX.value = withRepeat(
      withTiming(1, { duration: 1200 }),
      -1,  // 無限繰り返し
      false
    );
  }, []);

  const animStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value * 300 }],
  }));

  return (
    <View style={[{ width, height, borderRadius, overflow: 'hidden', backgroundColor: '#E5E7EB' }, style]}>
      <Animated.View style={[StyleSheet.absoluteFill, animStyle]}>
        <LinearGradient
          colors={['transparent', 'rgba(255,255,255,0.6)', 'transparent']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={StyleSheet.absoluteFill}
        />
      </Animated.View>
    </View>
  );
}
```

### チャット画面スケルトン

```tsx
// components/ChatMessageSkeleton.tsx
export function ChatMessageSkeleton() {
  return (
    <View style={{ padding: 16, gap: 12 }}>
      {/* AIメッセージのプレースホルダー */}
      <View style={{ flexDirection: 'row', gap: 10 }}>
        <Skeleton width={36} height={36} borderRadius={18} />  {/* アバター */}
        <View style={{ flex: 1, gap: 6 }}>
          <Skeleton width="80%" height={16} />
          <Skeleton width="60%" height={16} />
          <Skeleton width="45%" height={16} />
        </View>
      </View>

      {/* ユーザーメッセージのプレースホルダー */}
      <View style={{ alignItems: 'flex-end', gap: 6 }}>
        <Skeleton width="70%" height={16} />
        <Skeleton width="50%" height={16} />
      </View>
    </View>
  );
}

// チャット画面での使用
{isLoading ? (
  <>
    <ChatMessageSkeleton />
    <ChatMessageSkeleton />
    <ChatMessageSkeleton />
  </>
) : (
  <ChatList messages={messages} />
)}
```

### Emport AIへの応用
- AIの回答待ち（ストリーミング開始前）にスケルトン表示
- 履歴リスト読み込み中にカードスケルトン表示
- ダークモードでは `backgroundColor: '#2A2D3A'` に変更

---

## 121. ハプティクスフィードバック（expo-haptics）

### 調査日時
2026-05-15

### 概要
ハプティクス（触覚フィードバック）はユーザーの操作に対して物理的な振動で応答するUX技術。適切なハプティクスはアプリの「品質感」を大幅に向上させる。Appleのデザインガイドラインでは「インタラクションの確認・完了・警告」の3場面での使用を推奨。

### インストール

```bash
npx expo install expo-haptics
```

### フィードバック種別

```typescript
import * as Haptics from 'expo-haptics';

// ① Impact（物理的な衝突感）
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);   // 軽い
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);  // 中程度
await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);   // 重い

// ② Notification（システム通知レベル）
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success); // 成功
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning); // 警告
await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);   // エラー

// ③ Selection（軽い選択確認）
await Haptics.selectionAsync();
```

### useHaptic カスタムフック

```typescript
// hooks/useHaptic.ts
import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

type HapticType = 'light' | 'medium' | 'heavy' | 'success' | 'warning' | 'error' | 'selection';

export function useHaptic() {
  const trigger = async (type: HapticType) => {
    if (Platform.OS === 'web') return; // Webでは無効

    switch (type) {
      case 'light':
        return Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      case 'medium':
        return Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      case 'heavy':
        return Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
      case 'success':
        return Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      case 'warning':
        return Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      case 'error':
        return Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      case 'selection':
        return Haptics.selectionAsync();
    }
  };

  return { trigger };
}
```

### 適切な使用場面

```tsx
export function ChatSendButton({ onSend }: { onSend: () => void }) {
  const { trigger } = useHaptic();

  const handlePress = async () => {
    await trigger('light');     // ボタンタップ時
    onSend();
  };

  const handleSuccess = async () => {
    await trigger('success');   // AI回答受信完了
  };

  const handleError = async () => {
    await trigger('error');     // エラー発生時
  };
}

// 業種選択時（ピッカー的なUX）
const handleIndustrySelect = async (industry: string) => {
  await trigger('selection');  // 選択変更時
  setIndustry(industry);
};

// 長押しでコピー
const handleLongPress = async () => {
  await trigger('medium');     // 長押し確認
  Clipboard.setString(message.content);
};
```

### Emport AIへの応用
- 送信ボタンタップ: `light`（軽快な反応）
- AI回答完了: `success`（達成感を演出）
- エラー: `error`（問題があることを即座に伝える）
- 業種選択スクロール: `selection`（ピッカーUI感）

---

## 122. オンボーディング画面設計（2026年ベストプラクティス）

### 調査日時
2026-05-15

### 概要
インタラクティブなオンボーディングは7日後のリテンション率を50%改善し、ガイドツアーを完了したユーザーのコンバージョン率は2-3倍高い。2026年のトレンドは「静的なチュートリアル → パーソナライズされた対話型ガイダンス」への移行。

### Emport AI向けオンボーディングフロー

```
[スプラッシュ] → [ようこそ] → [業種選択] → [名前入力] → [最初のAI質問デモ] → [プラン選択(任意)] → [ホーム]
```

### 実装（Reanimated + FlatList）

```tsx
// app/(onboarding)/index.tsx
import { FlatList, View, Text, Dimensions } from 'react-native';
import Animated, { useSharedValue, useAnimatedScrollHandler, useAnimatedStyle, interpolate } from 'react-native-reanimated';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

const SLIDES = [
  {
    id: '1',
    title: 'AI経営アドバイザー',
    subtitle: '地方中小企業のためのAIアシスタント',
    emoji: '🤖',
    backgroundColor: '#1428C8',
  },
  {
    id: '2',
    title: 'あなたの業種に特化',
    subtitle: '建設・製造・水産・小売など
業種ごとに最適化されたAIが回答',
    emoji: '🏗️',
    backgroundColor: '#0D47A1',
  },
  {
    id: '3',
    title: '月額980円',
    subtitle: 'ChatGPTの3分の1の価格で
ビジネス特化AIを使い放題',
    emoji: '💰',
    backgroundColor: '#1565C0',
  },
];

export default function OnboardingScreen() {
  const scrollX = useSharedValue(0);
  const flatListRef = useRef<FlatList>(null);

  const scrollHandler = useAnimatedScrollHandler((event) => {
    scrollX.value = event.contentOffset.x;
  });

  const goToNext = (index: number) => {
    if (index < SLIDES.length - 1) {
      flatListRef.current?.scrollToIndex({ index: index + 1, animated: true });
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } else {
      // オンボーディング完了
      useOnboardingStore.getState().setCompleted(true);
      router.replace('/(tabs)');
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <Animated.FlatList
        ref={flatListRef}
        data={SLIDES}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onScroll={scrollHandler}
        scrollEventThrottle={16}
        renderItem={({ item, index }) => (
          <SlideItem slide={item} scrollX={scrollX} index={index} onNext={() => goToNext(index)} />
        )}
        keyExtractor={(item) => item.id}
      />
      <PaginationDots scrollX={scrollX} count={SLIDES.length} />
    </View>
  );
}
```

### 業種選択（パーソナライズ）

```tsx
// app/(onboarding)/industry.tsx
const INDUSTRIES = [
  { id: 'construction', label: '建設業', emoji: '🏗️' },
  { id: 'fishery', label: '水産業', emoji: '🐟' },
  { id: 'retail', label: '小売業', emoji: '🛒' },
  { id: 'manufacturing', label: '製造業', emoji: '🏭' },
  { id: 'hospitality', label: '旅館・宿泊業', emoji: '🏨' },
  { id: 'agriculture', label: '農業', emoji: '🌾' },
];

export default function IndustrySelectionScreen() {
  const [selected, setSelected] = useState<string | null>(null);

  const handleSelect = async (id: string) => {
    await Haptics.selectionAsync();
    setSelected(id);
  };

  return (
    <View style={{ flex: 1, padding: 24 }}>
      <Text className="text-2xl font-bold text-text-primary mb-2">業種を選択</Text>
      <Text className="text-text-secondary mb-6">あなたの業種に合わせてAIを最適化します</Text>

      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 12 }}>
        {INDUSTRIES.map((industry) => (
          <TouchableOpacity
            key={industry.id}
            onPress={() => handleSelect(industry.id)}
            style={[
              { padding: 16, borderRadius: 12, borderWidth: 2, minWidth: '45%' },
              selected === industry.id
                ? { borderColor: '#1428C8', backgroundColor: '#EEF0FF' }
                : { borderColor: '#E5E7EB', backgroundColor: '#F9FAFB' },
            ]}
          >
            <Text style={{ fontSize: 28 }}>{industry.emoji}</Text>
            <Text style={{ marginTop: 8, fontWeight: '600' }}>{industry.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Button
        title="次へ"
        onPress={() => {
          useProfileStore.getState().setIndustry(selected!);
          router.push('/(onboarding)/demo');
        }}
        style={{ marginTop: 'auto' }}
      />
    </View>
  );
}
```

### オンボーディング完了の永続化

```typescript
// stores/onboardingStore.ts（MMKV永続化）
const useOnboardingStore = create(persist(
  (set) => ({
    isCompleted: false,
    setCompleted: (v: boolean) => set({ isCompleted: v }),
  }),
  { name: 'onboarding', storage: createJSONStorage(() => mmkvStorage) }
));

// _layout.tsx で起動時チェック
const { isCompleted } = useOnboardingStore();
if (!isCompleted) {
  return <Redirect href="/(onboarding)" />;
}
```

### Emport AIへの応用
- 3スライド（価値提案）→ 業種選択 → デモチャット → ホーム の4ステップが最適
- 業種選択でパーソナライズ感を演出（ユーザーが「自分向け」と感じる）
- デモチャット（業種に合わせた質問例）で即座にAHAモーメントを提供

---

## 123. スプラッシュスクリーン・アプリアイコン（expo-splash-screen）

### 調査日時
2026-05-15

### 概要
スプラッシュスクリーンはアプリ起動時の第一印象。expo-splash-screen で初期化完了まで表示し、Reanimatedでスムーズなトランジションを実装する。アイコンとスプラッシュの一貫したブランドデザインがASO・ユーザー信頼度に影響する。

### 設定

```json
// app.json
{
  "expo": {
    "icon": "./assets/icon.png",          // 1024x1024 PNG
    "splash": {
      "image": "./assets/splash.png",     // 1284x2778 PNG（iPhone 15 Pro Max）
      "imageWidth": 200,
      "resizeMode": "contain",
      "backgroundColor": "#1428C8"        // ブランドカラー
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png", // 1024x1024
        "backgroundColor": "#1428C8"
      }
    }
  }
}
```

### カスタムアニメーション付きスプラッシュ

```tsx
// app/_layout.tsx
import * as SplashScreen from 'expo-splash-screen';
import Animated, { FadeOut } from 'react-native-reanimated';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [appReady, setAppReady] = useState(false);

  useEffect(() => {
    const prepare = async () => {
      try {
        // フォント・初期データ読み込み
        await Promise.all([
          Font.loadAsync({ 'NotoSansJP': require('./assets/fonts/NotoSansJP.ttf') }),
          initRevenueCat(),
          checkAuthStatus(),
        ]);
      } finally {
        setAppReady(true);
      }
    };
    prepare();
  }, []);

  const onLayoutRootView = useCallback(async () => {
    if (appReady) {
      await SplashScreen.hideAsync();
    }
  }, [appReady]);

  if (!appReady) return null;

  return (
    <Animated.View style={{ flex: 1 }} exiting={FadeOut.duration(300)} onLayout={onLayoutRootView}>
      <Stack />
    </Animated.View>
  );
}
```

### アイコン・スプラッシュデザイン原則

```
アイコン設計:
  - 1024x1024px の正方形
  - ブランドカラー（#1428C8）を背景に白いロゴマーク
  - 小サイズ（20x20px）でも識別できるシンプルさ
  - 角丸はOSが自動適用（指定不要）

スプラッシュ設計:
  - 中央にロゴのみ（テキスト不要 - 起動が速いため読む時間なし）
  - 背景色 = アイコン背景色（シームレスな起動体験）
  - iOS用: 1284x2778px、Android用: 1920x1080px
```

### Emport AIへの応用
- スプラッシュ色 `#1428C8` でブランドカラーを最初に刻む
- 起動時に RevenueCat 初期化・認証チェックをスプラッシュ中に実行
- フォント読み込みをスプラッシュ中に完了させてフォント切替フラッシュを防ぐ
