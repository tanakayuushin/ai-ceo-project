# ツール導入状況レポート
> 作成: 2026-05-17 by CEO Allen
> 目的: 最強環境ツールスタックの導入進捗と各ツールのURL/設定情報を管理

---

## ✅ 導入完了

### #1 GitHub MCP
- **状態**: 完了
- **設定**: `~/.claude.json` に `@github/mcp-server` 追加済み
- **環境変数**: `GITHUB_TOKEN` を Windows ユーザー環境変数に設定済み
- **再起動後に有効化**: Claude Code 再起動で接続確立

### #1 Notion MCP
- **状態**: 完了
- **設定**: `~/.claude.json` に `@notionhq/notion-mcp-server` 追加済み
- **API Key**: `NOTION_API_KEY` を `~/.claude.json` の env に設定済み
- **PAT**: `ntn_***（環境変数 NOTION_API_KEY に設定済み）`

### #2 Tally フォーム
- **状態**: 完了
- **フォーム名**: AI導入相談フォーム（Emport AI）
- **URL**: https://tally.so/r/（Tallyダッシュボードで確認）
- **項目**: お名前・メールアドレス・会社名・業種・AI活用の悩み・ご要望

### #3 HubSpot 無料CRM
- **状態**: 完了
- **アカウント**: tsubeyou081@gmail.com
- **ポータルID**: 246222751
- **ダッシュボードURL**: https://app-na2.hubspot.com/contacts/246222751
- **Gmail連携**: tsubeyou081@gmail.com 接続済み・9社自動同期済み
- **同期済み会社**: HubSpot, Uber, 中国新聞, SBI Sumishin Net Bank, Dan Martell, Tポイント, 株式会社フォーラムエン, 国立大学法人 山口大学 など

### #4 Jicoo 日程調整
- **状態**: 完了
- **アカウント**: tsubeyou081@gmail.com
- **チーム名**: Emport AI
- **Googleカレンダー連携**: tsubeyou081@gmail.com 接続済み
- **稼働時間**: 月〜金 10:00-19:00
- **予約ページURL（AI無料相談30分）**: https://www.jicoo.com/t/FNs9T5F423Pm/e/U_S3ek97
- **予約ページURL（60分ミーティング）**: https://www.jicoo.com/t/FNs9T5F423Pm/e/DUo0qQSz
- **個人予約ページ**: https://www.jicoo.com/t/FNs9T5F423Pm/users/Mp1mxPCg
- **ロケーション**: Google Meet（ゲスト選択式）

### #5 Gamma 提案書テンプレート
- **状態**: 完了
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **作成ドキュメント**: Emport AIによるAI導入支援提案書（10スライド）
- **ドキュメントURL**: https://gamma.app/docs/Emport-AIAI-r210yhsdqwdkamg
- **内容**: タイトル・課題提起・会社紹介・業種別事例・ロードマップ・料金プラン・補助金支援・CTA・クロージング
- **テーマ**: ダークブルー系プロフェッショナルデザイン

### #8 Looker Studio KPIダッシュボード
- **状態**: データ接続完了・チャート追加は手動で実施（Canvas操作のため）
- **アカウント**: yuubisinesu@gmail.com（Google認証）
- **レポートURL**: https://datastudio.google.com/u/0/reporting/69c03c8a-c87e-4d93-941f-5ef3162f78b5/page/9iRyF/edit
- **データソース**: Emport AI KPI Dashboard（Google スプレッドシート）
- **スプレッドシートURL**: https://docs.google.com/spreadsheets/d/1-z9LhwakMCSKl59U2h3SyCz46oRoIN3W6UcmfjadBxw/edit
- **KPIフィールド**: AI相談件数・月次目標・X投稿数・Xインプレッション・リード獲得数・補助金申請数・売上（万円）・月
- **データ期間**: 2026-01〜2026-06（6ヶ月分）
- **次のステップ**: Looker Studio でチャートを手動追加（スコアカード・折れ線・棒グラフ）

---

