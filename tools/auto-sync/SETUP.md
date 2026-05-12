# 自動 git pull / push セットアップ手順

別PCでも同じ環境を再現するための手順書。

---

## 概要

| 役割 | 方法 | 頻度 |
|------|------|------|
| ローカル自動pull | Windows Task Scheduler | 1分おき |
| 自動push | アレン（Claude）が成果物作成時に手動実行 | ファイル作成・更新時 |
| Notion同期push | GitHub Actions | 毎朝10:00 JST |

---

## ローカル自動pull セットアップ

### 前提条件
- Git がインストール済み
- リポジトリがローカルにクローン済み
- GitHub への認証設定済み（SSH or 認証情報マネージャー）

### 手順

**1. PowerShell を管理者として開く**
スタートメニューで `PowerShell` を右クリック → 「管理者として実行」

**2. スクリプト実行ポリシーを設定**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

**3. リポジトリをクローン（まだの場合）**
```powershell
git clone https://github.com/tanakayuushin/ai-ceo-project.git C:\Users\<ユーザー名>\OneDrive\ai-ceo-project
```

**4. local_pull.ps1 のパスを確認・修正**

[tools/auto-sync/local_pull.ps1](local_pull.ps1) の以下の行を自分のPCのパスに合わせて変更：
```powershell
$repoPath = "C:\Users\<ユーザー名>\OneDrive\ai-ceo-project"
$logFile  = "$repoPath\tools\auto-sync\pull.log"
```

**5. Task Scheduler に登録（1分おき）**
```powershell
schtasks /create /tn "Allen-AutoPull" /tr "powershell.exe -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File C:\Users\<ユーザー名>\OneDrive\ai-ceo-project\tools\auto-sync\local_pull.ps1" /sc minute /mo 1 /f
```

**6. 確認**
```powershell
schtasks /query /tn "Allen-AutoPull"
```
`準備完了` と表示されれば完了。

---

## タスクの削除・再登録

```powershell
# 削除
schtasks /delete /tn "Allen-AutoPull" /f

# 再登録（上記の手順5を再実行）
```

---

## ログ確認

```powershell
cat C:\Users\<ユーザー名>\OneDrive\ai-ceo-project\tools\auto-sync\pull.log
```

---

## GitHub Actions（自動設定済み・変更不要）

以下はリポジトリ側で自動実行されるため、新しいPCでの追加設定は不要。

| ワークフロー | 実行タイミング | 内容 |
|---|---|---|
| `notion_knowledge_sync.yml` | 毎朝10:00 JST | Notion録音→markdown保存→push |
| `timetree_sync.yml` | 6時間おき | TimeTree→LINE リマインダー同期 |
| `notion_transcription.yml` | 手動のみ | Soundcore音声文字起こし（停止中） |

必要なGitHub Secrets（リポジトリ設定で確認）：
- `NOTION_TOKEN`
- `NOTION_PAGE_ID`
- `ANTHROPIC_API_KEY`
- `TIMETREE_EMAIL`
- `TIMETREE_PASSWORD`
- `GAS_WEBHOOK_URL`
