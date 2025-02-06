# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import random
import numpy as np
import pygame as pg
from PIL import Image
from enum import Enum
from typing import List, Tuple

LEVEL_ONE = 1  # The first level
LEVEL_FILENAME = "res/level{}.png"

IMAGE_SPARKLE = "res/sparkle.png", 4, 1  # horizontal, vertical frame count
IMAGE_COIN = "res/coin.png", 1, 1
IMAGE_DIAMOND = "res/diamond.png", 1, 1

SOUND_COIN = "res/coin.ogg"
VOLUME_COIN = .7
SOUND_DIAMOND = "res/diamond.ogg"
VOLUME_DIAMOND = .2

# Map color codes
ENEMY_POSITION = 0x0F
ENEMY_PATH_FIRST = 0x01
ENEMY_PATH_LAST = ENEMY_POSITION
COLLECTIBLE_COIN = 0x32
COLLECTIBLE_DIAMOND = 0x33
FLOOR = 0x64
STAIRS = 0x65
STAIRS_TOP = 0x66
START_POSITION = 0xFA
LEVEL_END = 0xFB

####################################################################################################

current_level = 0
background: pg.Surface
map: np.ndarray  # The level map's skeleton
map_width = 0
map_height = 0
player_start_pos = 0, 0
enemies = pg.sprite.Group()
collectibles = pg.sprite.Group()


def load_assets():
    Collectible.sparkle_image = pg.image.load(IMAGE_SPARKLE[0]).convert_alpha()
    Collectible.sparkle_rect = Collectible.sparkle_image.get_rect()
    Collectible.sparkle_rect.w //= IMAGE_SPARKLE[1]
    Collectible.sparkle_rect.h //= IMAGE_SPARKLE[2]

    Coin.image = pg.image.load(IMAGE_COIN[0]).convert_alpha()
    Coin.rect = Coin.image.get_rect()
    Coin.rect.w //= IMAGE_COIN[1]
    Coin.rect.h //= IMAGE_COIN[2]
    Coin.sound = pg.mixer.Sound(SOUND_COIN)
    Coin.sound.set_volume(VOLUME_COIN)

    Diamond.image = pg.image.load(IMAGE_DIAMOND[0]).convert_alpha()
    Diamond.rect = Diamond.image.get_rect()
    Diamond.rect.w //= IMAGE_DIAMOND[1]
    Diamond.rect.h //= IMAGE_DIAMOND[2]
    Diamond.sound = pg.mixer.Sound(SOUND_DIAMOND)
    Diamond.sound.set_volume(VOLUME_DIAMOND)

    for i in range(100):
        try:
            img = pg.image.load(Enemy.IMAGE[0].format(i)).convert_alpha()
            rect = img.get_rect()
            rect.w //= Enemy.IMAGE[1]
            rect.h //= Enemy.IMAGE[2]
            Enemy.sprite_list.append((img, rect))
        except pg.error as e:
            if i < 1:
                raise e
        except FileNotFoundError as e:
            if i < 1:
                raise e


def load(level: int) -> bool:
    """
    Loads the given level and returns ``True`` on success, ``False`` otherwise.
    """
    global current_level, background, map, map_width, map_height, player_start_pos

    if current_level != level:
        # Load the level
        level_filename = LEVEL_FILENAME.format(level)
        try:
            background = pg.image.load(level_filename).convert()
            map = np.array(Image.open(level_filename).convert("RGBA"))[:, :, 3]
            map_height, map_width = map.shape
        except pg.error as e:
            if level == LEVEL_ONE:
                raise e
            return False
        except FileNotFoundError as e:
            if level == LEVEL_ONE:
                raise e
            return False

        # Instantiate enemies
        try:
            enemies.empty()
            pos = np.where(map == ENEMY_POSITION)
            count = len(pos[0])
            for i in range(count):
                enemies.add(Enemy([pos[1][i], pos[0][i]]))
        except IndexError:
            # There are no enemies at this level
            pass

        # Find the player's starting position
        try:
            pos = np.where(map == START_POSITION)
            player_start_pos = pos[1][0], pos[0][0]
        except IndexError:
            raise IndexError(
                "Can't find starting position. File \"{}\" corrupted.".format(level_filename))
    else:
        # Mutate existing enemies
        for enemy in enemies:
            enemy.mutate()

    # Instantiate collectibles
    try:
        collectibles.empty()
        for cls, code in [(Coin, COLLECTIBLE_COIN), (Diamond, COLLECTIBLE_DIAMOND)]:
            pos = np.where(map == code)
            count = len(pos[0])
            for i in range(count):
                collectibles.add(cls((pos[1][i], pos[0][i])))
    except IndexError:
        # There are no collectibles at this level
        pass

    # Set the level number
    current_level = level

    return True


