$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:USERPROFILE ".hermes" }

$Python = $env:HERMES_PYTHON
if (-not $Python) {
    $VenvPy = Join-Path $HermesHome "hermes-agent\venv\Scripts\python.exe"
    if (Test-Path $VenvPy) { $Python = $VenvPy }
}
if (-not $Python) {
    $Python = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $Python) { $Python = (Get-Command python3 -ErrorAction SilentlyContinue).Source }
}
if (-not $Python) {
    Write-Host "Error: Python not found. Install Python 3 or Hermes Agent." -ForegroundColor Red
    exit 1
}

$OnboardPy = Join-Path $Root "tools\onboard.py"
$Args = @("--nora-root", $Root, "--hermes-home", $HermesHome) + $args
& $Python $OnboardPy @Args
exit $LASTEXITCODE