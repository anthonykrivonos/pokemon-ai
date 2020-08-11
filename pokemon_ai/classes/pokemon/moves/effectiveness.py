from enum import Enum


class Effectiveness(Enum):
    """
    The effectiveness of a Pokemon move.
    """
    NO_EFFECT = 0
    NOT_EFFECTIVE = 0.5
    NORMAL = 1
    SUPER_EFFECTIVE = 2