### #6 Loom 動画メッセージ
- **状態**: アカウント作成完了・録画待ち
- **アカウント**: tsubeyou081@gmail.com（Google認証→Atlassian）
- **ダッシュボード**: https://www.loom.com/looms/videos
- **ワークスペース**: tsubeyou081
- **録画方法**: Chrome拡張 or デスクトップアプリをインストールして録画
- **動画スクリプト**: `tools/content-generator/loom_script_emport_ai.md` 参照
- **備考**: オンボーディングは最初の録画後に完了（Playwright不可のため手動録画が必要）

### #9 Notta 議事録自動化
- **状態**: 完了
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **ダッシュボードURL**: https://app.notta.ai/7262664717078478848/dashboard
- **会議予定URL**: https://app.notta.ai/7262664717078478848/meetings
- **Googleカレンダー連携**: tsubeyou081@gmail.com 接続済み（calendar.events + calendar.readonly）
- **無料枠**: 月120分の文字起こし（フリープラン）・カレンダー会議自動参加20回分
- **機能**: 録音開始・ファイルアップロード・Web会議文字起こし・URLからの文字起こし・AI要約
- **Notta Bot**: Googleカレンダーの会議に自動参加して文字起こし・議事録生成
- **利用リセット**: 2026-06-04 17:50

---

### #10 n8n on Railway 自動化ワークフロー
- **状態**: 完了（ワークフロー2件作成・稼働中）
- **デプロイ先**: Railway（ingenious-loveプロジェクト内）
- **Docker Image**: n8nio/n8n
- **公開URL**: https://n8n-production-6fd0.up.railway.app
- **管理者メール**: tsubeyou081@gmail.com
- **管理者名**: Allen EmportAI
- **パスワード**: 環境変数として管理（`EmportAI2026!`）
- **APIキー**: `N8N_API_KEY` として Windows ユーザー環境変数に設定済み（末尾: ...oFBM）
- **APIキー有効期限**: 2026-06-15
- **ポート**: 5678（Railway Magic 自動検出）
- **ライセンス**: 無料ライセンスキー送信済み（tsubeyou081@gmail.com宛）
- **無料機能**: Advanced debugging・Execution search and tagging・Folders
- **プライベートURL**: n8n.railway.internal
- **作成済みワークフロー**:
  - `Tally受信テスト（Webhook）` [ID: hiGoNktw5yYdLukf] — **アクティブ稼働中**
    - Webhook URL: `https://n8n-production-6fd0.up.railway.app/webhook/tally-lead`
  - `Tally フォーム送信 → Gmail通知` [ID: 0lqsNHmCIsIMzP38] — Gmail OAuth認証待ち
- **次のステップ**: n8n Credentials で Gmail OAuth2 を設定（Google Cloud Console でOAuthクライアント作成が必要）

### #11 Brevo メールマーケティング
- **状態**: アカウント作成中（電話番号SMS認証待ち）
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **オンボーディングURL**: https://onboarding.brevo.com/account/register/phone
- **入力済み情報**: Allen Tsube / Emport AI / Yamaguchi, Japan / 0-1 employee / 1-300 contacts
- **無料プラン**: 300メール/日・無制限コンタクト・メールキャンペーン・トランザクションメール
- **次のステップ**: 電話番号を入力してSMS認証コードを受け取る（手動操作が必要）

### #12 Context7 MCP（ライブラリドキュメント）
- **状態**: 完了
- **インストールコマンド**: `claude mcp add context7 npx @upstash/context7-mcp`
- **機能**: Claude Codeがリアルタイムで最新ライブラリドキュメントを参照可能
- **利用方法**: プロンプトに `use context7` と記述するだけ
- **料金**: 無料（Upstashのオープンソースプロジェクト）

### #13 n8n Instance-level MCP
- **状態**: 完了
- **MCPサーバーURL**: `https://n8n-production-6fd0.up.railway.app/mcp-server/http`
- **認証**: Bearerトークン（`N8N_MCP_TOKEN` 環境変数に保存済み）
- **Claude Code設定**: `claude mcp add --transport http n8n-mcp` で追加済み
- **機能**: Claude CodeからAPIなしでn8nワークフローを直接ビルド・実行・管理可能
- **MCP公開ワークフロー**: `Tally受信テスト（Webhook）` を Claude Code から呼び出し可能に設定済み

