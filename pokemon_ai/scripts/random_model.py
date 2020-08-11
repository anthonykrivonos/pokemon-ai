import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from pokemon_ai.battle import Battle

from pokemon_ai.data import get_random_party
from pokemon_ai.classes import Bag, Player
from pokemon_ai.ai.models import RandomModel


party1 = get_random_party()
party2 = get_random_party()

player1 = Player("Player 1", party1, Bag())
player2 = Player("Player 2", party2, Bag(), RandomModel())

battle = Battle(player1, player2)
battle.play()
