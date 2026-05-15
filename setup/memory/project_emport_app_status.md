---
name: project-emport-app-status
description: Emport AIアプリ・TaskMasterアプリの開発状況・直近の作業・次のアクション
metadata: 
  node_type: memory
  type: project
  originSessionId: 02bc9f6a-bf09-4ca4-bc9e-868df094be04
---

## TaskMaster アプリ（2026-05-15 完成）

### 場所
- 実行パス: `C:\taskmaster`（日本語パス回避のためデスクトップから移動）
- ソースコピー: `C:\Users\tsube\OneDrive\デスクトップ\taskmaster`

### 技術スタック
- Expo 55 + React Native 0.81.5 + expo-router v5
- NativeWind v4 (TailwindCSS)、darkMode: class設定済み
- Zustand v4 + AsyncStorage 永続化
- React Hook Form v7 + Zod v4 バリデーション
- @gorhom/bottom-sheet v5 (タスク追加UI)
- Reanimated v3 + Gesture Handler v2 (スワイプ削除)
- expo-haptics (触覚フィードバック)

### 機能
- タスクの追加・完了・削除（スワイプ）
- カテゴリ（仕事/プライベート/買い物/その他）
- 優先度（高/中/低）
- フィルタータブ（すべて/未完了/完了済み）
- AsyncStorage による永続化

### Web対応で解決した技術的問題
- `import.meta` エラー → `metro.config.js` で `unstable_enablePackageExports: false`
- ダークモード競合 → `tailwind.config.js` に `darkMode: 'class'`
- BottomSheetTextInput Web非対応 → `Platform.OS === 'web'` で TextInput に分岐
- react-dom バージョン不一致 → 19.1.0 に固定
- react-native-worklets → Reanimated v4→v3 にダウングレードで不要に

### 起動方法
```bash
cd C:\taskmaster
npx expo start --web --port 8094 --offline
```

## Emport AI アプリ（別プロジェクト）

### 現在の課題
- ユーザーが自分でClaude APIキーを取得・設定する必要がある → 中小企業オーナーには大きな障壁

### 次のアクション（優先順）
1. **バックエンドAPI化**（最優先）- Railway上Flaskアプリにプロキシエンドポイント追加
2. オンボーディング画面の追加

**Why:** 中小企業オーナー向けにAPIキー設定不要で即使えるアプリにすることが最重要課題。
**How to apply:** Emport AIの次回作業はバックエンドAPI化から着手する。
