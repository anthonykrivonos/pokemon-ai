from typing import *

import pokemon_ai.classes
from ..model import ModelInterface
from pokemon_ai.classes import Player, Move, Item, Party, Pokemon


class SmartModel(ModelInterface):

    def take_turn(self, player: Player, other_player: Player, attack: Callable[[Move], None],
                  use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        # I don't know what to do yet, so I'll just attack with my pokemon's first move.
        my_pokemon = player.get_party().get_starting()
        if my_pokemon.must_struggle():
            attack_move = Pokemon.STRUGGLE
        else:
            attack_move = my_pokemon.get_move_bank().get_move(0)
        attack(attack_move)

    def force_switch_pokemon(self, party: Party):
        # Switch in the first non-fainted Pokemon
        for i, pokemon in enumerate(party.get_as_list()):
            if pokemon.get_hp() != 0:
                return i
