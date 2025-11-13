from __future__ import annotations

from pathlib import Path
from typing import Dict

import pygame

from .config import SCALE_FACTOR, TILE_SIZE, PowerUpType, TileType

ASSET_ROOT = Path(__file__).resolve().parents[2] / "assets"

ASSET_PATHS = {
    "tiles": {
        TileType.FLOOR: ASSET_ROOT / "tiles/floor.ppm",
        TileType.SOLID: ASSET_ROOT / "tiles/solid.ppm",
        TileType.DESTRUCTIBLE: ASSET_ROOT / "tiles/destructible.ppm",
    },
    "players": {
        1: ASSET_ROOT / "sprites/player1.ppm",
        2: ASSET_ROOT / "sprites/player2.ppm",
    },
    "bomb": ASSET_ROOT / "sprites/bomb.ppm",
    "powerups": {
        PowerUpType.BOMB: ASSET_ROOT / "powerups/bomb.ppm",
        PowerUpType.FLAME: ASSET_ROOT / "powerups/flame.ppm",
    },
}


class AssetManager:
    def __init__(self) -> None:
        self._tile_images: Dict[TileType, pygame.Surface] = {}
        self._player_images: Dict[int, pygame.Surface] = {}
        self._powerup_images: Dict[PowerUpType, pygame.Surface] = {}
        self._bomb_image: pygame.Surface | None = None

    def load(self) -> None:
        for tile_type, path in ASSET_PATHS["tiles"].items():
            self._tile_images[tile_type] = self._load_scaled(str(path))
        for player_id, path in ASSET_PATHS["players"].items():
            self._player_images[player_id] = self._load_scaled(str(path))
        self._bomb_image = self._load_scaled(str(ASSET_PATHS["bomb"]))
        for power_type, path in ASSET_PATHS["powerups"].items():
            self._powerup_images[power_type] = self._load_scaled(str(path))

    def _load_scaled(self, path: str) -> pygame.Surface:
        surface = pygame.image.load(path)
        if surface.get_alpha() is not None:
            surface = surface.convert_alpha()
        else:
            surface = surface.convert()
        size = TILE_SIZE * SCALE_FACTOR
        return pygame.transform.scale(surface, (size, size))

    def tile_image(self, tile_type: TileType) -> pygame.Surface:
        return self._tile_images[tile_type]

    def player_image(self, player_id: int) -> pygame.Surface:
        return self._player_images[player_id]

    def bomb_image(self) -> pygame.Surface:
        assert self._bomb_image is not None
        return self._bomb_image

    def powerup_image(self, powerup_type: PowerUpType) -> pygame.Surface:
        return self._powerup_images[powerup_type]
