# -*- coding: utf-8 -*-
content = r"""

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
"""

with open(r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md", "a", encoding="utf-8") as f:
    f.write(content)

print("Done: Round 15 sections 82-88 appended successfully")
