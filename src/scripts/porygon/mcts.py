from typing import *
from enum import Enum
from copy import deepcopy
from random import random, shuffle

from src.models import Player, Move, Item, Pokemon
from src.battle import Battle
from src.utils import calculations
from src.ai import RandomModel, ModelInterface
from src.data import get_party, get_random_party

class MonteCarloActionType(Enum):
    ATTACK = 0
    SWITCH = 1


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
            denom = outcome_sum + max_outcome * len(self.root.children)
            prob = (max_outcome + child.outcome) / denom if denom != 0 else 1 / len(self.root.children)
            outcome_probs.append((child.outcome, prob, child.description))
        return sorted(outcome_probs, key=lambda o: o[1])


class MonteCarloNode:

    def __init__(self, player_id: int=0, action_type:MonteCarloActionType=-1, action_index:int=1, model:ModelInterface=None, outcome=0, description=""):
        """
        Initializes a MonteCarloNode.
        :param player_id: The ID of the player performing this action.
        :param action_type: The type of action taken by this node.
        :param action_index: The index of the action taken by this node.
        :param model: The model to use.
        :param outcome: The total outcome of all children of this node.
        :param description: The description of the action at the node.
        """
        self.player_id = player_id
        self.action_type = action_type
        self.action_index = action_index
        self.model = model
        self.outcome = outcome
        self.children = []
        self.childrenMap = {}
        self.description = description
        self.visits = 1
        self.is_leaf = False

    def visit(self):
        """
        Visits this node.
        """
        self.visits += 1

    def get_child(self, pokemon: Pokemon, action_type: MonteCarloActionType, action_index:int):
        """
        Is this node a child of the current node?
        :param pokemon: The pokemon the node concerns.
        :param action_type: The type of the action of the child.
        :param action_index: The index of the action of the child.
        :return: Returns the child with the specified action_type and action_index.
        """
        token = self._tokenize_child(pokemon, action_type)
        if self.has_child(pokemon, action_type, action_index):
            node_index = self.childrenMap[token][action_index]
            return self.children[node_index]
        return None

    def has_child(self, pokemon: Pokemon, action_type: MonteCarloActionType, action_index: int):
        """
        Is this node a child of the current node?
        :param pokemon: The pokemon the node concerns.
        :param action_type: The type of the action of the child.
        :param action_index: The index of the action of the child.
        :return: Returns true if the provided node is a child of the current node.
        """
        token = self._tokenize_child(pokemon, action_type)
        return token in self.childrenMap and action_index in self.childrenMap[token]

    def add_child(self, node, pokemon: Pokemon):
        """
        Add a child to the node.
        :param pokemon: The pokemon the node concerns.
        :param node: The node to add.
        """
        self.children.append(node)
        token = self._tokenize_child(pokemon, node.action_type)
        node_index = len(self.children) - 1
        if token not in self.childrenMap:
            self.childrenMap[token] = {}
        self.childrenMap[token][node.action_index] = node_index

    @staticmethod
    def _tokenize_child(pokemon: Pokemon, action_type: MonteCarloActionType) -> str:
        """
        Tokenizes a pokemon and action type for keeping track of nodes.
        :param pokemon: A Pokemon.
        :param action_type: A MonteCarloActionType.
        :return: A tokenized string.
        """
        return pokemon.name + "-" + str(action_type)

    def __str__(self):
        """
        Converts the node to a string.
        :return: The string version of the node.
        """
        return str((self.description, self.outcome))


