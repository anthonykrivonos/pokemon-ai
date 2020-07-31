from typing import *
from src.classes.pokemon.moves.status import Status

import random

from .pokemontype import PokemonType
from .stats import Stats
from .moves.move_bank import MoveBank


class Pokemon:
    """
    All attributes related to a Pokemon.
    """

    def __init__(self, pokemon_type: PokemonType, name: str, level: int, stats: Stats, move_bank: MoveBank, hp: int, status: Status = None, other_status: Status = None, status_turns: int = 0, other_status_turns: int = 0, pokemon_id = None):
        """
        Initializes a Pokemon.
        :param pokemon_type: The Pokemon's type.
        :param name: The name of the Pokemon.
        :param level: The Pokemon's level.
        :param stats: An object containing the Pokemon's stat scores.
        :param move_bank: A bank of the Pokemon's moves.
        :param hp: The health points on the Pokemon.
        :param status: The first status condition the Pokemon is affected by.
        :param other_status: The second status condition the Pokemon is affected by.
        :param status_turns: The number of turns remaining in the first status condition.
        :param other_status_turns: The number of turns remaining in the second status condition.
        :param pokemon_id: The ID of the Pokemon, usually preset by the Party object.
        """
        self._type = pokemon_type
        self._name = name
        self._level = level
        self._move_bank = move_bank
        self._stats = stats
        self._status = status
        self._other_status = other_status
        self._status_turns = status_turns
        self._other_status_turns = other_status_turns
        self._base_hp = hp
        self._hp = hp
        self._id = pokemon_id
        self._revealed = False

    ##
    #   Getter Functions
    ##

    def get_type(self) -> PokemonType:
        return self._type

    def get_name(self) -> str:
        return self._name

    def get_level(self) -> int:
        return self._level

    def get_move_bank(self) -> MoveBank:
        return self._move_bank

    def get_stats(self) -> Stats:
        return self._stats

    def get_status(self) -> Status:
        return self._status

    def get_other_status(self) -> Status:
        return self._other_status

    def get_status_turns(self) -> int:
        return self._status_turns

    def get_other_status_turns(self) -> int:
        return self._other_status_turns

    def get_base_hp(self) -> int:
        return self._base_hp

    def get_hp(self) -> int:
        return self._hp

    def get_id(self) -> int:
        return self._id

    def is_revealed(self) -> bool:
        return self._revealed

    ##
    #   Smart Functions
    ##

    def take_damage(self, damage: int):
        """
        Has the Pokemon take damage.
        :param damage: An integer amount of damage on the Pokemon.
        """
        self._hp = max(0, self._hp - abs(damage))

    def heal(self, hp: int):
        self._hp = min(self._base_hp, self._hp + abs(hp))

    def is_fainted(self) -> bool:
        """
        Checks to see if the Pokemon has fainted.
        :return: True if the Pokemon has fainted, False otherwise.
        """
        return self._hp == 0

    def set_status(self, status: Union[Status, None], status_turns: int = None):
        """
        Sets the status of the Pokemon.
        :param status: The status the Pokemon takes on.
        :param status_turns: The number of turns to inflict the status.
        """
        self._status = status
        if self._status is not None:
            self._status_turns = random.randint(1, 7) if status_turns is None else status_turns

    def set_other_status(self, other_status: Status, other_status_turns: int = 0):
        """
        Sets the other status of the Pokemon.
        :param other_status: The other status the Pokemon takes on.
        :param other_status_turns: The number of turns to inflict the status.
        """
        self._other_status = other_status
        self._other_status_turns = 0
        if self._other_status is not None:
            self._other_status_turns = other_status_turns

    def dec_status_turn(self):
        self._status_turns += 1

    def inc_other_status_turn(self):
        self._other_status_turns += 1

    def set_id(self, pokemon_id: int):
        self._id = pokemon_id

    def reveal(self):
        self._revealed = True

    def hide(self):
        self._revealed = False
