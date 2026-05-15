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

**Why:** オーナーは個別ファイルを見ずにブリーフィングだけを参照するため、全情報を統合して見せないと情報が抜ける。オーナーから「ほかの情報収集もブリーフィングと一緒に乗せるようにしてください」と明示的に指示を受けた（2026-05-13）。

**How to apply:** ブリーフィングを提示する際は必ず全11ファイルを読み込んでから統合提示する。summary.mdに含まれていない情報（個別ファイルにしか書かれていない具体的データ・事例）も必ず含める。特にEmport AIへの示唆・営業への活用法を添えて提示すること。
