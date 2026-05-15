# Allen AI CEO — 新しいPCへのセットアップ手順

このフォルダに入っているスクリプトを実行するだけで、アレンの全機能が再現できます。

---

## 何が再現されるか

| 機能 | 内容 |
|------|------|
| **自動承認** | git / npm / python / ファイル操作など 100+ コマンドを確認なしで実行 |
| **セキュリティガード** | 危険コマンドブロック・シークレット漏洩防止・監査ログ（4層構造） |
| **メモリ** | アレンの記憶（会社概要・行動ルール・プロジェクト状況・フィードバック）|
| **CLAUDE.md** | 会社構造・ディレクトリ構成・基本ルール（リポジトリに含まれる） |

---

## 手順

### 1. リポジトリをクローン

```powershell
git clone https://github.com/tanakayuushin/ai-ceo-project.git
cd ai-ceo-project
```

### 2. セットアップスクリプトを実行

```powershell
cd setup
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

これだけで以下が自動セットアップされます：
- `~/.claude/hooks/` にセキュリティフック4本をコピー
- `~/.claude/settings.json` を生成（フックパスをこのPCのパスに合わせて自動書き換え）
- `~/.claude/projects/<プロジェクトキー>/memory/` にメモリファイルをコピー

### 3. 確認スクリプトを実行

```powershell
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

**全項目 [OK]** になれば完了。[NG] が出たら表示される修正コマンドを実行して再度 verify.ps1 を実行してください。

### 4. Claude Code を起動

```powershell
# リポジトリのルートで起動
cd ..
claude
```

### 5. 動作確認

Claude Code で以下を送信して確認：

```
アレン、今日のブリーフィングをお願いします
```

許可ダイアログが出ずに応答が返ってくれば自動承認も有効です。

---

## git pull 後の確認手順（既存PCで最新版を取得した後）

```powershell
git pull
cd setup
powershell -ExecutionPolicy Bypass -File .\verify.ps1
```

[NG] が出た場合は install.ps1 を再実行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

---

## 別途必要な設定（スクリプトでは自動化できないもの）

### 環境変数 (.env)
API キーや外部サービスのトークンは `.env` に設定してください：

```
ANTHROPIC_API_KEY=sk-ant-...
NOTION_TOKEN=...
NOTION_PAGE_ID=...
X_CONSUMER_KEY=...
X_CONSUMER_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...
```

### MCP サーバー（Playwright / Gmail）
`~/.claude/` の MCP 設定は現在のPCの設定を参照してください。  
Claude Code の `/mcp` コマンドで確認・追加できます。

---

## フォルダ構造

```
setup/
├── SETUP.md              # この手順書
├── install.ps1           # セットアップスクリプト（Windows PowerShell）
├── verify.ps1            # セットアップ確認スクリプト（git pull後に実行）
├── settings_template.json # Claude Code 設定テンプレート
├── hooks/                # セキュリティフック（4層）
│   ├── layer2_bash_guard.py      # 危険Bashコマンドブロック
│   ├── layer3_secrets_guard.py   # シークレット漏洩防止
│   ├── layer4_file_guard.py      # 重要ファイル保護
│   └── layer5_audit_log.py       # 監査ログ + インジェクション検知
└── memory/               # アレンのメモリ（19ファイル）
    ├── MEMORY.md          # メモリインデックス
    ├── project_ai_ceo.md
    ├── feedback_ceo_rules.md
    ├── feedback_auto_push.md
    └── ... (その他16ファイル)
```

---

## トラブルシューティング

**「python が見つからない」と言われる**  
→ https://www.python.org/ から Python 3.x をインストールし、PATH を通してください。

**フックが動かない（コマンドが毎回確認を求められる）**  
→ Claude Code を再起動してください。設定は起動時に読み込まれます。

**メモリが反映されない**  
→ `install.ps1` を再実行し、プロジェクトキーが正しく生成されているか確認してください。  
　 表示される `targetMemDir` のパスに `.md` ファイルがあれば OK です。
