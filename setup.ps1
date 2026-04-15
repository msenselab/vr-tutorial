# VR Tutorial — Environment Setup (Windows PowerShell)
# Usage: Right-click > Run with PowerShell, or open PowerShell and run:
#   Set-ExecutionPolicy -Scope Process Bypass; .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== VR Tutorial Setup ===" -ForegroundColor Cyan

# 1. Check for uv
try {
    $uvVersion = uv --version
    Write-Host "uv found: $uvVersion"
} catch {
    Write-Host "Installing uv..."
    irm https://astral.sh/uv/install.ps1 | iex
    # Refresh PATH so uv is available in this session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + $env:Path
}

# 2. Install Python 3.11 via uv
Write-Host "Ensuring Python 3.11 is available..."
uv python install 3.11

# 3. Create virtual environment with Python 3.11
Write-Host "Creating virtual environment..."
uv venv --python 3.11

# 4. Install dependencies from pyproject.toml
Write-Host "Installing dependencies..."
uv pip install -e .

# 5. Verify
Write-Host ""
Write-Host "=== Verifying setup ===" -ForegroundColor Cyan
& .\.venv\Scripts\python.exe -c "import ursina; print(f'ursina {ursina.__version__} OK')"
& .\.venv\Scripts\python.exe -c "import pygame; print(f'pygame {pygame.ver} OK')"

Write-Host ""
Write-Host "Setup complete! Activate the environment with:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Then test with:"
Write-Host "  python exercises\ex1_hello_ursina\hello_cube.py"
