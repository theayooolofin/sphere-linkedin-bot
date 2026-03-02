Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$repoRoot = Split-Path -Path $scriptDir -Parent
$botPath = Join-Path -Path $repoRoot -ChildPath "bot.py"
$dotenvPath = Join-Path -Path $repoRoot -ChildPath ".env"
$venvPython = Join-Path -Path $repoRoot -ChildPath ".venv\Scripts\python.exe"
$logDir = Join-Path -Path $repoRoot -ChildPath "logs"
$logPath = Join-Path -Path $logDir -ChildPath "scheduler.log"

function Import-DotEnv {
    param([string]$Path)

    if (-not (Test-Path -Path $Path)) {
        return
    }

    foreach ($line in Get-Content -Path $Path) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) {
            continue
        }
        if ($trimmed.StartsWith("#")) {
            continue
        }
        if (-not $trimmed.Contains("=")) {
            continue
        }

        $parts = $trimmed.Split("=", 2)
        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        if ($name -eq "") {
            continue
        }

        if (
            ($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))
        ) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

Import-DotEnv -Path $dotenvPath

$required = @("GEMINI_API_KEY", "LINKEDIN_ACCESS_TOKEN", "LINKEDIN_PERSON_URN")
foreach ($name in $required) {
    $value = [Environment]::GetEnvironmentVariable($name, "Process")
    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Error "Missing required variable: $name. Set it in .env at $dotenvPath or user environment."
    }
}

if (-not (Test-Path -Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logPath -Value "[$timestamp] Starting bot run."

$pythonExe = if (Test-Path -Path $venvPython) { $venvPython } else { "python" }

Push-Location $repoRoot
try {
    & $pythonExe $botPath *>> $logPath
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $logPath -Value "[$ts] Bot exited with code $exitCode."
        exit $exitCode
    }

    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$ts] Bot completed successfully."
}
finally {
    Pop-Location
}

