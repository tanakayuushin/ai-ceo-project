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
