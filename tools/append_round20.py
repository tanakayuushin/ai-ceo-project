# -*- coding: utf-8 -*-
"""Round 20: Sections 117-123 - Navigation, Images, Design System, Skeleton, Haptics, Onboarding, Typed Routes"""
import os

REPORT_PATH = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md"

CONTENT = """
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
    subtitle: '建設・製造・水産・小売など\n業種ごとに最適化されたAIが回答',
    emoji: '🏗️',
    backgroundColor: '#0D47A1',
  },
  {
    id: '3',
    title: '月額980円',
    subtitle: 'ChatGPTの3分の1の価格で\nビジネス特化AIを使い放題',
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
"""

with open(REPORT_PATH, 'a', encoding='utf-8') as f:
    f.write(CONTENT)

print("Done: Round 20 sections 117-123 appended successfully")
