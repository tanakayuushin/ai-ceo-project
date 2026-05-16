# Soundcore→Notion自動同期をWindowsログイン時に自動起動するセットアップ
# 管理者権限不要

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$EnvFile     = Join-Path $ProjectRoot ".env"
$MainScript  = Join-Path $ScriptDir "soundcore_to_notion.py"
$WrapperVbs  = Join-Path $ScriptDir "start_silent.vbs"
$StartupDir  = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir "SoundcoreNotion.lnk"

Write-Host "=== Soundcore→Notion 自動起動セットアップ ===" -ForegroundColor Cyan

# 依存パッケージインストール
Write-Host "`n[1/4] 依存パッケージをインストール中..." -ForegroundColor Yellow
pip install -r (Join-Path $ScriptDir "requirements.txt") --quiet
Write-Host "  完了" -ForegroundColor Green

# .envの存在チェック
if (-not (Test-Path $EnvFile)) {
    Write-Host "`n[警告] .env ファイルが見つかりません: $EnvFile" -ForegroundColor Red
    Write-Host "以下の内容を .env に追記してください:"
    Write-Host "  ANTHROPIC_API_KEY=sk-ant-xxxxxx"
    Write-Host "  NOTION_TOKEN=secret_xxxxxx"
    Write-Host "  NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    Write-Host "  SOUNDCORE_INBOX=C:\Users\tsube\OneDrive\Soundcore\inbox"
}

# バックグラウンド起動用VBSラッパー作成（コンソールウィンドウを非表示）
Write-Host "`n[2/4] 起動ラッパーを作成中..." -ForegroundColor Yellow
$vbsContent = @"
' Soundcore→Notion バックグラウンド起動ラッパー
Dim WShell
Set WShell = CreateObject("WScript.Shell")

' .envを読み込んで環境変数をセット
Dim fso, f, line, parts
Set fso = CreateObject("Scripting.FileSystemObject")
Dim envPath : envPath = "$EnvFile"
If fso.FileExists(envPath) Then
    Set f = fso.OpenTextFile(envPath, 1)
    Do While Not f.AtEndOfStream
        line = Trim(f.ReadLine())
        If Len(line) > 0 And Left(line,1) <> "#" Then
            parts = Split(line, "=", 2)
            If UBound(parts) = 1 Then
                WShell.Environment("Process")(Trim(parts(0))) = Trim(parts(1))
            End If
        End If
    Loop
    f.Close
End If

' Pythonスクリプトをバックグラウンドで起動
WShell.Run "python ""$MainScript""", 0, False
"@
$vbsContent | Out-File -FilePath $WrapperVbs -Encoding utf8
Write-Host "  完了: $WrapperVbs" -ForegroundColor Green

# スタートアップショートカット作成
Write-Host "`n[3/4] スタートアップショートカットを作成中..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($ShortcutPath)
$shortcut.TargetPath  = $WrapperVbs
$shortcut.Description = "Soundcore→Notion自動同期"
$shortcut.Save()
Write-Host "  完了: $ShortcutPath" -ForegroundColor Green

# 監視フォルダ作成
Write-Host "`n[4/4] 監視フォルダを作成中..." -ForegroundColor Yellow
$InboxPath = "C:\Users\tsube\OneDrive\Soundcore\inbox"
New-Item -ItemType Directory -Force -Path $InboxPath | Out-Null
New-Item -ItemType Directory -Force -Path "C:\Users\tsube\OneDrive\Soundcore\archive" | Out-Null
Write-Host "  受信フォルダ: $InboxPath" -ForegroundColor Green
Write-Host "  アーカイブ  : C:\Users\tsube\OneDrive\Soundcore\archive" -ForegroundColor Green

Write-Host "`n=== セットアップ完了 ===" -ForegroundColor Cyan
Write-Host @"

【次のステップ】
1. .env に以下を追記してください:
   ANTHROPIC_API_KEY=sk-ant-xxxxxx
   NOTION_TOKEN=secret_xxxxxx
   NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

2. Soundcoreアプリで文字起こし後、テキストをエクスポート:
   保存先 → OneDrive\Soundcore\inbox

3. 自動でClaudeが要約してNotionに保存されます

4. 今すぐテストする場合:
   python "$MainScript"

"@ -ForegroundColor White
