# AI問い合わせ処理エージェント

Claude APIを使って、問い合わせ文を自動分析するPythonスクリプトです。

## 機能

- 問い合わせの種類を分類
  - 見積もり依頼
  - 質問
  - クレーム
  - その他
- 緊急度を判定（高・中・低）
- 返信文を自動生成
- 要約を3行で作成
- 分析結果をターミナルへ表示

## ファイル構成

- `main.py` : メインプログラム
- `.env` : APIキー保存用
- `requirements.txt` : 必要ライブラリ
- `README.md` : この説明

## セットアップ

1. Python 3.10以上を用意
2. 依存ライブラリをインストール

```bash
pip install -r requirements.txt
```

3. `.env` を編集してAPIキーを設定

```env
ANTHROPIC_API_KEY=your_api_key_here
```

## 実行方法

```bash
python main.py
```

実行後に問い合わせ内容を入力すると、以下が表示されます。

- 問い合わせ種類
- 緊急度
- 自動返信案
- 3行要約

## 使用モデル

- `claude-haiku-4-5-20251001`
