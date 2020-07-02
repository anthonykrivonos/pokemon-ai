import unittest

from src.battle import Battle
from src.classes import Player
from src.data import get_party
from src.ai import RandomModel

from .predictor import create_model, make_input_vector, make_actual_output_list, train_model, predict_move
from .mcts import make_tree, MonteCarloNode


class PredictorTestSuite(unittest.TestCase):

    def test_make_input_vector_small_team(self):
        # Create player objects
        party1 = get_party('venusaur', 'squirtle')
        player1 = Player('test', party1, model=RandomModel())
        party2 = get_party('charmander', 'blastoise')
        player2 = Player('test2', party2, model=RandomModel())

        # Play a turn
        battle = Battle(player1, player2, 0)
        battle.play_turn()

        # Create an input vector from the player objects
        input_vector = make_input_vector(player1, player2)

        # Simply ensure it's the correct length
        self.assertEqual(60, len(input_vector))

    def test_make_actual_output_list(self):
        # Create player objects
        party1 = get_party('venusaur', 'squirtle')
        player1 = Player('test', party1, model=RandomModel())
        party2 = get_party('charmander', 'blastoise')
        player2 = Player('test2', party2, model=RandomModel())

        tree = make_tree(player1, player2, 100, False)
        node = tree.root

        # Create an input vector from the player objects
        output_vector = make_actual_output_list(player1, node)

        # Simply ensure it's the correct length
        self.assertEqual(31, len(output_vector))


if __name__ == '__main__':
    unittest.main()
