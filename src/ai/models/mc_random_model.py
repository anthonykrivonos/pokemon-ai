from typing import *

from enum import Enum
from random import shuffle, randint
from copy import deepcopy
from ..model import ModelInterface
from src.models import Player, Move, Item, Party


class MonteCarloActionType(Enum):
    ATTACK = 0
    SWITCH = 1


class MonteCarloRandomModel(ModelInterface):
    """
    A model that picks random moves and returns Monte-Carlo pairs.
    """

    @staticmethod
    def on_take_turn(action_type:MonteCarloActionType, action_index:int) -> None:
        """
        Define this function to record the opponent's moves.
        :param action_type: The type of action taken.
        :param action_index: The index of the action taken.
        """
        pass

    @staticmethod
    def take_turn(player: Player, other_player: Player, attack: Callable[[Move], None], use_item: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]) -> (MonteCarloActionType, int):
        pokemon = player.party.get_starting()

        num_available_moves = sum([ int(move.pp > 0) for move in pokemon.move_bank.moves ])
        num_available_pokemon = sum([ int(pokemon.hp > 0) for pokemon in player.party.pokemon_list ]) - 1

        if randint(1, num_available_moves + num_available_pokemon) <= num_available_moves:
            # Perform a move
            move_list = [(move, i) for i, move in enumerate(deepcopy(pokemon.move_bank.moves))]
            shuffle(move_list)
            for move, i in move_list:
                if move.pp > 0:
                    attack(move)
                    MonteCarloRandomModel.on_take_turn(MonteCarloActionType.ATTACK, i)
                    break
        else:
            # Perform a switch
            idx = MonteCarloRandomModel.force_switch_pokemon(player.party)
            switch_pokemon_at_idx(idx)
            return MonteCarloRandomModel.on_take_turn(MonteCarloActionType.SWITCH, idx)

    @staticmethod
    def force_switch_pokemon(party: Party):
        party_list = deepcopy(party.pokemon_list)
        shuffle(party_list)
        for i, pokemon in enumerate(party_list):
            if pokemon.hp != 0:
                return i
        return 0
