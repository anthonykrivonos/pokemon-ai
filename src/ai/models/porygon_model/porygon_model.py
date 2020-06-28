from typing import *

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from random import shuffle

from src.classes import Player, Party, Move, Item
from .mcts import make_tree

from ...model import ModelInterface

NUM_SIMULATIONS = 25


def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None],
              switch_pokemon_at_idx: Callable[[int], None]) -> None:
    with ThreadPoolExecutor() as executor:
        make_tree_thread = executor.submit(make_tree, player, other_player, NUM_SIMULATIONS, verbose=False)
        print("%s is formulating a move..." % player.get_name())
        tree = make_tree_thread.result()
        model = tree.get_next_action()
        print("Done")
        model.take_turn(player, other_player, attack, use_item, switch_pokemon_at_idx)


def force_switch_pokemon(party: Party):
    party_list = deepcopy(party.get_as_list())
    shuffle(party_list)
    for i, pokemon in enumerate(party_list):
        if pokemon.get_hp() != 0:
            return i
    return 0


class PorygonModel(ModelInterface):
    """
    A sample model used to show how to create classes.
    """

    def __init__(self):
        self.take_turn = take_turn
        self.force_switch_pokemon = force_switch_pokemon

