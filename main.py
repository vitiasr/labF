#!/usr/bin/env python3
# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

import level
import struct
import pygame as pg
from player import Player
from pygame import KEYDOWN, K_m, QUIT

WINDOW_SIZE = 1167, 700
WINDOW_FRAME_RATE = 60
WINDOW_CAPTION = "4164 - 4273"

SAVE_FILENAME = "save"

SOUND_MUSIC = "res/music.ogg"
VOLUME_MUSIC = .4
SOUND_AMBIENT = "res/ambient.ogg"
VOLUME_AMBIENT = .3
SOUND_GAME_OVER = "res/game_over.ogg"
VOLUME_GAME_OVER = 1
SOUND_GAME_BEATEN = "res/game_beaten.ogg"
VOLUME_GAME_BEATEN = .8

FONT_FILENAME = "res/ARCADECLASSIC.TTF"
TEXT_COLOR = 0xFF, 0xFF, 0xFF
TEXT_OUTLINE_COLOR = 0x00, 0x00, 0x00
TEXT_OUTLINE_THICKNESS = 4

SCORE_POS = (25, 10), (WINDOW_SIZE[0] - 25, 10)  # score (top left), high score (top right)
SCORE_SIZE = 36
SCORE_TEXT = "Score", "High  score"
SCORE_LINE_SPACING = -8

GAME_OVER_POS = 0, -50  # center
GAME_OVER_SIZE = 200
GAME_OVER_TEXT = "GAME  OVER"
GAME_OVER_HINT_SIZE = 36
GAME_OVER_HINT_TEXT = "Press  any  key  to  play  again"

GAME_OVER_SCRIM_COLOR = 0x00, 0x00, 0x00
GAME_OVER_SCRIM_ALPHA = 0xA0

####################################################################################################

current_level = 1
score = 0
high_score = 0
is_game_over = False
is_game_beaten = False

font_ui: pg.font.Font
font_game_over: pg.font.Font
font_game_over_hint: pg.font.Font
sound_music: pg.mixer.Sound
sound_ambient: pg.mixer.Sound
sound_game_over: pg.mixer.Sound
sound_game_beaten: pg.mixer.Sound
game_over_scrim: pg.Surface

player: Player

music_on = True


def main():
    global current_level, score, high_score, is_game_over, game_over_scrim, player

    pg.font.init()
    pg.display.init()
    pg.display.set_caption(WINDOW_CAPTION)
    pg.mixer.init(44100, -16, 2, 64)
    clock = pg.time.Clock()
    screen = pg.display.set_mode(WINDOW_SIZE)

    load_assets()
    load_game()

    level.load(current_level)

    sound_ambient.play(-1)
    if music_on:
        sound_music.play(-1)

    player = Player()

    while handle_input(pg.event.get()):
        if player.dead:
            game_over()

        if player.promoted:
            player.promoted = False
            current_level += 1
            if level.load(current_level):
                player.initialize_position()
            else:
                # There are no more levels
                game_over(success=True)

        # Draw the level's background
        screen.blit(level.background, [0, 0])

        # Draw the level's collectibles
        if player.active():
            collected = pg.sprite.spritecollide(player, level.collectibles, False)
            for collectible in collected:
                score += collectible.collect()
                if score > high_score:
                    high_score = score
                    save_game()
        for collectible in level.collectibles.sprites():
            collectible.draw(screen)

        # Draw the level's enemies
        for enemy in level.enemies.sprites():
            enemy.update()
            collision_point = pg.sprite.collide_mask(player, enemy)
            if collision_point is not None:
                # Player hit an enemy
                player.die(collision_point)
            enemy.draw(screen)

        player.draw(screen)

        draw_ui(screen)

        pg.display.flip()
        clock.tick(WINDOW_FRAME_RATE)

    pg.quit()


def load_assets():
    """
    Loads the game's assets into the memory
    """
    global font_ui, font_game_over, font_game_over_hint, sound_music, sound_ambient, \
        sound_game_over, sound_game_beaten, game_over_scrim
    font_ui = pg.font.Font(FONT_FILENAME, SCORE_SIZE)
    font_game_over = pg.font.Font(FONT_FILENAME, GAME_OVER_SIZE)
    font_game_over_hint = pg.font.Font(FONT_FILENAME, GAME_OVER_HINT_SIZE)
    sound_music = pg.mixer.Sound(SOUND_MUSIC)
    sound_music.set_volume(VOLUME_MUSIC)
    sound_ambient = pg.mixer.Sound(SOUND_AMBIENT)
    sound_ambient.set_volume(VOLUME_AMBIENT)
    sound_game_over = pg.mixer.Sound(SOUND_GAME_OVER)
    sound_game_over.set_volume(VOLUME_GAME_OVER)
    sound_game_beaten = pg.mixer.Sound(SOUND_GAME_BEATEN)
    sound_game_beaten.set_volume(VOLUME_GAME_BEATEN)
    game_over_scrim = pg.Surface(WINDOW_SIZE)
    game_over_scrim.fill(GAME_OVER_SCRIM_COLOR)
    game_over_scrim.set_alpha(GAME_OVER_SCRIM_ALPHA)
    level.load_assets()
    Player.load_sounds()


