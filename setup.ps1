# ============================================
# AI CEO Project - 新PCセットアップスクリプト
# 使い方: git clone後、このファイルをダブルクリック
# ============================================

$projectRoot = $PSScriptRoot

Write-Host ""
Write-Host "=== AI CEO Project セットアップ ===" -ForegroundColor Cyan
Write-Host ""

# ── 1. メモリファイルのコピー ──────────────────

Write-Host "[1/2] Claude Codeメモリをセットアップ中..." -ForegroundColor Yellow

$claudeProjects = "$env:USERPROFILE\.claude\projects"
$memoryDir = Get-ChildItem $claudeProjects -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "*ai-ceo-project*" } |
    Select-Object -First 1

if ($memoryDir) {
    $targetPath = "$($memoryDir.FullName)\memory"
    New-Item -ItemType Directory -Force -Path $targetPath | Out-Null
    Copy-Item "$projectRoot\claude-memory\*.md" $targetPath -Force
    Write-Host "  完了: $targetPath" -ForegroundColor Green
} else {
    Write-Host "  ※ Claude Codeでこのプロジェクトを一度開いてから再実行してください" -ForegroundColor Red
    Write-Host "     (Cursor/VSCodeでフォルダを開き、Claude Codeを起動後に再実行)" -ForegroundColor Red
}

# ── 2. .envファイルの作成 ──────────────────────

Write-Host ""
Write-Host "[2/2] APIキーをセットアップ中..." -ForegroundColor Yellow

$envPath = "$projectRoot\.env"
if (Test-Path $envPath) {
    Write-Host "  .envは既に存在します（スキップ）" -ForegroundColor Gray
} else {
    Write-Host ""
    $apiKey = Read-Host "  Anthropic APIキーを入力してください（sk-ant-...）"
    if ($apiKey) {
        "ANTHROPIC_API_KEY=$apiKey" | Out-File -FilePath $envPath -Encoding utf8
        Write-Host "  完了: .env を作成しました" -ForegroundColor Green
    } else {
        Write-Host "  スキップ（後で .env ファイルを手動作成してください）" -ForegroundColor Gray
    }
}

# ── 完了 ──────────────────────────────────────

Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "次のステップ:"
Write-Host "  1. Cursorを再起動する"
Write-Host "  2. claude.ai/customize/connectors でGmail MCP・Playwrightを確認"
Write-Host ""
Read-Host "Enterキーで終了"
