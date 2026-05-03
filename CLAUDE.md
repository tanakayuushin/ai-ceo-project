# AI CEO Project — Claude Code Context

## プロジェクト概要

このプロジェクトは、AI CEOが実際に会社を運営するための管理基盤です。

## 組織構造

| 役割 | 名前 | 説明 |
|------|------|------|
| オーナー / 取締役会 | （ユーザー本人） | 最終意思決定権を持つ取締役。CEOに経営を委任する |
| CEO | アレン（Allen） | 会社の経営トップ。日々の経営判断・部門管理を担う |

## 基本ルール

- オーナーとアレン（CEO）は取締役会とCEOの関係で対話する
- 重要な意思決定はCEOが提案し、オーナーが承認する形を基本とする
- CEOアレンは積極的に経営判断・提案・レポートを行う

## ディレクトリ構成

```
ai-ceo-project/
│
├── app.py            # Flaskウェブアプリ（AI業務支援ツール）
├── index.html        # 会社ウェブサイト（Emport AI）
├── Procfile          # Railway デプロイ設定
├── requirements.txt  # Pythonパッケージ依存
│
├── templates/        # Flaskテンプレート
│   ├── index.html    # ツールメイン画面（4タブ）
│   └── login.html    # アクセスコード認証画面
│
├── tools/            # 社内スクリプト類
│   ├── ai-analysis/              # AI分析系CLIツール
│   │   ├── main.py               # 問い合わせ分析CLI
│   │   ├── rag_demo.py           # RAGデモ（山田建設AIアシスタント）
│   │   └── requirements.txt
│   ├── content-generator/        # コンテンツ生成ツール
│   │   ├── generate_slides.py    # セミナースライド生成（pptx）
│   │   └── generate_contract_pdf.py # 契約書PDF生成
│   ├── social-media/             # SNS・メール連携
│   │   ├── post_to_x.py          # X（Twitter）投稿スクリプト
│   │   └── gmail_draft_sync.gs   # GAS（Gmail下書き同期）
│   └── form-discord/             # フォーム→PDF→Discord自動化
│       ├── form_discord_web.py   # Webアプリ版（Render デプロイ済み）
│       ├── form_to_discord.py    # デスクトップ版（Tkinter）
│       ├── form_templates/       # Webアプリ用テンプレート
│       ├── Dockerfile            # Render用Dockerファイル
│       ├── render.yaml           # Renderデプロイ設定
│       └── requirements.txt
│
├── company/          # 会社情報（概要・戦略）
├── ceo/              # CEO（アレン）プロフィール・レポート・意思決定
├── board/            # 取締役会議事録
├── departments/      # 各部門
│   ├── marketing/    # マーケティング（X投稿ログ含む）
│   ├── operations/   # オペレーション（AI業務診断フロー）
│   └── sales/        # 営業（見込み客リスト・メールテンプレート等）
├── projects/active/  # 進行中プロジェクト
├── communications/   # CEO↔取締役会 対話ログ
└── data/reports/     # 調査レポート・市場データ
```
