from .party import Party
from ..bag.bag import Bag


class Player:
    """
    A Pokemon trainer with a name, Party object, and a bag. Also contains a flag denoting whether the player is AI.
    """

    def __init__(self, name: str, party: Party, bag: Bag=Bag(), model=None, id=0):
        """
        Initializes a Player.
        :param name: The name of the player.
        :param party: A party of Pokemon the player has.
        :param bag: A bag the player has.
        :param model: The model to use for this player, if it is AI.
        :param id: The id of the player. Automatically reset during battle.
        """
        self.name = name
        self.party = party
        self.bag = bag
        self.model = model
        self.id = id
        self.is_ai = model is not None

    def to_row(self):
        """
        Converts the player into a row containing its ID and name.
        :return: Returns a row containing the player's ID and name.
        """
        return [self.id, self.name]