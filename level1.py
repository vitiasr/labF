# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

from level import *

BACKGROUND_IMAGE = "res/bg_lvl_1.png"
BITMAP = "res/bmp_lvl_1.png"


class Level1(Level):
    def __init__(self):
        super().__init__(BACKGROUND_IMAGE, BITMAP)

    def get_player_pos(self) -> tuple:
        return 100, 100
