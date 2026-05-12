# Windows Task Scheduler に自動pull タスクを登録する
# 管理者権限で実行: PowerShell右クリック→「管理者として実行」→このスクリプトを実行

$taskName   = "Allen-AutoPull"
$scriptPath = "C:\Users\e046ffv\OneDrive\ai-ceo-project\tools\auto-sync\local_pull.ps1"
$action     = New-ScheduledTaskAction -Execute "powershell.exe" `
                  -Argument "-NonInteractive -WindowStyle Hidden -File `"$scriptPath`""

# 毎朝 8:00, 12:00, 18:00, 22:00 の4回
$triggers = @(
    New-ScheduledTaskTrigger -Daily -At "08:00",
    New-ScheduledTaskTrigger -Daily -At "12:00",
    New-ScheduledTaskTrigger -Daily -At "18:00",
    New-ScheduledTaskTrigger -Daily -At "22:00"
)

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $triggers `
    -Settings $settings `
    -RunLevel Limited `
    -Force

Write-Host "タスク '$taskName' を登録しました。8:00 / 12:00 / 18:00 / 22:00 に自動pull実行。"
