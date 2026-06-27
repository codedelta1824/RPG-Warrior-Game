# Warrior Game

## Overview
Warrior Game is a 2D local and LAN-capable fighting game prototype built with Python and Pygame. It features two sword-wielding characters, sprite-based animations, a dynamic background selector, and an in-game UI with avatars, health/shield bars, and multiplayer matchmaking support.

## Project Objectives / Scope
- Provide a compact, extensible fighting-game prototype demonstrating character animation, hit detection, and stage selection.
- Offer both local (split-keyboard) play and a basic LAN matchmaking flow using a broker-style network component.
- Keep a modular codebase so assets, art, and networking can be iterated independently.
- Not intended as a final commercial release — this repository is a working prototype under active development.

## Key Features
- Local two-player matches (left vs right characters) with movement, jumping, defend, and charge-attack mechanics.
- Animated sprite sheets for both characters with fallback assets when frames are missing.
- Background selector modal that previews and applies stage backgrounds at runtime.
- Avatar images rendered in round frames on the HUD.
- Health and shield bars with simple damage/defense logic.
- Lightweight LAN matchmaking client (broker-based) for hosting and joining games.
- Options overlay with runtime toggles (FPS, hitbox debug view, audio/music toggles).

## Technology Stack
- Python 3.10+ (tested on Python 3.13)
- Pygame (2.x)
- Standard library `socket` and `threading` for a simple networking client
- File-based assets (PNG/JPEG/JFIF) for sprites, avatars and backgrounds

## Project Structure
- [main.py](main.py) — game entrypoint; initializes Pygame, the UI manager, and game loop.
- [src/](src/) — game source code
  - [src/config.py](src/config.py) — global constants, UI rectangles, and paths to asset folders.
  - [src/player.py](src/player.py) — player class, sprite loader, background loader and animation arrays.
  - [src/ui.py](src/ui.py) — UIManager, drawing functions, menus and input handling.
  - [src/network.py](src/network.py) — simple `Network` client for broker matchmaking.
  - [src/states.py](src/states.py) — `GameState` enum used across the app.
- [assets/images/](assets/images/) — art assets (not checked into this README but expected in the repo):
  - `Avatar Logos/` — avatar images (displayed in HUD)
  - `Background Images/` — stage background images (used by background selector)
  - `Left Sword Man/` and `Right Sword Man/` — per-character animation frames (idle, walk, attack, defend, jump)
- [tests/](tests/) — lightweight scripts used during development for validating asset loading and rendering.

## How to Run
1. Install Python 3.10+ and create a virtual environment (recommended).
2. Install dependencies:

```bash
pip install pygame
```

3. From the repository root run:

```bash
python main.py
```

Notes:
- The `assets/images` folder must exist and contain the character sprites and background images.
- The game uses a simple broker address in `src/network.py`; for LAN testing you can replace `broker.yourdomain.com` with a reachable broker or your own testing server.

## Controls
- Left player (P1): Move A / D, Jump W, Down/Defend S, Attack F
- Right player (P2): Move ← / →, Jump ↑, Down/Defend ↓, Attack P
- Press `ESC` to toggle Pause/Resume when in-game.

## Conclusion
This repository is an actively developed prototype for a 2D fighting game. It is continually improved; expect iterative updates to animation handling, multiplayer flow, and UI polish.

## Contact
For technical inquiries, deployment assistance, bug reports, feature requests, or collaboration opportunities:

Email: codedelta1824@gmail.com

## Support
If you find this project useful, consider starring the repository. Contributions via issues or pull requests are highly appreciated.