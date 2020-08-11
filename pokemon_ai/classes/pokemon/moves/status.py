from enum import Enum


class Status(Enum):
    """
    The health status of a Pokemon.
    """
    INFATUATION = 0
    CONFUSION = 1
    SLEEP = 2
    POISON = 3
    BAD_POISON = 4
    PARALYSIS = 5
    FREEZE = 6
    BURN = 7


"""
A list of English names for each of the health statuses.
"""
status_names = {
    Status.CONFUSION: 'confused',
    Status.POISON: 'poisoned',
    Status.BAD_POISON: 'badly poisoned',
    Status.SLEEP: 'fast asleep',
    Status.BURN: 'burned',
    Status.FREEZE: 'frozen',
    Status.INFATUATION: 'infatuated',
    Status.PARALYSIS: 'paralyzed'
}