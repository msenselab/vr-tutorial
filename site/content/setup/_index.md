---
title: "Setup Guide"
description: "Pre-workshop installation and verification"
weight: 1
---

Complete these steps **before** the workshop. The entire process takes about 10 minutes with a decent internet connection.

## 1. Install Python 3.11+

### macOS

Download the latest Python from [python.org](https://www.python.org/downloads/) or install via Homebrew:

```bash
brew install python@3.12
```

### Windows

Download the installer from [python.org](https://www.python.org/downloads/). During installation, check **"Add Python to PATH"** -- this is critical.

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

### Verify Python

Open a terminal (macOS/Linux) or Command Prompt (Windows) and run:

```bash
python --version
# or
python3 --version
```

You should see `Python 3.11.x` or higher.

## 2. Create a Virtual Environment

Navigate to where you want to work and create a virtual environment:

```bash
cd vr-tutorial
uv venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Your terminal prompt should now show `(.venv)` at the beginning.

## 3. Install Dependencies

With the virtual environment activated:

```bash
uv pip install ursina pygame
```

This installs the Ursina game engine and pygame (used for gamepad input).

## 4. Verify Your Setup

Run the hello cube script:

```bash
python exercises/ex1_hello_ursina/hello_cube.py
```

A window should open showing an orange cube. Use your mouse to orbit around it:

- **Right-click + drag** -- orbit
- **Scroll wheel** -- zoom
- **Middle-click + drag** -- pan

If you see the cube, you are ready for the workshop.

## Troubleshooting

### ModuleNotFoundError: No module named 'ursina'

The most common cause is running Python from outside your virtual environment. Make sure you see `(.venv)` in your terminal prompt. If not, activate the environment first:

```bash
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

Then try again. If the error persists, reinstall:

```bash
uv pip install --force-reinstall ursina pygame
```

### Window opens and immediately closes

Check the terminal for error messages. Common causes:

- A missing dependency -- run `uv pip install ursina` again to make sure everything is installed.
- An outdated GPU driver -- update your graphics drivers.
- Python version too old -- Ursina requires Python 3.8+, and we recommend 3.11+.

### Display or window errors

Ursina needs a display to render. If you are running over SSH, use X-forwarding (`ssh -X`) or work on a machine with a monitor attached.

On some Linux systems you may need to install OpenGL libraries:

```bash
sudo apt install libgl1-mesa-glx
```

### macOS permission dialogs

macOS may ask for permission to control your computer or access the screen. Grant these permissions -- Ursina needs them to open a window and capture mouse input. You can find these in **System Settings > Privacy & Security > Accessibility**.

### Windows antivirus blocking

Some antivirus software flags Ursina's window creation as suspicious. If the script is blocked:

1. Add your project folder to the antivirus exclusion list.
2. Or temporarily disable real-time scanning while running exercises.

### Gamepad not detected

Gamepad support (Exercise 4) uses pygame, not Ursina. If your gamepad is not detected:

1. Make sure the gamepad is plugged in **before** starting the script.
2. On macOS, check **System Settings > Privacy & Security > Input Monitoring** for any required permissions.
3. Try a different USB port or cable.
4. Run the gamepad diagnostic: `python exercises/ex4_pick_up_star/gamepad_demo.py` -- it will tell you whether pygame sees your controller.

Gamepad input is optional. All exercises work with keyboard and mouse.

### pip install fails behind a corporate firewall

If `uv pip install` times out or fails with SSL errors, try:

```bash
uv pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ursina pygame
```

Or download the packages manually from [PyPI](https://pypi.org/) and install from local files.
