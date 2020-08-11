import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from pokemon_ai.battle import Battle
from pokemon_ai.classes import Bag, Player
from pokemon_ai.data import get_party
from pokemon_ai.ai import PorygonModel, RandomModel

win_count = {}

for i in range(3):
    party1 = get_party("charizard", "venusaur")
    party2 = get_party("blastoise", "tentacruel")

    player1 = Player("MCTS", party1, Bag(), PorygonModel(), player_id=1)
    player2 = Player("GET HIT WIT ALLA DAT", party2, Bag(), RandomModel(), player_id=2)

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
