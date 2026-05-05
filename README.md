# （社名） — AI CEO プロジェクト

山口県の中小企業向けAI活用支援会社「（社名）」の経営管理リポジトリです。  
CEO「アレン」（AI）がオーナー（取締役）の指示のもと、日々の経営業務を自律的に遂行します。

---

## 会社概要

| 項目 | 内容 |
|------|------|
| 会社名 | （社名） |
| ターゲット | 山口県の中小企業・小規模事業者 |
| 主力サービス | AI業務診断、AI導入支援、IT導入補助金サポート |
| X（旧Twitter） | [@AI_chuusyou](https://x.com/AI_chuusyou) |
| ランディングページ | [emport-ai-website](https://tanakayuushin.github.io/emport-ai-website/) |

---

## ディレクトリ構成

```
ai-ceo-project/
│
├── company/               # 会社情報
│   ├── overview/          # 会社概要
│   ├── strategy/          # 経営戦略
│   └── policies/          # 社内ポリシー
│
├── ceo/                   # CEO（アレン）関連
│   ├── profile/           # CEOプロフィール・行動ルール
│   ├── reports/           # 週次・月次レポート（自動生成）
│   └── decisions/         # 意思決定記録
│
├── board/                 # 取締役会
│   ├── meetings/          # 議事録
│   ├── directives/        # 取締役からの指示
│   └── approvals/         # 承認事項
│
├── departments/           # 各部門
│   ├── sales/             # 営業部門
│   │   ├── 見込み客リスト.md          # 見込み客一覧（自動更新）
│   │   ├── 営業メールテンプレート.md
│   │   ├── 業務委託契約書テンプレート.md
│   │   ├── サービス案内.md
│   │   ├── セミナー台本.md / スライド概要.md
│   │   ├── 商工会議所アプローチ計画.md
│   │   └── outreach-drafts/           # 営業メール下書き（毎週木曜自動生成）
│   ├── marketing/         # マーケティング部門
│   │   ├── X初期投稿リスト.md
│   │   ├── Xプロフィール設定.md
│   │   └── x-posts/                   # X投稿ファイル（毎日17時自動生成）
│   ├── operations/        # オペレーション部門
│   ├── finance/           # 財務部門
│   └── hr/                # 人事部門
│
├── projects/              # プロジェクト管理
│   ├── active/            # 進行中プロジェクト
│   └── completed/         # 完了済みプロジェクト
│
├── communications/        # 社内コミュニケーション
│   ├── ceo-to-board/      # CEOから取締役への報告・質問
│   └── board-to-ceo/      # 取締役からCEOへの指示
│
├── data/                  # データ・レポート
│   ├── reports/           # 市場調査・補助金情報（自動生成）
│   └── archives/          # 過去データ
│
├── tools/                 # 開発ツール・スクリプト
│   ├── main.py                   # 問い合わせ分析CLI版
│   ├── generate_slides.py        # セミナースライド生成
│   ├── generate_contract_pdf.py  # 契約書PDF生成
│   ├── rag_demo.py               # RAGデモ（山田建設AIアシスタント）
│   ├── gmail_draft_sync.gs       # Gmail下書き自動同期（Google Apps Script）
│   └── requirements_rag.txt      # RAGデモ用ライブラリ
│
├── templates/             # FlaskテンプレートHTML
│   └── index.html
│
├── app.py                 # Flask Webアプリ（問い合わせ分析 / X投稿生成）
├── requirements.txt       # Python依存パッケージ
└── index.html             # ランディングページ（ローカル確認用）
```

---

## 自動化エージェント一覧

CEOアレンがAnthropicのクラウド上で自動実行します。結果はすべてGitHubにコミットされます。

| エージェント名 | 実行タイミング | 出力先 |
|--------------|-------------|--------|
| Allen-Daily-Tweet | 毎日 17:00 JST | `departments/marketing/x-posts/` |
| Allen-Weekly-Report | 毎週月曜 09:00 JST | `ceo/reports/` |
| Allen-Lead-Research | 毎週火曜 09:00 JST | `departments/sales/見込み客リスト.md` |
| Allen-Market-Research | 毎週水曜 09:00 JST | `data/reports/` |
| Allen-Email-Outreach-Draft | 毎週木曜 09:00 JST | `departments/sales/outreach-drafts/` |
| Allen-Marketing-Planning | 毎週金曜 09:00 JST | `departments/marketing/` |
| Allen-Monthly-Summary | 毎月1日 09:00 JST | `ceo/reports/` |

管理画面: https://claude.ai/code/scheduled

---

## Webアプリの起動方法

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000 で起動
```

**機能：**
- 問い合わせ分析（カテゴリ・緊急度・返信文・要約を自動生成）
- X投稿文生成（3パターン自動生成）

---

## ツールの使い方

```bash
# 契約書PDFを生成
python tools/generate_contract_pdf.py

# RAGデモ（山田建設AIアシスタント）
pip install -r tools/requirements_rag.txt
python tools/rag_demo.py

# セミナースライドを再生成
python tools/generate_slides.py
```

---

## 組織構造

| 役割 | 名前 | 説明 |
|------|------|------|
| オーナー / 取締役会 | （ユーザー本人） | 最終意思決定権を持つ取締役 |
| CEO | アレン（Allen） | 経営トップ。日々の業務を自律的に遂行 |
