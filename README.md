# wMouseClicker

A simple, flexible periodic mouse clicker tool for Windows with UI safety checks.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## Features

- 🖱️ Click on any screen position at regular intervals
- ⏱️ Configurable interval (minutes and seconds)
- 🎲 Random interval option (e.g., between 5-20 minutes)
- 📍 Interactive 3-step screen capture with visual overlay
- 🛡️ UI safety check - only clicks if the target UI hasn't changed
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

2. Press **F6** to start the 3-step capture process:
   - **Step 1:** Click on the position where you want to auto-click
   - **Step 2:** Draw a rectangle around the UI area to monitor
   - **Step 3:** Click on the rest position (where mouse clicks after main click)

3. Set the interval (e.g., 5 minutes)

4. Optionally enable **Random interval** and set a max value

5. Press **F7** or click "Start" to begin

6. Press **F8** or click "Stop" to stop

## Hotkeys

| Key | Action |
|-----|--------|
| F6 | Start 3-step capture (click position, UI area, rest position) |
| F7 | Start clicking |
| F8 | Stop clicking |
| ESC | Cancel capture (during selection) |

## UI Safety Check

The tool includes a safety feature that prevents clicking when the UI has changed:

1. **Captured UI**: When you draw the rectangle in Step 2, a screenshot of that area is saved
2. **Before each click**: The tool takes a new screenshot of the same area
3. **Comparison**: If the UI matches the original (based on threshold %), it clicks; otherwise, it skips
4. **Threshold**: Default is 100% (exact match). Lower it if minor variations are acceptable

### Why Rest Position?

After clicking a button, the mouse cursor often triggers hover effects (e.g., hand cursor, color change). This would cause the next UI comparison to fail. The **rest position** (Step 3) solves this by clicking somewhere neutral after each main click, returning the UI to its normal state.

## Use Case Example: Oracle Cloud VM Retry

When Oracle Cloud shows "Out of capacity" error and you want to keep retrying:

1. Press **F6** to start capture
2. **Step 1:** Click on the "Create" button
3. **Step 2:** Draw a rectangle around the button (or error message area)
4. **Step 3:** Click on an empty area of the page (rest position)
5. Set interval to **5 minutes** (or enable random: 5-20 min)
6. Press **F7** to start

The tool will:
- Check if the UI looks the same as when captured
- If yes → click the Create button, then click the rest position
- If no → skip (page may have changed, navigated away, etc.)
- Wait for the interval, then repeat

## Safety Features

- **Fail-safe enabled**: Move your mouse to any corner of the screen to abort
- **UI safety check**: Skips clicking if the monitored UI area has changed
- **Countdown timer**: Shows time until next click
- **Click/Skip counters**: Track successful clicks and skipped attempts
- **Match percentage**: Shows how well the current UI matches the captured UI

## Screenshots

The tool displays:
- Current mouse position
- Captured click position (X, Y)
- Monitoring region info
- Rest position coordinates
- Preview of captured UI with click position marker
- Status with click count, skip count, and countdown

## License

MIT License - feel free to use and modify.
