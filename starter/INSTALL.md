# Workshop Setup Guide

Follow these steps before the workshop to make sure everything works.

## 1. Install Python

You need Python 3.11 or newer.

- **macOS**: `brew install python@3.11` or download from [python.org](https://python.org/downloads/)
- **Windows**: Download from [python.org](https://python.org/downloads/). Check "Add to PATH" during install.
- **Linux**: `sudo apt install python3.11 python3.11-venv` (Ubuntu/Debian)

## 2. Create a Virtual Environment

```bash
cd starter
uv venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

## 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

## 4. Verify Your Setup

```bash
python ex1_hello_ursina/hello_cube.py
```

You should see a window with an orange cube. You can orbit with right-click drag and zoom with scroll wheel.

If this works, you're ready for the workshop!

## Troubleshooting

- **ModuleNotFoundError: No module named 'ursina'**: Make sure your virtual environment is activated
- **No window appears**: Ursina needs a display. If you're on a headless server, use a machine with a monitor
- **macOS permission dialog**: Click "Allow" when macOS asks about screen recording or accessibility
- **Windows Defender warning**: Click "Run anyway" -- Ursina is safe
