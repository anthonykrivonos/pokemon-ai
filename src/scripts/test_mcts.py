import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.battle import Battle

from src.data import get_random_party, get_party
from src.classes import Bag, Player
from src.ai import PorygonModel
from src.ai import RandomModel
from src.ai.models.porygon_model.mcts import make_tree

party1 = get_party("charizard", "venusaur")
party2 = get_party("blastoise", "caterpie")
print("%s vs. %s" % (', '.join([pkmn._name for pkmn in party1._pokemon_list]), ', '.join([pkmn._name for pkmn in party2._pokemon_list])))

player1 = Player("Player 1", party1, None, RandomModel(), player_id=1)
player2 = Player("Player 2", party2, None, RandomModel(), player_id=2)

tree = make_tree(player1, player2, 1000)
tree.print()

outcome_probs = tree.get_action_probabilities()
for prob in outcome_probs:
    print("Outcome: %1.4f, Prob: %1.4f, Visits: %d, Move: %s" % prob)