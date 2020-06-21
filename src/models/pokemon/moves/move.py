from ..pokemontype import PokemonType
from .status import Status


class Move:
    """
    A move that can be performed by a Pokemon.
    """

    def __init__(self, name: str, base_damage: int, pp: int, type: PokemonType, is_special: bool, base_heal=0, status: Status = None):
        """
        Initializes a Move.
        :param name: The name of the move.
        :param base_damage: The base damage the move does, not including other calculations.
        :param pp: The number of times the move can be performed.
        :param type: The move's type.
        :param is_special: Is the move a special attack? In other words, does it require non-physical attacking?
        :param base_heal: The base amount of healing the move does to the Pokemon. Usually 0.
        :param status: The status the move inflicts onto the opposing Pokemon.
        """
        self.name = name
        self.base_damage = base_damage
        self.base_heal = base_heal
        self.pp = pp
        self.base_pp = pp
        self.type = type
        self.is_special = is_special
        self.status = status
