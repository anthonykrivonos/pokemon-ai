from typing import *


class Item:
    """
    An item that is used from the player's bag.
    """

    def __init__(self, name: str, use: Callable, description=""):
        """
        Initializes an Item.
        :param name: The name of the item.
        :param use: The function the item performs when used. First argument is Player. Second argument is Pokemon. Returns None.
        :param description: A description of the item.
        """
        self.name = name
        self.use = use
        self.description = description