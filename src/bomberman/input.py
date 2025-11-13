from __future__ import annotations

from typing import Dict

import pygame

from .entities import InputBuffer, InputState


class KeyboardController:
    def __init__(self) -> None:
        self.bindings: Dict[int, Dict[str, int]] = {
            1: {
                "up": pygame.K_w,
                "down": pygame.K_s,
                "left": pygame.K_a,
                "right": pygame.K_d,
                "bomb": pygame.K_SPACE,
            },
            2: {
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "bomb": pygame.K_RETURN,
            },
        }

    def poll(self, buffer: InputBuffer) -> None:
        keys = pygame.key.get_pressed()
        for player_id, binding in self.bindings.items():
            move_x = 0.0
            move_y = 0.0
            if keys[binding["left"]]:
                move_x -= 1
            if keys[binding["right"]]:
                move_x += 1
            if keys[binding["up"]]:
                move_y -= 1
            if keys[binding["down"]]:
                move_y += 1
            if move_x and move_y:
                move_x *= 0.7071
                move_y *= 0.7071
            place_bomb = keys[binding["bomb"]]
            buffer.set_state(player_id, InputState(move=(move_x, move_y), place_bomb=place_bomb))
