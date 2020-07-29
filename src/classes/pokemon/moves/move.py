from ..pokemontype import PokemonType
from .status import Status


class Move:
    """
    A move that can be performed by a Pokemon.
    """

    def __init__(self, name: str, base_damage: int, pp: int, type: PokemonType, is_special: bool, base_heal=0, status_inflict: Status = None):
        """
        Initializes a Move.
        :param name: The name of the move.
        :param base_damage: The base damage the move does, not including other calculations.
        :param pp: The number of times the move can be performed.
        :param type: The move's type.
        :param is_special: Is the move a special attack? In other words, does it require non-physical attacking?
        :param base_heal: The base amount of healing the move does to the Pokemon. Usually 0.
        :param status_inflict: The status the move inflicts onto the opposing Pokemon.
        """
        self._name = name
        self._base_damage = base_damage
        self._base_heal = base_heal
        self._pp = pp
        self._base_pp = pp
        self._type = type
        self._is_special = is_special
        self._status_inflict = status_inflict
        self._revealed = False

    def get_name(self) -> str:
        return self._name

    def get_base_damage(self) -> int:
        return self._base_damage

    def get_base_heal(self) -> int:
        return self._base_heal

    def get_pp(self) -> int:
        return self._pp

    def is_available(self) -> bool:
        return self._pp > 0

    def get_base_pp(self) -> int:
        return self._base_pp

    def get_type(self) -> PokemonType:
        return self._type

    def is_revealed(self) -> bool:
        return self._revealed

    def is_special(self) -> bool:
        return self._is_special

    def is_damaging(self) -> bool:
        """
        :return: True if the move inflicts damage, False otherwise.
        """
        return self._base_damage > 0

    def get_status_inflict(self) -> Status:
        return self._status_inflict

    def dec_pp(self):
        self._pp = max(0, self._pp - 1)

    def reveal(self):
        self._revealed = True
