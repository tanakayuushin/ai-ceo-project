# ==============================================================================
# Allen AI CEO — セットアップ確認スクリプト
# git pull 後にこのスクリプトを実行して全項目が OK か確認する
#
# 使い方:
#   cd ai-ceo-project\setup
#   powershell -ExecutionPolicy Bypass -File .\verify.ps1
# ==============================================================================

$REPO_ROOT  = Split-Path -Parent $PSScriptRoot
$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$HOOKS_DIR  = "$CLAUDE_DIR\hooks"
$MEM_DIR    = "$CLAUDE_DIR\projects"

$ok  = 0
$ng  = 0

function Pass($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green;  $script:ok++ }
function Fail($msg) { Write-Host "  [NG] $msg" -ForegroundColor Red;    $script:ng++ }
function Warn($msg) { Write-Host "  [!!] $msg" -ForegroundColor Yellow }
function Section($title) {
    Write-Host ""
    Write-Host "--- $title ---" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== Allen AI CEO セットアップ確認 ===" -ForegroundColor Cyan
Write-Host "REPO : $REPO_ROOT"
Write-Host "HOME : $env:USERPROFILE"

# ------------------------------------------------------------------------------
# 1. ~/.claude/settings.json
# ------------------------------------------------------------------------------
Section "1. settings.json（自動承認設定）"

$settingsPath = "$CLAUDE_DIR\settings.json"
if (-not (Test-Path $settingsPath)) {
    Fail "settings.json が存在しない → install.ps1 を実行してください"
} else {
    # BOMチェック
    $bytes = [System.IO.File]::ReadAllBytes($settingsPath)
    if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Fail "settings.json がBOM付き → Claude Codeが読めない"
        Write-Host "       修正コマンド:" -ForegroundColor DarkYellow
        Write-Host "       `$b=[System.IO.File]::ReadAllText('$settingsPath',(New-Object System.Text.UTF8Encoding(`$true)))" -ForegroundColor DarkGray
        Write-Host "       [System.IO.File]::WriteAllText('$settingsPath',`$b,(New-Object System.Text.UTF8Encoding(`$false)))" -ForegroundColor DarkGray
    } else {
        Pass "settings.json BOMなし"
    }

    # JSON構文チェック
    try {
        $json = Get-Content $settingsPath -Raw | ConvertFrom-Json
        Pass "settings.json JSON構文OK"

        # defaultMode確認
        $mode = $json.permissions.defaultMode
        if ($mode -eq "bypassPermissions") {
            Pass "defaultMode = bypassPermissions（自動承認有効）"
        } else {
            Fail "defaultMode = '$mode'（bypassPermissions ではない）"
        }
    } catch {
        Fail "settings.json JSON構文エラー: $_"
    }
}

# ------------------------------------------------------------------------------
# 2. セキュリティフック
# ------------------------------------------------------------------------------
Section "2. セキュリティフック（~/.claude/hooks/）"

$hooks = @("layer2_bash_guard.py", "layer3_secrets_guard.py", "layer4_file_guard.py", "layer5_audit_log.py")
foreach ($h in $hooks) {
    if (Test-Path "$HOOKS_DIR\$h") {
        Pass "$h"
    } else {
        Fail "$h が存在しない"
    }
}

# ------------------------------------------------------------------------------
# 3. Python
# ------------------------------------------------------------------------------
Section "3. Python（フック実行に必要）"

try {
    $pyVer = python --version 2>&1
    Pass "Python: $pyVer"
} catch {
    Fail "python コマンドが見つからない → https://www.python.org/ からインストール"
}

# フックが実際に動くかテスト
try {
    $testInput = '{"tool_name":"Bash","tool_input":{"command":"echo test"}}'
    $result = $testInput | python "$HOOKS_DIR\layer2_bash_guard.py" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Pass "layer2_bash_guard.py 動作確認OK"
    } else {
        Fail "layer2_bash_guard.py が exit $LASTEXITCODE を返した"
    }
} catch {
    Fail "フックのテスト実行に失敗: $_"
}

