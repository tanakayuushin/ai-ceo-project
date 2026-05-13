# 新しいPCへのセットアップ手順

このリポジトリをクローンするだけで、Claude Code の自動化設定が使えます。

---

## 必要なもの

| ツール | 説明 | インストール |
|--------|------|-------------|
| Git | バージョン管理 | https://git-scm.com/ |
| Node.js | Claude Code の実行環境 | https://nodejs.org/ (LTS推奨) |
| Claude Code | AIコーディングツール | npm install -g @anthropic-ai/claude-code |
| Python 3 | 社内ツール実行用 | https://www.python.org/ |

---

## セットアップ手順

### 1. リポジトリをクローン

`ash
git clone https://github.com/tanakayuushin/ai-ceo-project.git
cd ai-ceo-project
`

### 2. Claude Code を起動

`ash
claude
`

これだけで以下が自動的に有効になります：
- 許可プロンプトなし（bypassPermissions モード）
- Bash / PowerShell コマンド全許可
- セッション終了時に自動で git push

### 3. APIキーの設定（初回のみ）

Claude Code 起動後にAPIキーを入力するか、環境変数に設定してください。

**Windows (PowerShell):**
`powershell
# Anthropic Console から取得したキーを設定
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "取得したキー", "User")
`

**Mac/Linux:**
`ash
# ~/.bashrc または ~/.zshrc に追記
echo 'export ANTHROPIC_API_KEY=取得したキー' >> ~/.bashrc
`

APIキーの取得先: https://console.anthropic.com/

---

## 自動化されている動作（.claude/settings.json）

### 許可プロンプトなし
defaultMode: bypassPermissions + Bash(*) が設定済み。
すべてのBash/PowerShellコマンドが自動承認されます。

### 自動 git push
セッション終了時に自動でコミット＆プッシュします。
変更がなければ何もしません。

---

## 社内ツールの起動

`ash
# CRM（見込み客管理）→ http://localhost:5001
cd tools/crm && pip install -r requirements.txt && python crm.py

# AI議事録 → http://localhost:5002
cd tools/minutes && pip install -r requirements.txt && python minutes.py

# AI提案書生成 → http://localhost:5003
cd tools/proposal && pip install -r requirements.txt && python proposal.py

# AIメールマガジン → http://localhost:5004
cd tools/newsletter && pip install -r requirements.txt && python newsletter.py

# Webアプリ（メインツール）→ http://localhost:5000
pip install -r requirements.txt && python app.py
`

---

## トラブルシューティング

| 症状 | 対処法 |
|------|--------|
| 許可プロンプトが出る | Claude Code を終了して再起動。プロジェクトフォルダで起動しているか確認 |
| 自動pushが動かない | git remote -v でリモート確認、SSH/HTTPS認証の確認 |
| Pythonエラー | pip install -r requirements.txt を実行 |
| bash が見つからない | Git for Windows をインストール（Git Bash が同梱） |

---

設定ファイル: .claude/settings.json（git管理済み・変更不要）