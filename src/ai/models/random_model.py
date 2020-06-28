from typing import *

from random import shuffle, randint
from copy import deepcopy
from ..model import ModelInterface
from src.classes import Player, Move, Item, Party


def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None],
              switch_pokemon_at_idx: Callable[[int], None]) -> None:
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


def force_switch_pokemon(party: Party):
    party_list = deepcopy(party.get_as_list())
    shuffle(party_list)
    for i, pokemon in enumerate(party_list):
        if pokemon.get_hp() != 0:
            return i
    return 0


class RandomModel(ModelInterface):
    """
    A model that picks random moves.
    """

    def __init__(self):
        self.take_turn = take_turn
        self.force_switch_pokemon = force_switch_pokemon
