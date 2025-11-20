# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Bomberman Game is a Game Boy-inspired recreation of classic Bomberman with a tile-based 13x11 arena, local 1v1 multiplayer, power-ups, and explosion mechanics. Built with pygame for rendering and designed with a clean separation between simulation logic and display.

## Commands

### Installation

Create virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Game

Start the game:
```bash
python -m src.main
```

Controls:
- Player 1: WASD (move), Space (bomb)
- Player 2: Arrow keys (move), Enter (bomb)
- Esc: Quit
- R: Reset after round ends

### Testing

Run all tests:
```bash
pytest
```

Run specific test:
```bash
pytest tests/test_game_state.py::test_bomb_explosion
```

Tests run headlessly without requiring a display environment.

### Building Distribution

Create distributable wheel:
```bash
pip install build
python -m build
```

Ensure `assets/` directory is included when distributing.

## Architecture

### Module Organization

The codebase follows a clean separation between simulation and rendering:

- **game_state.py**: Core simulation state machine containing all game logic
- **entities.py**: Data classes for Player, Bomb, Explosion, PowerUp, and input handling
- **arena.py**: Tile-based grid with layout generation and tile manipulation
- **config.py**: Game constants (arena size, timers, power-up types, tile types)
- **assets.py**: Sprite loading from PPM files with runtime scaling
- **input.py**: Keyboard input mapping to InputBuffer for both players
- **main.py**: pygame event loop that wires input → update → render

### Game Loop Architecture

The main loop in `main.py` follows a fixed-timestep pattern:

1. **Input Collection**: `input.py` polls pygame events and populates `InputBuffer` with player commands
2. **Simulation Update**: `GameState.update(dt, inputs)` processes one frame of game logic (60 FPS)
3. **Rendering**: pygame draws arena tiles, players, bombs, explosions, and UI overlays
4. **Result Check**: Returns `MatchResult` indicating round status and winner

This design allows tests to exercise game logic without pygame by calling `GameState.update()` directly.

### Entity System

**Player**: Stores position as float coordinates, collision uses `tile_position()` for grid alignment. Each player tracks `bomb_capacity`, `flame_length`, `active_bombs` count, and alive status.

**Bomb**: Placed at tile coordinates, counts down `timer`, then triggers explosion. The `owner_id` links back to the player for decrementing `active_bombs` when it detonates.

**Explosion**: Contains a list of tile coordinates affected by a bomb blast. Timer counts down for visual duration, then removes itself. Checks player collision during its lifetime.

**PowerUp**: Spawned with configurable chance when destructible tiles are destroyed. Types include `EXTRA_BOMB` (increases capacity) and `FLAME_UP` (extends blast radius).

**InputBuffer**: Frame-based input collection that maps player IDs to `InputState` (movement vector + bomb placement flag). Cleared after each update to prevent input carry-over.

### Collision and Movement

Movement uses two-pass axis-aligned collision resolution (`_resolve_movement`):
1. Move along X-axis if target tile is open
2. Move along Y-axis if target tile is open

This allows sliding along walls when moving diagonally. Bombs block movement but don't kill players—only explosions cause death.

Tile walkability checks (`_tile_is_open`) verify:
- Position is in bounds
- Tile type is FLOOR (not SOLID or DESTRUCTIBLE)
- No bomb occupies that tile

### Explosion Propagation

Explosions spread in four cardinal directions from the bomb's tile:
1. Start at bomb position, extend outward for `flame_length` tiles
2. Stop at SOLID tiles (indestructible pillars)
3. Destroy DESTRUCTIBLE tiles and stop propagation in that direction
4. Collect all affected tiles into an `Explosion` entity
5. Check player collision against explosion tiles each frame
6. Spawn power-ups with `POWERUP_SPAWN_CHANCE` when destroying tiles

Implemented in `_detonate_bomb()` in game_state.py.

### Arena Layout Generation

The 13x11 grid follows classic Bomberman structure:
- Border tiles are SOLID (indestructible walls)
- Even x/y coordinates create a checkerboard of SOLID pillars
- All other tiles start as DESTRUCTIBLE (breakable crates)
- Carve out 3x3 safe zones at top-left (1,1) and bottom-right for player spawns

This creates the signature maze-like gameplay with strategic chokepoints.

## Important Conventions

- Position coordinates use floats for smooth movement; tile positions use `int(round(x))` for grid alignment
- The arena uses (x, y) indexing where y is the row index: `grid[y][x]`
- Power-ups are stored in the Tile's `powerup` field, revealed when the tile is destroyed
- Bombs don't immediately block the placing player, allowing escape from the blast
- The `InputBuffer` is cleared each frame—inputs must be re-applied continuously for movement
- Sprite assets are simple PPM files scaled to match Game Boy resolution aesthetics
- Headless mode for testing requires no pygame initialization (tests import only game_state module)
