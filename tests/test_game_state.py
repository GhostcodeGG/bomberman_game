from __future__ import annotations

import pytest

from src.bomberman.config import PowerUpType, TileType
from src.bomberman.entities import Bomb, InputBuffer, InputState, PowerUp
from src.bomberman.game_state import GameState


@pytest.fixture
def game_state() -> GameState:
    return GameState()


def test_bomb_explosion_clears_destructible(game_state: GameState) -> None:
    player = game_state.players[1]
    player.position = (2.0, 1.0)
    target_tile = (3, 1)
    assert game_state.arena.get_tile(*target_tile).tile_type == TileType.DESTRUCTIBLE
    game_state._try_place_bomb(player)
    bomb = game_state.bombs[0]
    bomb.timer = 0
    game_state._update_bombs(0)
    assert game_state.arena.get_tile(*target_tile).tile_type == TileType.FLOOR


def test_player_blocked_by_solid(game_state: GameState) -> None:
    player = game_state.players[1]
    player.position = (2.0, 1.0)
    buffer = InputBuffer()
    buffer.set_state(1, InputState(move=(0.0, 1.0)))
    game_state.update(0.25, buffer)
    assert player.position == (2.0, 1.0)


def test_powerup_pickup_increases_capacity(game_state: GameState) -> None:
    player = game_state.players[1]
    start_capacity = player.bomb_capacity
    tx, ty = 2, 1
    game_state.arena.place_powerup(tx, ty, PowerUpType.BOMB)
    game_state.powerups.append(PowerUp((tx, ty), PowerUpType.BOMB))
    buffer = InputBuffer()
    buffer.set_state(1, InputState(move=(1.0, 0.0)))
    game_state.update(0.25, buffer)
    assert player.bomb_capacity == start_capacity + 1


def test_round_end_when_opponent_defeated(game_state: GameState) -> None:
    player2 = game_state.players[2]
    bomb = Bomb(owner_id=1, position=player2.position, timer=0, flame_length=3)
    game_state.bombs.append(bomb)
    game_state._explode_bomb(bomb)
    buffer = InputBuffer()
    game_state.update(0.0, buffer)
    assert game_state.round_over is True
    assert game_state.winner == 1
    assert game_state.players[1].score == 1
