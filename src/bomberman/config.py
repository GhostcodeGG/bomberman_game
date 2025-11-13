from enum import Enum


class TileType(str, Enum):
    FLOOR = "floor"
    SOLID = "solid"
    DESTRUCTIBLE = "destructible"


TILE_SIZE = 16
SCALE_FACTOR = 2
ARENA_WIDTH = 13
ARENA_HEIGHT = 11

PLAYER_SPEED = 4.0  # tiles per second
BOMB_TIMER = 2.5  # seconds
EXPLOSION_DURATION = 0.5  # seconds
BASE_FLAME_LENGTH = 2
BASE_BOMB_COUNT = 1
POWERUP_SPAWN_CHANCE = 0.3


class PowerUpType(str, Enum):
    BOMB = "bomb"
    FLAME = "flame"