class Enemy(pg.sprite.Sprite):
    IMAGE = "res/enemy{}.png", 4, 4  # horizontal, vertical frame count
    ANI_UP = 3
    ANI_DOWN = 0
    ANI_LEFT = 1
    ANI_RIGHT = 2
    ANI_FRAME_UPDATE_DELAY = 10  # frames per second

    class Axis(Enum):
        VERTICAL = 0,
        HORIZONTAL = 1,

    # Static list of enemy sprites
    sprite_list: List[Tuple[pg.Surface, pg.Rect]] = []

    def __init__(self, position):
        super().__init__()

        # Essentials
        self.image, self.rect = random.choice(Enemy.sprite_list)
        self.rect = self.rect.copy()
        self.mask = pg.mask.from_surface(self.image.subsurface(self.rect))
        self.rect.center = position

        # Animation
        self.ani = 0
        self.prev_ani = 0
        self.ani_frame = 0
        self.prev_ani_frame = 0
        self.ani_frame_counter = 0

        # Movement
        self.speed = 0
        self.axis = Enemy.Axis.VERTICAL

        x, y = position
        for i in range(x - 1, x + 2, 2):
            if ENEMY_PATH_FIRST <= map[y][i] < ENEMY_PATH_LAST:
                self.speed = int(map[y][i]) - ENEMY_PATH_FIRST + 1
                self.axis = self.Axis.HORIZONTAL
        for i in range(y - 1, y + 2, 2):
            if ENEMY_PATH_FIRST <= map[i][x] < ENEMY_PATH_LAST:
                self.speed = int(map[i][x]) - ENEMY_PATH_FIRST + 1
                self.axis = self.Axis.VERTICAL

    def mutate(self, image: pg.Surface = None, rect: pg.Rect = None):
        pos = self.rect.center
        if image is not None:
            self.image = image
            self.rect = rect
        else:
            self.image, self.rect = random.choice(Enemy.sprite_list)
            self.rect = self.rect.copy()
        self.mask = pg.mask.from_surface(self.image.subsurface(self.rect))
        self.rect.center = pos

    def update(self, *args):
        delta = self.speed
        if self.axis == self.Axis.HORIZONTAL:
            for x in range(0, delta, 1 if delta >= 0 else -1):
                if not ENEMY_PATH_FIRST <= \
                       map[self.rect.centery][self.rect.centerx + x] <= ENEMY_PATH_LAST:
                    # Derailed
                    delta = -(self.speed - x)
                    self.speed *= -1
                    break
            self.rect.x += delta
            if delta < 0:
                self.ani = Enemy.ANI_LEFT
                self.ani_frame_counter += 1
            elif delta > 0:
                self.ani = Enemy.ANI_RIGHT
                self.ani_frame_counter += 1
        elif self.axis == self.Axis.VERTICAL:
            for y in range(0, delta, 1 if delta >= 0 else -1):
                if not ENEMY_PATH_FIRST <= \
                       map[self.rect.centery + y][self.rect.centerx] <= ENEMY_PATH_LAST:
                    # Derailed
                    delta = -(self.speed - y)
                    self.speed *= -1
                    break
            self.rect.y += delta
            if delta < 0:
                self.ani = Enemy.ANI_UP
                self.ani_frame_counter += 1
            elif delta > 0:
                self.ani = Enemy.ANI_DOWN
                self.ani_frame_counter += 1

        if self.ani_frame_counter >= Enemy.ANI_FRAME_UPDATE_DELAY:
            self.ani_frame_counter = 0
            if self.ani_frame >= 3:
                self.ani_frame = 0
            else:
                self.ani_frame += 1

        if self.ani != self.prev_ani or self.ani_frame != self.prev_ani_frame:
            # The sprite's frame has been updated. Update the mask as well.
            self.mask = pg.mask.from_surface(self.image.subsurface(
                [self.ani_frame * self.rect.w, self.ani * self.rect.h, *self.rect.size]))

        self.prev_ani = self.ani
        self.prev_ani_frame = self.ani_frame

    def draw(self, surface: pg.Surface):
        surface.blit(self.image, self.rect,
                     pg.Rect(self.ani_frame * self.rect.w, self.ani * self.rect.h, *self.rect.size))


