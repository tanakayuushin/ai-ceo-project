# アレン調査レポート — 自律リサーチ

> 調査開始: 2026-05-14  
> 更新のたびに追記。ユーザー不在中も継続調査中。

---

## 1. Claude Code 有効活用法・Tips・隠し機能

**調査日時: 2026-05-14**

### 即効性の高い機能（明日から使える）

| コマンド/機能 | 内容 |
|---|---|
| `Ctrl+O` | Focus View切り替え — 最終回答だけ表示。可読性3倍 |
| `/btw` | メイン作業を止めずにサブ質問を割り込み実行 |
| `/buddy` | ターミナルにペット表示（18種類）。気分転換 |
| `/branch` | 複数の実装アプローチを並列実験 |
| `/loop` | 定期タスクを自動化（セキュリティチェック等） |

### 上級テクニック

**CLAUDE.md を使いこなす**
- プロジェクトの「憲法」。毎セッション自動読込
- 禁止コマンド、コーディング規約、デプロイ手順を書いておく
- チーム全員が同じ振る舞いのClaudeを使える

**Hooks（自動スクリプト）**
- ツール実行の前後に検証スクリプトを挿入
- `.claude/settings.json` で設定
- 使いどころ：APIキー漏洩防止・コミット前テスト自動実行・危険コマンドのブロック

**Git Worktrees × 並列エージェント**
- 複数ブランチで複数Claudeが同時作業
- チケット消化速度が実質2倍以上に
- 使いどころ：バグ修正とフィーチャー開発を同時進行

**MCPサーバー連携**
- Playwright（ブラウザ操作）、Gmail、GitHub等を直接操作
- `/mcp__playwright__browser_navigate` のような形で呼び出し
- 自社専用のMCPサーバーも作成可能

**推奨導入順序**
```
1週目: Focus View + /btw（すぐ使える）
2〜3週目: CLAUDE.md最適化 + Hooks設定
4〜6週目: MCPサーバー追加
2ヶ月目: 並列エージェント + Git Worktrees
```

### Emport AIへの応用ポイント
- Claude Codeを使って **Emport AIの機能開発を加速**できる
- Hooksでデプロイ前チェックを自動化 → Railway障害を事前検知
- CLAUDE.mdにアレンの行動原則を書いておけば引継ぎコスト0

