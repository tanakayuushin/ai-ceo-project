# -*- coding: utf-8 -*-
"""Round 19: Sections 110-116 - ASO, Biometric, OTA, Offline, Monetization, Sentry, CI/CD"""
import os

REPORT_PATH = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md"

CONTENT = """
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
"""

with open(REPORT_PATH, 'a', encoding='utf-8') as f:
    f.write(CONTENT)

print("Done: Round 19 sections 110-116 appended successfully")
