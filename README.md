# wMouseClicker

A simple, flexible periodic mouse clicker tool for Windows.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## Features

- 🖱️ Click on any screen position at regular intervals
- ⏱️ Configurable interval (minutes and seconds)
- 📍 Easy position capture with hotkey
- 🔘 Support for left, right, and double clicks
- ⌨️ Global hotkeys for quick control
- 🎨 Modern dark theme UI

## Installation

1. Make sure you have Python 3.8+ installed
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the tool:

```bash
python mouse_clicker.py
```

2. Set the click position:
   - Enter X and Y coordinates manually, OR
   - Move your mouse to the desired position and press **F6** (or click "Capture Position")

3. Set the interval (e.g., 5 minutes for retrying Oracle Cloud VM creation)

4. Choose click type (left/right/double)

5. Press **F7** or click "Start" to begin

6. Press **F8** or click "Stop" to stop

## Hotkeys

| Key | Action |
|-----|--------|
| F6 | Capture current mouse position |
| F7 | Start clicking |
| F8 | Stop clicking |

## Safety

- **Fail-safe enabled**: Move your mouse to any corner of the screen to abort
- The tool shows a countdown to the next click
- Click counter helps you track activity

## Use Case Example: Oracle Cloud VM Retry

When Oracle Cloud shows "Out of capacity" error:

1. Position your mouse over the "Create" button
2. Press F6 to capture the position
3. Set interval to 5 minutes (or desired retry frequency)
4. Press F7 to start
5. The tool will automatically click the button every 5 minutes

## License

MIT License - feel free to use and modify.
