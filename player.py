# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import level
import pygame as pg
from enum import Enum
from typing import Tuple, List
from level import FLOOR, STAIRS, STAIRS_TOP, LEVEL_END
from pygame import KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_d, K_w, K_s, K_SPACE


class Player(pg.sprite.Sprite):
    IMAGE = "res/player.png", 4, 4  # horizontal, vertical frame count
    ANI_UP = 3
    ANI_DOWN = 0
    ANI_LEFT = 1
    ANI_RIGHT = 2
    ANI_FRAME_UPDATE_DELAY = 10  # frames per second

    MOVEMENT_SPEED = 3  # pixels per frame
    GRAVITATIONAL_ACCELERATION = 1  # pixels per frame
    JUMP_FORCE = 12  # pixels per frame
    JUMP_MIN_FORCE = 9  # pixels per frame
    JUMP_EASING_FORCE = 4  # pixels per frame
    DEATH_MOVEMENT_SPEED = 5  # pixels per frame
    DEATH_JUMP_FORCE = 20  # pixels per frame

    SOUND_JUMP = "res/foot1.ogg"
    SOUND_JUMP_VOLUME = .6
    SOUND_LAND = "res/land.ogg"
    SOUND_LAND_VOLUME = 1
    SOUND_FOOTSTEPS = "res/foot{}.ogg"
    SOUND_FOOTSTEPS_VOLUME = .6
    SOUND_DEATH = "res/death.ogg"
    SOUND_DEATH_VOLUME = .5
    SOUND_CHOMP = "res/chomp.ogg"
    SOUND_CHOMP_VOLUME = 1

    class State(Enum):
        STANDING = 0,
        CLIMBING = 1,
        JUMPING = 2,
        FALLING = 3,
        DYING = 4,

    sound_jump: pg.mixer.Sound
    sound_land: pg.mixer.Sound
    sound_death: pg.mixer.Sound
    sound_chomp: pg.mixer.Sound
    sound_list_footstep: List[pg.mixer.Sound] = []  # List of footstep sounds

    @staticmethod
    def load_sounds():
        Player.sound_jump = pg.mixer.Sound(Player.SOUND_JUMP)
        Player.sound_jump.set_volume(Player.SOUND_JUMP_VOLUME)
        Player.sound_land = pg.mixer.Sound(Player.SOUND_LAND)
        Player.sound_land.set_volume(Player.SOUND_LAND_VOLUME)
        Player.sound_death = pg.mixer.Sound(Player.SOUND_DEATH)
        Player.sound_death.set_volume(Player.SOUND_DEATH_VOLUME)
        Player.sound_chomp = pg.mixer.Sound(Player.SOUND_CHOMP)
        Player.sound_chomp.set_volume(Player.SOUND_CHOMP_VOLUME)
        for i in range(100):
            try:
                sound = pg.mixer.Sound(Player.SOUND_FOOTSTEPS.format(i))
                sound.set_volume(Player.SOUND_FOOTSTEPS_VOLUME)
                Player.sound_list_footstep.append(sound)
            except FileNotFoundError as e:
                if i < 1:
                    raise e
                break

    def __init__(self):
        super().__init__()

        # Essentials
        self.image = pg.image.load(Player.IMAGE[0]).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.w //= Player.IMAGE[1]
        self.rect.h //= Player.IMAGE[2]
        self.mask = pg.mask.from_surface(self.image.subsurface(self.rect))

        # Animation
        self.ani = 0
        self.prev_ani = 0
        self.ani_frame = 0
        self.prev_ani_frame = 0
        self.ani_frame_counter = 0

        # Movement
        self.state = Player.State.STANDING
        self.gravity = 0
        self.y_before_jump = 0
        self.can_climb_up = False
        self.can_climb_down = False

        # User input
        self.pressed_move_keys = []
        self.jump_key_down = False

        # Sounds
        self.footstep = 0

        # Other
        self.dead = False
        self.promoted = False

        self.initialize_position()

    def initialize_position(self):
        self.rect.bottomleft = level.player_start_pos

        self.ani = 0
        self.ani_frame = 0
        self.ani_frame_counter = 0

        self.state = Player.State.STANDING
        self.gravity = 0
        self.y_before_jump = 0
        self.can_climb_up = False
        self.can_climb_down = False

        self.pressed_move_keys.clear()
        self.jump_key_down = False

        self.dead = False
        self.promoted = False

    def handle_input(self, event_list):
        # Define horizontal and vertical deltas
        dx = 0
        dy = 0

        # Accelerate the gravitational pull
        if self.state == Player.State.CLIMBING:
            self.gravity = 0
        else:
            self.gravity += Player.GRAVITATIONAL_ACCELERATION

        # Check for input events
        for event in event_list:
            if self.state != Player.State.DYING:
                if event.type == KEYDOWN:
                    if event.key == K_LEFT or event.key == K_a \
                            or event.key == K_RIGHT or event.key == K_d \
                            or event.key == K_UP or event.key == K_w \
                            or event.key == K_DOWN or event.key == K_s:
                        self.pressed_move_keys.append(event.key)
                    elif event.key == K_SPACE and self.state == Player.State.STANDING:
                        Player.sound_jump.play()
                        self.state = Player.State.JUMPING
                        self.gravity = -Player.JUMP_FORCE
                        self.y_before_jump = self.rect.y
                        self.jump_key_down = True
                elif event.type == KEYUP:
                    if event.key == K_LEFT or event.key == K_a \
                            or event.key == K_RIGHT or event.key == K_d \
                            or event.key == K_UP or event.key == K_w \
                            or event.key == K_DOWN or event.key == K_s:
                        try:
                            self.pressed_move_keys.remove(event.key)
                        except ValueError:
                            pass
                    elif event.key == K_SPACE:
                        self.jump_key_down = False

        # React to the pressed move keys
        x_reacted = y_reacted = False
        for key in reversed(self.pressed_move_keys):
            if not x_reacted:
                if key == K_LEFT or key == K_a:
                    x_reacted = True
                    if self.state == Player.State.DYING:
                        dx -= Player.DEATH_MOVEMENT_SPEED
                    elif self.state != Player.State.CLIMBING:
                        dx -= Player.MOVEMENT_SPEED
                elif key == K_RIGHT or key == K_d:
                    x_reacted = True
                    if self.state == Player.State.DYING:
                        dx += Player.DEATH_MOVEMENT_SPEED
                    elif self.state != Player.State.CLIMBING:
                        dx += Player.MOVEMENT_SPEED
            if not y_reacted:
                if key == K_UP or key == K_w:
                    y_reacted = True
                    if self.can_climb_up:
                        dx = 0
                        self.gravity = 0
                        self.state = Player.State.CLIMBING
                        dy -= Player.MOVEMENT_SPEED
                elif key == K_DOWN or key == K_s:
                    y_reacted = True
                    if self.can_climb_down:
                        dx = 0
                        self.gravity = 0
                        self.state = Player.State.CLIMBING
                        dy += Player.MOVEMENT_SPEED

        # Cut the jump short if the key is released prematurely
        if self.state == Player.State.JUMPING and not self.jump_key_down \
                and -Player.JUMP_MIN_FORCE <= self.gravity < -Player.JUMP_EASING_FORCE:
            self.gravity = -Player.JUMP_EASING_FORCE

        # Move the player horizontally
        self.rect.x += dx
        if self.rect.left < 0:
            dx = 0
            self.rect.left = 0
        elif self.rect.right > level.map_width:
            dx = 0
            self.rect.right = level.map_width

        # Add the gravitational pull to the vertical delta
        dy += self.gravity

        if self.rect.bottom < level.map_height - dy:
            if self.state == Player.State.CLIMBING:
                if dy < 0:
                    # Climbing up
                    for y in range(0, dy, -1):
                        if level.map[self.rect.bottom + y][self.rect.left] == STAIRS_TOP:
                            # Reached top
                            dy = y
                            self.state = Player.State.STANDING
                            self.can_climb_up = False
                            self.can_climb_down = True
                            break
                        else:
                            self.can_climb_up = True
                            self.can_climb_down = True
                elif dy > 0:
                    # Climbing down
                    for y in range(dy):
                        if level.map[self.rect.bottom + y][self.rect.left] == FLOOR:
                            # Reached bottom
                            dy = y
                            self.state = Player.State.STANDING
                            self.can_climb_up = True
                            self.can_climb_down = False
                            break
                        else:
                            self.can_climb_up = True
                            self.can_climb_down = True
            elif self.gravity > 0 and self.state != Player.State.DYING:
                for y in range(dy):
                    # Check if standing on floor
                    pixels_on_floor = 0
                    pixels_on_stairs = 0
                    pixels_on_stairs_top = 0
                    for x in range(self.rect.width):

                        if level.map[self.rect.bottom + y - 1][self.rect.left + x] == STAIRS:
                            pixels_on_stairs += 1

                        if level.map[self.rect.bottom + y][self.rect.left + x] == FLOOR:
                            pixels_on_floor += 1
                        elif level.map[self.rect.bottom + y][self.rect.left + x] == STAIRS_TOP:
                            pixels_on_floor += 1
                            pixels_on_stairs_top += 1
                        elif level.map[self.rect.bottom + y][self.rect.left + x] == LEVEL_END:
                            self.promoted = True

                    if pixels_on_floor >= self.rect.width // 2:
                        if self.state != Player.State.STANDING:
                            Player.sound_land.play()
                        dy = y
                        self.gravity = 0
                        self.state = Player.State.STANDING
                        self.can_climb_up = pixels_on_stairs == self.rect.width
                        self.can_climb_down = pixels_on_stairs_top == self.rect.width
            else:
                self.can_climb_up = False
                self.can_climb_down = False

        # Determine the state
        if self.gravity > 0 and self.state != Player.State.DYING and (
                self.state != Player.State.JUMPING or self.rect.y > self.y_before_jump):
            self.state = Player.State.FALLING
            self.can_climb_up = False
            self.can_climb_down = False

        # Move the player vertically
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.gravity > 0:
            if self.rect.top > level.map_height:
                dx = dy = 0
                self.dead = True
        elif self.rect.bottom > level.map_height:
            self.rect.bottom = level.map_height

        # Animate the player's sprite
        if self.state in [Player.State.STANDING, Player.State.JUMPING, Player.State.FALLING]:
            if dx != 0:
                self.ani = Player.ANI_LEFT if dx < 0 else Player.ANI_RIGHT
                if self.state == Player.State.STANDING:
                    self.ani_frame_counter += 1
            elif self.state == Player.State.STANDING:
                if self.ani == Player.ANI_UP:
                    # Don't turn the back to the user :)
                    self.ani = Player.ANI_DOWN
                self.ani_frame = 0
                self.ani_frame_counter = Player.ANI_FRAME_UPDATE_DELAY - 1
            else:
                self.ani_frame = 1
                self.ani_frame_counter = 0
        elif self.state == Player.State.CLIMBING:
            if dy != 0:
                self.ani = Player.ANI_UP
                self.ani_frame_counter += 1
            else:
                self.ani_frame = 0
                self.ani_frame_counter = Player.ANI_FRAME_UPDATE_DELAY - 1
        else:
            self.ani_frame = 1
            self.ani_frame_counter = 0

        if self.ani_frame_counter >= Player.ANI_FRAME_UPDATE_DELAY:
            self.ani_frame_counter = 0
            if self.ani_frame >= 3:
                self.ani_frame = 0
            else:
                self.ani_frame += 1

        if self.ani != self.prev_ani or self.ani_frame != self.prev_ani_frame:
            # The sprite's frame has been updated. Update the mask as well.
            self.mask = pg.mask.from_surface(self.image.subsurface(
                [self.ani_frame * self.rect.w, self.ani * self.rect.h, *self.rect.size]))
            # Play the footstep sound
            if self.state in [Player.State.STANDING, Player.State.CLIMBING]:
                if self.ani_frame % 2 == 1:
                    Player.sound_list_footstep[self.footstep].play()
                if self.footstep >= len(Player.sound_list_footstep) - 1:
                    self.footstep = 0
                else:
                    self.footstep += 1

        self.prev_ani = self.ani
        self.prev_ani_frame = self.ani_frame

    def active(self):
        return not self.dead and self.state != Player.State.DYING

    def die(self, collision_point: Tuple[int, int] = (0, 0)):
        if self.state != Player.State.DYING:
            Player.sound_chomp.play()
            Player.sound_death.play()
            self.state = Player.State.DYING
            self.gravity = -Player.DEATH_JUMP_FORCE
            self.pressed_move_keys.clear()
            if self.ani == Player.ANI_LEFT:
                self.pressed_move_keys.append(K_RIGHT)
            elif self.ani == Player.ANI_RIGHT:
                self.pressed_move_keys.append(K_LEFT)
            elif collision_point[0] >= self.rect.w // 2:
                self.pressed_move_keys.append(K_LEFT)
            else:
                self.pressed_move_keys.append(K_RIGHT)

    def draw(self, surface: pg.Surface):
        surface.blit(self.image, self.rect,
                     pg.Rect(self.ani_frame * self.rect.w, self.ani * self.rect.h, *self.rect.size))
