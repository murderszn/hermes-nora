$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Bootstrapping Nora from $Root"
Write-Host ""

function Count-Skills {
    if (Test-Path (Join-Path $Root "skills")) {
        return (Get-ChildItem -Path (Join-Path $Root "skills") -Recurse -Filter "SKILL.md" -ErrorAction SilentlyContinue).Count
    }
    return 0
}

$SoulPath = Join-Path $Root "hermes\SOUL.md"
if (Test-Path $SoulPath) {
    $lines = (Get-Content $SoulPath | Where-Object { $_.Trim() -and $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*\*' }).Count
    if ($lines -gt 5) {
        Write-Host "  OK Soul document (hermes\SOUL.md)"
    } else {
        Write-Host "  Soul template present - customize hermes\SOUL.md"
    }
}

if (Test-Path (Join-Path $Root "persona")) {
    Write-Host "  OK Persona / roles (persona\)"
}

$n = Count-Skills
if ($n -gt 0) {
    Write-Host "  OK Skills library ($n skills)"
}

if (Test-Path (Join-Path $Root "tools")) {
    Write-Host "  OK Tools (tools\)"
}

Write-Host ""
Write-Host "Run the onboarding wizard (recommended):"
Write-Host "  $Root\scripts\onboard.ps1"
Write-Host ""
Write-Host "Or activate only:"
Write-Host "  $Root\scripts\activate.ps1"
Write-Host ""
Write-Host "Docs:  $Root\persona\hermes-setup.md"
Write-Host "Channels: $Root\persona\channels.md"