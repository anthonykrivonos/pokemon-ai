from typing import *

from ..model import ModelInterface
from pokemon_ai.classes import Player, Move, Item, Party, Pokemon
from pokemon_ai.utils import calculate_damage_deterministic

from .random_model import RandomModel


class DamageModel(ModelInterface):
    """
    A model that picks random moves.
    """

    # use the most effective move, otherwise use the highest base power move
    def take_turn(self, player: Player, other_player: Player, attack: Callable[[Move], None],
                  use_item: Callable[[Item], None],
                  switch_pokemon_at_idx: Callable[[int], None]) -> None:
        pokemon = player.get_party().get_starting()
        enemy = other_player.get_party().get_starting()

        damage_list = []

        for move in pokemon.get_move_bank().get_as_list():
            if move.is_available():
                damage = calculate_damage_deterministic(move, pokemon, enemy)[0]
                damage_list.append((move, damage))

        damage_list.sort(reverse=True, key=lambda x: x[1])
        if len(damage_list) == 0:
            attack(Pokemon.STRUGGLE)
        else:
            attack(damage_list[0][0])

    def force_switch_pokemon(self, party: Party):
        return RandomModel().force_switch_pokemon(party)
