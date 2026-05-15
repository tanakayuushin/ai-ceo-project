# -*- coding: utf-8 -*-
content = r"""

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
"""

with open(r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md", "a", encoding="utf-8") as f:
    f.write(content)

print("Done: Round 16 sections 89-95 appended successfully")
