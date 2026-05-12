# Allen auto-pull: GitHubの最新をローカルに取り込む
$repoPath = "C:\Users\e046ffv\OneDrive\ai-ceo-project"
$logFile  = "$repoPath\tools\auto-sync\pull.log"

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logLine   = "[$timestamp] git pull origin main"

try {
    $result = & git -C $repoPath pull origin main 2>&1
    $status = if ($LASTEXITCODE -eq 0) { "OK" } else { "FAIL" }
    Add-Content -Path $logFile -Value "$logLine => $status: $result"
} catch {
    Add-Content -Path $logFile -Value "$logLine => ERROR: $_"
}
