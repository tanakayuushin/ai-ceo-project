# -*- coding: utf-8 -*-
"""Round 21: Sections 124-130 - Gesture Handler, Charts, Maps, QR, Drag&Drop, PDF, Bottom Sheet"""
import os

REPORT_PATH = r"c:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\data\reports\research-app-dev.md"

CONTENT = """
---

## Round 21 — ジェスチャー・チャート・マップ・QRスキャン・ドラッグ&ドロップ・PDF・ボトムシート
調査日時: 2026-05-15

---

## 124. React Native Gesture Handler v3 — 高度なジェスチャーパターン

### 調査日時
2026-05-15

### 概要
React Native Gesture Handler (RNGH) は、ネイティブスレッドでジェスチャーを処理するライブラリ。v2以降はオブジェクトベースの宣言的APIに移行し、Reanimatedと組み合わせることで120fpsの滑らかなジェスチャーインタラクションを実現。

### 現代的なジェスチャーAPI（v2+）

```bash
npx expo install react-native-gesture-handler
```

```tsx
// 必須: アプリのルートをGestureHandlerRootViewで囲む
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <RootLayout />
    </GestureHandlerRootView>
  );
}
```

### スワイプで削除（チャット履歴向け）

```tsx
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';

interface SwipeableRowProps {
  children: React.ReactNode;
  onDelete: () => void;
}

export function SwipeableRow({ children, onDelete }: SwipeableRowProps) {
  const translateX = useSharedValue(0);
  const SWIPE_THRESHOLD = -80;

  const panGesture = Gesture.Pan()
    .activeOffsetX([-10, 10]) // 横方向10px以上で認識
    .onUpdate((e) => {
      translateX.value = Math.min(0, e.translationX); // 左方向のみ
    })
    .onEnd((e) => {
      if (e.translationX < SWIPE_THRESHOLD) {
        // 削除実行
        translateX.value = withTiming(-300, {}, () => runOnJS(onDelete)());
      } else {
        // 元の位置に戻る
        translateX.value = withSpring(0);
      }
    });

  const animStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={animStyle}>{children}</Animated.View>
    </GestureDetector>
  );
}
```

### ピンチズーム（画像・チャート向け）

```tsx
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, { useSharedValue, useAnimatedStyle } from 'react-native-reanimated';

export function PinchableImage({ source }: { source: string }) {
  const scale = useSharedValue(1);
  const savedScale = useSharedValue(1);

  const pinchGesture = Gesture.Pinch()
    .onUpdate((e) => {
      scale.value = savedScale.value * e.scale;
    })
    .onEnd(() => {
      savedScale.value = Math.max(1, Math.min(scale.value, 4)); // 1x-4xの範囲
      scale.value = withSpring(savedScale.value);
    });

  // ダブルタップでリセット
  const doubleTap = Gesture.Tap()
    .numberOfTaps(2)
    .onEnd(() => {
      scale.value = withSpring(1);
      savedScale.value = 1;
    });

  // ジェスチャーの同時実行
  const composed = Gesture.Simultaneous(pinchGesture, doubleTap);

  const animStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <GestureDetector gesture={composed}>
      <Animated.Image source={{ uri: source }} style={[styles.image, animStyle]} />
    </GestureDetector>
  );
}
```

### ジェスチャー優先度制御

```typescript
// Exclusive: 優先度の高いジェスチャーのみ実行
const gesture = Gesture.Exclusive(
  Gesture.Tap().onEnd(() => console.log('tap')),
  Gesture.LongPress().onStart(() => console.log('longpress'))
);

// Race: 最初に認識されたジェスチャーが勝つ
const raceGesture = Gesture.Race(panGesture, swipeGesture);
```

### Emport AIへの応用
- チャット履歴の左スワイプで「削除」アクション
- AI回答カードのピンチズームで長文を拡大表示
- 業種選択カードのドラッグで並べ替え

---

## 125. データビジュアライゼーション（Victory Native XL）

### 調査日時
2026-05-15

### 概要
Victory Native XL (v40+) は React Native Skia による GPU描画に対応したチャートライブラリ。従来のSVGベースより高パフォーマンスで、ジェスチャー操作・アニメーションに対応。Emport AIの売上グラフ・使用統計表示に活用できる。

### インストール

```bash
npm install victory-native@^40
npx expo install react-native-skia react-native-reanimated react-native-gesture-handler
```

### 棒グラフ（月次売上）

```tsx
import { CartesianChart, Bar } from 'victory-native';
import { useFont } from '@shopify/react-native-skia';

const MONTHLY_DATA = [
  { month: '1月', revenue: 0 },
  { month: '2月', revenue: 0 },
  { month: '3月', revenue: 30000 },
  { month: '4月', revenue: 60000 },
  { month: '5月', revenue: 100000 },
];

export function RevenueChart() {
  const font = useFont(require('../assets/fonts/NotoSansJP.ttf'), 12);

  return (
    <CartesianChart
      data={MONTHLY_DATA}
      xKey="month"
      yKeys={["revenue"]}
      axisOptions={{ font, formatYLabel: (v) => `¥${(v / 10000).toFixed(0)}万` }}
      domainPadding={{ left: 20, right: 20, top: 20 }}
    >
      {({ points, chartBounds }) => (
        <Bar
          points={points.revenue}
          chartBounds={chartBounds}
          color="#1428C8"
          roundedCorners={{ topLeft: 4, topRight: 4 }}
          animate={{ type: 'spring', stiffness: 100 }}
        />
      )}
    </CartesianChart>
  );
}
```

### 折れ線グラフ（AI使用回数）

```tsx
import { CartesianChart, Line, Area } from 'victory-native';

export function UsageChart({ data }: { data: { date: string; count: number }[] }) {
  const { state, isActive } = useChartPressState({ x: '', y: { count: 0 } });

  return (
    <CartesianChart
      data={data}
      xKey="date"
      yKeys={["count"]}
      chartPressState={state}   // タッチでデータポイントをハイライト
    >
      {({ points, chartBounds }) => (
        <>
          <Area
            points={points.count}
            chartBounds={chartBounds}
            color="#1428C8"
            opacity={0.15}
          />
          <Line
            points={points.count}
            color="#1428C8"
            strokeWidth={2}
            animate={{ type: 'timing', duration: 600 }}
          />
          {isActive && (
            <ToolTip x={state.x.position} y={state.y.count.position} />
          )}
        </>
      )}
    </CartesianChart>
  );
}
```

### 円グラフ（業種別ユーザー分布）

```tsx
import { PolarChart, Pie } from 'victory-native';

const INDUSTRY_DATA = [
  { label: '建設業', value: 35, color: '#1428C8' },
  { label: '製造業', value: 25, color: '#3F51B5' },
  { label: '水産業', value: 20, color: '#7986CB' },
  { label: '小売業', value: 15, color: '#9FA8DA' },
  { label: 'その他', value: 5, color: '#C5CAE9' },
];

export function IndustryPieChart() {
  return (
    <PolarChart
      data={INDUSTRY_DATA}
      labelKey="label"
      valueKey="value"
      colorKey="color"
    >
      <Pie.Chart>
        {({ slice }) => (
          <Pie.Slice>
            <Pie.Label />
          </Pie.Slice>
        )}
      </Pie.Chart>
    </PolarChart>
  );
}
```

### Emport AIへの応用
- ダッシュボード画面に月次売上・AI使用回数・顧客数のグラフ
- 管理者向け業種別ユーザー分布円グラフ
- フィンガータッチで特定データポイントの詳細表示

---

## 126. 位置情報・地図（expo-location + react-native-maps）

### 調査日時
2026-05-15

### 概要
expo-location でGPS位置情報を取得し、react-native-maps でMapView上にマーカーを表示。Emport AIの将来機能（近くの中小企業を可視化、補助金窓口の場所案内）に活用できる。

### インストール

```bash
npx expo install expo-location react-native-maps
```

### 位置情報の取得

```typescript
// hooks/useLocation.ts
import * as Location from 'expo-location';
import { useEffect, useState } from 'react';

export function useLocation() {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [error, setError] = useState<string | null>(null);

  const requestLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      setError('位置情報の許可が必要です');
      return;
    }

    const loc = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced,
    });
    setLocation(loc);
  };

  // リアルタイム追跡（移動中のユーザー向け）
  const watchLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return;

    return Location.watchPositionAsync(
      { accuracy: Location.Accuracy.Balanced, timeInterval: 5000, distanceInterval: 10 },
      (loc) => setLocation(loc)
    );
  };

  return { location, error, requestLocation, watchLocation };
}
```

### 地図表示（近くの商工会議所）

```tsx
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';

const SUPPORT_OFFICES = [
  { id: '1', name: '山口商工会議所', latitude: 34.1859, longitude: 131.4706 },
  { id: '2', name: 'やまぐち産業振興財団', latitude: 34.1820, longitude: 131.4550 },
  { id: '3', name: '下関商工会議所', latitude: 33.9600, longitude: 130.9420 },
];

export function SupportOfficeMap() {
  const { location } = useLocation();

  return (
    <MapView
      provider={PROVIDER_GOOGLE}
      style={{ flex: 1 }}
      initialRegion={{
        latitude: location?.coords.latitude ?? 34.1859,
        longitude: location?.coords.longitude ?? 131.4706,
        latitudeDelta: 0.1,
        longitudeDelta: 0.1,
      }}
      showsUserLocation={true}
      showsMyLocationButton={true}
    >
      {SUPPORT_OFFICES.map((office) => (
        <Marker
          key={office.id}
          coordinate={{ latitude: office.latitude, longitude: office.longitude }}
          title={office.name}
          description="補助金・支援窓口"
          pinColor="#1428C8"
        />
      ))}
    </MapView>
  );
}
```

### app.json の設定

```json
{
  "expo": {
    "plugins": [
      [
        "react-native-maps",
        { "androidGoogleMapsApiKey": "YOUR_ANDROID_MAPS_KEY" }
      ],
      [
        "expo-location",
        {
          "locationAlwaysAndWhenInUsePermission": "Emport AIが近くの支援窓口を案内するために位置情報を使用します"
        }
      ]
    ]
  }
}
```

### Emport AIへの応用
- 近くの商工会議所・補助金窓口をマップ上に表示
- 山口県内の対応企業（将来的な顧客リスト）の分布可視化
- 現在地から最寄りの支援機関への経路案内

---

## 127. QRコード・バーコードスキャン（expo-camera）

### 調査日時
2026-05-15

### 概要
Expo SDK 50以降、expo-barcode-scanner は非推奨となり expo-camera に統合。expo-camera の `onBarcodeScanned` プロパティでQRコード・各種バーコードのスキャンが可能。

### 実装

```bash
npx expo install expo-camera
```

```tsx
// components/QRScanner.tsx
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useState } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

interface QRScannerProps {
  onScan: (data: string) => void;
}

export function QRScanner({ onScan }: QRScannerProps) {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);

  if (!permission) return <View />; // ロード中

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text>カメラへのアクセス許可が必要です</Text>
        <Button title="許可する" onPress={requestPermission} />
      </View>
    );
  }

  const handleBarcodeScanned = ({ type, data }: { type: string; data: string }) => {
    if (scanned) return;
    setScanned(true);
    onScan(data);
    // 1秒後に再スキャン可能に
    setTimeout(() => setScanned(false), 1000);
  };

  return (
    <View style={styles.container}>
      <CameraView
        style={StyleSheet.absoluteFillObject}
        facing="back"
        onBarcodeScanned={handleBarcodeScanned}
        barcodeScannerSettings={{
          barcodeTypes: ['qr', 'ean13', 'code128', 'pdf417'],
        }}
      />
      {/* スキャンガイドオーバーレイ */}
      <View style={styles.overlay}>
        <View style={styles.scanBox} />
        <Text style={styles.hint}>QRコードをフレーム内に入れてください</Text>
      </View>
    </View>
  );
}
```

### QRコード生成

```tsx
// npm install react-native-qrcode-svg
import QRCode from 'react-native-qrcode-svg';

// ユーザー紹介コード・会社IDのQRコード生成
export function ShareQRCode({ userId }: { userId: string }) {
  const shareUrl = `https://emport-ai.vercel.app/invite/${userId}`;

  return (
    <QRCode
      value={shareUrl}
      size={200}
      color="#1428C8"
      backgroundColor="white"
      logo={require('../assets/icon.png')}
      logoSize={40}
      logoBackgroundColor="white"
    />
  );
}
```

### 使用場面

| 場面 | QRコードの内容 | 用途 |
|------|---------------|------|
| 名刺代わり | 会社紹介URL | ユーザー獲得 |
| 紹介キャンペーン | `invite/userId` | バイラル成長 |
| イベント受付 | 参加者ID | オフライン活用 |
| 補助金書類確認 | 書類番号 | 業務効率化 |

### Emport AIへの応用
- 「友達に紹介」機能でQRコードを表示→スキャンでEmport AIアプリに誘導
- 将来機能：名刺スキャン → AI名刺管理

---

## 128. ドラッグ＆ドロップリスト（react-native-draggable-flatlist）

### 調査日時
2026-05-15

### 概要
`react-native-draggable-flatlist` は長押し→ドラッグで並べ替えができるFlatList実装。Reanimated + Gesture Handlerで60fps滑らか動作。お気に入り機能や優先度設定のUI実装に使用。

### インストール

```bash
npm install react-native-draggable-flatlist
```

### 実装（よく使う質問の並べ替え）

```tsx
import DraggableFlatList, {
  RenderItemParams,
  ScaleDecorator,
} from 'react-native-draggable-flatlist';

interface FavoritePrompt {
  key: string;
  label: string;
  industry: string;
}

export function FavoritePromptList() {
  const [items, setItems] = useState<FavoritePrompt[]>([
    { key: '1', label: '資金繰りの改善方法', industry: '建設業' },
    { key: '2', label: '従業員採用のコツ', industry: '水産業' },
    { key: '3', label: '補助金申請のポイント', industry: '製造業' },
  ]);

  const renderItem = ({ item, drag, isActive }: RenderItemParams<FavoritePrompt>) => (
    <ScaleDecorator>
      <TouchableOpacity
        onLongPress={drag}  // 長押しでドラッグ開始
        disabled={isActive}
        style={[
          styles.item,
          { backgroundColor: isActive ? '#EEF0FF' : '#FFFFFF' },
        ]}
      >
        <Ionicons name="reorder-three" size={24} color="#9CA3AF" />
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={styles.label}>{item.label}</Text>
          <Text style={styles.industry}>{item.industry}</Text>
        </View>
      </TouchableOpacity>
    </ScaleDecorator>
  );

  return (
    <DraggableFlatList
      data={items}
      onDragEnd={({ data }) => {
        setItems(data);
        // 並び順をMMKV/バックエンドに保存
        saveFavoriteOrder(data.map((i) => i.key));
      }}
      keyExtractor={(item) => item.key}
      renderItem={renderItem}
    />
  );
}
```

### デコレーター（ドラッグ中のビジュアル）

```tsx
// ScaleDecorator: ドラッグ中に拡大
// ShadowDecorator: ドラッグ中に影を追加
// OpacityDecorator: ドラッグ中に半透明

import {
  ScaleDecorator,
  ShadowDecorator,
  OpacityDecorator,
} from 'react-native-draggable-flatlist';

// 組み合わせ可能
<ShadowDecorator>
  <ScaleDecorator>
    <TouchableOpacity onLongPress={drag}>...</TouchableOpacity>
  </ScaleDecorator>
</ShadowDecorator>
```

### Emport AIへの応用
- 「よく使う質問」のピン留め・並べ替え
- ダッシュボードウィジェットの順序カスタマイズ
- 業種ごとのプロンプトテンプレートの優先度設定

---

## 129. PDF生成・表示（expo-print + expo-sharing）

### 調査日時
2026-05-15

### 概要
expo-print はHTML文字列からPDFを生成し、expo-sharing でネイティブ共有シート（メール・Drive・LINEなど）から送信できる。AIの回答を整形したレポートPDFの出力がEmport AIの差別化機能になる。

### インストール

```bash
npx expo install expo-print expo-sharing
```

### HTML → PDF生成

```typescript
// services/pdfGenerator.ts
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';

interface AIReport {
  companyName: string;
  industry: string;
  question: string;
  answer: string;
  generatedAt: string;
}

export async function generateAIReport(report: AIReport): Promise<void> {
  const html = `
    <!DOCTYPE html>
    <html lang="ja">
    <head>
      <meta charset="UTF-8">
      <style>
        body { font-family: 'Helvetica', sans-serif; padding: 40px; color: #1a1a1a; }
        .header { background: #1428C8; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 20px; }
        .header p { margin: 4px 0 0; font-size: 12px; opacity: 0.8; }
        .section { margin-bottom: 24px; }
        .section h2 { color: #1428C8; font-size: 14px; border-bottom: 2px solid #1428C8; padding-bottom: 6px; }
        .question-box { background: #F3F4F6; padding: 16px; border-radius: 8px; margin: 8px 0; }
        .answer-box { background: #EEF0FF; padding: 16px; border-radius: 8px; line-height: 1.8; }
        .footer { text-align: center; color: #6B7280; font-size: 10px; margin-top: 40px; }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Emport AI — AI経営レポート</h1>
        <p>${report.companyName} | ${report.industry} | ${report.generatedAt}</p>
      </div>

      <div class="section">
        <h2>ご質問</h2>
        <div class="question-box">${report.question}</div>
      </div>

      <div class="section">
        <h2>AIアドバイス</h2>
        <div class="answer-box">${report.answer.replace(/\\n/g, '<br>')}</div>
      </div>

      <div class="footer">
        Generated by Emport AI — https://emport-ai.vercel.app
      </div>
    </body>
    </html>
  `;

  const { uri } = await Print.printToFileAsync({ html, base64: false });

  if (await Sharing.isAvailableAsync()) {
    await Sharing.shareAsync(uri, {
      mimeType: 'application/pdf',
      dialogTitle: 'AIレポートを共有',
      UTI: 'com.adobe.pdf',
    });
  }
}
```

### 使用例

```tsx
// AIチャット画面のエクスポートボタン
const handleExportPDF = async () => {
  await generateAIReport({
    companyName: profile.companyName,
    industry: profile.industry,
    question: currentMessage.question,
    answer: currentMessage.answer,
    generatedAt: new Date().toLocaleDateString('ja-JP'),
  });
};

// ペイウォールで制御（プレミアム機能）
<PaywallGate feature="AIレポートPDF出力">
  <TouchableOpacity onPress={handleExportPDF}>
    <Ionicons name="document-text" size={20} />
    <Text>PDFで保存</Text>
  </TouchableOpacity>
</PaywallGate>
```

### Emport AIへの応用
- AIの回答をPDFレポートとして出力 → 経営者が銀行・取引先に提出できる
- 補助金申請に使える「AI経営分析レポート」としてプレミアム差別化
- メール・LINE・Slackへの直接共有

---

## 130. ボトムシート（@gorhom/bottom-sheet）

### 調査日時
2026-05-15

### 概要
`@gorhom/bottom-sheet` (v5) はReanimated v3 + Gesture Handler v2で構築された高パフォーマンスのボトムシートコンポーネント。スナップポイント・キーボード対応・モーダル表示の3パターンを完全サポートし、iOSのネイティブシート体験に近い動作を実現。

### インストール

```bash
npm install @gorhom/bottom-sheet@^5
npx expo install react-native-reanimated react-native-gesture-handler
```

### 基本実装（フィルター・設定パネル）

```tsx
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';
import { useRef, useMemo, useCallback } from 'react';

export function IndustryFilterSheet({ onSelect }: { onSelect: (industry: string) => void }) {
  const bottomSheetRef = useRef<BottomSheet>(null);

  // スナップポイント（画面の25%・50%）
  const snapPoints = useMemo(() => ['25%', '50%'], []);

  const openSheet = useCallback(() => {
    bottomSheetRef.current?.expand();
  }, []);

  const closeSheet = useCallback(() => {
    bottomSheetRef.current?.close();
  }, []);

  const handleSelect = (industry: string) => {
    onSelect(industry);
    closeSheet();
  };

  return (
    <>
      <TouchableOpacity onPress={openSheet}>
        <Text>業種で絞り込む</Text>
      </TouchableOpacity>

      <BottomSheet
        ref={bottomSheetRef}
        index={-1}            // -1 = 最初は非表示
        snapPoints={snapPoints}
        enablePanDownToClose={true}
        backgroundStyle={{ borderRadius: 24, backgroundColor: '#FFFFFF' }}
        handleIndicatorStyle={{ backgroundColor: '#CBD5E1', width: 40 }}
      >
        <BottomSheetView style={{ padding: 24 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 16 }}>
            業種を選択
          </Text>
          {INDUSTRIES.map((industry) => (
            <TouchableOpacity
              key={industry.id}
              onPress={() => handleSelect(industry.id)}
              style={styles.industryItem}
            >
              <Text>{industry.emoji} {industry.label}</Text>
            </TouchableOpacity>
          ))}
        </BottomSheetView>
      </BottomSheet>
    </>
  );
}
```

### モーダル版（プレミアムアップセル）

```tsx
import { BottomSheetModal, BottomSheetModalProvider } from '@gorhom/bottom-sheet';

export function PremiumBottomSheet() {
  const modalRef = useRef<BottomSheetModal>(null);
  const snapPoints = useMemo(() => ['60%'], []);

  const present = () => modalRef.current?.present();
  const dismiss = () => modalRef.current?.dismiss();

  return (
    <BottomSheetModalProvider>
      <BottomSheetModal
        ref={modalRef}
        snapPoints={snapPoints}
        enableDynamicSizing={false}
        backdropComponent={BottomSheetBackdrop}
      >
        <BottomSheetView style={styles.content}>
          <Text style={styles.title}>プレミアムプランへアップグレード</Text>
          <Text style={styles.price}>月額 ¥980</Text>
          <PremiumFeatureList />
          <Button title="7日間無料で試す" onPress={handlePurchase} />
          <TouchableOpacity onPress={dismiss}>
            <Text style={styles.skip}>後で</Text>
          </TouchableOpacity>
        </BottomSheetView>
      </BottomSheetModal>
    </BottomSheetModalProvider>
  );
}
```

### スクロール可能なコンテンツ

```tsx
import { BottomSheetScrollView } from '@gorhom/bottom-sheet';

// 長いコンテンツ（利用規約・チャット履歴など）
<BottomSheet snapPoints={['90%']}>
  <BottomSheetScrollView>
    {messages.map((msg) => <ChatBubble key={msg.id} message={msg} />)}
  </BottomSheetScrollView>
</BottomSheet>
```

### キーボード対応

```tsx
import { BottomSheetTextInput } from '@gorhom/bottom-sheet';

// BottomSheet内のTextInputはBottomSheetTextInputを使う
// → キーボード表示時にシートが自動で上に移動
<BottomSheetTextInput
  placeholder="返信を入力..."
  style={styles.input}
  onChangeText={setText}
/>
```

### Emport AIへの応用
- 業種フィルター・並べ替えオプションのボトムシート
- プレミアムアップセル（チャット画面で適切なタイミングに表示）
- AI回答の「詳細設定」パネル（トーン・長さ・形式の調整）
"""

with open(REPORT_PATH, 'a', encoding='utf-8') as f:
    f.write(CONTENT)

print("Done: Round 21 sections 124-130 appended successfully")
