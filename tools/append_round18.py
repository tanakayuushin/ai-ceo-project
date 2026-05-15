# -*- coding: utf-8 -*-
"""Round 18: Sections 103-109 - Accessibility, i18n, Forms, Deep Linking, Performance, Push Notifications, Testing"""
import os

REPORT_PATH = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md"

CONTENT = """
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
"""

with open(REPORT_PATH, 'a', encoding='utf-8') as f:
    f.write(CONTENT)

print("Done: Round 18 sections 103-109 appended successfully")
