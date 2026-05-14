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
