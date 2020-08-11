import unittest

from pokemon_ai.battle import Battle
from pokemon_ai.classes import Player
from pokemon_ai.data import get_party
from pokemon_ai.ai.models import RandomModel

from .predictor import Predictor
from .mcts import make_tree


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
        input_vector = Predictor._make_input_vector(player1, player2)

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
        output_vector = Predictor._make_actual_output_list(player1, node)

        # Simply ensure it's the correct length
        self.assertEqual(31, len(output_vector))

    def test_train(self):
        model = Predictor()

        # Create player objects
        party1 = get_party('venusaur', 'squirtle')
        player1 = Player('test', party1, model=RandomModel())
        party2 = get_party('charmander', 'blastoise')
        player2 = Player('test2', party2, model=RandomModel())

        # Construct a game tree
        tree = make_tree(player1, player2, 100, False)

        # Train the model
        model.train_model(tree.root, player1, player2)

        # Predict the output
        model, move_probs, switch_probs = model.predict_move(player1, player2)

        print('Venusaur against Charmander:')
        print(["%s (prob. %.4f)" % (move.get_name(), prob) for move, prob in zip(player1.get_party().get_starting().get_move_bank().get_as_list(), move_probs)])


if __name__ == '__main__':
    unittest.main()
