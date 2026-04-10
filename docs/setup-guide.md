---
title: "Laptop Setup Guide"
subtitle: "From Screen to Scene: Building VR Experiments with Python"
author: "Chunyu Qu, Artyom Zinchenko & Zhuanghua Shi"
date: "April 2026"
---

Please complete all steps **before** the workshop. The entire process takes about 15 minutes. If you run into problems, check the Troubleshooting section at the end or contact the workshop organizers.

---

## What you need

- A laptop (macOS or Windows) with administrator access
- An internet connection (for downloading software)
- About 1 GB of free disk space

---

## Step 1: Install Python

You need **Python 3.11 or newer**.

### macOS

**Option A — Download the installer (recommended)**

1. Go to <https://www.python.org/downloads/>
2. Click the big yellow "Download Python 3.1x.x" button
3. Open the downloaded `.pkg` file and follow the installer

**Option B — Homebrew** (if you already use it)

```bash
brew install python@3.12
```

### Windows

1. Go to <https://www.python.org/downloads/>
2. Click "Download Python 3.1x.x"
3. Run the installer
4. **Important:** Check the box **"Add Python to PATH"** at the bottom of the first screen before clicking "Install Now"

### Verify Python

Open a terminal (macOS: Terminal.app) or Command Prompt (Windows: search for `cmd`), then type:

```
python3 --version        # macOS
python --version         # Windows
```

You should see `Python 3.11.x` or higher. If you see `Python 2.x` or "command not found", revisit the installation steps.

---

## Step 2: Install uv (package manager)

We use **uv** — a fast Python package manager — to set up the project environment.

### macOS

Open Terminal and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen Terminal after installation so the `uv` command becomes available.

### Windows

Open PowerShell and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen PowerShell after installation.

### Verify uv

```
uv --version
```

You should see a version number (e.g., `uv 0.7.x`).

---

## Step 3: Download the workshop materials

### Option A — Git clone (if you have Git)

```bash
git clone https://github.com/strongway/vr-tutorial.git
```

### Option B — Download ZIP

1. Go to the repository page provided by the workshop organizers
2. Click the green "Code" button, then "Download ZIP"
3. Unzip the downloaded file to a location you can find easily (e.g., Desktop or Documents)

---

## Step 4: Create a virtual environment

Open a terminal and navigate to the project folder:

### macOS

```bash
cd ~/Desktop/vr-tutorial       # adjust path to where you put the folder
uv venv
```

### Windows (Command Prompt)

```cmd
cd %USERPROFILE%\Desktop\vr-tutorial
uv venv
```

### Windows (PowerShell)

```powershell
cd ~\Desktop\vr-tutorial
uv venv
```

This creates a `.venv` folder inside the project directory.

---

## Step 5: Activate the virtual environment

### macOS

```bash
source .venv/bin/activate
```

### Windows (Command Prompt)

```cmd
.venv\Scripts\activate
```

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

Your terminal prompt should now start with `(.venv)`. This means the environment is active.

> **Note:** You need to activate the environment every time you open a new terminal window during the workshop. Keep this command handy.

---

## Step 6: Install dependencies

With the virtual environment activated (you see `(.venv)` in your prompt), run:

```bash
uv pip install ursina pygame
```

This installs:

- **Ursina** — a 3D game engine we use to build VR scenes
- **pygame** — used for gamepad input in later exercises

The download is about 130 MB. Wait until it finishes.

---

## Step 7: Verify your setup

Run the test script:

### macOS

```bash
python exercises/ex1_hello_ursina/hello_cube.py
```

### Windows

```cmd
python exercises\ex1_hello_ursina\hello_cube.py
```

**Expected result:** A window opens showing an orange cube on a gray background.

Try these mouse controls:

- **Middle-click + drag** — orbit around the cube
- **Scroll wheel** — zoom in and out

Close the window when done (click the X or press Escape).

**If you see the cube, you are ready for the workshop!**

---

## Quick reference card

Here is a summary of the commands you will use during the workshop:

| | macOS | Windows |
|---|---|---|
| **Terminal** | Terminal.app | cmd / PowerShell |
| **Go to project** | `cd ~/Desktop/vr-tutorial` | `cd Desktop\vr-tutorial` |
| **Activate env** | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| **Run exercise** | `python exercises/ex1/hello_cube.py` | `python exercises\ex1\hello_cube.py` |
| **Install pkg** | `uv pip install <name>` | `uv pip install <name>` |

---

## Troubleshooting

### "python" or "python3" not found

- **macOS:** Try `python3` instead of `python`. If neither works, reinstall Python from python.org.
- **Windows:** You likely missed the "Add Python to PATH" checkbox. Rerun the installer, select "Modify", and make sure PATH is checked.

### "uv" not found

Close your terminal and reopen it. The `uv` installer updates your PATH, but the change only takes effect in new terminal sessions.

### ModuleNotFoundError: No module named 'ursina'

Your virtual environment is not activated. Look for `(.venv)` at the start of your prompt. If it is missing, activate the environment again (Step 5).

### The Ursina window opens and closes immediately

- Check the terminal for error messages.
- Make sure you are running the correct script path.
- Update your graphics drivers (Ursina needs OpenGL support).

### macOS asks for permissions

macOS may show dialogs about screen recording or accessibility. Click **Allow** — Ursina needs these permissions to open a window and capture mouse input. You can manage these in **System Settings > Privacy & Security**.

### Windows Defender or antivirus blocks the script

Some antivirus tools flag Ursina's window creation. Either add the project folder to your antivirus exclusion list, or temporarily disable real-time scanning while running exercises.

### Installation fails behind a corporate firewall

If `uv pip install` times out or shows SSL errors, try:

```bash
uv pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ursina pygame
```

### Gamepad not detected (Exercise 4 only)

1. Plug in the gamepad **before** starting the script.
2. On macOS, check **System Settings > Privacy & Security > Input Monitoring**.
3. Try a different USB port.
4. Gamepad is optional — all exercises work with keyboard and mouse.

---

## Getting help

If none of the above solves your problem, bring your laptop to the workshop. We will have time at the start to debug setup issues together.
