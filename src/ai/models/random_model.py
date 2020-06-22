from typing import *

from random import shuffle, randint
from copy import deepcopy
from ..model import ModelInterface
from src.models import Player, Move, Item, Party


class RandomModel(ModelInterface):
    """
    A model that picks random moves.
    """

    @staticmethod
    def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        pokemon = player.party.get_starting()

        num_available_moves = sum([ int(move.pp > 0) for move in pokemon.move_bank.moves ])
        num_available_pokemon = sum([ int(pokemon.hp > 0) for pokemon in player.party.pokemon_list ]) - 1

        if randint(1, num_available_moves + num_available_pokemon) <= num_available_moves:
            # Perform a move
            move_list = deepcopy(pokemon.move_bank.moves)
            shuffle(move_list)
            for move in move_list:
                if move.pp > 0:
                    attack(move)
                    break
        else:
            # Perform a switch
            idx = RandomModel.force_switch_pokemon(player.party)
            switch_pokemon_at_idx(idx)

    @staticmethod
    def force_switch_pokemon(party: Party):
        party_list = deepcopy(party.pokemon_list)
        shuffle(party_list)
        for i, pokemon in enumerate(party_list):
            if pokemon.hp != 0:
                return i
        return 0
