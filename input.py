#!/usr/bin/env python3
# Κωσταντίνος Χρυσικός (ΑΜ: 4164)
# Βίκτωρ Ριζκόβ (ΑΜ: 4273)

from pygame import *
from player import Player


def handle_event(event_list, player: Player) -> bool:
    for event in event_list:

        if event.type == QUIT:
            return False

    player.handle_input(event_list)

    return True
