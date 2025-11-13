from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

from .config import ARENA_HEIGHT, ARENA_WIDTH, PowerUpType, TileType


@dataclass
class Tile:
    tile_type: TileType
    powerup: Optional[PowerUpType] = None


class Arena:
    """Represents the tile-based arena using the classic Bomberman layout."""

    def __init__(self) -> None:
        self.grid: List[List[Tile]] = self._generate_default_layout()

    def _generate_default_layout(self) -> List[List[Tile]]:
        grid: List[List[Tile]] = []
        for y in range(ARENA_HEIGHT):
            row: List[Tile] = []
            for x in range(ARENA_WIDTH):
                if x == 0 or y == 0 or x == ARENA_WIDTH - 1 or y == ARENA_HEIGHT - 1:
                    row.append(Tile(TileType.SOLID))
                elif x % 2 == 0 and y % 2 == 0:
                    row.append(Tile(TileType.SOLID))
                else:
                    row.append(Tile(TileType.DESTRUCTIBLE))
            grid.append(row)

        # carve out starting positions for two players (top-left and bottom-right corners)
        for (sx, sy) in [(1, 1), (1, 2), (2, 1), (ARENA_WIDTH - 2, ARENA_HEIGHT - 2),
                         (ARENA_WIDTH - 2, ARENA_HEIGHT - 3), (ARENA_WIDTH - 3, ARENA_HEIGHT - 2)]:
            grid[sy][sx] = Tile(TileType.FLOOR)

        return grid

    def reset(self) -> None:
        self.grid = self._generate_default_layout()

    def in_bounds(self, tx: int, ty: int) -> bool:
        return 0 <= tx < ARENA_WIDTH and 0 <= ty < ARENA_HEIGHT

    def get_tile(self, tx: int, ty: int) -> Tile:
        return self.grid[ty][tx]

    def set_tile(self, tx: int, ty: int, tile: Tile) -> None:
        self.grid[ty][tx] = tile

    def is_walkable(self, tx: int, ty: int) -> bool:
        if not self.in_bounds(tx, ty):
            return False
        tile = self.get_tile(tx, ty)
        return tile.tile_type == TileType.FLOOR

    def is_passable(self, tx: int, ty: int) -> bool:
        if not self.in_bounds(tx, ty):
            return False
        tile = self.get_tile(tx, ty)
        return tile.tile_type == TileType.FLOOR

    def destroy_tile(self, tx: int, ty: int) -> Optional[TileType]:
        tile = self.get_tile(tx, ty)
        if tile.tile_type == TileType.DESTRUCTIBLE:
            self.set_tile(tx, ty, Tile(TileType.FLOOR, tile.powerup))
            return TileType.DESTRUCTIBLE
        return None

    def collect_powerup(self, tx: int, ty: int) -> Optional[PowerUpType]:
        tile = self.get_tile(tx, ty)
        if tile.powerup:
            power = tile.powerup
            tile.powerup = None
            return power
        return None

    def place_powerup(self, tx: int, ty: int, powerup: PowerUpType) -> None:
        tile = self.get_tile(tx, ty)
        if tile.tile_type == TileType.FLOOR:
            tile.powerup = powerup

    def iter_tiles(self) -> Iterator[Tuple[int, int, Tile]]:
        for y in range(ARENA_HEIGHT):
            for x in range(ARENA_WIDTH):
                yield x, y, self.grid[y][x]
