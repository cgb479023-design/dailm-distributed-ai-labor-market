param(
    [switch]$NoBackup
)

$ErrorActionPreference = "Stop"

$settingsPath = Join-Path $env:APPDATA "Antigravity\User\settings.json"
$settingsDir = Split-Path -Parent $settingsPath
$backupDir = Join-Path $settingsDir "backups"

function Remove-JsoncComments {
    param([string]$InputText)

    $sb = New-Object System.Text.StringBuilder
    $inString = $false
    $escaped = $false
    $inLineComment = $false
    $inBlockComment = $false

    for ($i = 0; $i -lt $InputText.Length; $i++) {
        $c = $InputText[$i]
        $next = if ($i + 1 -lt $InputText.Length) { $InputText[$i + 1] } else { [char]0 }

        if ($inLineComment) {
            if ($c -eq "`n") {
                $inLineComment = $false
                [void]$sb.Append($c)
            }
            continue
        }

        if ($inBlockComment) {
            if ($c -eq "*" -and $next -eq "/") {
                $inBlockComment = $false
                $i++
            }
            continue
        }

        if ($inString) {
            [void]$sb.Append($c)
            if ($escaped) {
                $escaped = $false
            } elseif ($c -eq "\\") {
                $escaped = $true
            } elseif ($c -eq '"') {
                $inString = $false
            }
            continue
        }

        if ($c -eq "/" -and $next -eq "/") {
            $inLineComment = $true
            $i++
            continue
        }

        if ($c -eq "/" -and $next -eq "*") {
            $inBlockComment = $true
            $i++
            continue
        }

        if ($c -eq '"') {
            $inString = $true
            [void]$sb.Append($c)
            continue
        }

        [void]$sb.Append($c)
    }

    return $sb.ToString()
}

function Normalize-JsonText {
    param([string]$Text)
    $noComments = Remove-JsoncComments -InputText $Text
    $normalized = [regex]::Replace($noComments, ",(?=\s*[}\]])", "")
    return $normalized
}

if (-not (Test-Path $settingsDir)) {
    New-Item -ItemType Directory -Force $settingsDir | Out-Null
}

if ((Test-Path $settingsPath) -and (-not $NoBackup)) {
    New-Item -ItemType Directory -Force $backupDir | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item $settingsPath (Join-Path $backupDir "settings-$stamp.json.bak") -Force
}

$existing = @{}
$parseSucceeded = $false
if (Test-Path $settingsPath) {
    $raw = Get-Content -Raw $settingsPath
    $normalized = Normalize-JsonText -Text $raw
    try {
        $parsed = $normalized | ConvertFrom-Json -AsHashtable
        if ($parsed -is [hashtable]) {
            $existing = $parsed
            $parseSucceeded = $true
        }
    } catch {
        $parseSucceeded = $false
    }
}

# Baseline keys that keep Antigravity + Claude Code auto-execution persistent across upgrades.
$existing["claudeCode.allowDangerouslySkipPermissions"] = $true
$existing["antigravity-plus.autoApprove.enabled"] = $true
$existing["tfa.system.autoAccept"] = $true
$existing["claudeCode.disableLoginPrompt"] = $true
$existing["claudeCode.useCtrlEnterToSend"] = $true
$existing["claudeCode.useTerminal"] = $true
$existing["claudeCode.preferredLocation"] = "editor-right"
$existing["antigravity.manager.position"] = "left"
$existing["files.autoSave"] = "afterDelay"
$existing["files.autoSaveDelay"] = 500

if (-not $existing.ContainsKey("permissions") -or -not ($existing["permissions"] -is [hashtable])) {
    $existing["permissions"] = @{}
}
$existing["permissions"]["defaultMode"] = "acceptEdits"

$json = $existing | ConvertTo-Json -Depth 100
Set-Content -Path $settingsPath -Value $json -Encoding UTF8

[pscustomobject]@{
    SettingsPath = $settingsPath
    ParseSucceeded = $parseSucceeded
    WroteFile = $true
    Timestamp = (Get-Date).ToString("s")
} | ConvertTo-Json -Depth 5
