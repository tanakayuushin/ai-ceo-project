# Allen AI CEO - Setup Verification Script
# Run this after git pull or install.ps1 to confirm all settings are correct.
#
# Usage:
#   cd <repo>\setup
#   powershell -ExecutionPolicy Bypass -File .\verify.ps1

$REPO_ROOT  = Split-Path -Parent $PSScriptRoot
$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$HOOKS_DIR  = "$CLAUDE_DIR\hooks"
$MEM_DIR    = "$CLAUDE_DIR\projects"

$ok = 0
$ng = 0

function Pass($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green;  $script:ok++ }
function Fail($msg) { Write-Host "  [NG] $msg" -ForegroundColor Red;    $script:ng++ }
function Warn($msg) { Write-Host "  [!!] $msg" -ForegroundColor Yellow }
function Section($title) {
    Write-Host ""
    Write-Host "--- $title ---" -ForegroundColor Cyan
}

function HasBom($path) {
    $b = [System.IO.File]::ReadAllBytes($path)
    return ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
}

function RemoveBom($path) {
    $enc   = New-Object System.Text.UTF8Encoding($true)
    $noBom = New-Object System.Text.UTF8Encoding($false)
    $text  = [System.IO.File]::ReadAllText($path, $enc)
    [System.IO.File]::WriteAllText($path, $text, $noBom)
}

Write-Host ""
Write-Host "=== Allen AI CEO Setup Verification ===" -ForegroundColor Cyan
Write-Host "REPO : $REPO_ROOT"
Write-Host "HOME : $env:USERPROFILE"

# --- 1. ~/.claude/settings.json ---
Section "1. settings.json (auto-approval)"

$settingsPath = "$CLAUDE_DIR\settings.json"
if (-not (Test-Path $settingsPath)) {
    Fail "settings.json not found -- run install.ps1 first"
} else {
    if (HasBom $settingsPath) {
        Write-Host "  [!!] settings.json has BOM -- fixing automatically..." -ForegroundColor Yellow
        RemoveBom $settingsPath
        if (HasBom $settingsPath) { Fail "Could not remove BOM from settings.json" }
        else                      { Pass "settings.json BOM removed (now OK)" }
    } else {
        Pass "settings.json: no BOM"
    }

    try {
        $json = Get-Content $settingsPath -Raw | ConvertFrom-Json
        Pass "settings.json: valid JSON"
        $mode = $json.permissions.defaultMode
        if ($mode -eq "bypassPermissions") {
            Pass "defaultMode = bypassPermissions (auto-approval enabled)"
        } else {
            Fail "defaultMode = '$mode' (expected: bypassPermissions)"
        }
    } catch {
        Fail "settings.json: JSON parse error -- $_"
    }
}

# --- 2. Security hooks ---
Section "2. Security hooks (~/.claude/hooks/)"

$hooks = @("layer2_bash_guard.py","layer3_secrets_guard.py","layer4_file_guard.py","layer5_audit_log.py")
foreach ($h in $hooks) {
    if (Test-Path "$HOOKS_DIR\$h") { Pass $h }
    else                           { Fail "$h missing" }
}

# --- 3. Python ---
Section "3. Python (required for hooks)"

try {
    $pyVer = python --version 2>&1
    Pass "Python: $pyVer"
    $testInput = '{"tool_name":"Bash","tool_input":{"command":"echo test"}}'
    $null = $testInput | python "$HOOKS_DIR\layer2_bash_guard.py" 2>&1
    if ($LASTEXITCODE -eq 0) { Pass "layer2_bash_guard.py runs OK" }
    else                     { Fail "layer2_bash_guard.py exited $LASTEXITCODE" }
} catch {
    Fail "python not found -- install from https://www.python.org/"
}

# --- 4. Memory files ---
Section "4. Allen memory (~/.claude/projects/)"

$projectKey = $REPO_ROOT[0].ToString().ToLower() + ($REPO_ROOT.Substring(1) -replace '[^a-zA-Z0-9]', '-')
$memDir = "$MEM_DIR\$projectKey\memory"

if (Test-Path $memDir) {
    $count = (Get-ChildItem $memDir -Filter "*.md").Count
    if ($count -ge 10) { Pass "Memory: $count files found" }
    else               { Warn "Memory: only $count files (expected 19+) -- re-run install.ps1" }
} else {
    Fail "Memory directory not found: $memDir"
}

# --- 5. Project .claude/settings.json ---
Section "5. Project settings (.claude/settings.json)"

$projSettings = "$REPO_ROOT\.claude\settings.json"
if (Test-Path $projSettings) {
    if (HasBom $projSettings) {
        Write-Host "  [!!] .claude/settings.json has BOM -- fixing automatically..." -ForegroundColor Yellow
        RemoveBom $projSettings
        if (HasBom $projSettings) { Fail "Could not remove BOM from .claude/settings.json" }
        else                      { Pass ".claude/settings.json BOM removed (now OK)" }
    } else {
        Pass ".claude/settings.json: no BOM"
    }
    try {
        Get-Content $projSettings -Raw | ConvertFrom-Json | Out-Null
        Pass ".claude/settings.json: valid JSON"
    } catch {
        Fail ".claude/settings.json: JSON parse error"
    }
} else {
    Fail ".claude/settings.json not found"
}

# --- 6. Git status ---
Section "6. Git status"

Push-Location $REPO_ROOT
try {
    git fetch origin main --quiet 2>$null
    $behind = git rev-list HEAD..origin/main --count 2>$null
    if ($behind -eq "0" -or $behind -eq "") { Pass "Repo is up to date with origin/main" }
    else                                     { Warn "$behind commit(s) behind origin/main -- run: git pull" }

    $dirty = git status --porcelain 2>$null
    if (-not $dirty) { Pass "No uncommitted changes" }
    else             { Warn "Uncommitted changes ($($dirty.Count) files)" }
} catch {
    Warn "git fetch failed (check network)"
} finally {
    Pop-Location
}

# --- 7. Claude Code CLI ---
Section "7. Claude Code CLI"

try {
    $claudeVer = claude --version 2>&1
    Pass "Claude Code: $claudeVer"
} catch {
    Fail "claude not found -- run: npm install -g @anthropic-ai/claude-code"
}

# --- Summary ---
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
if ($ng -eq 0) {
    Write-Host "  All checks passed ($ok/$($ok+$ng)) -- Setup complete!" -ForegroundColor Green
    Write-Host "  Start Claude Code and test with: git status" -ForegroundColor Gray
} else {
    Write-Host "  $ng check(s) failed -- fix [NG] items above" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Quick fix:" -ForegroundColor Yellow
    Write-Host "    git pull" -ForegroundColor Gray
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\install.ps1" -ForegroundColor Gray
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\verify.ps1" -ForegroundColor Gray
}
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
