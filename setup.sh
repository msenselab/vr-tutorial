#!/usr/bin/env bash
# VR Tutorial — Environment Setup (macOS / Linux)
# Usage: bash setup.sh

set -e

echo "=== VR Tutorial Setup ==="

# 1. Check for uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "uv found: $(uv --version)"
fi

# 2. Install Python 3.11 via uv (if not already available)
echo "Ensuring Python 3.11 is available..."
uv python install 3.11

# 3. Create virtual environment with Python 3.11
echo "Creating virtual environment..."
uv venv --python 3.11

# 4. Install dependencies from pyproject.toml
echo "Installing dependencies..."
uv pip install -e .

# 5. Verify
echo ""
echo "=== Verifying setup ==="
.venv/bin/python -c "import ursina; print(f'ursina {ursina.__version__} OK')"
.venv/bin/python -c "import pygame; print(f'pygame {pygame.ver} OK')"

echo ""
echo "Setup complete! Activate the environment with:"
echo "  source .venv/bin/activate"
echo ""
echo "Then test with:"
echo "  python exercises/ex1_hello_ursina/hello_cube.py"
