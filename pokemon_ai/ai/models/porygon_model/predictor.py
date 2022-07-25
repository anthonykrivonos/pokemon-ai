from typing import *
import numpy as np

from sklearn.neural_network import MLPRegressor

from pokemon_ai.ai.models import RandomModel
from pokemon_ai.classes import Player, Pokemon, Move, Item
from pokemon_ai.utils import POKEMON_MOVE_LIMIT, POKEMON_PARTY_LIMIT
from pokemon_ai.utils import to_probs, chance, chances

from .models import MonteCarloActionType

# Very small value used in place of zero to avoid neural net training issues
EPSILON = 1e-16

# Input and output sizes of the network
INPUT_SIZE = 60  # (1 HP, 4 Moves) x 6 Pokemon x 2 Players
OUTPUT_SIZE = 31  # 6 switches + 4 Moves x 6 Pokemon + 1 outcome value


class Predictor:

    def __init__(self, hidden_layer_sizes: Tuple[int] = (INPUT_SIZE * 4, INPUT_SIZE * 2), batch_size: Union[int, str] = 'auto', verbose = True):
        """
        Create an MLP model for training.
        """
        self._is_trained = False
        self._model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver='adam',
            alpha=0.0001,
            batch_size=batch_size,
            learning_rate="constant",
            learning_rate_init=0.001,
            power_t=0.5,
            max_iter=200,
            shuffle=False,
            random_state=None,
            tol=1e-4,
            verbose=verbose,
            warm_start=False,
            momentum=0.9,
            nesterovs_momentum=True,
            early_stopping=False,
            validation_fraction=0.1,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-8,
            n_iter_no_change=10
        )

    def train_model(self, node: Any, player: Player, other_player: Player) -> None:
        """
        Trains a sequential model given a list of inputs and outputs.
        :param node: The node where the decision must be made.
        :param player: The player.
        :param other_player: The opposing player.
        """
        self._is_trained = True
        self._model.fit([self._make_input_vector(player, other_player)], [self._make_actual_output_list(player, node)])

    def predict_move(self, player: Player, other_player: Player) -> Tuple[RandomModel, MonteCarloActionType, int, List[float], List[float]]:
        """
        Predict the move the player should make.
        :param player: The player.
        :param other_player: The opposing player.
        :return: A tuple containing the <move model, move type, move index, move probabilities, switch-out probabilities>.
        """
        if not self._is_trained:
            return RandomModel(), MonteCarloActionType.ATTACK, 0, POKEMON_MOVE_LIMIT*[round(1/POKEMON_MOVE_LIMIT)], POKEMON_PARTY_LIMIT* [round(1/POKEMON_PARTY_LIMIT)]

        input_matrix = self._make_input_vector(player, other_player)
        output = self._model.predict([input_matrix])[0]

        # Get the index of the 4 current Pokemon moves from the output
        current_pokemon_id = player.get_party().get_starting().get_id()
        current_pokemon_idx = -1
        for idx, pokemon in enumerate(player.get_party().get_sorted_list()):
            if pokemon.get_id() == current_pokemon_id:
                current_pokemon_idx = idx
                break

        # Create probabilities for picking moves and switches
        move_probs = []
        if current_pokemon_idx >= 0:
            start_idx = POKEMON_PARTY_LIMIT + current_pokemon_idx * POKEMON_MOVE_LIMIT
            move_probs = output[start_idx:start_idx + POKEMON_MOVE_LIMIT]
        switch_probs = output[:POKEMON_PARTY_LIMIT]

        # Create the model
        model = RandomModel()

        # Get probability of attacking and switching
        all_moves = list(np.concatenate((move_probs, switch_probs), axis=0))
        all_moves_probs = to_probs(all_moves)
        prob_attack = sum(all_moves_probs[:len(move_probs)])
        move_type = chance(prob_attack, MonteCarloActionType.ATTACK, MonteCarloActionType.SWITCH)
        move_idx = 0

        # Randomly select a move given the move weights
        if move_type == MonteCarloActionType.ATTACK:
            if player.get_party().get_starting().must_struggle():
                attack = Pokemon.STRUGGLE
            else:
                # Get a random move
                move_idx = chances(move_probs, list(range(len(player.get_party().get_starting().get_move_bank().get_as_list()))))
                attack = player.get_party().get_starting().get_move_bank().get_move(move_idx)

            # Create a turn function
            def take_turn(_: Player, __: Player, do_move: Callable[[Move], None], ___: Callable[[Item], None],
                          ____: Callable[[int], None]):
                do_move(attack)

            # Create the model
            model.take_turn = take_turn
        else:
            # Get a random switch index
            move_idx = chances(switch_probs, [i for i, _ in enumerate(switch_probs)])

            # Create a turn function
            def take_turn(_: Player, __: Player, ___: Callable[[Move], None], ____: Callable[[Item], None],
                          switch_pokemon: Callable[[int], None]):
                switch_pokemon(move_idx)

            # Create the model
            model.take_turn = take_turn

        return model, move_type, move_idx, move_probs, switch_probs

    @staticmethod
    def _calculate_loss(game_output: np.ndarray, output: np.ndarray):
        """
        Calculates the loss between the output from searching and output from finishing the game.
        :param game_output: The output from finishing the game.
        :param output: The output from searching/learning.
        :return: A float representing the loss.
        """

        # Calculate outcome component
        predicted_outcome = output[-1]
        game_outcome = game_output[-1]
        outcome_loss = np.square(game_outcome - predicted_outcome)

        # Calculate policy component
        search_probs = output[:-1]
        policy_probs = game_output[:-1]
        policy_comp = np.dot(search_probs, np.log(policy_probs))

        return outcome_loss + policy_comp

    @staticmethod
    def _make_input_vector(player: Player, other_player: Player) -> np.ndarray:
        """
        Creates an input vector for the dense net.
        :param player: The focused player.
        :param other_player: The other player.
        :return: A 60-len numpy array with [HP ratio, Move 1 PP ratio, ... Move 4 PP ratio] at each row for max 12 Pokemon,
        flattened.
        """
        # Store each player's Pokemon lists
        player_pokemon = player.get_party().get_sorted_list()
        other_player_pokemon = other_player.get_party().get_sorted_list()

        mat = []

        def fill_rows(pokemon_list: List[Pokemon]):
            """
            Fills a list of rows with Pokemon stats.
            :param pokemon_list: A list of Pokemon.
            """
            for pkmn in pokemon_list:
                row = []

                # Add HP component
                hp_comp = pkmn.get_hp() / pkmn.get_base_hp()
                row.append(hp_comp)

                # Add move components
                move_list = pkmn.get_move_bank().get_as_list()
                for move in move_list:
                    move_comp = move.get_pp() / move.get_base_pp()
                    row.append(move_comp)
                # Fill remaining moves with 0
                for _ in range(POKEMON_MOVE_LIMIT - len(move_list)):
                    row.append(EPSILON)

                # Add row to matrix
                mat.append(row)

        def fill_empty(num: int):
            for _ in range(num):
                mat.append([EPSILON, EPSILON, EPSILON, EPSILON, EPSILON])

        # Fill rows
        fill_rows(player_pokemon)
        fill_empty(POKEMON_PARTY_LIMIT - len(player_pokemon))
        fill_rows(other_player_pokemon)
        fill_empty(POKEMON_PARTY_LIMIT - len(other_player_pokemon))

        return np.array(mat).flatten()

    @staticmethod
    def _make_actual_output_list(player: Player, node: Any) -> np.ndarray:
        """
        Creates a list of actual output values from a player object and a single node.
        :param player: A Player that owns the action in the node.
        :param node: A MonteCarloNode.
        :return: A list of output values of length OUTPUT_SIZE (31).
        """

        # Get list of Pokemon
        player_pokemon = player.get_party().get_as_list()

        # Calculate switch probabilities
        switch_probs = [EPSILON] * len(player_pokemon)
        for child in node.children:
            if child.action_type == 0:  # SWITCH
                pkmn_id = child.action_descriptor
                switch_idx = 0
                for i, pkmn in enumerate(player_pokemon):
                    if pkmn.get_id() == pkmn_id:
                        switch_idx = i
                switch_probs[switch_idx] = child.outcome / node.outcome
        # Create a tuple of switch probability / Pokemon values
        pokemon_switch_tuple: List[Tuple[float, Pokemon]] = []
        for i, switch_prob in enumerate(switch_probs):
            pokemon_switch_tuple.append((switch_prob, player_pokemon[i]))
        # Sort the tuple by Pokemon ID to retain order
        pokemon_switch_tuple.sort(key=lambda v: v[1].get_id())
        # Remake switch_probs in order
        switch_probs = [tup[0] for tup in pokemon_switch_tuple]
        # Add extra probs in case of short party
        for _ in range(POKEMON_PARTY_LIMIT - len(player_pokemon)):
            switch_probs.append(EPSILON)

        # Add attack moves of every Pokemon
        pkmn_id_to_move_prob_map = {}
        for child in node.children:
            if child.action_type == 0:  # ATTACK
                pkmn_id = child.detokenize_child()
                move_idx = child.action_descriptor
                if pkmn_id not in pkmn_id_to_move_prob_map:
                    pkmn_id_to_move_prob_map[pkmn_id] = [EPSILON] * POKEMON_MOVE_LIMIT
                pkmn_id_to_move_prob_map[pkmn_id][move_idx] = child.outcome / node.outcome
        # Create a list of moves for all Pokemon and then traverse the sorted Pokemon list, adding the prob of each move
        # one by one.
        move_probs = []
        for pkmn in player.get_party().get_sorted_list():
            pkmn_id = pkmn.get_id()
            move_probs_for_pkmn = []
            if pkmn_id in pkmn_id_to_move_prob_map:
                for move_prob in pkmn_id_to_move_prob_map[pkmn_id]:
                    move_probs_for_pkmn.append(move_prob)
            while len(move_probs_for_pkmn) < 4:
                move_probs_for_pkmn.append(EPSILON)
            move_probs += move_probs_for_pkmn
        while len(move_probs) < POKEMON_PARTY_LIMIT * POKEMON_MOVE_LIMIT:
            move_probs += [EPSILON] * POKEMON_MOVE_LIMIT

        outcome_list = [node.outcome]

        mat = switch_probs + move_probs + outcome_list
        return np.array(mat)
