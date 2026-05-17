---
name: 日次ブリーフィングに全インテリジェンスファイルを含める
description: 毎日のブリーフィング提示時は01〜10の個別情報収集ファイルを全て読み込み、summary.mdと統合して提示する
type: feedback
originSessionId: 02bc9f6a-bf09-4ca4-bc9e-868df094be04
---
毎日のブリーフィングを提示する際は、その日の `ceo/intelligence/daily/YYYY-MM-DD/` ディレクトリにある以下の全ファイルを読み込み、summary.md の内容と統合して提示する。

対象ファイル:
- 01-world-news.md（世界ビジネス・M&Aニュース）
- 02-japan-corporate.md（日本企業動向）
- 03-ai-companies.md（AI企業・資金調達動向）
- 04-competitors-now.md（競合・DX支援業界現況）
- 05-competitors-origin.md（AIコンサル競合の起業・成長戦略）
- 06-yamaguchi.md（山口県DX・補助金動向）
- 07-bizmodel.md（AIコンサルビジネスモデル・価格設計）
- 08-subsidy.md（補助金最新情報）
- 09-funding.md（日本SaaS・スタートアップ資金調達）
- 10-saas-market.md（AI SaaS B2B Japan SMB市場）
- summary.md（アレンが作成したブリーフィング本体）

## Jicoo予約チェック（必須）

ブリーフィング時に必ずPlaywright MCPで以下を実行し、新規予約をオーナーに報告する。

1. `https://www.jicoo.com/dashboard` にアクセス
2. 予約一覧（左メニュー「予約」）を確認
3. 新規・直近の予約があれば「予約者名・日時・ミーティング種別」をブリーフィングに含める
4. 予約がなければ「Jicoo：新規予約なし」と一言記載する

**Why:** Jicooで無料相談の予約が入った場合、オーナーが朝のブリーフィングで確認して当日対応できるようにするため（2026-05-17指示）。

**How to apply:** ブリーフィングを提示する際は必ず全11ファイルを読み込んでから統合提示する。summary.mdに含まれていない情報（個別ファイルにしか書かれていない具体的データ・事例）も必ず含める。特にEmport AIへの示唆・営業への活用法を添えて提示すること。Jicoo予約チェックも毎回実施する。