### #14 HeyGen AIアバター動画
- **状態**: 完了（無料プランでアカウント作成済み）
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **ダッシュボードURL**: https://app.heygen.com/home
- **無料プラン**: 動画3本/月・1分/本・720p・ウォーターマーク付き・クレジットカード不要
- **主な機能**: AIアバター動画生成・テキストから動画・写真からアバター動画・175言語翻訳・Loom形式のサービス紹介動画
- **Emport AI活用**: スクリプトを入力するだけでAllenのAIアバターが日本語で話すサービス紹介動画を生成。商工会議所向けLP動画・X投稿用リール・Loom代替
- **次のステップ**: 「Emport AIサービス紹介動画」をHeyGenで生成してX・HubSpotに配布

### #16 Cloudflare 無料プラン
- **状態**: 完了（アカウント作成・ダッシュボードログイン確認）
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **アカウントID**: e8a467ae5c796e22e8018d4d0885dfd3
- **ダッシュボードURL**: https://dash.cloudflare.com/e8a467ae5c796e22e8018d4d0885dfd3
- **無料プラン機能**: CDN・DDoS対策・Zero Trust（50ユーザーまで無料）・Cloudflare Tunnel
- **プロファイル設定**: Professional / Executive & Founder / 1名 / Application Security
- **次のステップ**: 独自ドメイン取得後に「Connect a domain」でEmport AIサイトを接続。Zero TrustでRailwayアプリをTunnelで保護

### #15 GitHub MCP（修正済み）
- **状態**: 設定修正完了（`github-mcp-custom`パッケージに変更）
- **原因**: `@github/mcp-server`はnpmに存在しないパッケージだった
- **修正**: `github-mcp-custom stdio`に変更済み（~/.claude.json）
- **有効化**: Claude Code再起動後に `github: ✓ Connected` になる予定

### #17 L Message（エルメ）LINE自動化
- **状態**: 認証メール送信済み・メール確認待ち（tsubeyou081@gmail.com）
- **アカウント**: tsubeyou081@gmail.com
- **登録URL**: https://step.lme.jp/register_user/null
- **無料プラン**: 1,000通/月・5万人友だちまで・カレンダー予約機能・ステップ配信・セグメント配信
- **Emport AI活用**: 相談申込み後の自動フォローアップ・セミナー参加者へのステップ配信・商工会議所会員への一斉配信
- **次のステップ**: tsubeyou081@gmail.com のメールを確認してアカウント登録URLをクリックし、LINE公式アカウントを連携する

---

### #22 Canva AI（デザイン自動生成）
- **状態**: 完了（tsubeyou081@gmail.com でGoogle認証ログイン確認）
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **ダッシュボードURL**: https://www.canva.com/
- **無料プラン**: Magic Design（AIデザイン自動生成）月30回・背景除去・Magic Eraser・テンプレート無制限
- **Emport AI活用**: X投稿ビジュアル・セミナー告知バナー・提案書サムネイル・名刺デザインをAIで量産
- **即使用可能機能**: Magic Design（デザイン自動生成）・Magic Media（AI画像生成）・BG Remover（背景除去）

---

### #21 STUDIO（ノーコードLP制作）
- **状態**: アカウント登録済み・確認メール送信済み（tsubeyou081@gmail.com）
- **アカウント**: tsubeyou081@gmail.com
- **ダッシュボードURL**: https://app.studio.design/
- **無料プラン**: 3プロジェクト・1カスタムドメイン・STUDIO AI（LP自動生成）
- **Emport AI活用**: Emport AIコーポレートサイト・クライアント向けLP・セミナー申込ページをノーコードで高品質作成
- **次のステップ**: tsubeyou081@gmail.comの確認メールのリンクをクリックして本登録完了

---

