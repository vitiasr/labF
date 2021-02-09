# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

from pygame import *

PLAYER_IMAGE = "res/player.png"
PLAYER_COLOR = (0x7f, 0x7f, 0x7f)

MOVEMENT_SPEED = 5

JUMP_SPEED = 5
JUMP_HEIGHT = 80

STATE_STANDING = 0
STATE_JUMP = 1
STATE_FALL = 2
STATE_FREE_FALL = 3

NOT_JUMPING = 0
JUMPING = 1
LANDING = 2

UP = 0
LEFT = -1
RIGHT = 1

# Jump and fall mechanics
FALL_SPEED = 5  # pixels per frame
FALL_ACCELERATION = 3  # pixels per frame

JUMP_STEP = 5
JUMP_MIN_HEIGHT = 20
JUMP_MAX_HEIGHT = 80


class Player(Rect):
    def __init__(self):
        super().__init__(Rect(0, 0, 0, 0))

        self.image = image.load(PLAYER_IMAGE)
        self.x, self.y, self.w, self.h = self.image.get_rect()

        self.vertical_movement = False

        # Jump and fall mechanics
        self.jump_dy = 0
        self.falling = False
        self.fall_speed = 0

    def draw(self, surface: Surface) -> None:
        # surface.blit(self.image, self.rect)
        draw.rect(surface, PLAYER_COLOR, self)
