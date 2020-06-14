from typing import *

from ..pokemon.pokemon import Pokemon


class Party:
    """
    A player's Pokemon party.
    """

    def __init__(self, pokemon_list: List[Pokemon] = []):
        """
        Initializes a Party.
        :param pokemon_list: A list of Pokemon in the party.
        """
        self.pokemon_list = pokemon_list

    def make_starting(self, pokemon_index: int):
        """
        Makes the Pokemon at the given index the starting, or the first, Pokemon.
        :param pokemon_index: The index of the Pokemon to move.
        """
        if 0 < pokemon_index < len(self.pokemon_list):
            temp = self.pokemon_list[pokemon_index]
            del self.pokemon_list[pokemon_index]
            self.pokemon_list.insert(0, temp)

    def get_at_index(self, idx: int) -> Pokemon:
        """
        Gets the Pokemon in the party at the given index or None if it is not found.
        :param idx: The index of the Pokemon.
        :return: The Pokemon in the party at the given index.
        """
        return self.pokemon_list[idx] if len(self.pokemon_list) > idx else None

    def get_starting(self) -> Pokemon:
        """
        Gets the starting Pokemon in the party or None if the party is empty.
        :return: The starting Pokemon in the party.
        """
        return self.get_at_index(0)
