param(
    [string[]]$AgentExtensions = @(
        "openai.chatgpt",
        "github.copilot",
        "github.copilot-chat"
    ),
    [switch]$SkipExtensionInstall
)

$ErrorActionPreference = "Stop"

function Write-Section([string]$title) {
    Write-Output ""
    Write-Output "=== $title ==="
}

function Assert-FileExists([string]$path, [string]$name) {
    if (-not (Test-Path $path)) {
        throw "Missing $name at: $path"
    }
}

function Get-CodeCli {
    $candidates = @("code", "cursor")
    foreach ($cmd in $candidates) {
        $hit = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($null -ne $hit) {
            return $cmd
        }
    }
    return $null
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$fixScript = Join-Path $PSScriptRoot "fix-antigravity-agent.ps1"
$guardScript = Join-Path $PSScriptRoot "install-antigravity-guard.ps1"

$agentsPath = Join-Path $repoRoot "AGENTS.md"
$cursorRulesPath = Join-Path $repoRoot ".cursorrules"
$claudePath = Join-Path $repoRoot "CLAUDE.md"
$dnaPath = Join-Path $repoRoot "archives\MISSION_DNA.txt"

Write-Section "Preflight"
Assert-FileExists $fixScript "fix script"
Assert-FileExists $guardScript "guard script"
Assert-FileExists $agentsPath "AGENTS.md"
Assert-FileExists $cursorRulesPath ".cursorrules"
Assert-FileExists $claudePath "CLAUDE.md"
Assert-FileExists $dnaPath "MISSION_DNA"
Write-Output "Repo: $repoRoot"
Write-Output "User: $env:USERNAME"

Write-Section "Repair Antigravity Settings"
& powershell -NoProfile -ExecutionPolicy Bypass -File $fixScript | Out-String | Write-Output

Write-Section "Install Self-Heal Guard"
& powershell -NoProfile -ExecutionPolicy Bypass -File $guardScript | Out-String | Write-Output

Write-Section "Verify Guard Hooks"
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$runName = "AntigravityAgentSelfHeal"
$runValue = (Get-ItemProperty -Path $runKey -Name $runName -ErrorAction Stop).$runName
$taskInfo = schtasks /Query /TN "Antigravity-Agent-SelfHeal-Hourly" /FO LIST /V
Write-Output "RunKey: $runName = $runValue"
Write-Output $taskInfo

Write-Section "Verify Mission Anchors"
$anchorChecks = @(
    @{ Name = "AGENTS.md"; Path = $agentsPath; Pattern = "Priority Matrix|Mandatory Execution Directive" },
    @{ Name = ".cursorrules"; Path = $cursorRulesPath; Pattern = "MANDATORY EXECUTION DIRECTIVE" },
    @{ Name = "CLAUDE.md"; Path = $claudePath; Pattern = "Mission Anchor|MISSION ANCHOR|ASO|RCRP" },
    @{ Name = "MISSION_DNA"; Path = $dnaPath; Pattern = "DAILM MISSION DNA|SYNCED_AT|STATUS: ACTIVE" }
)

$anchorResults = @()
foreach ($item in $anchorChecks) {
    $content = Get-Content -Raw $item.Path
    $ok = [bool]($content -match $item.Pattern)
    $anchorResults += [pscustomobject]@{
        Item = $item.Name
        Path = $item.Path
        Passed = $ok
    }
}
$anchorResults | Format-Table -AutoSize
if (($anchorResults | Where-Object { -not $_.Passed }).Count -gt 0) {
    throw "Mission anchor verification failed."
}

Write-Section "Verify/Install IDE Agent Extensions"
$codeCli = Get-CodeCli
if ($null -eq $codeCli) {
    Write-Output "No IDE CLI found (code/cursor). Skipping extension checks."
    $extResults = @()
} else {
    $installed = @(&$codeCli --list-extensions 2>$null)
    $extResults = @()
    foreach ($ext in $AgentExtensions) {
        $exists = $installed -contains $ext
        $action = "none"
        if (-not $exists -and -not $SkipExtensionInstall) {
            & $codeCli --install-extension $ext --force | Out-Null
            $action = "installed"
            $installed = @(&$codeCli --list-extensions 2>$null)
            $exists = $installed -contains $ext
        }
        $extResults += [pscustomobject]@{
            Extension = $ext
            Present = $exists
            Action = $action
        }
    }
    $extResults | Format-Table -AutoSize
}

Write-Section "Final Status"
$summary = [pscustomobject]@{
    Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
    User = $env:USERNAME
    Repo = $repoRoot
    MissionAnchors = "OK"
    GuardTask = "Antigravity-Agent-SelfHeal-Hourly"
    RunKey = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\AntigravityAgentSelfHeal"
    ExtensionsChecked = $AgentExtensions.Count
    ExtensionsMissing = @($extResults | Where-Object { -not $_.Present }).Count
}
$summary | Format-List
Write-Output "Bootstrap complete."
