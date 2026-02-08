<#
  setup_and_run.ps1

  Usage: Run this in PowerShell from the repository root.
    - To only check prerequisites: `.\setup_and_run.ps1 -CheckOnly`
    - To create venv, install requirements and run server interactively: `.\setup_and_run.ps1`

  The script will NOT auto-install Python. It will offer winget command suggestions if Python is missing.
#>

param(
    [switch]$CheckOnly
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Info "Checking Python and pip availability..."

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Err "Python not found on PATH. Install Python 3.10+ and enable 'Add to PATH'."
    Write-Host "You can install via Microsoft Store or winget. Example (Admin):"
    Write-Host "  winget install --id Python.Python.3 -e --source winget"
    if ($CheckOnly) { exit 1 }
    Read-Host "Press Enter after installing Python to continue or Ctrl+C to abort"
}

Write-Info "Creating and activating virtual environment '.venv' (if missing)..."
if (-not (Test-Path .venv)) {
    python -m venv .venv
}

Write-Info "Activating venv"
. .\.venv\Scripts\Activate.ps1

Write-Info "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($CheckOnly) { Write-Info "Checks completed."; exit 0 }

Write-Info "Starting server (server.py) on port 5000..."
python server.py
