import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.battle import Battle

from src.data import get_party
from src.models import Bag, Player
from src.ai import PorygonModel


party1 = get_party('charizard', 'charizard', 'charizard')
party2 = get_party('bulbasaur', 'bulbasaur', 'bulbasaur')

player1 = Player("Player 1", party1, Bag())
player2 = Player("Player 2", party2, Bag(), PorygonModel)

battle = Battle(player1, player2)
battle.play()
