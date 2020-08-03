from typing import *

import sys
import random
from os.path import join, dirname

sys.path.append(join(dirname(__file__), '../..'))


def chance(percentage: float, success: any = None, failure: any = None):
    """
    Calculates a random value and returns success if it is within the threshold and returns failure otherwise. If success and failure are functions, they get called.
    :param percentage: The percentage of success. For instance, 0.9 would return success 90% of the time.
    :param success: The value to return on success.
    :param failure: The value to return on failure.
    :return: success or failure if they are not callable, or success() or failure() otherwise.
    """
    if percentage >= random.random():
        return (success() if callable(success) else success) if success is not None else None
    return (failure() if callable(failure) else failure) if failure is not None else None


def chances(probabilities: List[float], results: List[any]):
    """
    Uniformly selects the result based on the list of probability percentages.
    :param probabilities: The percentage associated with each result.
    :param results: The list of results, lining up with percentages.
    :return: success or failure if they are not callable, or success() or failure() otherwise.
    """
    assert len(probabilities) == len(results)
    thresh = random.random()
    for i, percentage in enumerate(probabilities):
        lower = sum(probabilities[:i]) if i > 0 else 0
        upper = lower + percentage
        if lower <= thresh < upper:
            return results[i]
    return results[-1]


def random_int(start: int, end: int):
    """
    Returns a random integer between the start and end values, exclusive to the end value but inclusive to the start value.
    :param start: The starting integer.
    :param end: The ending integer. Never returns this exact integer.
    :return: The random integer.
    """
    return random.randint(start, end)


def random_pct(start: int = 0, end: int = 100):
    """
    Returns a random percentage value.
    :param start: The starting percentage.
    :param end: The ending percentage.
    :return: The random percentage out of 1.
    """
    return random_int(start, end) / 100
