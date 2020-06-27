from typing import *

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from random import shuffle

from src.classes import Player, Party, Move, Item
from src.ai.models.porygon_model import make_tree
from src.ai.models.random_model import RandomModel

NUM_SIMULATIONS = 25


class PorygonModel(RandomModel):
    """
    A sample model used to show how to create classes.
    """

    @staticmethod
    def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        with ThreadPoolExecutor() as executor:
            make_tree_thread = executor.submit(make_tree, player, other_player, NUM_SIMULATIONS, verbose=False)
            print("%s is formulating a move..." % player.get_name())
            tree = make_tree_thread.result()
            model = tree.get_next_action()
            print("Done")
            model.take_turn(player, other_player, attack, use_item, switch_pokemon_at_idx)

    @staticmethod
    def force_switch_pokemon(party: Party):
        party_list = deepcopy(party.get_as_list())
        shuffle(party_list)
        for i, pokemon in enumerate(party_list):
            if pokemon.get_hp() != 0:
                return i
        return 0
