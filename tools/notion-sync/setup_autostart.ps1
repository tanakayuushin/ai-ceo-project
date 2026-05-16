# Soundcore -> Notion auto-sync: Windows startup setup (no admin required)

$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$EnvFile      = Join-Path $ProjectRoot ".env"
$MainScript   = Join-Path $ScriptDir "soundcore_to_notion.py"
$WrapperVbs   = Join-Path $ScriptDir "start_silent.vbs"
$StartupDir   = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir "SoundcoreNotion.lnk"

Write-Host "=== Soundcore -> Notion Setup ===" -ForegroundColor Cyan

# Step 1: Install pip dependencies
Write-Host "`n[1/4] Installing pip packages..." -ForegroundColor Yellow
pip install -r (Join-Path $ScriptDir "requirements.txt") --quiet
Write-Host "  Done." -ForegroundColor Green

# Step 2: Check .env
if (-not (Test-Path $EnvFile)) {
    Write-Host "`n[WARN] .env not found: $EnvFile" -ForegroundColor Red
    Write-Host "Please add to .env:"
    Write-Host "  ANTHROPIC_API_KEY=sk-ant-xxxxxx"
    Write-Host "  NOTION_TOKEN=secret_xxxxxx"
    Write-Host "  NOTION_PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    Write-Host "  SOUNDCORE_INBOX=C:\Users\tsube\OneDrive\Soundcore\inbox"
}

# Step 3: Create VBS wrapper (runs Python silently, no console window)
# Python script loads .env itself, so VBS only needs to launch it.
Write-Host "`n[2/4] Creating VBS launcher..." -ForegroundColor Yellow

# Build VBS line using [char]34 (double-quote) to avoid PowerShell quote confusion
$q = [char]34
$vbsRunLine = "WShell.Run " + $q + "python " + $q + $q + $MainScript + $q + $q + $q + ", 0, False"

$vbsLines = @(
    "' Soundcore -> Notion silent launcher",
    "Dim WShell",
    "Set WShell = CreateObject(" + $q + "WScript.Shell" + $q + ")",
    $vbsRunLine
)
Set-Content -Path $WrapperVbs -Value $vbsLines -Encoding ASCII
Write-Host "  Created: $WrapperVbs" -ForegroundColor Green

# Step 4: Create Startup shortcut pointing to wscript.exe + VBS
Write-Host "`n[3/4] Creating Startup shortcut..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($ShortcutPath)
$shortcut.TargetPath  = "wscript.exe"
$shortcut.Arguments   = "`"$WrapperVbs`""
$shortcut.Description = "Soundcore Notion auto-sync"
$shortcut.Save()
Write-Host "  Created: $ShortcutPath" -ForegroundColor Green

# Step 5: Create inbox/archive folders
Write-Host "`n[4/4] Creating inbox/archive folders..." -ForegroundColor Yellow
$InboxPath   = "C:\Users\tsube\OneDrive\Soundcore\inbox"
$ArchivePath = "C:\Users\tsube\OneDrive\Soundcore\archive"
New-Item -ItemType Directory -Force -Path $InboxPath   | Out-Null
New-Item -ItemType Directory -Force -Path $ArchivePath | Out-Null
Write-Host "  Inbox  : $InboxPath" -ForegroundColor Green
Write-Host "  Archive: $ArchivePath" -ForegroundColor Green

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Next steps:"
Write-Host "  1. Confirm .env has: ANTHROPIC_API_KEY, NOTION_TOKEN, NOTION_PAGE_ID"
Write-Host "  2. Export Soundcore transcript to: $InboxPath"
Write-Host "  3. Test now: python $MainScript"
Write-Host "  4. Will auto-start on next Windows login."
