from src.models.pokemon.moves.status import Status

from .pokemontype import PokemonType
from .stats import Stats
from .moves.move_bank import MoveBank


class Pokemon:
    """
    All attributes related to a Pokemon.
    """

    def __init__(self, type: PokemonType, name: str, level: int, stats: Stats, move_bank: MoveBank, hp: int, status: Status = None, other_status: Status = None, status_turns: int = 0, other_status_turns: int = 0):
        """
        Initializes a Pokemon.
        :param type: The Pokemon's type.
        :param name: The name of the Pokemon.
        :param level: The Pokemon's level.
        :param stats: An object containing the Pokemon's stat scores.
        :param move_bank: A bank of the Pokemon's moves.
        :param hp: The health points on the Pokemon.
        :param status: The first status condition the Pokemon is affected by.
        :param other_status: The second status condition the Pokemon is affected by.
        :param status_turns: The number of turns remaining in the first status condition.
        :param other_status_turns: The number of turns remaining in the second status condition.
        """
        self.type = type
        self.name = name
        self.level = level
        self.move_bank = move_bank
        self.stats = stats
        self.status = status
        self.other_status = other_status
        self.status_turns = status_turns
        self.other_status_turns = other_status_turns
        self.base_hp = hp
        self.hp = hp