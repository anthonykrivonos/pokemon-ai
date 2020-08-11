from random import shuffle, randint
from copy import deepcopy
from typing import Callable

from .. import ModelInterface
from pokemon_ai.classes import Player, Move, Item, Party


class RandomModel(ModelInterface):
    """
    A model that picks random moves.
    """

    def take_turn(self, player: Player, other_player: Player, attack: Callable[[Move], None],
                  use_item: Callable[[Item], None],
                  switch_pokemon_at_idx: Callable[[int], None]) -> None:
        pokemon = player.get_party().get_starting()

        num_available_moves = sum([int(move.is_available()) for move in pokemon.get_move_bank().get_as_list()])
        num_available_pokemon = sum([int(not pokemon.is_fainted()) for pokemon in player.get_party().get_as_list()]) - 1

        if num_available_moves + num_available_pokemon > 0 and randint(1, num_available_moves + num_available_pokemon) <= num_available_moves:
            # Perform a move
            move_list = deepcopy(pokemon.get_move_bank().get_as_list())
            shuffle(move_list)
            for move in move_list:
                if move.is_available():
                    attack(move)
                    break
        else:
            # Perform a switch
            idx = self.force_switch_pokemon(player.get_party())
            switch_pokemon_at_idx(idx)

    def force_switch_pokemon(self, party: Party):
        party_list = deepcopy(party.get_as_list())
        for i, pokemon in enumerate(party_list):
            if pokemon.get_hp() != 0 and pokemon.get_id() != party.get_starting().get_id():
                return i
        return 0
