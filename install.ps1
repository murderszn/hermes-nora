$ErrorActionPreference = "Stop"

$Repo = "https://github.com/murderszn/hermes-nora.git"
$InstallDir = if ($env:NORA_INSTALL_DIR) { $env:NORA_INSTALL_DIR } else { Join-Path $env:USERPROFILE ".nora" }

Write-Host "  Nora - Hermes Agent Ops Persona" -ForegroundColor Yellow
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Error: git is required. Install Git and retry." -ForegroundColor Red
    exit 1
}

if (Test-Path (Join-Path $InstallDir ".git")) {
    Write-Host "Updating existing install at $InstallDir"
    git -C $InstallDir pull --ff-only
} else {
    Write-Host "Cloning into $InstallDir"
    git clone $Repo $InstallDir
}

$Bootstrap = Join-Path $InstallDir "bootstrap.ps1"
if (Test-Path $Bootstrap) {
    & $Bootstrap
} else {
    Write-Host ""
    Write-Host "Installed to $InstallDir"
    Write-Host "Run: cd $InstallDir"
}

Write-Host ""
Write-Host "  Nora files are in $InstallDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Next - run the onboarding wizard:"
Write-Host "    $InstallDir\scripts\onboard.ps1"
Write-Host ""
Write-Host "  Or activate only:"
Write-Host "    $InstallDir\scripts\activate.ps1"
Write-Host ""
Write-Host "  Docs: $InstallDir\persona\channels.md"