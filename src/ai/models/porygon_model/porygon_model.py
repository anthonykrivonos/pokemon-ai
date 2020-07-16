from typing import *

from concurrent.futures import ThreadPoolExecutor
from src.classes import Player, Party, Move, Item
from .mcts import make_tree
from ..random_model import RandomModel

from src.ai import ModelInterface

NUM_SIMULATIONS = 50


class PorygonModel(ModelInterface):
    """
    A sample model used to show how to create classes.
    """

    def __init__(self):
        pass

    def take_turn(self, player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        with ThreadPoolExecutor() as executor:
            make_tree_thread = executor.submit(make_tree, player, other_player, NUM_SIMULATIONS, verbose=False)
            print("%s is formulating a move..." % player.get_name())
            tree = make_tree_thread.result()
            model = tree.get_next_action()
            print("Done")
            model.take_turn(player, other_player, attack, use_item, switch_pokemon_at_idx)

    def force_switch_pokemon(self, party: Party):
        return RandomModel().force_switch_pokemon(party)