class Collectible(pg.sprite.Sprite):
    FLOAT_DELTA = .1  # sub-pixels per frame
    FLOAT_MAX_DELTA = 3  # pixels

    SPARKLE_MIN_DELAY = 120  # frames per second
    SPARKLE_MAX_DELAY = 600  # frames per second
    SPARKLE_FRAME_UPDATE_DELAY = 10  # frames per second

    GRAVITATIONAL_ACCELERATION = -3  # frames per second

    sparkle_image: pg.Surface
    sparkle_rect: pg.Rect

    def __init__(self, image: pg.Surface, rect: pg.Rect, position: Tuple[int, int],
                 sound: pg.mixer.Sound):
        super().__init__()
        self.image = image
        self.rect = rect
        self.rect.center = position
        self.pos = position

        self.float_delta = random.randrange(-Collectible.FLOAT_MAX_DELTA,
                                            Collectible.FLOAT_MAX_DELTA)
        self.float_direction = random.choice([1, -1])

        self.sparkle_rect = Collectible.sparkle_rect.copy()
        self.sparkle_rect.center = position

        self.sparkle_frame = 0
        self.sparkle_counter = 0
        self.sparkle_frame_counter = 0
        self.sparkle_delay = random.randint(Collectible.SPARKLE_MIN_DELAY,
                                            Collectible.SPARKLE_MAX_DELAY)

        self.gravity = 0
        self.collected = False
        self.ani_collection = False

        self.sound = sound

    def score(self) -> int:
        pass

    def collect(self) -> int:
        if not self.collected:
            self.sound.play()
            self.collected = True
            self.ani_collection = True
            return self.score()
        return 0

    def draw(self, surface: pg.Surface):
        if self.ani_collection:
            if self.rect.bottom < 0 or self.rect.top > map_height:
                collectibles.remove(self)
                self.ani_collection = False
            self.gravity += Collectible.GRAVITATIONAL_ACCELERATION
            self.rect.y += self.gravity
        else:
            if not -Collectible.FLOAT_MAX_DELTA < self.float_delta < Collectible.FLOAT_MAX_DELTA:
                self.float_direction *= -1
            self.float_delta += Collectible.FLOAT_DELTA * self.float_direction
            self.rect.centery = self.sparkle_rect.centery = self.pos[1] + int(self.float_delta)

        surface.blit(self.image, self.rect)

        if not self.collected:
            if self.sparkle_counter >= self.sparkle_delay:
                if self.sparkle_frame_counter >= Collectible.SPARKLE_FRAME_UPDATE_DELAY:
                    if self.sparkle_frame >= 3:
                        self.sparkle_frame = 0
                        self.sparkle_counter = 0
                        self.sparkle_frame_counter = 0
                        self.sparkle_delay = random.randint(Collectible.SPARKLE_MIN_DELAY,
                                                            Collectible.SPARKLE_MAX_DELAY)
                    else:
                        self.sparkle_frame += 1
                        self.sparkle_frame_counter = 0
                else:
                    self.sparkle_frame_counter += 1
                surface.blit(Collectible.sparkle_image, self.sparkle_rect,
                             pg.Rect(self.sparkle_frame * self.sparkle_rect.w, 0,
                                     *self.sparkle_rect.size))
            else:
                self.sparkle_counter += 1


class Coin(Collectible):
    image: pg.Surface
    rect: pg.Rect
    sound: pg.mixer.Sound

    def __init__(self, position):
        super().__init__(Coin.image, Coin.rect.copy(), position, Coin.sound)

    def score(self):
        return 5


class Diamond(Collectible):
    image: pg.Surface
    rect: pg.Rect
    sound: pg.mixer.Sound

    def __init__(self, position):
        super().__init__(Diamond.image, Diamond.rect.copy(), position, Diamond.sound)

    def score(self):
        return 15
