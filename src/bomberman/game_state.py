from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from .arena import Arena
from .config import (
    ARENA_HEIGHT,
    ARENA_WIDTH,
    BASE_BOMB_COUNT,
    BASE_FLAME_LENGTH,
    BOMB_TIMER,
    EXPLOSION_DURATION,
    PLAYER_SPEED,
    POWERUP_SPAWN_CHANCE,
    PowerUpType,
    TileType,
)
from .entities import Bomb, Explosion, InputBuffer, InputState, Player, PowerUp


@dataclass
class MatchResult:
    round_over: bool
    winner: Optional[int] = None


class GameState:
    """Contains the entire simulation state for a Bomberman match."""

    def __init__(self) -> None:
        self.arena = Arena()
        self.players: Dict[int, Player] = {}
        self.bombs: List[Bomb] = []
        self.explosions: List[Explosion] = []
        self.powerups: List[PowerUp] = []
        self.round_over: bool = False
        self.winner: Optional[int] = None
        self.spawn_players()

    def spawn_players(self) -> None:
        self.players = {
            1: Player(1, (1.0, 1.0), speed=PLAYER_SPEED),
            2: Player(2, (ARENA_WIDTH - 2.0, ARENA_HEIGHT - 2.0), speed=PLAYER_SPEED),
        }
        for player in self.players.values():
            player.bomb_capacity = BASE_BOMB_COUNT
            player.flame_length = BASE_FLAME_LENGTH
            player.active_bombs = 0
            player.alive = True
        self.bombs.clear()
        self.explosions.clear()
        self.powerups.clear()
        self.round_over = False
        self.winner = None
        self.arena.reset()

    def update(self, dt: float, inputs: InputBuffer) -> MatchResult:
        if self.round_over:
            return MatchResult(True, self.winner)

        for player_id, player in self.players.items():
            if not player.alive:
                continue
            state = inputs.get_state(player_id)
            self._apply_player_input(player, state, dt)
            if state.place_bomb:
                self._try_place_bomb(player)

        self._update_bombs(dt)
        self._update_explosions(dt)
        self._check_powerup_pickups()
        self._determine_round_winner()

        inputs.clear()
        return MatchResult(self.round_over, self.winner)

    def _apply_player_input(self, player: Player, state: InputState, dt: float) -> None:
        move_x, move_y = state.move
        if move_x == 0 and move_y == 0:
            return
        desired = (player.position[0] + move_x * player.speed * dt,
                   player.position[1] + move_y * player.speed * dt)
        player.position = self._resolve_movement(player, desired)

    def _resolve_movement(self, player: Player, desired: tuple[float, float]) -> tuple[float, float]:
        current_x, current_y = player.position
        new_x, new_y = desired
        rx, ry = self._move_axis((current_x, current_y), (new_x, current_y))
        fx, fy = self._move_axis((rx, ry), (rx, new_y))
        return fx, fy

    def _move_axis(self, start: tuple[float, float], end: tuple[float, float]) -> tuple[float, float]:
        sx, sy = start
        ex, ey = end
        target_tile = (int(round(ex)), int(round(ey)))
        if not self._tile_is_open(target_tile[0], target_tile[1]):
            return sx, sy
        return ex, ey

    def _tile_is_open(self, tx: int, ty: int) -> bool:
        if not self.arena.in_bounds(tx, ty):
            return False
        tile = self.arena.get_tile(tx, ty)
        if tile.tile_type in (TileType.SOLID, TileType.DESTRUCTIBLE):
            return False
        if any(bomb.tile_position() == (tx, ty) for bomb in self.bombs):
            return False
        return True

    def _try_place_bomb(self, player: Player) -> None:
        if player.active_bombs >= player.bomb_capacity:
            return
        tile_pos = player.tile_position()
        if any(bomb.tile_position() == tile_pos for bomb in self.bombs):
            return
        bomb = Bomb(player.player_id, tile_pos, BOMB_TIMER, player.flame_length)
        self.bombs.append(bomb)
        player.active_bombs += 1

    def _update_bombs(self, dt: float) -> None:
        for bomb in list(self.bombs):
            bomb.timer -= dt
            if bomb.timer <= 0:
                self._explode_bomb(bomb)

    def _explode_bomb(self, bomb: Bomb) -> None:
        if bomb not in self.bombs:
            return
        self.bombs.remove(bomb)
        owner = self.players.get(bomb.owner_id)
        if owner:
            owner.active_bombs = max(0, owner.active_bombs - 1)
        tiles = self._collect_explosion_tiles(bomb)
        self.explosions.append(Explosion(tiles, EXPLOSION_DURATION))
        self._apply_explosion_effects(tiles)

    def _collect_explosion_tiles(self, bomb: Bomb) -> List[tuple[int, int]]:
        cx, cy = bomb.tile_position()
        tiles = [(cx, cy)]
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for step in range(1, bomb.flame_length + 1):
                tx, ty = cx + dx * step, cy + dy * step
                if not self.arena.in_bounds(tx, ty):
                    break
                tile = self.arena.get_tile(tx, ty)
                tiles.append((tx, ty))
                if tile.tile_type == TileType.SOLID:
                    tiles.pop()  # cannot occupy solid tile
                    break
                if tile.tile_type == TileType.DESTRUCTIBLE:
                    break
        return tiles

    def _apply_explosion_effects(self, tiles: List[tuple[int, int]]) -> None:
        for tx, ty in tiles:
            tile = self.arena.get_tile(tx, ty)
            if tile.tile_type == TileType.DESTRUCTIBLE:
                destroyed = self.arena.destroy_tile(tx, ty)
                if destroyed and random.random() < POWERUP_SPAWN_CHANCE:
                    power_type = random.choice([PowerUpType.BOMB, PowerUpType.FLAME])
                    self.arena.place_powerup(tx, ty, power_type)
                    self.powerups.append(PowerUp((tx, ty), power_type))
            for player in self.players.values():
                if player.alive and player.tile_position() == (tx, ty):
                    player.alive = False

        # chain reaction: explode bombs caught in blast
        for bomb in list(self.bombs):
            if bomb.tile_position() in tiles:
                bomb.timer = 0
                self._explode_bomb(bomb)

    def _update_explosions(self, dt: float) -> None:
        for explosion in list(self.explosions):
            explosion.timer -= dt
            if explosion.timer <= 0:
                self.explosions.remove(explosion)

    def _check_powerup_pickups(self) -> None:
        for player in self.players.values():
            if not player.alive:
                continue
            tx, ty = player.tile_position()
            tile = self.arena.get_tile(tx, ty)
            if tile.powerup:
                powerup_type = tile.powerup
                tile.powerup = None
                self.powerups = [p for p in self.powerups if p.position != (tx, ty)]
                if powerup_type == PowerUpType.BOMB:
                    player.bomb_capacity += 1
                elif powerup_type == PowerUpType.FLAME:
                    player.flame_length += 1

    def _determine_round_winner(self) -> None:
        living = [player_id for player_id, player in self.players.items() if player.alive]
        if len(living) <= 1:
            self.round_over = True
            self.winner = living[0] if living else None
            if self.winner:
                self.players[self.winner].score += 1

    def reset_round(self) -> None:
        self.spawn_players()
