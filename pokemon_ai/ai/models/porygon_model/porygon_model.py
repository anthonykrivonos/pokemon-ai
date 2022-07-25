from typing import *

from concurrent.futures import ThreadPoolExecutor
from pokemon_ai.classes import Player, Party, Move, Item
from .mcts import make_tree, MonteCarloNode
from ..random_model import RandomModel
from .predictor import Predictor

from pokemon_ai.ai import ModelInterface

NUM_SIMULATIONS = 50


class PorygonModel(ModelInterface):
    """
    A sample model used to show how to create classes.
    """
    def __init__(self, use_damage_model=False, verbose=False):
        super()
        self._verbose = verbose
        self._use_damage_model = use_damage_model
        self._predictor = Predictor(verbose=verbose)

    def train_model(self, player: Player, other_player):
        node = MonteCarloNode(player, other_player)
        self._predictor.train_model(node=node, player=player, other_player=other_player)

    def take_turn(self, player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        with ThreadPoolExecutor() as executor:
            self._predictor.predict_move(player, other_player)
            make_tree_thread = executor.submit(make_tree, player, other_player, NUM_SIMULATIONS, predictor=self._predictor, use_damage_model=self._use_damage_model, verbose=False)
            if self._verbose:
                print("%s is formulating a move..." % player.get_name())
            tree = make_tree_thread.result()
            model = tree.get_next_action()
            if self._verbose:
                print("Done")
            model.take_turn(player, other_player, attack, use_item, switch_pokemon_at_idx)

    def force_switch_pokemon(self, party: Party):
        return RandomModel().force_switch_pokemon(party)
