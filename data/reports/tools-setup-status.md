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

---

## 🚧 未導入（優先順）

| # | ツール | 目的 | 難易度 |
|---|--------|------|--------|
| 6 | Loom | サービス紹介動画作成 | ★☆☆ |
| 7 | EAS Build | アプリストア申請 | ★★★ |
| 8 | Looker Studio | KPIダッシュボード | ★★☆ |
| 9 | Notta | 議事録自動化 | ★☆☆ |
| 10 | n8n on Railway | 自動化ワークフロー | ★★☆ |