def handle_input(event_list) -> bool:
    global current_level, score, is_game_over, is_game_beaten, music_on
    for event in event_list:
        if event.type == KEYDOWN:
            if event.key == K_m:
                if music_on:
                    music_on = False
                    sound_music.stop()
                else:
                    music_on = True
                    sound_music.play(-1)
                save_game()
            elif is_game_over:
                if music_on and is_game_beaten:
                    sound_music.play(-1)
                score = 0
                is_game_over = False
                is_game_beaten = False
                current_level = level.LEVEL_ONE
                level.load(current_level)
                player.initialize_position()
        elif event.type == QUIT:
            return False
    if not is_game_over:
        player.handle_input(event_list)
    return True


def draw_ui(surface: pg.Surface):
    """
    Draws the game's user interface
    """
    if is_game_over:
        surface.blit(game_over_scrim, [0, 0])

    # Current score
    label_rect = pg.Rect([0, 0, *font_ui.size(SCORE_TEXT[0])])
    label_rect.topleft = SCORE_POS[0]
    draw_text(surface, font_ui, SCORE_TEXT[0], TEXT_COLOR, label_rect)
    value_rect = pg.Rect(
        [0, label_rect.bottom + SCORE_LINE_SPACING, *font_ui.size(str(score))])
    value_rect.centerx = label_rect.centerx
    draw_text(surface, font_ui, str(score), TEXT_COLOR, value_rect)

    # High score
    label_rect = pg.Rect([0, 0, *font_ui.size(SCORE_TEXT[1])])
    label_rect.topright = SCORE_POS[1]
    draw_text(surface, font_ui, SCORE_TEXT[1], TEXT_COLOR, label_rect)
    value_rect = pg.Rect(
        [0, label_rect.bottom + SCORE_LINE_SPACING, *font_ui.size(str(high_score))])
    value_rect.centerx = label_rect.centerx
    draw_text(surface, font_ui, str(high_score), TEXT_COLOR, value_rect)

    if is_game_over:
        text_rect = pg.Rect([0, 0, *font_game_over.size(GAME_OVER_TEXT)])
        text_rect.centerx = WINDOW_SIZE[0] // 2 + GAME_OVER_POS[0]
        text_rect.centery = WINDOW_SIZE[1] // 2 + + GAME_OVER_POS[1]
        draw_text(surface, font_game_over, GAME_OVER_TEXT, TEXT_COLOR, text_rect)

        hint_rect = pg.Rect([0, 0, *font_game_over_hint.size(GAME_OVER_HINT_TEXT)])
        hint_rect.centerx = WINDOW_SIZE[0] // 2
        hint_rect.top = text_rect.bottom  # WINDOW_SIZE[1] // 2
        draw_text(surface, font_game_over_hint, GAME_OVER_HINT_TEXT, TEXT_COLOR, hint_rect)


def game_over(success=False):
    global is_game_over, is_game_beaten
    if not is_game_over:
        is_game_over = True
        if success:
            sound_music.stop()
            sound_game_beaten.play()
            is_game_beaten = True
        else:
            sound_game_over.play()


def draw_text(surface: pg.Surface, font: pg.font.Font, text: str, color, rect: pg.Rect):
    """
    Draws outlined text to the given surface
    """
    render = font.render(text, False, color)
    outline = font.render(text, False, TEXT_OUTLINE_COLOR)
    surface.blit(outline, [rect.x - TEXT_OUTLINE_THICKNESS, rect.y, *rect.size])
    surface.blit(outline, [rect.x + TEXT_OUTLINE_THICKNESS, rect.y, *rect.size])
    surface.blit(outline, [rect.x, rect.y - TEXT_OUTLINE_THICKNESS, *rect.size])
    surface.blit(outline, [rect.x, rect.y + TEXT_OUTLINE_THICKNESS, *rect.size])
    surface.blit(render, rect)


def load_game():
    """
    Loads the previously saved high score from the disk
    """
    global music_on, high_score
    try:
        with open(SAVE_FILENAME, "rb") as file:
            music_on, high_score = struct.unpack("<?I", file.read())
    except FileNotFoundError:
        pass
    except OSError as e:
        print("Error loading high score. {}.".format(e.strerror))
    except struct.error:
        print("Error loading high score. Save file corrupted.")


def save_game():
    """
    Saves the high score to disk
    """
    try:
        with open(SAVE_FILENAME, "wb") as file:
            file.write(struct.pack("<?I", music_on, high_score))
    except OSError as e:
        print("Error saving high score. {}.".format(e.strerror))


if __name__ == '__main__':
    main()
