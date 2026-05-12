# Windows Task Scheduler auto-pull setup
# Run as Administrator

$taskName   = "Allen-AutoPull"
$scriptPath = "C:\Users\tsube\OneDrive\デスクトップ\ai-ceo-project\tools\auto-sync\local_pull.ps1"
$action     = New-ScheduledTaskAction -Execute "powershell.exe" `
                  -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""

$triggers = @(
    (New-ScheduledTaskTrigger -Daily -At "08:00"),
    (New-ScheduledTaskTrigger -Daily -At "12:00"),
    (New-ScheduledTaskTrigger -Daily -At "18:00"),
    (New-ScheduledTaskTrigger -Daily -At "22:00")
)

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $triggers `
    -Settings $settings `
    -RunLevel Limited `
    -Force

Write-Host "Task '$taskName' registered. Auto-pull runs at 08:00 / 12:00 / 18:00 / 22:00."
