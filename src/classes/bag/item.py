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
        self._name = name
        self._use = use
        self._description = description

    def get_name(self) -> str:
        return self._name

    def use(self) -> None:
        self._use()

    def get_description(self) -> str:
        return self._description
