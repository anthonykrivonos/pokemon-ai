from typing import *

from .item import Item


class Bag:
    """
    A player's bag of items that may be used on a Pokemon. Pokeballs not implemented.
    """

    def __init__(self, item_list: List[Item] = []):
        """
        Initializes a Bag.
        :param item_list: A list of items in the bag.
        """
        self._item_list = item_list

    def get_as_list(self) -> List[Item]:
        return self._item_list
