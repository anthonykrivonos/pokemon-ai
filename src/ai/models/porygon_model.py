from typing import *
from copy import deepcopy
from random import shuffle

from src.models import Player, Party, Move, Item
from src.scripts.porygon.mcts import make_tree
from .random_model import RandomModel

NUM_SIMULATIONS = 10


class PorygonModel(RandomModel):
    """
    A sample model used to show how to create models.
    """

    @staticmethod
    def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        tree = make_tree(player, other_player, NUM_SIMULATIONS, verbose=True)
        model = tree.get_next_action()
        model.take_turn(player, other_player, attack, use_item, switch_pokemon_at_idx)

    @staticmethod
    def force_switch_pokemon(party: Party):
        party_list = deepcopy(party.pokemon_list)
        shuffle(party_list)
        for i, pokemon in enumerate(party_list):
            if pokemon.hp != 0:
                return i
        return 0
