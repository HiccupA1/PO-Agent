param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendDir = Join-Path $ProjectRoot "backend"
$ActivateScript = Join-Path $BackendDir ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $ActivateScript)) {
    Write-Host "backend/.venv was not found. Create it and install requirements first."
    Write-Host "cd backend"
    Write-Host "python -m venv .venv"
    Write-Host ".\.venv\Scripts\Activate.ps1"
    Write-Host "pip install -r requirements.txt"
    exit 1
}

Set-Location $BackendDir
. $ActivateScript

Write-Host "Starting PO Agent backend on port $Port"
python -m uvicorn app.main:app --reload --port $Port