def make_tree(player: Player, other_player: Player, num_plays=1):
    """
    Creates a MonteCarloTree of actions for the given battle.
    :param player: The player to find actions for.
    :param other_player: The opposing player.
    :param num_plays: The number of Monte Carlo simulations to perform.
    :return: A MonteCarloTree.
    """

    # Make both models random
    player.model = RandomModel
    other_player.model = RandomModel

    # Create tree
    tree = MonteCarloTree()
    root = tree.root
    root.description = 'Battle Start'

    def calculate_recursive_outcomes(node: MonteCarloNode):
        cumulative_outcome = 0
        for child in node.children:
            cumulative_outcome += calculate_recursive_outcomes(child)
        cumulative_outcome += node.outcome
        node.outcome = cumulative_outcome
        return cumulative_outcome

    # Play num_plays amount of times
    for _ in range(num_plays):
        # Keep track of nodes being added into the tree
        tree_queue = [(root, player, other_player, 1)]

        while len(tree_queue) > 0:
            # Store useful variables
            node, node_player, node_other_player, depth = tree_queue[0]
            pokemon = node_player.party.get_starting()

            # Pop the node from the queue
            del tree_queue[0]

            # Battle if on an even layer
            if node != root and node.player_id == player.id:
                # Simulate the battle
                battle = Battle(node_player, node_other_player, 0)
                winner = battle.play_turn()
                # Get battle outcome
                if winner is not None:
                    # We assume that player 1 goes second, since should_perform_battle is true on even layers
                    outcome = calculations.outcome_func_v1(node_player, node_other_player)
                    node.outcome = outcome
                    node.is_leaf = True
                    continue

            # Decide whether to attack or switch
            num_moves = sum([int(move.pp > 0) for move in pokemon.move_bank.moves])
            num_switches = sum([int(pkmn.hp > 0) for pkmn in node_player.party.pokemon_list]) - 1  # Account for self

            move_threshold = num_moves / (num_moves + num_switches)
            perform_move = random() < move_threshold

            if perform_move:
                # Get a random move
                moves = list(filter(lambda m: m[0].pp > 0, [(move, i) for i, move in enumerate(deepcopy(pokemon.move_bank.moves))]))
                shuffle(moves)
                attack, i = moves[0]

                if not node.has_child(pokemon, MonteCarloActionType.ATTACK, i):
                    # Make the bot attack on this child's turn
                    model = RandomModel

                    def take_turn(_: Player, __: Player, do_move: Callable[[Move], None], ___: Callable[[Item], None],
                                  ____: Callable[[int], None]):
                        do_move(attack)

                    model.take_turn = take_turn

                    # Add the attack node
                    child = MonteCarloNode(node_player.id, MonteCarloActionType.ATTACK, i, model, 0,
                                           "%s used %s." % (pokemon.name, attack.name))
                    node.add_child(child, pokemon)
                else:
                    # If the node has already been visited, visit it again
                    child = node.get_child(pokemon, MonteCarloActionType.ATTACK, i)
                    child.visit()

                tree_queue.insert(0, (child, deepcopy(node_other_player), deepcopy(node_player), depth + 1))
            else:
                # Get a random pokemon
                party = list(filter(lambda p: p[0].hp > 0, [(pkmn, i) for i, pkmn in enumerate(deepcopy(node_player.party.pokemon_list[1:]))]))
                shuffle(party)
                switch_pokemon, i = party[0]

                if not node.has_child(pokemon, MonteCarloActionType.SWITCH, i):
                    # Make the bot switch on this child's turn
                    model = RandomModel

                    def take_turn(_: Player, __: Player, ___: Callable[[Move], None], ____: Callable[[Item], None],
                                  switch_pokemon_at_idx: Callable[[int], None]):
                        switch_pokemon_at_idx(i)

                    model.take_turn = take_turn
                    model.force_switch_pokemon = lambda _: i

                    # Add the attack node
                    child = MonteCarloNode(node_player.id, MonteCarloActionType.ATTACK, i, model, 0,
                                           "Switched %s with %s." % (pokemon.name, switch_pokemon.name))
                    node.add_child(child, pokemon)
                else:
                    # If the node has already been visited, visit it again
                    child = node.get_child(pokemon, MonteCarloActionType.SWITCH, i)
                    child.visit()
                tree_queue.insert(0, (child, deepcopy(node_other_player), deepcopy(node_player), depth + 1))

        # On each run, calculate the outcomes via backpropagation
        calculate_recursive_outcomes(root)

    return tree


if __name__ == "__main__":
    party1 = get_party('venonat')
    party2 = get_party('graveler')
    print("%s vs. %s" % (', '.join([pkmn.name for pkmn in party1.pokemon_list]), ', '.join([pkmn.name for pkmn in party2.pokemon_list])))

    player1 = Player("Player 1", party1, None, RandomModel, id=1)
    player2 = Player("Player 2", party2, None, RandomModel, id=2)

    tree = make_tree(player1, player2, 100)
    # tree.pre_order_print()

    # print("Next move: %s" % tree.get_next_action().description)
    outcome_probs = tree.get_action_probabilities()
    for prob in outcome_probs:
        print("Outcome: %1.4f, Prob: %1.4f, Move: %s" % prob)
