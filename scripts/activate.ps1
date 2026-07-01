$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:USERPROFILE ".hermes" }

Write-Host "  Activate Nora -> Hermes" -ForegroundColor Yellow
Write-Host "     Nora root:   $Root"
Write-Host "     Hermes home: $HermesHome"
Write-Host ""

$Config = Join-Path $HermesHome "config.yaml"
if (-not (Test-Path $Config)) {
    Write-Host "Error: Hermes not set up. Run: hermes setup" -ForegroundColor Red
    exit 1
}

$Python = $env:HERMES_PYTHON
if (-not $Python) {
    $VenvPy = Join-Path $HermesHome "hermes-agent\venv\Scripts\python.exe"
    if (Test-Path $VenvPy) { $Python = $VenvPy }
}
if (-not $Python) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $Python) { $Python = (Get-Command python3 -ErrorAction SilentlyContinue).Source }
}

$ActivateArgs = @("$Root\tools\activate_nora.py", "--nora-root", $Root, "--hermes-home", $HermesHome)
if ($args -contains "--merge-only") {
    $ActivateArgs += "--merge-only"
}

& $Python @ActivateArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    & $Python "$Root\tools\sync_env.py" --nora-root $Root --hermes-home $HermesHome
} else {
    Write-Host "  No $EnvFile - Discord secrets stay in $HermesHome\.env"
}

Write-Host ""
Write-Host "  Nora is live in Hermes." -ForegroundColor Yellow
Write-Host "  Start Discord: hermes gateway run"