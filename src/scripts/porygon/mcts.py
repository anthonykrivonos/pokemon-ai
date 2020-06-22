from typing import *
from enum import Enum
from copy import deepcopy

from src.models import Player, Move, Item
from src.battle import Battle
from src.utils import calculations
from src.ai import RandomModel
from src.data import get_random_party


class MonteCarloTree:

    def __init__(self):
        """
        Initializes a MonteCarloTree.
        """
        self.root = MonteCarloNode()

    def pre_order_print(self):
        """
        Prints tuples of the tree node's descriptions and outcomes in a pre-order fashion.
        """
        def pre_order(node: MonteCarloNode):
            print(node)
            for child in node.children:
                pre_order(child)
        pre_order(self.root)

    def get_next_action(self):
        """
        Decides the next action to take from the root.
        :return: Returns the model for the next action to take.
        """
        max_outcome = -1
        max_child = None
        for child, _ in self.root.children:
            if child.outcome > max_outcome:
                max_outcome = child.outcome
                max_child = child
        return max_child.model

    def get_action_probabilities(self):
        """
        Gets the nodes and probabilities as tuples from the root.
        :return: Returns a list of (node, probability, description) tuples from the root.
        """
        outcome_sum = 0
        max_outcome = 0
        for child in self.root.children:
            outcome_sum += child.outcome
            max_outcome = max(max_outcome, abs(child.outcome))
        outcome_probs = []
        for child in self.root.children:
            prob = (max_outcome + child.outcome) / (outcome_sum + max_outcome * len(self.root.children)) if outcome_sum != 0 else 1 / len(self.root.children)
            outcome_probs.append((child.outcome, prob, child.description))
        return sorted(outcome_probs, key=lambda o: o[1])


class MonteCarloNode:

    def __init__(self, model=None, outcome=0, description=""):
        """
        Initializes a MonteCarloNode.
        :param model: The model to use.
        :param outcome: The total outcome of all children of this node.
        :param description: The description of the action at the node.
        """
        self.model = model
        self.outcome = outcome
        self.children = []
        self.description = description

    def add_child(self, node):
        """
        Add a child to the node.
        :param node: The node to add.
        """
        self.children.append(node)

    def __str__(self):
        """
        Converts the node to a string.
        :return: The string version of the node.
        """
        return str(self.description, self.outcome)


def make_tree(player: Player, other_player: Player):
    """
    Creates a MonteCarloTree of actions for the given battle.
    :param player: The player to find actions for.
    :param other_player: The opposing player.
    :return: A MonteCarloTree.
    """

    # Make other model be entirely random
    other_player.model = RandomModel

    # Create tree
    tree = MonteCarloTree()
    root = tree.root

    def next_turn(node: MonteCarloNode, player: Player, other_player: Player, did_just_switch=False):

        # Get currently battling Pokemon
        pokemon = player.party.get_starting()

        # Add attack-move nodes
        for attack in pokemon.move_bank.moves:
            if attack.pp == 0:
                continue

            # Create an attacking model
            model = RandomModel
            def take_turn(_: Player, __: Player, do_move: Callable[[Move], None], ___: Callable[[Item], None], ____: Callable[[int], None]):
                do_move(attack)
            model.take_turn = take_turn

            # Add the attack node
            node.add_child(MonteCarloNode(model, 0, "%s used %s." % (pokemon.name, attack.name)))

        # Add switch-move nodes
        if not did_just_switch:
            for i, switch_pokemon in enumerate(player.party.pokemon_list):
                if switch_pokemon.hp == 0 or i == 0:
                    continue

                # Create a switching model
                model = RandomModel
                def take_turn(_: Player, __: Player, ___: Callable[[Move], None], ____: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]):
                    switch_pokemon_at_idx(i)
                model.take_turn = take_turn
                model.force_switch_pokemon = lambda _: i

                # Add the attack node
                node.add_child(MonteCarloNode(model, 0, "Switched %s with %s." % (pokemon.name, switch_pokemon.name)))

        # Recur through children
        for child in node.children:
            player.model = child.model

            temp_player = deepcopy(player)
            temp_other_player = deepcopy(other_player)

            battle = Battle(temp_player, temp_other_player, 1)
            winner = battle.play_turn()

            # Get battle outcome
            if winner is not None:
                outcome = calculations.outcome_func_v1(player, other_player)
                # print("%s won with outcome %1.5f" % (winner.name, outcome))
                child.outcome = outcome
            else:
                next_turn(child, battle.player1, battle.player2, not did_just_switch)

    def calculate_recursive_outcomes(node: MonteCarloNode):
        cumulative_outcome = 0
        for child in node.children:
            cumulative_outcome += calculate_recursive_outcomes(child)
        cumulative_outcome += node.outcome
        node.outcome = cumulative_outcome
        return cumulative_outcome

    next_turn(root, player, other_player)
    calculate_recursive_outcomes(root)

    return tree


if __name__ == "__main__":

    party1 = get_random_party(1)
    party2 = get_random_party(1)

    player1 = Player("Player 1", party1, None, RandomModel)
    player2 = Player("Player 2", party2, None, RandomModel)

    tree = make_tree(player1, player2)
    # tree.pre_order_print()

    # print("Next move: %s" % tree.get_next_action().description)
    outcome_probs = tree.get_action_probabilities()
    print("%s vs. %s" % (party1.get_starting().name, party2.get_starting().name))
    for prob in outcome_probs:
        print("Outcome: %1.4f, Prob: %1.4f, Move: %s" % prob)
