from typing import *

from src.models import Player, Move, Item


class ModelInterface:

    @staticmethod
    def take_turn(self, player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> None:
        """
        Placeholder for taking a turn using the model's algorithm.
        :param player: The player for whom the turn is being taken.
        :param other_player: The opponent.
        :param attack: A function to call if the model chooses to attack.
        :param use_item: A function to call if the model chooses to use an item.
        :param switch_pokemon_at_idx: A function to call if the model chooses to switch Pokemon.
        """
        pass