### #18 Misoca 見積書・請求書
- **状態**: 弥生ID新規登録フォーム入力済み・確認コードメール送信済み（tsubeyou081@gmail.com）
- **登録名**: Tsube Allen
- **メール**: tsubeyou081@gmail.com
- **パスワード**: 環境変数管理（n8nと共通）
- **登録URL**: https://app.misoca.jp/sessions/new
- **無料プラン**: 月10通の請求書・見積書・納品書が永久無料。freee連携対応
- **次のステップ**: tsubeyou081@gmail.com の受信箱で弥生からの確認コードを確認して入力する

---

### #25 Perplexity AI（AIリサーチ・情報収集）
- **状態**: 完了（tsubeyou081@gmail.com でGoogle認証ログイン確認）
- **アカウント**: tsubeyou081@gmail.com（Google認証）→ Perplexityユーザー名: `tsubeyou0825590`
- **ダッシュボードURL**: https://www.perplexity.ai/
- **無料プラン**: 1日5回 Pro検索・無制限スタンダード検索・スペース機能・Computer機能（アーティファクト生成）
- **主な機能**: Web検索AI・リアルタイム情報取得・ソース付き回答・スペースでチーム共有・PDF/画像分析
- **Emport AI活用**: 競合他社調査・補助金最新情報収集・業界トレンドリサーチ・クライアント向け市場調査

---

### #24 v0.dev（Vercel AIコンポーネント生成）
- **状態**: 完了（tsubeyou081@gmail.com でGoogle認証新規登録・ログイン確認）
- **アカウント**: tsubeyou081@gmail.com（Google認証）→ Vercelユーザー名: `tsubeyou081-5871`
- **ダッシュボードURL**: https://v0.app/
- **チャット一覧**: https://v0.app/chats
- **無料プラン**: 月200クレジット・React/Next.jsコンポーネント生成・shadcn/ui対応
- **主な機能**: テキストでUIコンポーネント生成・コード出力・GitHub連携・デザインシステム対応
- **Emport AI活用**: LP・管理画面・商工会議所向けフォームUIをテキストで即時生成。bolt.newと組み合わせてフルスタック開発

---

### #23 bolt.new（AIフルスタックアプリ生成）
- **状態**: 完了（tsubeyou081@gmail.com でGoogle認証ログイン確認）
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **ダッシュボードURL**: https://bolt.new/
- **プロジェクト一覧**: https://bolt.new/projects
- **無料プラン**: テキストでフルスタックWebアプリ生成・Figma/GitHub連携・無制限ビュー
- **主な機能**: React/Next.js/Vite対応・AI自動テスト・デザインシステム連携・SupabaseDB連携
- **Emport AI活用**: クライアント向けAIツールのプロトタイプを数分で生成・商工会議所向けデモアプリ作成・LP高速プロトタイピング

---

### #26 Apollo.io（AIセールス・リード獲得）
- **状態**: 完了（tsubeyou081@gmail.com でGoogle認証新規登録・ダッシュボード到達確認）
- **アカウント**: tsubeyou081@gmail.com（Google認証）
- **ダッシュボードURL**: https://app.apollo.io/#/people
- **会社情報**: Emport AI / emportai.com / Founder & CEO
- **無料プラン**: 月50件エクスポート・メール10,000件/月・シーケンス自動化・CRM連携
- **主な機能**: 2.1億件企業/個人DBからリード検索・メールシーケンス自動送信・LinkedIn連携・HubSpot/Salesforce CRM同期
- **Emport AI活用**: 商工会議所会員・製造業・小売業の意思決定者をDB検索→自動メールシーケンスでアウトバウンド営業自動化
- **利用開始**: 2026-05-17

---

## 🚧 未導入（優先順）

| # | ツール | 目的 | 難易度 | 備考 |
|---|--------|------|--------|------|
| 7 | EAS Build | アプリストア申請 | ★★★ | |
| 11 | Brevo | メールマーケティング | ★☆☆ | SMS認証待ち |
| 19 | Airワーク | 採用ページ・Indeed連携 | ★☆☆ | 電話番号（連絡先）入力が必要・手動操作 |
| 20 | Misoca | 見積書・請求書 | ★☆☆ | 弥生ID確認コード入力待ち（tsubeyou081@gmail.com） |
