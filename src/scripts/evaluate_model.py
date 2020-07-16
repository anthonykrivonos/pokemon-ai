import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.battle import Battle
from src.classes import Bag, Party, Player, Move, MoveBank, Pokemon, Stats, PokemonType
from src.data import get_random_party, get_party
from src.ai import DamageModel, PorygonModel

win_count = {}

for i in range(1):
    party1 = get_party("squirtle", "charizard", "wartortle")
    party2 = get_party("bulbasaur", "venusaur", "ivysaur")

    player1 = Player("MCTS", party1, Bag(), PorygonModel())
    player2 = Player("GET HIT WIT ALLA DAT", party2, Bag(), DamageModel())

    battle = Battle(player1, player2, 1)
    winner = battle.play()

    win_count[winner.get_name()] = int(0 if win_count.get(winner.get_name()) is None else win_count.get(winner.get_name())) + 1

# for i in range(5):
#     party3 = get_party("bulbasaur", "venusaur", "ivysaur")
#     party4 = get_party("squirtle", "charizard", "wartortle")
#
#     player3 = Player("MCTS", party3, Bag(), PorygonModel())
#     player4 = Player("GET HIT WIT ALLA DAT", party4, Bag(), DamageModel())
#
#     battle = Battle(player3, player4)
#     winner = battle.play()
#
#     win_count[winner.get_name()] = int(0 if win_count.get(winner.get_name()) is None else win_count.get(winner.get_name())) + 1

print(win_count)