# ------------------------------------------------------------------------------
# 4. メモリファイル
# ------------------------------------------------------------------------------
Section "4. アレンのメモリ（~/.claude/projects/）"

$projectKey = $REPO_ROOT[0].ToString().ToLower() + ($REPO_ROOT.Substring(1) -replace '[^a-zA-Z0-9]', '-')
$memDir = "$MEM_DIR\$projectKey\memory"

if (Test-Path $memDir) {
    $count = (Get-ChildItem $memDir -Filter "*.md").Count
    if ($count -ge 10) {
        Pass "メモリ $count 件 → $memDir"
    } else {
        Warn "メモリが $count 件しかない（19件あるはず）→ install.ps1 を再実行"
    }
} else {
    Fail "メモリディレクトリが存在しない → $memDir"
}

# ------------------------------------------------------------------------------
# 5. プロジェクト .claude/settings.json（自動プッシュ等）
# ------------------------------------------------------------------------------
Section "5. プロジェクト設定（.claude/settings.json）"

$projSettings = "$REPO_ROOT\.claude\settings.json"
if (Test-Path $projSettings) {
    $bytes2 = [System.IO.File]::ReadAllBytes($projSettings)
    if ($bytes2[0] -eq 0xEF -and $bytes2[1] -eq 0xBB -and $bytes2[2] -eq 0xBF) {
        Fail ".claude/settings.json がBOM付き（git pullで最新版を取得してください）"
    } else {
        Pass ".claude/settings.json BOMなし"
    }
    try {
        Get-Content $projSettings -Raw | ConvertFrom-Json | Out-Null
        Pass ".claude/settings.json JSON構文OK"
    } catch {
        Fail ".claude/settings.json JSON構文エラー"
    }
} else {
    Fail ".claude/settings.json が存在しない"
}

# ------------------------------------------------------------------------------
# 6. git 状態（リポジトリが最新か）
# ------------------------------------------------------------------------------
Section "6. git 状態"

Push-Location $REPO_ROOT
try {
    git fetch origin main --quiet 2>$null
    $behind = git rev-list HEAD..origin/main --count 2>$null
    if ($behind -eq "0" -or $behind -eq "") {
        Pass "リポジトリは最新（origin/main と同期済み）"
    } else {
        Warn "origin/main より $behind コミット遅れている → git pull を実行"
    }

    $status = git status --porcelain 2>$null
    if (-not $status) {
        Pass "未コミットの変更なし"
    } else {
        Warn "未コミットの変更あり（$($status.Count) 件）"
    }
} catch {
    Warn "git fetch に失敗（ネットワーク確認）"
} finally {
    Pop-Location
}

# ------------------------------------------------------------------------------
# 7. Claude Code のインストール確認
# ------------------------------------------------------------------------------
Section "7. Claude Code CLI"

try {
    $claudeVer = claude --version 2>&1
    Pass "Claude Code: $claudeVer"
} catch {
    Fail "claude コマンドが見つからない → npm install -g @anthropic-ai/claude-code"
}

# ------------------------------------------------------------------------------
# 結果サマリー
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
if ($ng -eq 0) {
    Write-Host "  全項目OK ($ok/$($ok+$ng)) — セットアップ完了！" -ForegroundColor Green
    Write-Host "  Claude Code を起動して動作確認してください。" -ForegroundColor Gray
} else {
    Write-Host "  NG あり ($ng 件) — 上記の [NG] 項目を修正してください" -ForegroundColor Red
    Write-Host ""
    Write-Host "  まず試すこと:" -ForegroundColor Yellow
    Write-Host "    git pull" -ForegroundColor Gray
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\install.ps1" -ForegroundColor Gray
    Write-Host "    → その後このスクリプトを再実行" -ForegroundColor Gray
}
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
