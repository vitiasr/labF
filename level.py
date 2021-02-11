# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import pygame as pg
import numpy as np
from PIL import Image

# Resources
BACKGROUND_FILENAME = "res/bg_lvl_{}.png"
MAP_FILENAME = "res/bmp_lvl_{}.png"

# Color codes
FLOOR = 0xFF
STAIRS = 0x7F
STAIRS_TOP = 0x80
START_POSITION = 0x10

# The current level
current_level = 0

# The level's background surface
background: pg.Surface
# The level map's skeleton surface
background_map: pg.Surface  # TODO: Remove

# The level map's skeleton
map: np.ndarray
# The level map's width
map_width: int
# The level map's height
map_height: int


def next_level() -> None:
    global current_level, background, background_map, map, map_width, map_height

    current_level += 1

    background = pg.image.load(BACKGROUND_FILENAME.format(current_level)).convert()
    background_map = pg.image.load(MAP_FILENAME.format(current_level)).convert()
    # background_map.set_colorkey((0, 0, 0))

    map = np.array(Image.open(MAP_FILENAME.format(current_level)).convert())
    map_width = map.shape[1]
    map_height = map.shape[0]


def get_player_pos() -> tuple:
    try:
        pos = np.where(map == START_POSITION)
        return pos[1][0], pos[0][0]
    except IndexError:
        raise IndexError(
            "Can't find starting position. File \"{}\" corrupted.".format(
                MAP_FILENAME.format(current_level)))


def draw(surface: pg.Surface) -> None:
    surface.blit(background, [0, 0])
    surface.blit(background_map, [0, 0])
