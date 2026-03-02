param(
    [string]$TaskName = "SphereLinkedInBotDaily",
    [string]$StartTime = "08:00"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($StartTime -notmatch "^\d{2}:\d{2}$") {
    throw "StartTime must be in HH:mm format."
}

$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$runScript = Join-Path -Path $scriptDir -ChildPath "run_bot.ps1"

if (-not (Test-Path -Path $runScript)) {
    throw "Run script not found: $runScript"
}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runScript`""
$trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Description "Runs sphere-linkedin-bot daily." `
    -Force | Out-Null

Write-Output "Task '$TaskName' installed. Daily run time: $StartTime"
