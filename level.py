# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

from player import *
from PIL import Image
import numpy as np

FLOOR = 0xFF
STAIRS = 0x7F
STAIRS_TOP = 0x80


class Level:
    def __init__(self, background_image: str, bitmap: str):
        self.background = image.load(background_image)
        self.background_map = image.load(bitmap)  # TODO: Remove
        # self.background_map.set_colorkey((0, 0, 0))

        self.map = np.array(Image.open(bitmap).convert())
        self.map_width = self.map.shape[1]
        self.map_height = self.map.shape[0]

        self.player = Player()
        self.initialize_position()

        # List of pressed keys that move the player (i.e. K_LEFT, K_A, etc.)
        self.pressed_move_keys = []
        # Whether the jump key is being held pressed
        self.jump_key_down = False

    def get_horizontal_boundaries(self):
        pass

    def get_player_pos(self) -> tuple:
        pass

    def handle_input(self, event_list) -> None:
        # Define horizontal and vertical deltas
        dx = 0
        dy = 0

        # Check for input events
        for event in event_list:
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_a \
                        or event.key == K_RIGHT or event.key == K_d \
                        or event.key == K_UP or event.key == K_w \
                        or event.key == K_DOWN or event.key == K_s:
                    self.pressed_move_keys.append(event.key)
                elif event.key == K_SPACE:
                    if self.player.can_jump and self.player.jmp == 0 and self.player.fall == 0:
                        self.jump_key_down = True
                        self.player.jmp = JUMP_FORCE
            elif event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_a \
                        or event.key == K_RIGHT or event.key == K_d \
                        or event.key == K_UP or event.key == K_w \
                        or event.key == K_DOWN or event.key == K_s:
                    self.pressed_move_keys.remove(event.key)
                elif event.key == K_SPACE:
                    self.jump_key_down = False

        # React to the pressed move keys
        x_reacted = y_reacted = False
        for key in reversed(self.pressed_move_keys):
            if not x_reacted:
                if key == K_LEFT or key == K_a:
                    x_reacted = True
                    dx -= MOVEMENT_SPEED
                elif key == K_RIGHT or key == K_d:
                    x_reacted = True
                    dx += MOVEMENT_SPEED
            if self.player.vertical_movement and not y_reacted:
                if key == K_UP or key == K_w:
                    y_reacted = True
                    dy -= MOVEMENT_SPEED
                elif key == K_DOWN or key == K_s:
                    y_reacted = True
                    dy += MOVEMENT_SPEED

        # React to the pressed jump key
        if self.jump_key_down and self.player.jmp > 0 \
                or self.player.jmp > JUMP_MIN_FORCE:
            dy -= self.player.jmp
            self.player.jmp -= FALL_ACCELERATION
        else:
            self.player.jmp = 0

        # React to gravitational pull
        if self.player.jmp == 0:
            if self.player.fall == 0:
                self.player.fall = FALL_SPEED
            else:
                self.player.fall += FALL_ACCELERATION
            dy += self.player.fall
            if self.player.bottom < self.map_height - dy:
                for y in range(dy):
                    # Check if standing on floor
                    pixels_on_floor = 0
                    for x in range(self.player.width):
                        if self.map[self.player.bottom + y][self.player.left + x] == FLOOR:
                            pixels_on_floor += 1
                            if pixels_on_floor >= self.player.width // 2:
                                dy = dy - self.player.fall + y
                                self.player.fall = 0
                                break
                    if self.player.fall == 0:
                        break

        # Move the player horizontally
        self.player.x += dx
        if self.player.left < 0:
            self.player.left = 0
        elif self.player.right > self.map_width:
            self.player.right = self.map_width

        # Move the player vertically
        self.player.y += dy
        if self.player.top < 0:
            self.player.top = 0
        elif self.player.fall > 0:
            if self.player.top > self.map_height:
                self.game_over()
        elif self.player.bottom > self.map_height:
            self.player.bottom = self.map_height

    def game_over(self):
        # TODO: Game over
        self.initialize_position()

    def initialize_position(self):
        self.player.x, self.player.y = self.get_player_pos()

    def draw(self, surface: Surface) -> None:
        surface.blit(self.background, [0, 0])
        surface.blit(self.background_map, [0, 0])
        self.player.draw(surface)
