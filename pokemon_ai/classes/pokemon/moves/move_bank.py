from typing import *

from pokemon_ai.errors import *

from .move import Move


class MoveBank:
    """
    Bank of moves a given Pokemon has.
    """

    _CAPACITY = 4

    def __init__(self, moves: List[Move] = []):
        """
        Initialize a MoveBank.
        :param moves: A list of moves in the bank.
        """
        self._moves = moves

    def get_as_list(self) -> List[Move]:
        return self._moves

    def add_move(self, move: Move, idx_to_delete: int = -1):
        """
        Add a move to the move bank.
        :param move: The move to add.
        :param idx_to_delete: The index to delete.
        :raises: MoveCapacityError if the move bank is full and no move is being deleted.
        """
        if len(self._moves) < self._CAPACITY:
            self._moves.append(move)
        elif idx_to_delete != -1:
            self._moves.pop(idx_to_delete)
            self._moves.insert(idx_to_delete, move)
        else:
            raise MoveCapacityError('Could not add new move.')

    def delete_move(self, idx_to_delete: int):
        """
        Delete a move from the move bank.
        :param idx_to_delete: The index to delete.
        :raises: MoveDeleteError if the move could not be deleted.
        """
        if idx_to_delete < len(self._moves):
            self._moves.pop(idx_to_delete)
        else:
            raise MoveDeleteError('Could not delete the move.')

    def get_move(self, idx: int):
        """
        Gets a move from the move bank.
        :param idx: The index to get the move from.
        :raises: MoveGetError if the move does not exist at the given index.
        """
        if len(self._moves) > idx >= 0:
            return self._moves[idx]
        else:
            raise MoveGetError('Could not get the move.')
