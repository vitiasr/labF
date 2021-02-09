#!/usr/bin/env python3
# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import pygame
from level1 import Level1

WINDOW_SIZE = 1167, 700
WINDOW_FRAME_RATE = 60
WINDOW_CAPTION = "4164 - 4273"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def main():
    pygame.display.init()
    pygame.display.set_caption(WINDOW_CAPTION)
    # pygame.key.set_repeat(1)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    level = Level1()

    while handle_input(pygame.event.get(), level):
        level.draw(screen)
        pygame.display.flip()
        clock.tick(WINDOW_FRAME_RATE)

    pygame.quit()


def handle_input(event_list, level) -> bool:
    for event in event_list:
        if event.type == pygame.QUIT:
            return False
    level.handle_input(event_list)
    return True


if __name__ == '__main__':
    main()
