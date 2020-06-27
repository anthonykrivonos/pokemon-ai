from typing import *
import time

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
        self._pokemon_list = pokemon_list
        self._preset_ids()

    def get_as_list(self) -> List[Pokemon]:
        return self._pokemon_list

    def _preset_ids(self):
        """
        Sets the IDs of the Pokemon in the Party sequentially.
        """
        # Uses the current millis timestamp as a base to ensure Pokemon only belong to one party
        id_base = int(time.time())
        for idx, pokemon in enumerate(self._pokemon_list):
            pokemon_id = id_base + idx
            pokemon.set_id(pokemon_id)

    def make_starting(self, pokemon_index: int):
        """
        Makes the Pokemon at the given index the starting, or the first, Pokemon.
        :param pokemon_index: The index of the Pokemon to move.
        """
        if 0 < pokemon_index < len(self._pokemon_list):
            temp = self._pokemon_list[pokemon_index]
            del self._pokemon_list[pokemon_index]
            self._pokemon_list.insert(0, temp)

    def get_at_index(self, idx: int) -> Pokemon:
        """
        Gets the Pokemon in the party at the given index or None if it is not found.
        :param idx: The index of the Pokemon.
        :return: The Pokemon in the party at the given index.
        """
        return self._pokemon_list[idx] if len(self._pokemon_list) > idx else None

    def get_index_of(self, pokemon: Pokemon) -> int:
        """
        Gets the index of the Pokemon using its ID. Will not work with Pokemon not belonging to the party.
        :param pokemon: The Pokemon to find the index of.
        :return: The int index of the Pokemon or -1 if it doesn't belong to the Party.
        """
        for idx, other_pokemon in enumerate(self._pokemon_list):
            if other_pokemon.get_id() == pokemon.get_id():
                return idx
        return -1

    def get_starting(self) -> Pokemon:
        """
        Gets the starting Pokemon in the party or None if the party is empty.
        :return: The starting Pokemon in the party.
        """
        return self.get_at_index(0)
