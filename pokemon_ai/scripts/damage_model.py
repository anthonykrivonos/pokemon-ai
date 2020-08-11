import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from pokemon_ai.battle import Battle
from pokemon_ai.classes import Bag, Player
from pokemon_ai.data import get_party
from pokemon_ai.ai.models import DamageModel


party1 = get_party("charizard")
party2 = get_party("bulbasaur")

player1 = Player("Player 1", party1, Bag())
player2 = Player("Player 2", party2, Bag(), DamageModel())

battle = Battle(player1, player2)
battle.play()
