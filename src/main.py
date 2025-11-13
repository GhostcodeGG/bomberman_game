from __future__ import annotations
import os

import pygame

from .bomberman.assets import AssetManager
from .bomberman.config import ARENA_HEIGHT, ARENA_WIDTH, SCALE_FACTOR, TILE_SIZE
from .bomberman.entities import InputBuffer
from .bomberman.game_state import GameState
from .bomberman.input import KeyboardController

WINDOW_WIDTH = ARENA_WIDTH * TILE_SIZE * SCALE_FACTOR
WINDOW_HEIGHT = ARENA_HEIGHT * TILE_SIZE * SCALE_FACTOR


def draw_arena(screen: pygame.Surface, assets: AssetManager, state: GameState) -> None:
    tile_size = TILE_SIZE * SCALE_FACTOR
    for x, y, tile in state.arena.iter_tiles():
        image = assets.tile_image(tile.tile_type)
        screen.blit(image, (x * tile_size, y * tile_size))

    for powerup in state.powerups:
        px, py = powerup.position
        screen.blit(assets.powerup_image(powerup.powerup_type), (px * tile_size, py * tile_size))

    for bomb in state.bombs:
        bx, by = bomb.tile_position()
        screen.blit(assets.bomb_image(), (bx * tile_size, by * tile_size))

    explosion_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    explosion_surface.fill((255, 200, 50, 160))
    for explosion in state.explosions:
        for tx, ty in explosion.tiles:
            screen.blit(explosion_surface, (tx * tile_size, ty * tile_size))

    for player_id, player in state.players.items():
        if not player.alive:
            continue
        px = int(player.position[0] * tile_size)
        py = int(player.position[1] * tile_size)
        screen.blit(assets.player_image(player_id), (px - tile_size // 2, py - tile_size // 2))


def main() -> None:
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    pygame.init()
    pygame.display.set_caption("Bomberman GB Arena")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    assets = AssetManager()
    assets.load()
    state = GameState()
    controller = KeyboardController()
    inputs = InputBuffer()
    font = pygame.font.SysFont("Arial", 18)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and state.round_over:
                state.reset_round()

        controller.poll(inputs)
        result = state.update(dt, inputs)

        screen.fill((0, 0, 0))
        draw_arena(screen, assets, state)

        score_text = font.render(
            f"P1: {state.players[1].score}  P2: {state.players[2].score}", True, (255, 255, 255)
        )
        screen.blit(score_text, (10, 10))
        if result.round_over:
            if result.winner:
                message = f"Player {result.winner} wins! Press R to reset."
            else:
                message = "Draw! Press R to reset."
            msg_surface = font.render(message, True, (255, 255, 0))
            screen.blit(msg_surface, (10, 30))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
