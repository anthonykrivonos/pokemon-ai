import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))


class MoveCapacityError(Exception):
    """Raised when the move bank capacity is exceeded."""
    pass


class MoveDeleteError(Exception):
    """Raised when the move bank cannot delete a move."""
    pass


class MoveGetError(Exception):
    """Raised when the move bank cannot return a move."""
    pass
