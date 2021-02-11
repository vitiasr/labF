#!/usr/bin/env python3
# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import pygame as pg
from pygame import QUIT
import level
import player

WINDOW_SIZE = 1167, 700
WINDOW_FRAME_RATE = 60
WINDOW_CAPTION = "4164 - 4273"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def main():
    pg.display.init()
    pg.display.set_caption(WINDOW_CAPTION)
    # pygame.key.set_repeat(1)
    clock = pg.time.Clock()
    screen = pg.display.set_mode(WINDOW_SIZE)

    level.next_level()
    player.init()

    while handle_input(pg.event.get()):
        level.draw(screen)
        player.draw(screen)
        pg.display.flip()
        clock.tick(WINDOW_FRAME_RATE)

    pg.quit()


def handle_input(event_list) -> bool:
    for event in event_list:
        if event.type == QUIT:
            return False
    player.handle_input(event_list)
    return True


if __name__ == '__main__':
    main()
