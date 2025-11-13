from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .config import BASE_BOMB_COUNT, BASE_FLAME_LENGTH, PowerUpType

Vec2 = Tuple[float, float]


@dataclass
class Player:
    player_id: int
    position: Vec2
    direction: Vec2 = (0.0, 0.0)
    speed: float = 4.0
    bomb_capacity: int = BASE_BOMB_COUNT
    flame_length: int = BASE_FLAME_LENGTH
    active_bombs: int = 0
    alive: bool = True
    score: int = 0

    def tile_position(self) -> Tuple[int, int]:
        return int(round(self.position[0])), int(round(self.position[1]))


@dataclass
class Bomb:
    owner_id: int
    position: Vec2
    timer: float
    flame_length: int

    def tile_position(self) -> Tuple[int, int]:
        return int(round(self.position[0])), int(round(self.position[1]))


@dataclass
class Explosion:
    tiles: List[Tuple[int, int]]
    timer: float


@dataclass
class PowerUp:
    position: Tuple[int, int]
    powerup_type: PowerUpType


@dataclass
class InputState:
    move: Vec2 = (0.0, 0.0)
    place_bomb: bool = False


class InputBuffer:
    """Collects input state for each player for the current frame."""

    def __init__(self) -> None:
        self.states: Dict[int, InputState] = {}

    def set_state(self, player_id: int, state: InputState) -> None:
        self.states[player_id] = state

    def get_state(self, player_id: int) -> InputState:
        return self.states.get(player_id, InputState())

    def clear(self) -> None:
        self.states.clear()