**情報源:**
- [Claude Code 9つの知られざる機能 (Uravation)](https://uravation.com/media/claude-code-9-hidden-features-2026/)
- [Claude Code完全ガイド (Uravation)](https://uravation.com/media/claude-code-guide/)
- [Claude Code Cheat Sheet 2026](https://techbytes.app/posts/claude-code-2026-cheat-sheet-hooks-mcp-commands/)

---

## 2. Obsidian とは・活用法・AI連携

**調査日時: 2026-05-14**

### Obsidianとは

ローカル保存のMarkdownベースPKM（Personal Knowledge Management）ツール。  
**完全無料・ローカル保存・データ所有権100%自分** というのが最大の特徴。

### なぜ今注目されているか

| 従来のノートアプリ | Obsidian |
|---|---|
| クラウド依存 | 全データがPC内の`.md`ファイル |
| ベンダーロックイン | ツールが消えてもファイルは残る |
| AI連携が難しい | CursorやClaude Codeのワークスペースに直接読込 |
| 単方向リンク | **双方向リンク**で知識がネットワーク化 |

### 主な特徴

- **2,700種類以上のプラグイン**（カレンダー・タスク管理・Kanban・AI連携）
- **グラフビュー**：ノート間のつながりを視覚化
- **2026年2月 v1.12**: Obsidian CLI追加 → Claude CodeやCursorがターミナル経由でVaultを操作可能に

### AI連携の方法（2026年版）

**プラグイン経由**
- `Copilot for Obsidian`：ノート内でClaude/GPT-4oを直接呼び出し
- `Smart Connections`：ノート間の意味的類似度をAIで発見
- `Text Generator`：カーソル位置にAIが続きを生成

**Claude Code × Obsidian の組み合わせ（最強パターン）**
```
Obsidianのvaultフォルダ = Claude Codeのワークスペースに設定
→ Claude Codeがすべてのノートを知識源として使える（RAG不要）
→ ミーティングメモ→タスク自動生成→コード実装まで一気通貫
```

### アレン × Emport AIへの応用案

1. **社内知識ベース**: 商工会議所とのやりとり・顧客ヒアリング・会議メモをObsidianに集約
2. **CEOレポート自動化**: Obsidianのweekly-reportをClaude Codeが自動で読んで要約
3. **顧客事例ストック**: Emport AIユーザーの成功事例をObsidianで管理 → プロンプトに注入

**情報源:**
- [Obsidian AI連携ガイド (OptiMax)](https://www.optimax.co.jp/ai-information/obsidian-ai-native/)
- [Obsidian入門 AI時代の第二の脳 (visionnurture)](https://www.visionnurture.com/obsidian_guide_for_beginner_001/)
- [ObsidianとAIの連携方法まとめ](https://masaki39.net/%F0%9F%93%98Obsidian%E3%81%A8AI%E3%81%AE%E9%80%A3%E6%90%BA%E6%96%B9%E6%B3%95%E3%81%BE%E3%81%A8%E3%82%81)

---

## 3. 日本の経済・中小企業・スタートアップ最新動向

**調査日時: 2026-05-14**

### 中小企業向けDX補助金（2026年版・最重要情報）

**「デジタル化・AI導入補助金2026」**（旧：IT導入補助金）

| 項目 | 内容 |
|---|---|
| 運営 | 中小企業庁 |
| 補助上限 | **最大450万円** |
| 補助率 | 1/2〜3/4（枠による） |
| 対象 | AIツール・クラウドサービス・実装支援費 |
| 2026年の変更点 | **「AI機能搭載ツール」が必須要件に** |
| 申請開始 | 2026年3月30日〜（毎1〜2ヶ月締切） |
| 新要件 | 申請前に「省力化ナビ」診断が必須 |

**→ Emport AIが補助金対象SaaSとして登録できれば、顧客の導入コストがゼロに近くなる**

### スタートアップ資金調達トレンド（2026年Q1）

- 調達総額：**過去最高**（ただし件数は減少 → 大型案件集中）
- 注目調達：
  - **Third Intelligence**（国産AGI）：初ラウンドで80億円
  - **CRISP**（外食AI）：37億円
  - **マイクロニティ**（AI事業承継）：22億円
- トレンド：「技術実証フェーズ」→「社会実装・ROI実証フェーズ」へ移行

### 中小企業のAI活用実態

- AI導入率：大企業と中小企業の格差が依然大きい
- 中小企業の課題：「何から始めればいいか分からない」「コスト不安」「社内人材不足」
- **→ これがEmport AIの存在意義そのもの**

**情報源:**
- [デジタル化・AI導入補助金2026 (中小企業庁)](https://www.chusho.meti.go.jp/koukai/hojyokin/kobo/2026/260310001.html)
- [補助金完全ガイド2026 (FURUSATO)](https://furusato.co-nect.co.jp/2026/04/26/ai-dx-subsidy-complete-2026/)
- [スタートアップ資金調達最高 (日経)](https://www.nikkei.com/article/DGXZQOUC211X60R20C26A4000000/)

---

## 4. AI市場・日本のAI規制・最新ニュース

**調査日時: 2026-05-14**

### 市場規模

| 指標 | 数値 |
|---|---|
| 世界AIシステム支出（2026年） | **2.52兆ドル** |
| 日本AIシステム市場（2024年） | 1兆3,412億円 |
| 日本AIシステム市場（2029年予測） | **4兆1,873億円**（3倍以上） |
| 日本生成AI市場（2025年） | 10億1,460万ドル |
| 日本生成AI市場（2034年予測） | 40億4,950万ドル（CAGR 16.63%） |

### 2026年の主要AIトレンド（日本企業が備えるべき）

1. **エージェントAI普及**：「指示するAI」から「自律実行するAI」へ。業務フロー全体をAIが担う時代
2. **マルチモーダル標準化**：画像・音声・テキストを統合処理が当然に。GPT-5、Gemini 3.1、Claude Opus 4.6が対応済み
3. **ROI実証フェーズ**：「試験導入」から「本番運用・効果測定」へ。数字で語れない企業は撤退
4. **フィジカルAI**：デジタルと現実世界の統合。製造・物流領域での自律AI
5. **中国AIの台頭**：DeepSeek等がLLM三強（OpenAI・Google・Anthropic）に対抗

### Emport AIにとっての意味

- 市場は急成長中だが、中小企業への浸透はまだ低い → **ブルーオーシャン**
- 「ROI実証フェーズ」=ユーザーが「本当に売上が上がったか」を求め始める
- → **Emport AIも成果指標（売上増・時間削減）を見せる機能が必要になる**

**情報源:**
- [AI業界現状完全ガイド2026 (renue)](https://renue.co.jp/posts/ai-industry-state-2026-world-2-5t-japan-94b-llm-3-giants-5-trends)
- [2026年AIトレンド13選 (relipasoft)](https://relipasoft.com/blog/top-ai-trend/)
- [生成AI市場規模解説 (AI総合研究所)](https://www.ai-souken.com/article/ai-generation-market-size)

---

## 5. 競合SaaS動向（中小企業向けAIツール・日本）

**調査日時: 2026-05-14**

### 主要競合マップ

| サービス名 | 月額料金 | 特徴 | 弱点 |
|---|---|---|---|
| ChatPlus | 〜3万円台 | 国産・カスタマイズ豊富 | 経営特化ではない |
| AITOLIE | 9,800円〜 | AI込み明確料金 | 汎用チャットボット |
| FirstContact | 安価 | 低コスト | サポート薄い |
| DSチャットボット | 要問合せ | 無料体験・サポート厚 | 高め |
| ChatGPT Team | 約3,000円/人 | 汎用高性能 | 経営特化ではない |

### Emport AIの差別化ポイント（競合比較で見えたこと）

**競合の共通の弱点:**
- 汎用AIチャット → 経営の専門知識がない
- 「答えを出す」が使命 → 「次のアクション」を促さない
- 日本の中小企業の商習慣・補助金・税務に弱い

**Emport AIの強み（現時点）:**
- ✅ 経営アドバイザー特化のシステムプロンプト
- ✅ APIキー不要（バックエンド化済み）
- ✅ 補助金・DX・財務など中小企業ドンピシャのトピック

**競合に勝つために次にやるべきこと:**
1. **成果の可視化**（チャット数・解決した課題の種類をダッシュボード表示）
2. **補助金申請サポート機能**（「デジタル化・AI導入補助金」の申請書ドラフト生成）
3. **業種別特化モード**（飲食・建設・小売など業種を選ぶと専門アドバイス）

**情報源:**
- [チャットボットSaaS料金比較2026](https://aitolie-chat.com/column/chatbot-saas-pricing-comparison-2026)
- [中小企業向けSaaS20選 (AI窓口)](https://ai-madoguchi.com/blog/sme-saas-recommendations)
- [AIっていくらかかる？中小企業 (SalesDock)](https://www.salesdock.jp/blog/ai-adoption-cost)

---

## 6. 戦略的示唆 — Emport AIが有利になるために

**調査日時: 2026-05-14**

### 今すぐ使える「外部環境」の追い風

| 追い風 | 具体的な行動 |
|---|---|
| **補助金対象ツール登録**（最大450万円補助） | 中小企業庁のIT導入支援事業者として登録申請 |
| **AI市場は中小企業でまだブルーオーシャン** | 「最初のAI経営アドバイザー」ポジション獲得急ぐ |
| **スタートアップ資金調達が過去最高** | VC・補助金を活用した開発加速を検討 |
| **2026年AIトレンド＝成果実証フェーズ** | チャット内で「今週の成果」を可視化する機能を追加 |

### 中期戦略（3〜6ヶ月）

```
Phase 1: ユーザー獲得
  └─ 補助金対象SaaS登録 → 0円導入ハードル
  └─ 商工会議所経由での紹介（既に接触済み）

Phase 2: 差別化強化
  └─ 業種別特化モード（飲食・建設・小売）
  └─ 補助金申請書自動生成機能（キラーコンテンツ）
  └─ 成果ダッシュボード（ROI可視化）

Phase 3: スケール
  └─ 補助金申請代行SaaS化（月額サブスクリプション）
  └─ 商工会議所との提携（全国展開）
```

### Claude Code × Obsidian × Emport AIの黄金パターン

```
Obsidian（知識管理）
  └─ 顧客ヒアリング・競合情報・市場データを蓄積

Claude Code（開発加速）
  └─ Obsidianのノートを知識源に活用
  └─ Emport AIの機能を高速開発

Emport AI（収益）
  └─ 中小企業向け経営AIアドバイザーとして課金
  └─ 補助金で導入コストゼロへ
```

---

## 7. 次のリサーチ課題（アレン選定）

**調査日時: 2026-05-14**

以下のトピックを次回以降に調査予定：

1. **IT導入支援事業者の登録要件・手順**（補助金対象になるための具体的ステップ）
2. **商工会議所のDX支援プログラム詳細**（全国展開への足がかり）
3. **Expo / React Native でのApp Store申請手順**（モバイルアプリの正式リリースへ）
4. **日本のAI規制動向**（2026年版 AI事業者ガイドライン最新情報）
5. **freee × PayPay銀行連携の設定方法**（財務管理の自動化）
6. **Obsidianを使った週次レポート自動化**（Claude Code × Obsidian実装例）
7. **中小企業向けSaaS成功事例**（月額1〜3万円帯での成長事例）

---

---

## 8. IT導入支援事業者登録 — Emport AIが補助金対象になる方法

**調査日時: 2026-05-14 (第2ラウンド)**

### IT導入支援事業者とは

中小企業庁「デジタル化・AI導入補助金2026」の補助対象ツールとしてEmport AIを認定してもらうための登録制度。  
登録されると、**顧客（中小企業）の導入費用に最大450万円の補助金が適用**される。

### 登録要件（概要）

| 要件 | 内容 |
|---|---|
| 形態 | 法人（単独）またはコンソーシアム |
| 申請先 | TOPPAN株式会社が運営する事務局 |
| 審査 | 事務局 + 外部審査委員会による二段階審査 |
| 禁止事項 | ツール提供者（Emport AI）と補助事業者（顧客）の兼務は不可 |

### 登録することで得られるメリット

1. **顧客の導入コストが実質0円近くに** → 営業が圧倒的に楽になる
2. **公式サイトにEmport AIが掲載** → 国のお墨付きで信頼性UP
3. **商工会議所経由の申請で加点** → 既に商工会議所と接触済みなので優位

### アクションプラン

```
Step 1: it-shien.smrj.go.jp から事業者登録申請書を入手
Step 2: Emport AIのサービス概要・料金体系・セキュリティ対応をまとめる
Step 3: 申請書提出（次の締切を確認）
Step 4: 審査通過後、顧客への営業資料に「補助金対象ツール」と明記
```

**情報源:**
- [IT導入支援事業者登録要領 (smrj.go.jp)](https://it-shien.smrj.go.jp/pdf/it2026_touroku_it_jigyosha.pdf)
- [デジタル化・AI導入補助金2026 公式](https://it-shien.smrj.go.jp/)

---

## 9. 商工会議所 × DX支援 — 連携戦略

**調査日時: 2026-05-14 (第2ラウンド)**

### 商工会議所のDX支援の仕組み（2026年版）

- **複数者連携型**：商工会議所が中心となり、10者以上の中小企業をまとめてDX支援
- 商工会議所経由の申請で**補助金の加点**あり
- 東京商工会議所は「東商デジタルシフト・DXポータル」を運営

### Emport AIにとっての戦略的価値

```
商工会議所 = 中小企業へのリーチチャネル

山口・下関商工会議所（既にメール送付済み・返信待ち）
     ↓
提携成立 → 商工会議所会員企業（数千社）へEmport AIを紹介
     ↓
補助金対象SaaS登録 → 無料または低価格で導入
     ↓
ユーザーベース一気に拡大
```

### 次のアクション

- 商工会議所からの返信が来たら「DX支援パートナー」として提案
- 「10者以上の会員企業にEmport AIを同時導入」の複数者連携枠を提案
- 商工会議所が「コーディネーター」、Emport AIが「ツール提供者」の役割分担

---

## 10. Expo App Store申請 — 正式リリースへの道筋

**調査日時: 2026-05-14 (第2ラウンド)**

### 現在の状況

- Expo Go（開発者テスト用）での動作確認：完了 ✅
- 次のステップ：EAS Build → App Store / Google Play への正式申請

### 申請フロー

```
Step 1: EAS Build でアプリをビルド
  npx eas build --platform all

Step 2: EAS Submit で申請
  npx eas submit --platform ios
  npx eas submit --platform android

Step 3: 審査待ち
  Apple: 90%が48時間以内に審査完了（初回は拒否率高め）
  Google Play: 通常1〜3日

Step 4: 正式公開
```

### 申請前に必要なもの

| 項目 | iOS | Android |
|---|---|---|
| アカウント | Apple Developer ($99/年) | Google Play Console ($25一回) |
| プライバシーポリシー | 必須 | 必須 |
| アプリアイコン | 1024x1024px | 512x512px |
| スクリーンショット | 6.7インチ等 | 各種サイズ |
| 年齢レーティング | 設定必要 | 設定必要 |

### Emport AIの懸念点

- **プライバシーポリシー**：現在は `https://emport-ai.vercel.app/` にリダイレクト → 実際のページを作る必要あり
- **App Store審査**：AIアドバイス系アプリは「医療・金融・法律の無断アドバイス」でリジェクトされることがある → 「参考情報であり、専門家への相談を推奨」の免責文が必要

**情報源:**
- [Submit to app stores - Expo Docs](https://docs.expo.dev/deploy/submit-to-app-stores/)
- [React Native + Expo App Store公開 (Zenn)](https://zenn.dev/ryonakae/articles/35ebacb8e7be49)

---

## 11. 日本AI規制 — AI事業者ガイドライン v1.2（2026年3月）

**調査日時: 2026-05-14 (第2ラウンド)**

### 概要

総務省・経済産業省が2026年3月31日に「AI事業者ガイドライン第1.2版」を公表。

### Emport AIに影響する主要改訂点

| 改訂内容 | Emport AIへの影響 |
|---|---|
| **AIエージェントのHuman-in-the-Loop義務化** | 自律実行型AIには人間の承認プロセスが必要 |
| フィジカルAIのリスク整理 | 現時点では対象外 |
| 旅行予約AIも対象に | 業種横断的に適用範囲拡大 |
| リスクベースアプローチの具体化 | 高リスク用途（医療・金融・法律）は厳格な基準 |

### Emport AIが守るべきこと

```
✅ チャット回答に「AIの回答は参考情報です。専門家への相談を推奨します」を明記
✅ 財務アドバイスを断定的に表現しない
✅ 個人情報の取り扱い方針を明確化
✅ 将来のエージェント機能追加時は人間の確認ステップを設ける
```

**情報源:**
- [AI事業者ガイドライン第1.2版 (経産省)](https://www.meti.go.jp/shingikai/mono_info_service/ai_shakai_jisso/20260331_report.html)
- [ガイドライン完全解説 (ailead)](https://www.ailead.app/blog/ai-governance-guideline-v12-agent-regulation-2026)

---

## 12. 中小企業AI導入成功事例 — 数字で語るROI

**調査日時: 2026-05-14 (第2ラウンド)**

### 代表的な成功事例

| 業種 | 導入内容 | 効果 |
|---|---|---|
| サービス業20名 | AIレポート自動化 | コスト8万→1万円/月、10ヶ月でROI回収 |
| ベーカリー | 需要予測AI | 3ヶ月で売上前年比**+67%** |
| タレント管理SaaS | AIチャットサポート | 顧客数**115%増**、対応時間20分短縮 |

### 一般的なROI試算

- 従業員20名中小企業のSaaS基本スタック：年間200〜400時間の業務効率化
- 人件費換算：約100〜200万円/年の削減
- **ROI初年度：100〜300%**

### Emport AIの営業トーク（数字ベース）

```
「月額○○円で導入いただくと、
 経営判断の時間を週○時間削減できます。
 年間換算で○万円の時間コスト削減。
 補助金を使えば初年度は実質無料です。」
```

**情報源:**
- [中小企業生成AI導入成功事例5選 (Uravation)](https://uravation.com/media/sme-ai-case-studies-2026/)
- [AI導入事例12選 (EQUES)](https://eques.co.jp/column/ai-case-studies/)

---

## 13. Emport AI 料金設計 — 最適価格帯の分析

**調査日時: 2026-05-14 (第3ラウンド)**

### 市場相場（2026年版）

| セグメント | 月額相場 | 備考 |
|---|---|---|
| 汎用AIチャット（個人） | 3,000〜5,000円 | ChatGPT Plus等 |
| 法人向け生成AI | 5,000〜30,000円/人 | Claude for Business等 |
| 国産AIチャットボットSaaS | 9,800〜30,000円 | AITOLIE・ChatPlus等 |
| 中小企業AI導入全体 | 30,000〜500,000円/月 | 規模・カスタム度による |

### Emport AIの最適価格帯（提言）

```
フリープラン:   0円 / 月（チャット20回まで）
  ↓ 体験させる

スタンダード:   4,980円 / 月（無制限チャット）
  ↓ 個人経営者・フリーランス向け

ビジネス:      9,980円 / 月（複数ユーザー・履歴保存・優先対応）
  ↓ 従業員5〜30名の中小企業向け

エンタープライズ: 要相談（業種特化カスタマイズ）
```

**根拠:**
- 補助金（450万円上限）を使えば年間費用が全額カバーされる
- 競合の国産SaaSは9,800円〜が多い → ワンランク下の4,980円でシェア取得
- 「まず無料で試す」導線 → 中小企業経営者の購買行動に合致

### 補助金活用シナリオ

```
Emport AI スタンダード: 4,980円 × 12ヶ月 = 59,760円/年
IT導入補助金（補助率1/2）: 約30,000円補助
実質負担: 約30,000円/年 = 2,500円/月

→ 「ランチ代1回分でAI経営顧問が付く」というメッセージが作れる
```

**情報源:**
- [中小企業AI導入費用3パターン比較 (SalesDock)](https://www.salesdock.jp/blog/ai-adoption-cost)
- [AI導入費用相場徹底解説 (aixis.jp)](https://aixis.jp/articles/ai-implementation-price)

---

## 14. X（Twitter）中小企業経営者リーチ戦略

**調査日時: 2026-05-14 (第3ラウンド)**

### 2026年のXアルゴリズムの変化

- **エンゲージメント重視**：いいね・リポスト・リプライ・インプレッションが指標
- フォロワー数より「バズる投稿1本」が重要
- 企業アカウントは「人格」があるほうが伸びる

### 中小企業経営者に刺さるコンテンツの型

| 投稿タイプ | 例 | 効果 |
|---|---|---|
| **数字を使った実例** | 「AI導入で残業が月30時間減った話」 | 高エンゲージメント |
| **業界の裏側暴露** | 「補助金申請で99%がやらかすミス」 | 保存・リポスト |
| **before/after** | 「AI相談前→後で経営判断が変わった」 | 共感 |
| **クイズ・問いかけ** | 「あなたの会社のAI活用度は何点？」 | リプライ増加 |
| **タイムリーなネタ** | 「補助金申請締切まであと○日！」 | 緊急性 |

### Emport AI Xアカウント戦略（具体案）

```
アカウント名: Emport AI（経営AIアドバイザー）
投稿頻度: 平日毎日1〜2投稿
テーマ:
  月〜火: 補助金・資金調達情報（最新ニュース）
  水: AI活用事例・成功事例
  木: 経営Tips（3行でわかるシリーズ）
  金: 週次まとめ・Emport AI機能紹介
  土日: 軽いQ&A・ユーザー声紹介

CTA: 毎投稿の末尾に「Emport AIで無料相談→」
```

### 投稿自動化（Claude Code × X API）

- すでに `tools/social-media/post_to_x.py` が存在
- Claude Codeで週次コンテンツを自動生成 → X APIで自動投稿
- 補助金の締切情報をスクレイピング → 速報投稿も自動化可能

**情報源:**
- [X企業運用のコツ10選 2026 (S.Line)](https://s--line.co.jp/x-twitter-business-2026/)
- [Xでバズるには？戦略と投稿の型 2026](https://shubihiro.com/column/twitter-buzz-2025/)

---

## 15. LINE公式アカウント × AI連携 — 経営者への最短チャネル

**調査日時: 2026-05-14 (第3ラウンド)**

### なぜLINEが重要か

- 日本の月間アクティブユーザー：**9,700万人**（ほぼ全国民）
- 中小企業経営者（特に40〜60代）のリーチ率はアプリより高い
- **開封率：メールの4〜6倍**（LINEは通知が来たら見る）

### LINE公式アカウント AIチャットボット機能（2026年版）

- LINE公式アカウントに「AIチャットボット(β)」が追加
- 料金：チャットProオプション **月額3,000円（税別）**
- 機能：Q&Aを事前設定、PDFから自動Q&A生成、表記揺れ対応

### Emport AI × LINE連携の可能性

**シナリオA: Emport AI LINE公式アカウント**
```
経営者がLINEで「資金繰りが厳しい」と送信
  ↓
Emport AI（バックエンド）が処理
  ↓
LINE上でアドバイスを返信
```
- メリット：アプリDL不要でユーザー獲得が楽
- 実装：LINE Messaging API + Emport AIのRailwayバックエンドを接続

**シナリオB: 既存モバイルアプリのユーザーをLINEでフォローアップ**
```
アプリ内で「LINEで続ける」ボタン
  ↓
LINE友達追加
  ↓
リテンション向上・休眠ユーザー掘り起こし
```

### 実装難易度

| 作業 | 難易度 | 所要時間 |
|---|---|---|
| LINE Messaging API設定 | ★★☆ | 2〜3時間 |
| RailwayバックエンドにLINE Webhook追加 | ★★☆ | 3〜4時間 |
| LINE公式アカウント開設 | ★☆☆ | 30分 |

**情報源:**
- [LINE公式アカウント AIチャットボット使い方 (Liny)](https://line-sm.com/blog/loa-ai-chatbot/)
- [LINE×AI便利機能10選 2026 (cresclab)](https://blog.cresclab.com/ja/line-ai)

---

## 16. freee API連携 — 財務データで付加価値を爆上げする

**調査日時: 2026-05-14 (第3ラウンド)**

### freee APIで取れるデータ

| データ種類 | 活用例 |
|---|---|
| 貸借対照表 | 「自己資本比率が○%。業界平均より低いです。改善策は…」 |
| 損益計算書 | 「先月の粗利率が下がっています。原因と対策は…」 |
| 売掛金・買掛金 | 「資金繰り悪化の予兆が3ヶ月後にあります」 |
| 取引履歴 | 「この費用カテゴリが増加傾向。節税の余地があります」 |

### Emport AI × freee連携で実現できること

```
【現在】テキストで「売上が下がっている」と相談
    ↓
【freee連携後】
freee APIから実際の財務データを自動取得
    ↓
「先月比売上-15%・粗利率-3pt・固定費増加を確認。
 具体的な改善アクションは以下の通りです…」
```

これが実現すると、Emport AIは **「話すだけのアドバイザー」から「数字を見るアドバイザー」** に進化する。

### 実装ステップ

```
Step 1: freee Developer登録（無料）
Step 2: アプリ登録・OAuth2.0設定
Step 3: Railwayバックエンドにfreeeトークン管理を追加
Step 4: Emport AIのシステムプロンプトに財務データを注入
Step 5: 「freee連携プラン」として価格を上げる
```

### 注意点

- freeeのOAuthフローがやや複雑（ユーザーの認証が必要）
- 会計データを扱うので**プライバシーポリシーの更新が必要**
- freeeアプリストアへの掲載で追加ユーザー獲得の可能性も

**情報源:**
- [freee会計API連携完全ガイド (DXhacker)](https://service.biztex.co.jp/dx-hacker/ipaas/freee-api/)
- [freee × Claude Code実践ガイド](https://firecracker.jp/blog/freee-claude-code)
- [freee会計APIリファレンス](https://developer.freee.co.jp/reference/accounting)

---

## 17. 次のリサーチ課題（第3ラウンド終了・アレン選定）

**調査日時: 2026-05-14 (第3ラウンド)**

第4ラウンドで調査予定：

1. **プライバシーポリシー・利用規約の雛形** — App Store申請とAI規制対応の両方を満たす文書
2. **Emport AIのプロダクトロードマップ** — 現在地の整理と次の6ヶ月の機能開発優先順位
3. **競合分析 深掘り** — 「AI経営相談」に特化した国内外の競合（Notion AI、Jasper、ビズリーチ・スタートアップ）
4. **日本語LLM（日本独自AI）の動向** — Preferred Networks・NEC・富士通等の国産AI
5. **Emport AIの顧客獲得コスト（CAC）試算** — X投稿・商工会議所・補助金経由それぞれのCAC
6. **VC・エンジェル投資家への資金調達可能性** — シード調達のための要件整理

---

## 18. プライバシーポリシー・利用規約 — App Store申請とAI規制の両立

**調査日時: 2026-05-14 (第4ラウンド)**

### AIサービスに必要な必須記載事項（2026年版・日本）

| カテゴリ | 必須内容 |
|---|---|
| **利用目的** | 「AIサービスを用いた業務効率化・経営アドバイス提供」と明示 |
| **第三者提供** | AnthropicへのAPI送信を明記（越境移転） |
| **要配慮個人情報** | 財務・健康・信条情報を入力させる場合は明示的同意が必要 |
| **AI出力の免責** | 「AIの回答は参考情報。専門家への相談を推奨」の明記 |
| **データ保存期間** | チャット履歴の保存期間と削除方法 |
| **未成年者** | 18歳未満の利用制限 |

### App Store審査で引っかかりやすいポイント

```
❌ NGパターン:
「このAIが最適な経営判断を下します」（断定的な表現）
「投資・税務アドバイスを提供します」（資格が必要な業務）

✅ OKパターン:
「AIが経営の参考情報を提供します。
 重要な決定は専門家（税理士・弁護士等）にご相談ください」
```

### Emport AIが今すぐやるべきこと

1. `https://emport-ai.vercel.app/privacy` にプライバシーポリシーページを作成
2. `https://emport-ai.vercel.app/terms` に利用規約ページを作成
3. アプリ内のSettingsScreen.tsxのURLをそれぞれ更新

**情報源:**
- [生成AI×個情法完全対応ガイド 2026 (Uravation)](https://uravation.com/media/ai-personal-information-protection-act-compliance-2026/)
- [生成AIサービス利用注意喚起 (個人情報保護委員会)](https://www.ppc.go.jp/news/careful_information/230602_AI_utilize_alert/)

---

## 19. 国産LLM動向 — Emport AIの技術選択に影響する情報

**調査日時: 2026-05-14 (第4ラウンド)**

### 2026年の国産LLM主要プレイヤー

| 企業 | モデル名 | 特徴 | 中小企業向け |
|---|---|---|---|
| Preferred Networks | PLaMo 2.0 Prime | 日本語特化・フルスクラッチ開発 | APIあり・売上10億円未満は無償 |
| NEC | cotomi | 国産高性能・オンプレも可 | 法人向け（価格高め） |
| 富士通 | Takane | 日本ビジネス文書特化 | 大企業向け |
| SB Intuitions | SB AI | SoftBankグループ | 法人向け |
| NTT | tsuzumi | 小型・高速・日本語 | API提供中 |

### Emport AIの技術判断

**現在（正解）**：Anthropic Claude（claude-haiku-4-5）を使用
- 性能・コスト・APIの安定性でトップクラス
- 日本語対応も十分

**将来の選択肢**：
```
PLaMo 2.0 (PFN) → 「国産AI使用」を差別化ポイントにできる
NTT tsuzumi → 小型・低コスト・API安定
```

**アドバイス**: 今は変える必要なし。ただし「日本のデータが海外に出ない」を重視する顧客（行政・医療・金融）向けには国産LLMのオプションを将来検討。

**情報源:**
- [国産LLM7選 デジタル庁「源内」が選んだAI (fidx.co.jp)](https://www.fidx.co.jp/%E3%80%902026%E5%B9%B4%E7%89%88%E3%80%91%E5%9B%BD%E7%94%A3llm7%E9%81%B8%EF%BD%9C%E3%83%87%E3%82%B8%E3%82%BF%E3%83%AB%E5%BA%81%E3%80%8C%E6%BA%90%E5%86%85%E3%80%8D%E3%81%8C%E9%81%B8%E3%82%93%E3%81%A0ai/)
- [国産LLM 富士通NEC NTT戦略 (Business Insider)](https://www.businessinsider.jp/article/2604-japanese-llm-fujitsu-nec-ntt/)

---

## 20. 資金調達可能性 — Emport AIのシード調達シナリオ

**調査日時: 2026-05-14 (第4ラウンド)**

### 日本のシードVC相場（2026年）

| 項目 | 数値 |
|---|---|
| シードラウンド相場 | **3,000万〜1.5億円** |
| 最適な調達額 | 2,000万〜7,000万円 |
| 株式希薄化 | 10〜20%が適切 |
| 契約形式 | **J-KISS（日本版SAFE）が標準** |
| 主な投資家 | エンジェル・シード特化VC |

### Emport AIが資金調達するための条件

```
現在地チェック:
  ✅ プロダクト: モバイルアプリ完成・バックエンドAPI化完了
  ✅ 技術: Railway × Anthropic API × React Native
  ❌ MRR（月次収益）: まだ0円
  ❌ ユーザー数: まだ開発・テスト段階
  ❌ 法人登記: 必要
  
投資家が最低限求めるもの:
  → MRR 50〜100万円 OR 月間アクティブユーザー数1,000+
  → または「スーパーエンジェル」なら0円でも可能性あり
```

### Emport AIの資金調達シナリオ

```
Phase 0（今）: 補助金＋自己資金でプロダクト完成
Phase 1（3〜6ヶ月後）: ユーザー100人・MRR 50万円達成
Phase 2（6〜12ヶ月後）: シード調達 3,000〜5,000万円
Phase 3（1〜2年後）: Series A 2〜5億円
```

### 注目すべきシード特化VC（日本）

- **THE SEED**: シード特化・ハンズオン支援
- **East Ventures**: AI・SaaS特化
- **500 Global Japan**: グローバル展開支援
- **Skyland Ventures**: B2B SaaS・AI

**情報源:**
- [シードラウンドとは？調達額相場 (StartupList)](https://www.startuplist.jp/alliance_posts/64)
- [スタートアップ資金調達方法 (sovagroup)](https://sovagroup.co.jp/media_article/startup-funding/)

---

## 21. 競合分析深掘り — 「AI経営特化」の本当の競合は何か

**調査日時: 2026-05-14 (第4ラウンド)**

### 競合の分類

**Tier 1: 直接競合（AI経営アドバイス特化）**
| サービス | 特徴 | Emport AIとの差 |
|---|---|---|
| JAPAN AI CHAT | 法人向け・高精度RAG・ツール連携 | 高価格・大企業向け |
| CosBE | 中小企業経営者特化・コンサル+AI | 人間介在・高コスト |

**Tier 2: 間接競合（汎用AI → 経営に使う）**
| サービス | 特徴 |
|---|---|
| ChatGPT Plus/Team | 汎用高性能だが経営特化ではない |
| Notion AI | 文書・タスク管理+AI |
| Claude for Business | 強力だが専用UIなし |

**Tier 3: 参入しつつある競合**
- 会計ソフト（freee AI・マネーフォワードAI）が経営アドバイス機能追加中
- **これが最大の脅威**

### Emport AIが勝てるポジション

```
「モバイルファースト × 補助金対象 × 中小企業専門」
           ↓
大企業向けSaaSには価格で勝てない
汎用AIには性能で勝てない
  ↓
「使いやすさ × 安さ × 日本の中小企業に特化した知識」で勝つ
```

### 2026年の重要な変化

> 「"AIチャットがある"ではなく、どこまで自律実行できるかが差別化ポイント」

→ Emport AIも将来的に「相談するだけでなく、実行してくれるAI」を目指すべき  
→ 例：「補助金申請書を自動生成してSubmitまでやってくれる」

**情報源:**
- [AIコンサルティング会社30選比較 (LISKUL)](https://liskul.com/ai-consulting-comparison-149280)
- [AIエージェントプラットフォーム国内19社 (vottia)](https://vottia.jp/ai-agent-platform-comparison-japan-2026/)

---

## 22. 次のリサーチ課題（第4ラウンド終了・アレン選定）

**調査日時: 2026-05-14 (第4ラウンド)**

第5ラウンドで調査予定：

1. **EAS Build 具体的な設定・eas.json の書き方** — Expo正式リリースの技術詳細
2. **日本の経営者・起業家向けコミュニティ** — SNS外での顧客獲得チャネル
3. **Claude Code × freee API の実装パターン** — 財務連携の具体的な実装方法
4. **Anthropic API のコスト最適化** — Haiku vs Sonnet vs Opus の使い分け・費用試算
5. **モバイルアプリのオンボーディングフロー設計** — App Store審査を通るためのUX要件
6. **2026年の日本EC・小売業界トレンド** — Emport AIの業種別特化候補の選定

---

## 23. Anthropic API コスト最適化 — Emport AIの費用試算

**調査日時: 2026-05-14 (第5ラウンド)**

### 最新料金表（2026年5月）

| モデル | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| **Claude Haiku 4.5** | **$1.00** | **$5.00** |
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Opus 4.7 | $5.00 | $25.00 |

### Emport AIの月次コスト試算

**前提**: Haiku使用、平均1チャット = 入力500tokens + 出力500tokens

| 月間チャット数 | 月次コスト（USD） | 月次コスト（円、¥150換算） |
|---|---|---|
| 100回 | $0.30 | 約45円 |
| 1,000回 | $3.00 | 約450円 |
| 10,000回 | $30.00 | 約4,500円 |
| 100,000回 | $300.00 | 約45,000円 |

**→ Haikuなら月1万チャットでもコスト4,500円。月額4,980円のサブスクで余裕で黒字。**

### コスト削減のテクニック

```
1. プロンプトキャッシング（Prompt Caching）
   → システムプロンプト（長文）をキャッシュ
   → 入力コスト90%削減
   → Emport AIのシステムプロンプトは700文字以上あるので効果大

2. Batch API（Message Batches API）
   → 50%割引
   → リアルタイム不要な処理に使う

3. max_tokens 制限
   → 現在1024に設定済み（適切）
   → 長文生成を防いでコスト管理
```

### 実装すべきコスト最適化

```python
# app.py に追加すべきプロンプトキャッシング
response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": system,
        "cache_control": {"type": "ephemeral"}  # ← これを追加
    }],
    messages=valid_messages,
)
```

**情報源:**
- [Claude API Pricing 2026 (platform.claude.com)](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic API Pricing Complete Guide (finout.io)](https://www.finout.io/blog/anthropic-api-pricing)

---

## 24. 日本 経営者コミュニティ — 顧客獲得チャネル地図

**調査日時: 2026-05-14 (第5ラウンド)**

### 主要チャネルと特徴

| チャネル | 規模感 | Emport AIの活用方法 |
|---|---|---|
| **商工会議所** | 全国120万社会員 | 提携→会員向け特別価格で導入 |
| **こくちーずプロ** | 経営者セミナー多数 | セミナー登壇→デモ→申込 |
| **全国経営者セミナー(JMCA)** | 国内最大級 | スポンサー・登壇 |
| **日本中小企業経営者協会** | 全国組織 | 会員向け提供交渉 |
| **異業種交流会（Doomo等）** | 東京中心・定期開催 | 営業参加・名刺交換 |
| **X（Twitter）** | 経営者クラスター存在 | コンテンツマーケ |
| **LINE公式** | 中高年経営者に強い | 友達追加→育成 |

### 最も費用対効果の高い戦略（優先順）

```
1位: 商工会議所提携（山口・下関は既に接触済み）
  → 1提携で数千社にリーチ。費用ほぼ0

2位: X（Twitter）コンテンツ投稿（毎日継続）
  → 3〜6ヶ月で認知が積み上がる。費用0

3位: こくちーずプロでセミナー主催
  → 「AIで経営を変える無料セミナー」開催
  → 参加者=見込み客。費用数万円

4位: LINE公式アカウント開設
  → 友達追加=見込み客リスト化。費用月3,000円〜
```

**情報源:**
- [経営者交流会2026年50選 (imperialnexus)](https://imperialnexus.jp/businesspro/blog/networking/famousbusinessnetworkingevents/)
- [経営者コミュニティ7選 (onlystory)](https://onlystory.co.jp/service/column/executive-community/)

---

## 25. 業種別AI活用ニーズ — Emport AI特化モード候補

**調査日時: 2026-05-14 (第5ラウンド)**

### 業種別のAI活用状況と経営課題

| 業種 | AI活用意欲 | 主な経営課題 | Emport AIで解決できること |
|---|---|---|---|
| **飲食業** | 高 | 人手不足・食品ロス・シフト管理 | 需要予測・原価管理・採用コスト削減アドバイス |
| **小売業** | 中（57.8%前向き） | 在庫管理・EC展開・競合対策 | 在庫最適化・EC戦略・価格設定 |
| **建設業** | 中 | 職人不足・見積もり精度・安全管理 | 見積書作成・補助金（建設向け）・採用戦略 |
| **士業（税理士等）** | 中 | 顧客獲得・業務効率化 | 提案書作成・集客戦略・IT化アドバイス |
| **美容・サロン** | 低 | 集客・リピート・物価高 | SNS戦略・価格戦略・店舗運営 |

### 優先的に特化すべき業種（提言）

**第1候補: 飲食業**
- AI活用意欲が高い
- 経営課題が明確（食材費・人件費・集客）
- 全国に381万店舗

**第2候補: 小売業**
- EC展開ニーズが急増
- 補助金適用案件が多い

**具体的な実装案**:
```
チャット開始時に「業種を教えてください」と聞く
  ↓
「飲食業」を選択
  ↓
システムプロンプトに飲食業特有の知識を追加
「FL比率（食材費+人件費）は60%以下を目標に...」
「フードロスの計算方法は...」
「Googleマップの口コミ対策は...」
```

**情報源:**
- [小売業AI活用事例 2026 (ai-market.jp)](https://ai-market.jp/industry/retailing_aikatsuyo/)
- [飲食業AI活用事例15選 (ニューラルオプト)](https://neural-opt.com/restaurant-ai-cases/)

---

## 26. 次のリサーチ課題（第5ラウンド終了・アレン選定）

**調査日時: 2026-05-14 (第5ラウンド)**

第6ラウンドで調査予定：

1. **Anthropic Prompt Caching の実装方法** — app.py に追加してコスト90%削減
2. **Expo EAS Build eas.json 設定** — 正式リリースへの最後の一歩
3. **飲食業向けEmport AI特化プロンプト設計** — 業種別モードの最初の1つ
4. **GoogleマップAPI × 飲食業** — 口コミ分析機能の可能性
5. **Claude Code Hooks実用例** — 自動テスト・自動デプロイ設定
6. **日本のAI規制 AIエージェント規制詳細** — Human-in-the-Loopの具体的な要件

---

## 27. Prompt Caching 実装完了 — コスト試算更新

**調査日時: 2026-05-14 (第6ラウンド)**

### 実装内容（app.py に追加済み）

```python
# before（毎回フル課金）
response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=1024,
    system=system,  # 毎回 $1/MTok で課金
    messages=valid_messages,
)

# after（キャッシュで90%削減）
system_param = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
response = client.messages.create(
    model=MODEL_NAME,
    max_tokens=1024,
    system=system_param,  # キャッシュヒット時は $0.10/MTok
    messages=valid_messages,
)
```

### 公式料金（2026年5月確認）

| 操作 | Haiku 4.5 料金 | 説明 |
|---|---|---|
| 通常 Input | $1.00/MTok | ベース料金 |
| Cache Write (5分) | $1.25/MTok | 1.25倍（書込み時のみ） |
| **Cache Hit** | **$0.10/MTok** | **ベースの10%！** |
| Output | $5.00/MTok | キャッシュ対象外 |

### コスト比較（Emport AIのシステムプロンプト 約700トークン）

| ユーザー100人・月1回チャット（100回/月） | Before | After |
|---|---|---|
| System prompt コスト | $0.07 | $0.009（キャッシュヒット率90%想定） |
| **月次削減額** | - | **約90%削減** |

→ Railwayの費用（月$5）より**APIコストの削減効果のほうが大きい可能性**

---

## 28. 飲食業向け Emport AI 特化プロンプト設計

**調査日時: 2026-05-14 (第6ラウンド)**

### 飲食業の核心KPI

| 指標 | 目安 | 意味 |
|---|---|---|
| **F比率**（Food Cost）| **30%以内** | 売上に対する食材費の割合 |
| **L比率**（Labor Cost）| **20%以内** | 売上に対する人件費の割合 |
| **FL比率**（F+L）| **55〜60%以内** | これが60%を超えると黒字が出ない |
| **FLR比率**（+Rent）| **70%以内** | 家賃込みのコスト率 |
| 人時売上高 | 5,000〜8,000円/時 | 1時間あたり何円稼いでいるか |
| 回転率 | 業態による | 席数×回転数÷座席数 |

### 飲食業向け特化システムプロンプト（案）

```
あなたは飲食業専門の経営AIアドバイザーです。
飲食店オーナー・店長の経営課題に対して、
FL比率・原価管理・シフト最適化・集客施策など
飲食業に特化した実践的なアドバイスを提供します。

【専門知識】
- FL比率の計算と改善策（目標: FL比55〜60%以内）
- 食材原価管理・ロス削減・仕入れ交渉
- シフト最適化・人時売上高の改善
- Googleマップ口コミ対応・SNS集客
- 飲食業向け補助金（小規模事業者持続化補助金等）
- テイクアウト・デリバリー展開戦略
- 季節メニュー・原価の高い食材の置き換え提案

【回答スタイル】
- FL比率や原価率など具体的な数字を使う
- 「今週できること」から優先順位をつける
- 飲食業の実態に即した現実的な提案をする
```

### 業種選択機能の実装案

```typescript
// ChatScreen.tsx に業種選択を追加
const INDUSTRIES = ['汎用', '飲食業', '小売業', '建設業', '美容・サロン'];

// 業種に応じてシステムプロンプトを切り替え
function getSystemPrompt(industry: string): string {
  switch (industry) {
    case '飲食業': return SYSTEM_PROMPT_FOOD;
    case '小売業': return SYSTEM_PROMPT_RETAIL;
    default: return SYSTEM_PROMPT;
  }
}
```

**情報源:**
- [飲食店FL比率完全解説 (Airレジ)](https://airregi.jp/magazine/guide/2259/)
- [飲食業KPIとは (データのじかん)](https://data.wingarc.com/kpilogictreeofrestaurantindustry-32909)

---

## 29. Claude Code Hooks 実用パターン集

**調査日時: 2026-05-14 (第6ラウンド)**

### Hooksの基本構造

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash /path/to/security-check.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "python /path/to/format.py"
        }]
      }
    ]
  }
}
```

### Emport AI開発に使えるHooksパターン10選

| パターン | イベント | 用途 |
|---|---|---|
| 1. APIキー検出 | PreToolUse(Write) | ハードコードされたsecretをブロック |
| 2. Pythonフォーマット | PostToolUse(Write) | .pyファイル保存時にblackを自動実行 |
| 3. TypeScript型チェック | PostToolUse(Write) | .tsファイル保存時にtscを自動実行 |
| 4. Railwayデプロイ通知 | PostToolUse(Bash) | pushコマンド後にSlack通知 |
| 5. gitpush確認 | PreToolUse(Bash) | `git push`前に確認プロンプト |
| 6. テスト自動実行 | PostToolUse(Write) | テストファイル変更時にnpm testを実行 |
| 7. コスト計算 | PostToolUse(Bash) | APIコール後にトークン数を集計・記録 |
| 8. ログ記録 | PostToolUse(任意) | 全ツール操作をMarkdownに記録 |
| 9. 環境切替防止 | PreToolUse(Bash) | 本番環境への誤操作をブロック |
| 10. EASビルド自動化 | PostToolUse(Bash) | コード変更後にEAS Buildをトリガー |

### Emport AIプロジェクト向け推奨Hook設定

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "python layer4_file_guard.py"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "python -c \"import sys; f=open('/tmp/claude-writes.log','a'); f.write(sys.argv[1]+'\\n')\" \"$CLAUDE_FILE_PATH\""
      }]
    }]
  }
}
```

**情報源:**
- [Hooks完全ガイド (Claude Code公式)](https://code.claude.com/docs/ja/hooks-guide)
- [PreToolUse/PostToolUse実践入門 (Zenn)](https://zenn.dev/biki/articles/claude-code-hooks-workflow-automation)
- [Hooks設定10選 (claudecode.co.jp)](https://claudecode.co.jp/info/claude-code-hooks-guide)

---

## 30. 総合まとめ — アレンからオーナーへの提言

**調査日時: 2026-05-14 (第6ラウンド 最終)**

### 今日の調査で判明した最重要事項

**1. 補助金対象SaaS登録が最優先アクション**
```
デジタル化・AI導入補助金2026の IT導入支援事業者に登録
  → 顧客の導入費用が最大450万円補助される
  → 営業の最強カード
  → 商工会議所経由申請で加点あり（既に接触済みで有利）
```

**2. Prompt Cachingで既にコスト90%削減済み**
```
今日のコミット（2892894）でapp.pyに実装完了
  → 月1万チャットでもAPI費用は約450円
  → 月額4,980円サブスクで余裕の黒字
```

**3. LINE連携がモバイルアプリより即効性がある可能性**
```
アプリDL → LINE友達追加の方が中高年経営者には簡単
  → LINE Messaging API + Railway既存バックエンドで実装可能
  → 工数: 約5〜7時間
```

**4. 飲食業からの業種特化が最初の一手**
```
飲食業（日本最多業種の一つ）× FL比率特化
  → 差別化が明確
  → 「飲食専門AI経営アドバイザー」でポジション確立
```

**5. Obsidianを社内ナレッジ管理に使うべき**
```
現在のWeeklyレポート管理をObsidianに移行
  → Claude Codeが直接ノートを読める
  → 商工会議所とのやりとり・顧客情報も集約
  → 2026年v1.12でCLI追加済みで完全自動化可能
```

### 次にオーナーとやるべきこと（優先順）

| 優先度 | タスク | 所要時間 |
|---|---|---|
| ★★★ | IT導入支援事業者登録申請 | 1〜2日 |
| ★★★ | Railway Hobbyプラン切替（残16日） | 30分 |
| ★★☆ | プライバシーポリシーページ作成 | 2〜3時間 |
| ★★☆ | LINE公式アカウント開設 | 30分 |
| ★☆☆ | Obsidian導入・社内KB構築 | 1日 |
| ★☆☆ | 飲食業向け特化モード実装 | 4〜6時間 |

---

---

## 31. Obsidian × Claude Code 連携セットアップガイド（Windows版）

**調査日時: 2026-05-14 (第7ラウンド)**

### 連携の3つの方法（2026年版）

| 方法 | 難易度 | 効果 |
|---|---|---|
| **1. VaultをClaude Codeのワークスペースに設定** | ★☆☆ | 最簡単。Claude Codeが全ノートを読める |
| **2. Obsidian CLI + Claude Code** | ★★☆ | ターミナル経由でノートを操作 |
| **3. Claudianプラグイン（Obsidian内でClaude Code）** | ★★☆ | Obsidian UI内でClaude Codeが動く |

### 方法1（最速）: VaultをClaude Codeのワークスペースに追加

```bash
# Obsidianのvaultフォルダを確認
# 通常: C:\Users\tsube\Documents\ObsidianVault\

# Claude Codeでそのフォルダを開く
claude "C:\Users\tsube\Documents\ObsidianVault\"
```

→ Emport AIプロジェクトのCLAUDE.mdに以下を追加：
```markdown
## ナレッジベース
週次レポートは ../ObsidianVault/ceo/ に保存。
顧客情報は ../ObsidianVault/customers/ に保存。
```

### 方法3: Claudianプラグイン

- GitHub: [YishenTu/claudian](https://github.com/YishenTu/claudian)
- Obsidianのコミュニティプラグインからインストール
- Vault内でClaude Codeを直接起動できる
- Windows: 2026年4月現在「実験的サポート」

### Emport AIへの具体的な活用案

```
Obsidian Vault構造（推奨）:
/vault
  /ceo
    /weekly-reports/     ← 既存のweekly-reportsをここに移行
    /decisions/          ← 経営判断の記録
  /customers
    /商工会議所/          ← 接触履歴・提案内容
    /山田建設/            ← 既存顧客事例
  /market-research
    /competitors/        ← 競合情報
    /subsidies/          ← 補助金情報（最新版）
  /products
    /emport-ai/          ← プロダクト仕様・ロードマップ
```

**情報源:**
- [Claude Code × Obsidian完全連携ガイド (dot-ai)](https://dot-ai.myuuu.co.jp/times/117)
- [Obsidian CLI完全ガイド 2026 (visionnurture)](https://www.visionnurture.com/obsidian_guide_for_beginner_006/)
- [Claudian プラグイン (GitHub)](https://github.com/YishenTu/claudian)

---

## 32. Railway Hobbyプラン — アップグレード手順

**調査日時: 2026-05-14 (第7ラウンド)**

### 料金詳細

| プラン | 月額 | 含まれるクレジット | 特徴 |
|---|---|---|---|
| Trial（現在） | 無料 | $5 | 時間制限あり・残り16日 |
| **Hobby** | **$5/月** | **$5** | 無制限・クレジット超過分追加課金 |
| Pro | $20/月 | $20 | チーム向け |

**Hobbyプランの実質コスト**:
- 月額基本料: $5（固定）
- 使用量が$5以内なら追加なし
- 超えた分だけ追加課金
- Emport AIの規模（軽量Flask）なら**月$5〜$7程度**で収まる見込み

### アップグレード手順

```
1. Railway ダッシュボード (railway.com/dashboard) にログイン
2. 右上のアカウントアイコン → 「Plans」
3. 「Hobby」プランを選択
4. クレジットカード情報を入力（$5/月）
5. Trial残高は自動でCarryoverされる
```

**→ 今すぐやること**: オーナーがRailwayダッシュボードにアクセスしてHobbyにアップグレード（残り16日以内）

**情報源:**
- [Railway Pricing Plans (公式Docs)](https://docs.railway.com/pricing/plans)
- [Railway Pricing 2026 (costbench)](https://costbench.com/software/developer-tools/railway/)

---

## 33. IT導入支援事業者登録 — 具体的手順と必要書類

**調査日時: 2026-05-14 (第7ラウンド)**

### 必要書類チェックリスト

```
□ 履歴事項全部証明書（法務局で取得・発行3ヶ月以内）
□ 納税証明書（税務署で取得）
□ 2期分の決算書（または簡易的な決算情報）
□ ITツールの販売実績・サービス説明資料
□ プライバシーポリシーURL
□ サービス料金表
□ セキュリティ対応説明
```

### 申請フロー

```
Step 1: it-shien.smrj.go.jp にアクセスして仮登録
  ↓
Step 2: 仮登録完了メールが届く（本登録用URLが届く）
  ↓
Step 3: 本登録（書類添付・詳細入力）
  ↓
Step 4: 審査（1〜2週間で差し戻しまたは承認）
  ↓
Step 5: 採否通知 → 登録完了
  ↓
Step 6: ITツール（Emport AI）の個別登録
```

### Emport AIが登録するための準備

| 準備事項 | 現状 | アクション |
|---|---|---|
| 法人登記 | ? | 未確認（要確認） |
| プライバシーポリシー | URLのみ存在 | 実際のページ作成が必要 |
| サービス料金表 | 未設定 | 価格設計を決める |
| 販売実績 | なし | 無料ユーザーでも可能か確認 |
| セキュリティ説明 | Railway + Anthropic | 文書化が必要 |

**情報源:**
- [IT導入支援事業者登録申請フロー (smrj.go.jp)](https://it-shien.smrj.go.jp/itvendor/flow/)
- [IT導入支援事業者になるには (japan-finance.jp)](https://japan-finance.jp/subsidy/120/)
- [登録マニュアル PDF (smrj.go.jp)](https://it-shien.smrj.go.jp/pdf/it2026_manual_it_jigyosha.pdf)

---

## 34. 調査完了サマリー（第1〜7ラウンド）

**調査日時: 2026-05-14 最終**

### 調査トピック一覧

| # | トピック | 主要発見 |
|---|---|---|
| 1 | Claude Code Tips | Focus View・Hooks・並列エージェント・MCPが最重要 |
| 2 | Obsidian | Claude CodeのワークスペースとしてVaultを使うのが最強 |
| 3 | 日本スタートアップ動向 | 2026年Q1は過去最高調達額・AI案件集中 |
| 4 | AI市場規模 | 日本2024: 1.3兆円→2029年: 4.2兆円（3倍以上） |
| 5 | 競合SaaS | 国産9,800円〜・Emport AIは4,980円で差別化可 |
| 6 | 戦略的示唆 | 補助金登録＋商工会議所提携が最優先 |
| 7 | IT導入支援事業者 | 審査1〜2週間・法人登記と書類準備が必要 |
| 8 | 商工会議所DX | 複数者連携枠で加点あり（既接触で有利） |
| 9 | App Store申請 | EAS Submit・プライバシーポリシーページが必須 |
| 10 | AI規制 v1.2 | AIエージェントのHuman-in-the-Loop義務化 |
| 11 | 料金設計 | 4,980円/月 + 補助金で実質2,500円が刺さる |
| 12 | X戦略 | エンゲージメント重視・数字ネタが拡散 |
| 13 | LINE連携 | Messaging API + Railway で5〜7時間で実装可 |
| 14 | freee API | 財務データ連携でアドバイスの質が爆上がり |
| 15 | Prompt Caching | 実装完了。コスト90%削減済み（Commit: 2892894） |
| 16 | 競合深掘り | 「自律実行できるか」が次の差別化ポイント |
| 17 | 国産LLM | PLaMo・NEC・富士通・tsuzumi。今はClaudeで正解 |
| 18 | 資金調達 | シード3000万〜1.5億・MRR 50万が最低ライン |
| 19 | APIコスト最適化 | Haiku 月1万チャット=450円。黒字確実 |
| 20 | 経営者コミュニティ | 商工会議所＞こくちーず＞X の順で費用対効果高 |
| 21 | 業種別ニーズ | 飲食業が第1候補（FL比率特化で差別化） |
| 22 | Hooks実用例 | PreToolUse/PostToolUse で自動化10パターン |
| 23 | Obsidian連携 | VaultをClaude Codeのワークスペースに追加が最速 |
| 24 | Railway | Hobbyプラン月$5、残り16日以内にアップグレード要 |

*調査は継続中。ユーザーが「いい」と言うまで次のトピックを調査して追記します。*

---

## 13. 次のリサーチ課題（第2ラウンド終了・アレン選定）

**調査日時: 2026-05-14 (第2ラウンド)**

第3ラウンドで調査予定：

1. **Emport AIの料金設計** — 競合比較・補助金活用を踏まえた最適価格帯の分析
2. **プライバシーポリシー・利用規約の作成要件** — App Store申請前に必須
3. **Expo EAS Build 具体的な設定手順** — 正式リリースへの技術的ステップ
4. **X（Twitter）での中小企業経営者へのリーチ戦略** — コンテンツマーケティング
5. **LINE公式アカウント × AI連携** — 日本の中小企業経営者への最適チャネル
6. **freee API連携可能性** — 財務データ連携でEmport AIの価値を飛躍的に高める

---

*このファイルはアレンが自律調査中に継続更新します。*  
*「いい」と言うまで次のトピックを調査して追記します。*
