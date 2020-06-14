from typing import *

from ..model import ModelInterface
from src.models import Player, Move, Item


class SampleModel(ModelInterface):
    """
    A sample model used to show how to create models.
    """

    @staticmethod
    def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        # I don't know what to do yet, so I'll just attack with my pokemon's first move.
        my_pokemon = player.party.get_starting()
        attack_move = my_pokemon.move_bank.get_move(0)
        attack(attack_move)
