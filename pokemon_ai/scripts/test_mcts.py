import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from pokemon_ai.data import get_party
from pokemon_ai.classes import Player
from pokemon_ai.ai.models import RandomModel
from pokemon_ai.ai.models.porygon_model.mcts import make_tree

party1 = get_party("charizard", "venusaur")
party2 = get_party("blastoise", "caterpie")
print("%s vs. %s" % (', '.join([pkmn.get_name() for pkmn in party1.get_as_list()]), ', '.join([pkmn.get_name() for pkmn in party2.get_as_list()])))

player1 = Player("Player 1", party1, None, RandomModel(), player_id=1)
player2 = Player("Player 2", party2, None, RandomModel(), player_id=2)

tree = make_tree(player1, player2, 1000)
tree.print()

outcome_probs = tree.get_action_probabilities()
for prob in outcome_probs:
    print("Outcome: %1.4f, Prob: %1.4f, Visits: %d, Move: %s" % prob)
