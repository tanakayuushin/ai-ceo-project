# -*- coding: utf-8 -*-
"""Round 22: Sections 131-137 - Lottie, Video/Audio, WebView, Skia, FileSystem, Storybook, Clipboard/Share"""
import os

REPORT_PATH = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md"

CONTENT = """
---

## Round 22 — Lottie・動画音声・WebView・Skia・ファイルシステム・Storybook・クリップボード共有
調査日時: 2026-05-15

---

## 131. Lottie アニメーション（lottie-react-native）

### 調査日時
2026-05-15

### 概要
Lottie は Adobe After Effects で作ったアニメーションを JSON ファイルとしてエクスポートし、ネイティブに再生するライブラリ。静的な画像より遥かにリッチなUXを低コストで実現できる。LottieFiles.com に無料素材が豊富にある。

### インストール

```bash
npx expo install lottie-react-native
```

### 基本使用法

```tsx
import LottieView from 'lottie-react-native';
import { useRef } from 'react';

// ① autoPlayとloopで常時再生
<LottieView
  source={require('../assets/animations/ai-thinking.json')}
  autoPlay
  loop
  style={{ width: 200, height: 200 }}
/>

// ② プログラム制御（送信完了アニメーションなど）
export function SuccessAnimation({ onFinish }: { onFinish: () => void }) {
  const animRef = useRef<LottieView>(null);

  useEffect(() => {
    animRef.current?.play();
  }, []);

  return (
    <LottieView
      ref={animRef}
      source={require('../assets/animations/success.json')}
      loop={false}
      onAnimationFinish={onFinish}
      style={{ width: 150, height: 150 }}
    />
  );
}
```

### dotLottie形式（2026年推奨）

```tsx
// @lottiefiles/dotlottie-react-native (新形式・ファイルサイズが小さい)
import { DotLottie } from '@lottiefiles/dotlottie-react-native';

<DotLottie
  source={require('../assets/animations/loading.lottie')}
  autoplay
  loop
  style={{ width: 200, height: 200 }}
/>
```

### Emport AIでの活用場面

| 場面 | アニメーション | 効果 |
|------|--------------|------|
| AI思考中 | ローディングスピナー | 待機時間の体感短縮 |
| 回答完了 | チェックマーク | 達成感・完了感 |
| エラー発生 | 警告アイコン | 即座の状況把握 |
| 空の履歴 | キャラクターアニメ | 空状態のUX改善 |
| オンボーディング | ストーリーアニメ | エンゲージメント向上 |

### LottieFilesからの素材調達

```
https://lottiefiles.com/search?q=AI+loading  # 無料素材検索
ダウンロード形式: .lottie (dotLottie) または .json (Lottie)
```

### Emport AIへの応用
- AI回答生成中は「AIが考えるアニメーション」（脳や星が光るLottie）を表示
- 初回ログイン成功時に「Welcome」アニメーションで感動的な体験を提供
- 空の履歴画面に「チャットを始めよう」キャラクターアニメで離脱防止

---

## 132. 動画・音声（expo-video + expo-audio）

### 調査日時
2026-05-15

### 概要
Expo SDK 55（2026年2月）で expo-av が廃止され、expo-video と expo-audio に分離。VideoPlayerとVideoViewを分けたアーキテクチャで、バックグラウンド再生・ピクチャーインピクチャーなど高度な機能をサポート。

### インストール

```bash
npx expo install expo-video expo-audio
```

### expo-video 実装

```tsx
import { useVideoPlayer, VideoView } from 'expo-video';
import { useRef } from 'react';

// プレイヤーロジックとビューを分離（新アーキテクチャ）
export function TutorialVideo({ uri }: { uri: string }) {
  const player = useVideoPlayer(uri, (p) => {
    p.loop = false;
    p.volume = 1.0;
    p.play(); // 自動再生
  });

  return (
    <VideoView
      player={player}
      style={{ width: '100%', height: 220, borderRadius: 12 }}
      allowsFullscreen
      allowsPictureInPicture   // iOS: PiP対応
      contentFit="contain"
    />
  );
}

// 再生制御（外部ボタンで操作）
const handlePlayPause = () => {
  if (player.playing) {
    player.pause();
  } else {
    player.play();
  }
};

// ストリーミングURL（HLS）
const player = useVideoPlayer('https://example.com/stream.m3u8', (p) => {
  p.play();
});
```

### expo-audio 実装（音声録音・再生）

```tsx
import { useAudioPlayer, useAudioRecorder, AudioModule } from 'expo-audio';

// 音声再生（AIの音声回答・BGMなど）
export function AudioPlayer({ uri }: { uri: string }) {
  const player = useAudioPlayer(uri);

  return (
    <TouchableOpacity onPress={() => player.playing ? player.pause() : player.play()}>
      <Ionicons name={player.playing ? 'pause' : 'play'} size={32} />
      <Text>{Math.round(player.currentTime)}s / {Math.round(player.duration)}s</Text>
    </TouchableOpacity>
  );
}

// 音声録音（将来機能: 音声でAI質問）
export function VoiceRecorder({ onRecorded }: { onRecorded: (uri: string) => void }) {
  const recorder = useAudioRecorder({ ios: { extension: '.m4a' }, android: { extension: '.3gp' } });

  const startRecording = async () => {
    await AudioModule.requestRecordingPermissionsAsync();
    recorder.record();
  };

  const stopRecording = async () => {
    const recording = await recorder.stop();
    if (recording?.uri) onRecorded(recording.uri);
  };

  return (
    <TouchableOpacity
      onPress={recorder.isRecording ? stopRecording : startRecording}
      style={recorder.isRecording ? styles.recording : styles.idle}
    >
      <Ionicons name={recorder.isRecording ? 'stop' : 'mic'} size={32} color="white" />
    </TouchableOpacity>
  );
}
```

### expo-av からの移行

| 旧 (expo-av) | 新 (expo-video / expo-audio) |
|-------------|------------------------------|
| `Video` コンポーネント | `VideoView` + `useVideoPlayer()` |
| `Audio.Sound.createAsync()` | `useAudioPlayer(uri)` |
| `Audio.Recording` | `useAudioRecorder()` |
| `AVPlaybackStatus` | `player.currentTime`, `player.duration` |

### Emport AIへの応用
- チュートリアル動画（アプリの使い方解説）の埋め込み
- 将来機能: 音声でAIに質問 → `useAudioRecorder` で録音 → Whisper APIでテキスト変換
- セミナー録画の再生機能（B2Bプランの付加価値）

---

## 133. WebView統合（react-native-webview + webview-bridge）

### 調査日時
2026-05-15

### 概要
react-native-webview でアプリ内にWebコンテンツを表示し、webview-bridge でネイティブとWebの双方向通信を型安全に実現。既存のWebサービス（freee・銀行Webページ等）をアプリ内に組み込む際に使用。

### インストール

```bash
npx expo install react-native-webview
npm install @webview-bridge/react-native @webview-bridge/web
```

### 基本WebView実装

```tsx
import { WebView } from 'react-native-webview';
import { useRef } from 'react';

export function BankWebView({ url }: { url: string }) {
  const webViewRef = useRef<WebView>(null);

  return (
    <WebView
      ref={webViewRef}
      source={{ uri: url }}
      style={{ flex: 1 }}
      // ネイティブからWebへメッセージ送信
      onMessage={(event) => {
        const data = JSON.parse(event.nativeEvent.data);
        console.log('Webから受信:', data);
      }}
      // JavaScriptを挿入（ページ読み込み後に実行）
      injectedJavaScriptBeforeContentLoaded={`
        window.isNativeApp = true;
        window.appVersion = '1.0.0';
        true; // 最後にtrueが必要
      `}
    />
  );
}

// WebからネイティブへメッセージをPostMessage（Web側のコード）
// window.ReactNativeWebView.postMessage(JSON.stringify({ action: 'login', userId: '123' }));

// ネイティブからWebへメッセージ送信
webViewRef.current?.injectJavaScript(`
  window.postMessage('{ "action": "updateTheme", "theme": "dark" }', '*');
  true;
`);
```

### 型安全な双方向通信（webview-bridge）

```typescript
// bridge/index.ts（ネイティブ・Web両方から参照する共有型定義）
import { createWebView } from '@webview-bridge/react-native';

export const { WebView, linkNativeMethod } = createWebView({
  bridge: {
    // ネイティブからWebへ提供するメソッド
    showToast: async (message: string) => {
      console.log('Toast:', message); // ネイティブ側の実装
    },
    getUserInfo: async () => {
      return { name: '田中悠清', industry: '建設業' };
    },
    // AIチャットをネイティブ処理に委譲
    sendAIMessage: async (message: string) => {
      return await api.chat(message);
    },
  },
});

// Web側（Webページ内のJS）
import { bridge } from '@webview-bridge/web';

await bridge.showToast('成功しました！');
const user = await bridge.getUserInfo(); // 型付き戻り値
const response = await bridge.sendAIMessage('質問です');
```

### Emport AIへの応用
- 補助金申請のWebフォーム（やまぐち産業振興財団）をアプリ内表示
- freee・弥生会計へのWebログイン
- 銀行のオンラインバンキング（アプリ内ブラウザとして）
- LP（ランディングページ）のアプリ内プレビュー

---

## 134. React Native Skia — GPUグラフィックス・カスタム描画

### 調査日時
2026-05-15

### 概要
@shopify/react-native-skia は Google Skia グラフィックスエンジンをReact Nativeに統合したライブラリ。GPU加速のCanvas描画で、カスタムチャート・ブラー効果・シェーダーアニメーション・画像フィルターを実装できる。Victory Native XLの内部エンジンとしても使用されている。

### インストール

```bash
npx expo install @shopify/react-native-skia
```

### 基本図形描画

```tsx
import { Canvas, Circle, Rect, Path, Text, useFont } from '@shopify/react-native-skia';

export function CustomGraphic() {
  const font = useFont(require('../assets/fonts/NotoSansJP.ttf'), 14);

  return (
    <Canvas style={{ width: 300, height: 200 }}>
      {/* 背景矩形 */}
      <Rect x={0} y={0} width={300} height={200} color="#EEF0FF" />

      {/* 円グラデーション */}
      <Circle cx={150} cy={100} r={80}>
        <RadialGradient
          c={{ x: 150, y: 100 }}
          r={80}
          colors={['#1428C8', '#7986CB']}
        />
      </Circle>

      {/* テキスト */}
      {font && (
        <Text x={100} y={110} font={font} text="Emport AI" color="white" />
      )}
    </Canvas>
  );
}
```

### ブラー効果（フロスト・ガラス効果）

```tsx
import { Canvas, Image, Blur, useImage, BackdropBlur } from '@shopify/react-native-skia';

export function FrostedGlassCard({ children }: { children: React.ReactNode }) {
  return (
    <View style={styles.container}>
      {children}
      <Canvas style={StyleSheet.absoluteFill}>
        <BackdropBlur blur={20} clip={styles.cardShape}>
          <Rect x={0} y={0} width={300} height={200} color="rgba(255,255,255,0.3)" />
        </BackdropBlur>
      </Canvas>
    </View>
  );
}
```

### Reanimatedとの統合（動くグラフィック）

```tsx
import { useSharedValue, withTiming } from 'react-native-reanimated';
import { Canvas, Circle, useAnimatedProps } from '@shopify/react-native-skia';

export function AnimatedRing({ progress }: { progress: SharedValue<number> }) {
  // SVGパスを計算して円弧を描画（進捗リング）
  const animatedProps = useAnimatedProps(() => {
    const angle = progress.value * 2 * Math.PI;
    return {
      // 円弧のパスをアニメーション
      start: 0,
      end: progress.value,
    };
  });

  return (
    <Canvas style={{ width: 100, height: 100 }}>
      <Arc
        x={10} y={10} width={80} height={80}
        startAngle={-90}
        sweepAngle={progress.value * 360}
        style="stroke"
        strokeWidth={8}
        color="#1428C8"
        animatedProps={animatedProps}
      />
    </Canvas>
  );
}
```

### 主要な使い道（2026年）

| 用途 | 技術 |
|------|------|
| カスタムチャート（Victory Native XL内部） | Path描画 + GPU描画 |
| 画像フィルター | ColorMatrix, Blur |
| グロー・ネオン効果 | BlurMaskFilter |
| カスタムアニメーション | Reanimated + Canvas |
| ゲーム的な演出 | Skia + Reanimated |

### Emport AIへの応用
- AI使用率の進捗リング（円形プログレスバー）
- プレミアム画面のグラスモーフィズム（フロストガラス）エフェクト
- ダッシュボードの美しいカスタムチャート（Victory Native XL経由）

---

## 135. ファイルシステム管理（expo-file-system）

### 調査日時
2026-05-15

### 概要
expo-file-system はデバイスのファイルシステムへのアクセスを提供。ファイルのダウンロード・アップロード・読み書き・ディレクトリ管理を行える。AIが生成したレポートのローカル保存やキャッシュ管理に活用する。

### インストール

```bash
npx expo install expo-file-system
```

### ファイルのダウンロード・保存

```typescript
// services/fileStorage.ts
import * as FileSystem from 'expo-file-system';

const REPORTS_DIR = FileSystem.documentDirectory + 'reports/';

// ディレクトリ初期化
export async function initStorageDir() {
  const dirInfo = await FileSystem.getInfoAsync(REPORTS_DIR);
  if (!dirInfo.exists) {
    await FileSystem.makeDirectoryAsync(REPORTS_DIR, { intermediates: true });
  }
}

// AI回答をテキストファイルとして保存
export async function saveReport(filename: string, content: string): Promise<string> {
  const filePath = REPORTS_DIR + filename;
  await FileSystem.writeAsStringAsync(filePath, content, {
    encoding: FileSystem.EncodingType.UTF8,
  });
  return filePath;
}

// 保存済みレポート一覧
export async function listReports(): Promise<string[]> {
  const files = await FileSystem.readDirectoryAsync(REPORTS_DIR);
  return files.filter((f) => f.endsWith('.txt') || f.endsWith('.json'));
}

// ファイル読み込み
export async function readReport(filename: string): Promise<string> {
  const filePath = REPORTS_DIR + filename;
  return FileSystem.readAsStringAsync(filePath, {
    encoding: FileSystem.EncodingType.UTF8,
  });
}

// ファイル削除
export async function deleteReport(filename: string) {
  const filePath = REPORTS_DIR + filename;
  await FileSystem.deleteAsync(filePath, { idempotent: true });
}
```

### URLからファイルをダウンロード（進捗表示付き）

```typescript
// 大きなファイルのダウンロード（進捗バー付き）
export async function downloadWithProgress(
  url: string,
  filename: string,
  onProgress: (progress: number) => void
): Promise<string> {
  const filePath = REPORTS_DIR + filename;

  const downloadResumable = FileSystem.createDownloadResumable(
    url,
    filePath,
    {},
    (downloadProgress) => {
      const progress = downloadProgress.totalBytesWritten / downloadProgress.totalBytesExpectedToWrite;
      onProgress(progress);
    }
  );

  const result = await downloadResumable.downloadAsync();
  return result?.uri ?? filePath;
}

// 中断・再開（ダウンロード再開機能）
const pauseDownload = await downloadResumable.pauseAsync();
const savedState = downloadResumable.savable(); // MMKVに保存

// 後で再開
const resumed = new FileSystem.DownloadResumable(
  savedState.url, savedState.fileUri, savedState.options,
  onProgress, savedState.resumeData
);
await resumed.resumeAsync();
```

### ファイルアップロード（バックエンドへ）

```typescript
// 音声ファイルをバックエンドにアップロード（Whisper API用など）
export async function uploadAudio(localUri: string): Promise<string> {
  const result = await FileSystem.uploadAsync(
    'https://api.emport-ai.com/transcribe',
    localUri,
    {
      httpMethod: 'POST',
      uploadType: FileSystem.FileSystemUploadType.MULTIPART,
      fieldName: 'audio',
      mimeType: 'audio/m4a',
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  const { transcription } = JSON.parse(result.body);
  return transcription;
}
```

### ストレージ容量管理

```typescript
// キャッシュサイズ確認・クリア
const cacheInfo = await FileSystem.getInfoAsync(FileSystem.cacheDirectory!);
console.log('キャッシュサイズ:', cacheInfo.size, 'bytes');

// 古いキャッシュを自動削除（30日以上前のファイル）
const files = await FileSystem.readDirectoryAsync(FileSystem.cacheDirectory!);
for (const file of files) {
  const info = await FileSystem.getInfoAsync(FileSystem.cacheDirectory + file, { md5: false });
  if (info.exists && info.modificationTime) {
    const ageInDays = (Date.now() / 1000 - info.modificationTime) / 86400;
    if (ageInDays > 30) {
      await FileSystem.deleteAsync(FileSystem.cacheDirectory + file, { idempotent: true });
    }
  }
}
```

### Emport AIへの応用
- AI回答レポートをローカルに保存してオフライン閲覧
- 音声録音ファイルの一時保存→バックエンドアップロード→削除
- ユーザーのキャッシュデータ管理（設定画面からキャッシュクリア）

---

## 136. Storybook for React Native — コンポーネント開発環境

### 調査日時
2026-05-15

### 概要
Storybook はUIコンポーネントを個別に開発・テスト・文書化するワークショップ。React Native版はデバイス上でストーリーを確認でき、デザイナーとの連携・コンポーネントの品質管理に効果的。

### インストール

```bash
npx storybook@latest init
# または Expo向け
npx expo install @storybook/react-native
```

### Storyファイルの作成

```tsx
// components/ui/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  args: {
    title: 'ボタン',
    onPress: () => console.log('pressed'),
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'ghost'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: { variant: 'primary', title: 'AIに質問する' },
};

export const Secondary: Story = {
  args: { variant: 'secondary', title: '後で確認する' },
};

export const Ghost: Story = {
  args: { variant: 'ghost', title: 'スキップ' },
};

// チャットバブルのストーリー
export const ChatBubble: Story = {
  render: () => (
    <View style={{ padding: 16 }}>
      <ChatBubble message={{ role: 'user', content: 'テスト質問', id: '1' }} />
      <ChatBubble message={{ role: 'assistant', content: 'テスト回答', id: '2' }} />
    </View>
  ),
};
```

### Storybook + Jest 連携（ポータブルストーリー）

```typescript
// components/ui/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react-native';
import { composeStories } from '@storybook/react';
import * as stories from '../Button.stories';

const { Primary, Secondary } = composeStories(stories);

describe('Button stories', () => {
  it('Primary storyがレンダリングされる', () => {
    render(<Primary />);
    expect(screen.getByText('AIに質問する')).toBeTruthy();
  });
});
```

### ストーリーをチームと共有（Chromatic）

```bash
# ChromaticでStorybookをクラウドに公開（ビジュアルテスト自動化）
npm install --save-dev chromatic
npx chromatic --project-token=YOUR_TOKEN

# PRごとにビジュアル差分をレポート（UIリグレッション検知）
```

### Emport AIへの応用
- Button・ChatBubble・IndustryCard などの全UIコンポーネントをStorybookで管理
- デザイナー（将来の外注）にStorybookのURLを共有してUI確認
- ビジュアルリグレッションテストでUIの意図しない変更を即検知

---

## 137. クリップボード・ネイティブ共有（expo-clipboard + expo-sharing）

### 調査日時
2026-05-15

### 概要
expo-clipboard でテキスト・画像をクリップボードに保存し、expo-sharing でネイティブ共有シート（メール・LINE・Slack・Twitter等）からファイルを送信。AI回答のコピー・共有機能に不可欠。

### インストール

```bash
npx expo install expo-clipboard expo-sharing
```

### クリップボード実装

```typescript
// services/clipboard.ts
import * as Clipboard from 'expo-clipboard';

// テキストをクリップボードにコピー
export async function copyText(text: string): Promise<void> {
  await Clipboard.setStringAsync(text);
}

// クリップボードの内容を取得
export async function getClipboardText(): Promise<string> {
  return Clipboard.getStringAsync();
}

// 画像URLをコピー
export async function copyImageUrl(url: string) {
  await Clipboard.setUrlAsync(url);
}

// クリップボードにコンテンツがあるか確認
export async function hasClipboardContent(): Promise<boolean> {
  return Clipboard.hasStringAsync();
}
```

### チャット画面でのコピー機能

```tsx
// チャットバブルの長押し → コピー
export function ChatBubble({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    await Clipboard.setStringAsync(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <TouchableOpacity onLongPress={handleCopy}>
      <View style={styles.bubble}>
        <Text>{message.content}</Text>
        {copied && (
          <Animated.Text entering={FadeIn} exiting={FadeOut} style={styles.copiedBadge}>
            コピーしました ✓
          </Animated.Text>
        )}
      </View>
    </TouchableOpacity>
  );
}
```

### ネイティブ共有シート

```typescript
// expo-sharing でファイルを共有
import * as Sharing from 'expo-sharing';
import { Share } from 'react-native'; // テキスト共有はこちら

// テキストの共有（React Native 標準）
export const shareText = async (text: string, title?: string) => {
  await Share.share({ message: text, title });
};

// ファイルの共有（PDF・画像など）
export const shareFile = async (uri: string, mimeType: string) => {
  if (await Sharing.isAvailableAsync()) {
    await Sharing.shareAsync(uri, { mimeType, dialogTitle: '共有先を選択' });
  }
};

// スクリーンショット撮影 + 共有（react-native-view-shot）
import ViewShot from 'react-native-view-shot';

const viewRef = useRef<ViewShot>(null);
const captureAndShare = async () => {
  const uri = await viewRef.current!.capture!();
  await shareFile(uri, 'image/png');
};

// チャット画面を画像としてキャプチャして共有
<ViewShot ref={viewRef} options={{ format: 'png', quality: 0.9 }}>
  <ChatContent messages={messages} />
</ViewShot>
<Button title="スクリーンショットを共有" onPress={captureAndShare} />
```

### Share APIパターン一覧

```typescript
// ① テキスト共有（標準 Share API）
Share.share({ message: 'Emport AIを使ってみてください！\nhttps://emport-ai.vercel.app' });

// ② ファイル共有（expo-sharing）
Sharing.shareAsync(pdfUri, { mimeType: 'application/pdf' });

// ③ URLのコピー（expo-clipboard）
Clipboard.setStringAsync('https://emport-ai.vercel.app/invite/ABC123');

// ④ 紹介リンク + App Store URL を合わせて共有
Share.share({
  message: '地方中小企業向けAI経営アドバイザー！月額980円\\n',
  url: 'https://apps.apple.com/jp/app/emport-ai', // iOS: message + url
});
```

### Emport AIへの応用
- チャット回答の長押し → クリップボードコピー（最頻出機能）
- PDF レポートをメール・LINEで共有
- 「友達に紹介」ボタンで招待リンクを共有シート経由で送付
- AI回答のスクリーンショット → SNS投稿でバイラル効果
"""

with open(REPORT_PATH, 'a', encoding='utf-8') as f:
    f.write(CONTENT)

print("Done: Round 22 sections 131-137 appended successfully")
