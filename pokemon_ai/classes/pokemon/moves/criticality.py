from enum import Enum


class Criticality(Enum):
    """
    The criticality of a move.
    """
    NOT_CRITICAL = 1
    CRITICAL = 2
