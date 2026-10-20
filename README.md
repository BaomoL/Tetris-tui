# Tetris tui

Modern guideline-style Tetris that runs in your terminal, written in Python.

<img width="325" alt="tetriirasfd" src="https://github.com/user-attachments/assets/d506a611-eb71-4e56-9dae-b0c6e599bb4f" />

## Features

- **SRS rotation** with full wall kick tables, including the separate I-piece kicks
- **180° rotation** with its own kicks
- **T-spins** detected with the 3-corner rule (T-Spin Single, Double and Triple)
- **Guideline scoring:** back-to-back bonus (1.5x, with a B2B streak counter), combos and perfect clears
- **7-bag randomizer**, so you never wait forever for an I piece
- **Hold** and a **5-piece next queue**
- **Ghost piece** showing where the piece will land
- **Adjustable handling:** DAS, ARR, soft drop speed and lock delay
- **Four modes:** Marathon, Sprint, Ultra and Hardcore
- Colored blocks with ANSI, emoji or plain ASCII styles


## Requirements

- Python 3
- [pynput](https://pypi.org/project/pynput/) (for keyboard input)
- A terminal that supports ANSI colors

## Install and run

```bash
git clone https://github.com/BaomoL/Tetris-tui.git
cd Tetris-tui
pip install -r requirements.txt
python main.py
```

### Platform notes

- **macOS:** pynput needs permission to read the keyboard. Go to System Settings → Privacy & Security → Accessibility (and Input Monitoring) and allow your terminal app.
- **Linux:** pynput needs an X server. It may not work under Wayland.
- **Windows:** works in the standard console and Windows Terminal.

## Controls

| Action | Key |
| --- | --- |
| Move left / right | ← / → |
| Soft drop | ↓ |
| Hard drop | Space |
| Rotate clockwise | D or ↑ (Default) |
| Rotate counter-clockwise | A |
| Rotate 180° | W |
| Hold | Shift |
| Back to mode menu | Tab |
| Quit | Esc |

All keys except ↑, Tab and Esc can be changed in `config.py`.

## Game modes

- **Marathon:** play until you top out. Level goes up every 10 lines (max level 15) and pieces fall faster.
- **Sprint:** clear 20, 40 or 100 lines as fast as you can.
- **Ultra:** score as much as you can in 1, 2 or 5 minutes.
- **Hardcore:** Marathon, but pieces lock the instant they touch down.

## Customization

Edit `config.py` to change:

- Handling: `das`, `arr`, `soft_drop_multiplier` and lock delay times
- Key bindings
- Look: ANSI colors (default), emoji blocks, or plain ASCII. Uncomment one style section and comment out the others.

## Building an executable

The repo includes a PyInstaller spec file:

```bash
pip install pyinstaller
pyinstaller tetris.spec
```

The executable ends up in `dist/`.

## Project structure

| File | What it does |
| --- | --- |
| `main.py` | Entry point and mode menus |
| `game.py` | Game loop, scoring, modes |
| `board.py` | Board drawing and line clears |
| `pieces.py` | Tetromino shapes and rotation |
| `keys.py` | Keyboard listener |
| `terminal.py` | Terminal input handling (Windows / macOS / Linux) |
| `config.py` | User settings |
