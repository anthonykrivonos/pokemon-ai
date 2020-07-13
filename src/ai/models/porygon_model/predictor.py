from typing import *
import numpy as np

from sklearn.neural_network import MLPRegressor

from src.ai import ModelInterface

from src.ai.models import RandomModel
from src.classes import Player, Pokemon, Move, Item
from src.utils.config import POKEMON_MOVE_LIMIT, POKEMON_PARTY_LIMIT
from src.utils import to_probs

from .mcts import MonteCarloNode, MonteCarloActionType

# Very small value used in place of zero to avoid neural net training issues
EPSILON = 1e-16

# Input and output sizes of the network
INPUT_SIZE = 60  # (1 HP, 4 Moves) x 6 Pokemon x 2 Players
OUTPUT_SIZE = 31  # 6 switches + 4 Moves x 6 Pokemon + 1 outcome value


def make_input_vector(player: Player, other_player: Player) -> np.ndarray:
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


def make_actual_output_list(player: Player, node: MonteCarloNode) -> np.ndarray:
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
        if child.action_type == MonteCarloActionType.SWITCH:
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
        if child.action_type == MonteCarloActionType.ATTACK:
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


def calculate_loss(game_output: np.ndarray, output: np.ndarray):
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


def create_model() -> MLPRegressor:
    """
    Create an MLP model for training.
    :return: An MLP model.
    """
    return MLPRegressor(
        hidden_layer_sizes=(INPUT_SIZE * 4, INPUT_SIZE * 2),
        activation='relu',
        solver='adam',
        alpha=0.0001,
        batch_size='auto',
        learning_rate="constant",
        learning_rate_init=0.001,
        power_t=0.5,
        max_iter=200,
        shuffle=False,
        random_state=None,
        tol=1e-4,
        verbose=True,
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


def train_model(model: MLPRegressor, input_list: np.ndarray, output_list: np.ndarray) -> None:
    """
    Trains a sequential model given a list of inputs and outputs.
    :param model: The model to train.
    :param input_list: The input list.
    :param output_list: The output list.
    """
    model.fit([input_list], [output_list])


def predict_move(model: MLPRegressor, player: Player, other_player: Player) -> Tuple[ModelInterface, List[float], List[float]]:
    input_matrix = make_input_vector(player, other_player)
    output = model.predict([input_matrix])[0]

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

    # Get the max move and switch probabilities
    highest_move_prob = max(move_probs)
    highest_switch_prob = max(switch_probs)

    # Create the model
    model = RandomModel

    if highest_move_prob >= highest_switch_prob:
        highest_move_idx = list(move_probs).index(highest_move_prob)
        attack = player.get_party().get_starting().get_move_bank().get_as_list()[highest_move_idx]

        # Create a turn function
        def take_turn(_: Player, __: Player, do_move: Callable[[Move], None], ___: Callable[[Item], None],
                      ____: Callable[[int], None]):
            do_move(attack)

        # Create the model
        model.take_turn = take_turn
    else:
        highest_switch_idx = list(switch_probs).index(highest_switch_prob)

        # Create a turn function
        def take_turn(_: Player, __: Player, ___: Callable[[Move], None], ____: Callable[[Item], None],
                      switch_pokemon: Callable[[int], None]):
            switch_pokemon(highest_switch_idx)

        # Create the model
        model.take_turn = take_turn

    return model, to_probs(move_probs), to_probs(switch_probs)
