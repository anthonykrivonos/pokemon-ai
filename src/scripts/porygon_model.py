import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.battle import Battle

from src.data import get_random_party, get_party
from src.classes import Bag, Player
from src.ai import PorygonModel


party1 = get_party("zapdos", "sandslash", "starmie", "charizard", "tauros", "chansey")  # get_random_party()
party2 = get_party("caterpie", "diglett", "rattata", "poliwag", "meowth", "vulpix")  # get_random_party()

player1 = Player("Player 1", party1, Bag())
player2 = Player("Player 2", party2, Bag(), PorygonModel())

battle = Battle(player1, player2, 2, use_hints=True)
battle.play()
