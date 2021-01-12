#!/usr/bin/env python3
# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import pygame
from drawable import Drawable
from constants import BLACK
from pygame import *

INITIAL_SPEED = 5

JUMP_SPEED = 10
JUMP_HEIGHT = 20


class Player(Drawable):
    def __init__(self):
        self.x = 0
        self.y = 100
        self.can_move_vertically = False

        # List of pressed keys that move the player (i.e. K_LEFT, K_A, etc.)
        self.pressed_move_keys = []

    def handle_input(self, event_list) -> bool:
        for event in event_list:
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_a \
                        or event.key == K_RIGHT or event.key == K_d \
                        or event.key == K_UP or event.key == K_w \
                        or event.key == K_DOWN or event.key == K_s:
                    self.pressed_move_keys.append(event.key)
            elif event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_a \
                        or event.key == K_RIGHT or event.key == K_d \
                        or event.key == K_UP or event.key == K_w \
                        or event.key == K_DOWN or event.key == K_s:
                    self.pressed_move_keys.remove(event.key)

        is_moving_horizontally = is_moving_vertically = False
        for key in reversed(self.pressed_move_keys):
            if not is_moving_horizontally:
                if key == K_LEFT or key == K_a:
                    self.x -= INITIAL_SPEED
                    is_moving_horizontally = True
                elif key == K_RIGHT or key == K_d:
                    self.x += INITIAL_SPEED
                    is_moving_horizontally = True
            if self.can_move_vertically and not is_moving_vertically:
                if key == K_UP or key == K_w:
                    self.y -= INITIAL_SPEED
                    is_moving_vertically = True
                elif key == K_DOWN or key == K_s:
                    self.y += INITIAL_SPEED
                    is_moving_vertically = True

        return True

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BLACK, [self.x, self.y, 50, 50])
        pass
