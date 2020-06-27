from typing import *
from .party import Party
from ..bag.bag import Bag

from copy import deepcopy
# NOTE: This class uses but does not import Model to avoid circular dependency errors.


class Player:
    """
    A Pokemon trainer with a name, Party object, and a bag. Also contains a flag denoting whether the player is AI.
    """

    def __init__(self, name: str, party: Party, bag: Bag=Bag(), model=None, player_id=0):
        """
        Initializes a Player.
        :param name: The name of the player.
        :param party: A party of Pokemon the player has.
        :param bag: A bag the player has.
        :param model: The model to use for this player, if it is AI.
        :param player_id: The id of the player. Automatically reset during battle.
        """
        self._name = name
        self._party = party
        self._bag = bag
        self._model = model
        self._id = player_id
        self._is_ai = model is not None

    ##
    #   Getter Functions
    ##

    def get_name(self) -> str:
        return self._name

    def get_party(self) -> Party:
        return self._party

    def get_bag(self) -> Bag:
        return self._bag

    def get_model(self) -> Any:
        return self._model

    def get_id(self) -> int:
        return self._id

    ##
    #   Smart Functions
    ##

    def copy(self):
        return deepcopy(self)

    def set_model(self, model):
        self._model = model
        self._is_ai = model is not None

    def set_id(self, player_id) -> int:
        self._id = player_id

    def to_row(self):
        """
        Converts the player into a row containing its ID and name.
        :return: Returns a row containing the player's ID and name.
        """
        return [self._id, self._name]

    def is_ai(self) -> bool:
        return self._is_ai
