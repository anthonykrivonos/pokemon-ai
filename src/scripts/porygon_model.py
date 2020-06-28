import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.battle import Battle

from src.data import get_random_party, get_party
from src.classes import Bag, Player
from src.ai import PorygonModel


party2 = get_random_party()
# party2 = get_random_party()
party1 = get_party('magikarp', 'ditto')

player1 = Player("Player 1", party1, Bag())
player2 = Player("Player 2", party2, Bag(), PorygonModel)

battle = Battle(player1, player2, 2, use_hints=True)
battle.play()
