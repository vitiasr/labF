#!/usr/bin/env python3
# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import pygame
from constants import WHITE
from input import handle_event
from player import Player

WINDOW_SIZE = (640, 480)
WINDOW_CAPTION = "4164 - 4273"
WINDOW_REFRESH_RATE = 60

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption(WINDOW_CAPTION)
    # pygame.key.set_repeat(1)

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    player = Player()

    while handle_event(pygame.event.get(), player):
        # --- Game logic should go here

        # --- Screen-clearing code goes here

        # Here, we clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.

        # If you want a background image, replace this clear with blit-ing the
        # background image.
        screen.fill(WHITE)

        # --- Drawing code should go here
        player.draw(screen)

        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # --- Limit to 60 frames per second
        clock.tick(WINDOW_REFRESH_RATE)

    pygame.quit()
