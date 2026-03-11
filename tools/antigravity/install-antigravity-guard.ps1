$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "fix-antigravity-agent.ps1"
if (-not (Test-Path $scriptPath)) {
    throw "Missing script: $scriptPath"
}

$taskHourly = "Antigravity-Agent-SelfHeal-Hourly"
$tr = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""$scriptPath"""

# 1) Hourly self-heal task.
schtasks /Create /TN $taskHourly /TR $tr /SC HOURLY /MO 1 /F | Out-Null
schtasks /Run /TN $taskHourly | Out-Null

# 2) Per-login self-heal via HKCU Run key (works without admin rights).
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$runName = "AntigravityAgentSelfHeal"
$runValue = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""$scriptPath"""
New-Item -Path $runKey -Force | Out-Null
Set-ItemProperty -Path $runKey -Name $runName -Value $runValue

Start-Sleep -Seconds 2
$q = schtasks /Query /TN $taskHourly /FO LIST

"=== Login Hook (Registry Run) ==="
"$runKey::$runName = $runValue"
"=== Hourly Task ==="
$q
