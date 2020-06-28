from typing import *

from random import shuffle, randint
from copy import deepcopy
from ..model import ModelInterface
from src.classes import Player, Move, Item, Party


class RandomModel(ModelInterface):
    """
    A model that picks random moves.
    """

    @staticmethod
    def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        pokemon = player.get_party().get_starting()

        num_available_moves = sum([int(move.is_available()) for move in pokemon.get_move_bank().get_as_list()])
        num_available_pokemon = sum([int(not pokemon.is_fainted()) for pokemon in player.get_party().get_as_list()]) - 1

        if randint(1, num_available_moves + num_available_pokemon) <= num_available_moves:
            # Perform a move
            move_list = deepcopy(pokemon.get_move_bank().get_as_list())
            shuffle(move_list)
            for move in move_list:
                if move.is_available():
                    attack(move)
                    break
        else:
            # Perform a switch
            idx = RandomModel.force_switch_pokemon(player.get_party())
            switch_pokemon_at_idx(idx)

    @staticmethod
    def force_switch_pokemon(party: Party):
        party_indices = list(range(len(party.get_as_list())))
        print(party_indices)
        shuffle(party_indices)
        for i in party_indices:
            pokemon = party.get_at_index(i)
            if i != 0 and not pokemon.is_fainted():
                return i
        return 0
