# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

from pygame import *
from enum import Enum

PLAYER_IMAGE = "res/player.png"
PLAYER_COLOR = (0x7f, 0x00, 0x00)

MOVEMENT_SPEED = 3  # pixels per frame
FALL_SPEED = 1  # pixels per frame
FALL_ACCELERATION = 1  # pixels per frame
JUMP_FORCE = 12  # pixels per frame
JUMP_MIN_FORCE = 7  # pixels per frame


class Movement(Enum):
    FLOOR = 0,
    STAIRS = 1,


class Player(Rect):
    def __init__(self):
        super().__init__(Rect(0, 0, 0, 0))

        self.image = image.load(PLAYER_IMAGE)
        self.x, self.y, self.w, self.h = self.image.get_rect()

        self.vertical_movement = False
        self.horizontal_movement = False

        self.climbing = False
        self.can_jump = True
        self.jmp = 0
        self.fall = 0
        self.can_move_up = False
        self.can_move_down = False

        self.movement = Movement.FLOOR

    def draw(self, surface: Surface) -> None:
        # surface.blit(self.image, self)
        draw.rect(surface, PLAYER_COLOR, self)
