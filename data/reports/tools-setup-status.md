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
- **状態**: 完了
- **デプロイ先**: Railway（ingenious-loveプロジェクト内）
- **Docker Image**: n8nio/n8n
- **公開URL**: https://n8n-production-6fd0.up.railway.app
- **管理者メール**: tsubeyou081@gmail.com
- **管理者名**: Allen EmportAI
- **パスワード**: 環境変数として管理（`EmportAI2026!`）
- **ポート**: 5678（Railway Magic 自動検出）
- **ライセンス**: 無料ライセンスキー送信済み（tsubeyou081@gmail.com宛）
- **無料機能**: Advanced debugging・Execution search and tagging・Folders
- **プライベートURL**: n8n.railway.internal
- **推奨ワークフロー**: Tally→HubSpot連携・X投稿スケジュール・Notta議事録→Notion保存

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

---

## 🚧 未導入（優先順）

| # | ツール | 目的 | 難易度 |
|---|--------|------|--------|
| 7 | EAS Build | アプリストア申請 | ★★★ |
| 11 | Brevo | メールマーケティング（SMS認証待ち） | ★☆☆ |
