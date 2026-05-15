# ==============================================================================
# Allen (AI CEO) セットアップスクリプト
# 新しいPCでこのスクリプトを実行すると、全ての設定が再現されます。
#
# 使い方:
#   PowerShell を管理者権限で起動し、以下を実行:
#   cd <このリポジトリのパス>\setup
#   .\install.ps1
# ==============================================================================

$ErrorActionPreference = "Stop"

$REPO_ROOT  = Split-Path -Parent $PSScriptRoot
$SETUP_DIR  = $PSScriptRoot
$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$HOOKS_DIR  = "$CLAUDE_DIR\hooks"
$MEM_DIR    = "$CLAUDE_DIR\projects"

Write-Host ""
Write-Host "=== Allen AI CEO セットアップ開始 ===" -ForegroundColor Cyan
Write-Host "REPO : $REPO_ROOT"
Write-Host "HOME : $env:USERPROFILE"
Write-Host ""

# ------------------------------------------------------------------------------
# 1. ~/.claude/hooks/ にセキュリティフックをコピー
# ------------------------------------------------------------------------------
Write-Host "[1/4] セキュリティフックをインストール..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force $HOOKS_DIR | Out-Null
Copy-Item "$SETUP_DIR\hooks\*.py" $HOOKS_DIR -Force
Write-Host "      OK: $HOOKS_DIR" -ForegroundColor Green

# ------------------------------------------------------------------------------
# 2. ~/.claude/settings.json を生成（フックパスを実際のパスに置換）
# ------------------------------------------------------------------------------
Write-Host "[2/4] settings.json を生成..." -ForegroundColor Yellow
$template = Get-Content "$SETUP_DIR\settings_template.json" -Raw
$settings = $template -replace '\{\{HOOKS_DIR\}\}', ($HOOKS_DIR -replace '\\', '\\')
$settingsPath = "$CLAUDE_DIR\settings.json"

if (Test-Path $settingsPath) {
    $backup = "$CLAUDE_DIR\settings.json.bak"
    Copy-Item $settingsPath $backup -Force
    Write-Host "      既存の settings.json を $backup にバックアップしました" -ForegroundColor DarkYellow
}

# PS5.1の Set-Content -Encoding UTF8 はBOM付きになるため .NET で直接書き込む
$noBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($settingsPath, $settings, $noBom)
Write-Host "      OK: $settingsPath" -ForegroundColor Green

# ------------------------------------------------------------------------------
# 3. メモリファイルをプロジェクト用ディレクトリにコピー
#    Claude Code はプロジェクトパスをキーとしてメモリを管理するため、
#    このPC上のリポジトリパスに合わせたディレクトリを作成します。
# ------------------------------------------------------------------------------
Write-Host "[3/4] メモリファイルをインストール..." -ForegroundColor Yellow

# リポジトリの絶対パスをClaude Codeのプロジェクトキー形式に変換
# 例: C:\Users\foo\Documents\ai-ceo-project
#   → c--Users-foo-Documents-ai-ceo-project
$rawPath = $REPO_ROOT
# Claude Codeのプロジェクトキー生成: ドライブ文字小文字化 + 非英数字をすべて'-'に置換
# 例: C:\Users\foo\OneDrive\デスクトップ\ai-ceo-project → c--Users-foo-OneDrive--------ai-ceo-project
# ※ PS5.1ではスクリプトブロック置換が使えないため文字列操作で実装
$projectKey = $rawPath[0].ToString().ToLower() + ($rawPath.Substring(1) -replace '[^a-zA-Z0-9]', '-')

$targetMemDir = "$MEM_DIR\$projectKey\memory"
New-Item -ItemType Directory -Force $targetMemDir | Out-Null
Copy-Item "$SETUP_DIR\memory\*.md" $targetMemDir -Force
Write-Host "      OK: $targetMemDir" -ForegroundColor Green
Write-Host "      ($((Get-ChildItem $targetMemDir).Count) 件のメモリファイル)" -ForegroundColor DarkGray

# ------------------------------------------------------------------------------
# 4. Python の確認
# ------------------------------------------------------------------------------
Write-Host "[4/4] Python を確認..." -ForegroundColor Yellow
try {
    $pyVer = python --version 2>&1
    Write-Host "      OK: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "      WARNING: python コマンドが見つかりません。" -ForegroundColor Red
    Write-Host "      https://www.python.org/ から Python をインストールしてください。" -ForegroundColor Red
    Write-Host "      フックはPythonが必要です。" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 完了
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor White
Write-Host "  1. Claude Code を起動（または再起動）" -ForegroundColor Gray
Write-Host "  2. このリポジトリ ($REPO_ROOT) で Claude Code を開く" -ForegroundColor Gray
Write-Host "  3. 動作確認: 'アレン、今日のブリーフィングをお願いします' と話しかける" -ForegroundColor Gray
Write-Host ""
Write-Host "メモ: GitHub token や API key は .env ファイルに別途設定が必要です。" -ForegroundColor DarkYellow
