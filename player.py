# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import pygame as pg
from pygame import KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_d, K_w, K_s, K_SPACE
import level
from level import FLOOR, STAIRS, STAIRS_TOP

# Resources
PLAYER_FILENAME = "res/player.png"
PLAYER_COLOR = (0xee, 0xee, 0xee)

# TODO: Temp resources
PLAYER_COLOR_STANDING = (0x00, 0x00, 0xaa)
PLAYER_COLOR_CLIMBING = (0xaa, 0x00, 0xaa)
PLAYER_COLOR_JUMPING = (0x00, 0xaa, 0x00)
PLAYER_COLOR_FALLING = (0xaa, 0x00, 0x00)

# Constants (in pixels per frame)
MOVEMENT_SPEED = 3
GRAVITATIONAL_ACCELERATION = 1
JUMP_FORCE = 12
JUMP_MIN_FORCE = 9
JUMP_EASING_FORCE = 4

# Enumeration of states
STANDING = 0
CLIMBING = 1
JUMPING = 2
FALLING = 3

# The player's sprite to draw
sprite: pg.Surface
# The player sprite's rectangle
rect: pg.Rect

# The player's state
state = STANDING

# The force of the gravitational pull (in pixels per frame)
gravity = 0
# The vertical (Y) position of the player before jumping
y_before_jump = 0

# Whether the player can climb up
can_climb_up = False
# Whether the player can climb down
can_climb_down = False

# List of pressed keys that move the player (i.e. K_LEFT, K_A, etc.)
pressed_move_keys = []
# Whether the jump key is being held pressed
jump_key_down = False


def init():
    global sprite, rect, state, gravity, y_before_jump, can_climb_up, can_climb_down, \
        pressed_move_keys, jump_key_down

    sprite = pg.image.load(PLAYER_FILENAME).convert()
    rect = sprite.get_rect()

    initialize_position()

    state = STANDING

    gravity = 0
    y_before_jump = 0

    can_climb_up = False
    can_climb_down = False

    pressed_move_keys = []
    jump_key_down = False


def initialize_position():
    rect.bottomleft = level.get_player_pos()


def handle_input(event_list) -> None:
    global state, gravity, y_before_jump, can_climb_up, can_climb_down, jump_key_down

    # Define horizontal and vertical deltas
    dx = 0
    dy = 0

    # Accelerate the gravitational pull
    if state == CLIMBING:
        gravity = 0
    else:
        gravity += GRAVITATIONAL_ACCELERATION

    # Check for input events
    for event in event_list:
        if event.type == KEYDOWN:
            if event.key == K_LEFT or event.key == K_a \
                    or event.key == K_RIGHT or event.key == K_d \
                    or event.key == K_UP or event.key == K_w \
                    or event.key == K_DOWN or event.key == K_s:
                pressed_move_keys.append(event.key)
            elif event.key == K_SPACE and state == STANDING:
                state = JUMPING
                gravity = -JUMP_FORCE
                y_before_jump = rect.y
                jump_key_down = True
        elif event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_a \
                    or event.key == K_RIGHT or event.key == K_d \
                    or event.key == K_UP or event.key == K_w \
                    or event.key == K_DOWN or event.key == K_s:
                try:
                    pressed_move_keys.remove(event.key)
                except ValueError:
                    pass
            elif event.key == K_SPACE:
                jump_key_down = False

    # React to the pressed move keys
    x_reacted = y_reacted = False
    for key in reversed(pressed_move_keys):
        if not x_reacted:
            if key == K_LEFT or key == K_a:
                x_reacted = True
                if not state == CLIMBING:
                    dx -= MOVEMENT_SPEED
            elif key == K_RIGHT or key == K_d:
                x_reacted = True
                if not state == CLIMBING:
                    dx += MOVEMENT_SPEED
        if not y_reacted:
            if key == K_UP or key == K_w:
                y_reacted = True
                if can_climb_up:
                    dx = 0
                    gravity = 0
                    state = CLIMBING
                    dy -= MOVEMENT_SPEED
            elif key == K_DOWN or key == K_s:
                y_reacted = True
                if can_climb_down:
                    dx = 0
                    gravity = 0
                    state = CLIMBING
                    dy += MOVEMENT_SPEED

    # Cut the jump short if the key is released prematurely
    if state == JUMPING and not jump_key_down \
            and -JUMP_MIN_FORCE <= gravity < -JUMP_EASING_FORCE:
        gravity = -JUMP_EASING_FORCE

    # Move the player horizontally
    rect.x += dx
    if rect.left < 0:
        rect.left = 0
    elif rect.right > level.map_width:
        rect.right = level.map_width

    # Add the gravitational pull to the vertical delta
    dy += gravity

    if rect.bottom < level.map_height - dy:
        if state == CLIMBING:
            if dy < 0:
                # Climbing up
                for y in range(0, dy, -1):
                    if level.map[rect.bottom + y][rect.left] == STAIRS_TOP:
                        # Reached top
                        dy = y
                        state = STANDING
                        can_climb_up = False
                        can_climb_down = True
                        break
                    else:
                        can_climb_up = True
                        can_climb_down = True
            elif dy > 0:
                # Climbing down
                for y in range(dy):
                    if level.map[rect.bottom + y][rect.left] == FLOOR:
                        # Reached bottom
                        dy = y
                        state = STANDING
                        can_climb_up = True
                        can_climb_down = False
                        break
                    else:
                        can_climb_up = True
                        can_climb_down = True
        elif gravity > 0:
            for y in range(dy):
                # Check if standing on floor
                pixels_on_floor = 0
                pixels_on_stairs = 0
                pixels_on_stairs_top = 0
                for x in range(rect.width):

                    if level.map[rect.bottom - 1 + y][rect.left + x] == STAIRS:
                        pixels_on_stairs += 1

                    if level.map[rect.bottom + y][rect.left + x] == FLOOR:
                        pixels_on_floor += 1

                    elif level.map[rect.bottom + y][rect.left + x] == STAIRS_TOP:
                        pixels_on_floor += 1
                        pixels_on_stairs_top += 1

                if pixels_on_floor >= rect.width // 2:
                    dy = y
                    gravity = 0
                    state = STANDING
                    can_climb_up = pixels_on_stairs == rect.width
                    can_climb_down = pixels_on_stairs_top == rect.width
        else:
            can_climb_up = False
            can_climb_down = False

    # Determine the state
    if gravity > 0 and (state != JUMPING or rect.y > y_before_jump):
        state = FALLING
        can_climb_up = False
        can_climb_down = False

    # Move the player vertically
    rect.y += dy
    if rect.top < 0:
        rect.top = 0
    elif gravity > 0:
        if rect.top > level.map_height:
            game_over()
    elif rect.bottom > level.map_height:
        rect.bottom = level.map_height


def game_over():
    # TODO: Game over
    initialize_position()


def draw(surface: pg.Surface) -> None:
    # pg.surface.blit(sprite, rect)
    clr = PLAYER_COLOR
    if state == STANDING:
        clr = PLAYER_COLOR_STANDING
    elif state == CLIMBING:
        clr = PLAYER_COLOR_CLIMBING
    elif state == JUMPING:
        clr = PLAYER_COLOR_JUMPING
    elif state == FALLING:
        clr = PLAYER_COLOR_FALLING
    pg.draw.rect(surface, clr, rect)
    if can_climb_up:
        pg.draw.rect(surface, (0xff, 0xff, 0x00), [rect.x, rect.y, rect.width, 5])
    if can_climb_down:
        pg.draw.rect(surface, (0xff, 0xff, 0x00), [rect.x, rect.bottom - 5, rect.width, 5])
