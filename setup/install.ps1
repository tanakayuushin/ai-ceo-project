# Allen AI CEO - Setup Script
# Run this script on a new PC to reproduce all Allen configurations.
#
# Usage:
#   cd <repo>\setup
#   powershell -ExecutionPolicy Bypass -File .\install.ps1

$ErrorActionPreference = "Stop"

$REPO_ROOT  = Split-Path -Parent $PSScriptRoot
$SETUP_DIR  = $PSScriptRoot
$CLAUDE_DIR = "$env:USERPROFILE\.claude"
$HOOKS_DIR  = "$CLAUDE_DIR\hooks"
$MEM_DIR    = "$CLAUDE_DIR\projects"

Write-Host ""
Write-Host "=== Allen AI CEO Setup ===" -ForegroundColor Cyan
Write-Host "REPO : $REPO_ROOT"
Write-Host "HOME : $env:USERPROFILE"
Write-Host ""

# Step 1: Copy security hooks to ~/.claude/hooks/
Write-Host "[1/4] Installing security hooks..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force $HOOKS_DIR | Out-Null
Copy-Item "$SETUP_DIR\hooks\*.py" $HOOKS_DIR -Force
Write-Host "      OK: $HOOKS_DIR" -ForegroundColor Green

# Step 2: Generate ~/.claude/settings.json (replace {{HOOKS_DIR}} with actual path)
Write-Host "[2/4] Generating settings.json..." -ForegroundColor Yellow
$template = [System.IO.File]::ReadAllText("$SETUP_DIR\settings_template.json", (New-Object System.Text.UTF8Encoding($false)))
$settings = $template -replace '\{\{HOOKS_DIR\}\}', ($HOOKS_DIR -replace '\\', '\\')
$settingsPath = "$CLAUDE_DIR\settings.json"

if (Test-Path $settingsPath) {
    $backup = "$CLAUDE_DIR\settings.json.bak"
    Copy-Item $settingsPath $backup -Force
    Write-Host "      Backed up existing settings.json to $backup" -ForegroundColor DarkYellow
}

# Write as UTF-8 without BOM (PS5.1 Set-Content -Encoding UTF8 adds BOM which breaks JSON parsing)
$noBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($settingsPath, $settings, $noBom)
Write-Host "      OK: $settingsPath" -ForegroundColor Green

# Step 3: Copy memory files to project-keyed directory
# Claude Code manages memory per project path. Convert absolute path to key format.
# Example: C:\Users\foo\OneDrive\Desktop\ai-ceo-project -> c--Users-foo-OneDrive--Desktop--ai-ceo-project
Write-Host "[3/4] Installing memory files..." -ForegroundColor Yellow
$rawPath = $REPO_ROOT
$projectKey = $rawPath[0].ToString().ToLower() + ($rawPath.Substring(1) -replace '[^a-zA-Z0-9]', '-')

$targetMemDir = "$MEM_DIR\$projectKey\memory"
New-Item -ItemType Directory -Force $targetMemDir | Out-Null
Copy-Item "$SETUP_DIR\memory\*.md" $targetMemDir -Force
Write-Host "      OK: $targetMemDir" -ForegroundColor Green
Write-Host "      ($((Get-ChildItem $targetMemDir).Count) memory files)" -ForegroundColor DarkGray

# Step 4: Verify Python installation
Write-Host "[4/4] Checking Python..." -ForegroundColor Yellow
try {
    $pyVer = python --version 2>&1
    Write-Host "      OK: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "      WARNING: python command not found." -ForegroundColor Red
    Write-Host "      Install Python from https://www.python.org/" -ForegroundColor Red
    Write-Host "      Hooks require Python to run." -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Run verify.ps1 to confirm all settings are correct" -ForegroundColor Gray
Write-Host "     powershell -ExecutionPolicy Bypass -File .\verify.ps1" -ForegroundColor Gray
Write-Host "  2. Start (or restart) Claude Code" -ForegroundColor Gray
Write-Host "  3. Open this repo in Claude Code: $REPO_ROOT" -ForegroundColor Gray
Write-Host ""
Write-Host "Note: API keys must be configured separately in the .env file." -ForegroundColor DarkYellow
