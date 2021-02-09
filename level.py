# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

from player import *
from PIL import Image
import numpy as np


class Level:
    def __init__(self, background_image: str, bitmap: str):
        self.background = image.load(background_image)
        self.background_map = image.load(bitmap)  # TODO: Remove

        self.map = np.array(Image.open(bitmap).convert())  # "I" for 32-bit int
        self.map_width = self.map.shape[1]
        self.map_height = self.map.shape[0]

        self.player = Player()
        self.initialize_position()

        # List of pressed keys that move the player (i.e. K_LEFT, K_A, etc.)
        self.pressed_move_keys = []

    def get_horizontal_boundaries(self):
        pass

    def get_player_pos(self) -> tuple:
        pass

    def handle_input(self, event_list) -> bool:
        for event in event_list:
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_a \
                        or event.key == K_RIGHT or event.key == K_d \
                        or event.key == K_UP or event.key == K_w \
                        or event.key == K_DOWN or event.key == K_s:
                    self.pressed_move_keys.append(event.key)
                # elif event.key == K_SPACE:
                #     if not self.jumping and not self.falling:
                #         self.jumping = JUMPING
            elif event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_a \
                        or event.key == K_RIGHT or event.key == K_d \
                        or event.key == K_UP or event.key == K_w \
                        or event.key == K_DOWN or event.key == K_s:
                    self.pressed_move_keys.remove(event.key)

        moving_horizontally = moving_vertically = False
        for key in reversed(self.pressed_move_keys):
            if not moving_horizontally:
                if key == K_LEFT or key == K_a:
                    moving_horizontally = True
                    if self.player.left > MOVEMENT_SPEED:
                        self.player.x -= MOVEMENT_SPEED
                    else:
                        self.player.left = 0
                elif key == K_RIGHT or key == K_d:
                    moving_horizontally = True
                    if self.player.right < self.map_width - MOVEMENT_SPEED:
                        self.player.x += MOVEMENT_SPEED
                    else:
                        self.player.right = self.map_width
            if self.player.vertical_movement and not moving_vertically:
                if key == K_UP or key == K_w:
                    moving_vertically = True
                    if self.player.top > MOVEMENT_SPEED:
                        self.player.y -= MOVEMENT_SPEED
                    else:
                        self.player.top = 0
                elif key == K_DOWN or key == K_s:
                    moving_vertically = True
                    if self.player.bottom < self.map_height - MOVEMENT_SPEED:
                        self.player.y += MOVEMENT_SPEED
                    else:
                        self.player.bottom = self.map_height

        # Gravity
        self.fall()

        # if self.jumping == JUMPING:
        #     if self.jump_y < JUMP_HEIGHT:
        #         self.jump_y += JUMP_SPEED
        #         self.rect.y -= JUMP_SPEED
        #     if self.jump_y >= JUMP_HEIGHT:
        #         self.jumping = LANDING
        #
        # if self.jumping == LANDING:
        #     if self.jump_y > 0:
        #         self.jump_y -= JUMP_SPEED
        #         self.rect.y += JUMP_SPEED
        #     if self.jump_y <= 0:
        #         self.jump_y = 0
        #         self.jumping = NOT_JUMPING
        #
        # if self.jumping == NOT_JUMPING:
        #     self.falling = True
        #     if self.rect.bottom < MAGIC:
        #         for x in range(self.rect.width):
        #             for y in range(FALL_SPEED):
        #                 if self.level.map[self.rect.bottom + y][self.rect.left + x][1] == 0xFF:
        #                     self.falling = False
        #     elif self.rect.top > MAGIC:
        #         # TODO: Game over
        #         self.initialize_position()
        #
        #     if self.falling:
        #         self.rect.y += FALL_SPEED

        # if self.jumping:
        #     if self.jump_y < JUMP_HEIGHT:
        #         self.jump_y += JUMP_SPEED
        #         self.rect.y -= JUMP_SPEED
        #     else:
        #         self.jump_y = 0
        #         self.jumping = False
        # elif self.falling:
        #     self.rect.y += FALL_SPEED

        return True

    def fall(self):
        if self.player.fall_speed == 0:
            self.player.fall_speed = FALL_SPEED
        else:
            self.player.fall_speed += FALL_ACCELERATION

        if self.player.bottom < self.map_height - self.player.fall_speed:
            for y in range(self.player.fall_speed):
                for x in range(self.player.width):
                    if self.map[self.player.bottom + y][self.player.left + x][1] == 0xFF:
                        self.player.fall_speed = 0
                        self.player.bottom = self.player.bottom + y
                        return
        elif self.player.top > self.map_height:
            self.game_over()

        self.player.y += self.player.fall_speed

    def game_over(self):
        # TODO: Game over
        self.initialize_position()

    def initialize_position(self):
        self.player.x, self.player.y = self.get_player_pos()

    def draw(self, surface: Surface) -> None:
        surface.blit(self.background, [0, 0])
        surface.blit(self.background_map, [0, 0])
        self.player.draw(surface)
