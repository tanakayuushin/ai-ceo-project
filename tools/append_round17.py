# -*- coding: utf-8 -*-
content = r"""

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
"""

with open(r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md", "a", encoding="utf-8") as f:
    f.write(content)

print("Done: Round 17 sections 96-102 appended successfully")
