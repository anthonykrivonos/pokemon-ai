import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.battle import Battle
from src.classes import Bag, Party, Player, Move, MoveBank, Pokemon, Stats, PokemonType
from src.data import get_random_party, get_party
from src.ai import DamageModel


party1 = get_party("charizard")
party2 = get_party("bulbasaur")

player1 = Player("Player 1", party1, Bag())
player2 = Player("Player 2", party2, Bag(), DamageModel())

battle = Battle(player1, player2)
battle.play()
