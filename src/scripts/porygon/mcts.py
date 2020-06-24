from typing import *
from copy import deepcopy

from src.models import Player, Move, Item
from src.battle import Battle
from src.utils import calculations
from src.ai import RandomModel, MonteCarloRandomModel, ModelInterface, MonteCarloActionType
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

    def visit(self):
        """
        Visits this node.
        """
        self.visits += 1

    def get_child(self, action_type:MonteCarloActionType, action_index:int):
        """
        Is this node a child of the current node?
        :param action_type: The type of the action of the child.
        :param action_index: The index of the action of the child.
        :return: Returns the child with the specified action_type and action_index.
        """
        if self.has_child(action_type, action_index):
            child_index = self.childrenMap[action_type][action_index]
            return self.children[child_index]
        return None

    def has_child(self, action_type:MonteCarloActionType, action_index:int):
        """
        Is this node a child of the current node?
        :param action_type: The type of the action of the child.
        :param action_index: The index of the action of the child.
        :return: Returns true if the provided node is a child of the current node.
        """
        return action_type in self.childrenMap and action_index in self.childrenMap[action_type]

    def add_child(self, node):
        """
        Add a child to the node.
        :param node: The node to add.
        """
        self.children.append(node)
        node_index = len(self.children) - 1
        if node.action_type not in self.childrenMap:
            self.childrenMap[node.action_type] = { node.action_index: node_index }
        else:
            self.childrenMap[node.action_type][node.action_index] = node_index

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
    :return: A MonteCarloTree.
    """

    # Make both models random
    player.model = RandomModel
    other_player.model = RandomModel

    # Create tree
    tree = MonteCarloTree()
    root = tree.root
    root.description = 'Battle Start'

    # Keep track of nodes being added into the tree
    tree_queue = [(root, player, other_player)]

    while len(tree_queue) > 0:
        # Store useful variables
        node, node_player, node_other_player = tree_queue[0]

        pokemon = player.party.get_starting()
        # Pop the node from the queue
        del tree_queue[0]

        # Battle if on an even layer
        if node.player_id == player.id:
            # Simulate the battle
            battle = Battle(node_player, node_other_player, 0)
            winner = battle.play_turn()
            # Get battle outcome
            if winner is not None:
                # We assume that player 1 goes second, since should_perform_battle is true on even layers
                outcome = calculations.outcome_func_v1(player, other_player)
                node.outcome = outcome
                print("%s won" % winner.name)
                continue

        # Add attack actions
        for i, attack in enumerate(pokemon.move_bank.moves):
            if attack.pp == 0:
                continue

            if not node.has_child(MonteCarloActionType.ATTACK, i):
                # Make the bot attack on this child's turn
                model = RandomModel
                def take_turn(_: Player, __: Player, do_move: Callable[[Move], None], ___: Callable[[Item], None], ____: Callable[[int], None]):
                    do_move(attack)
                model.take_turn = take_turn

                # Add the attack node
                child = MonteCarloNode(player.id, MonteCarloActionType.ATTACK, i, model, 0, "%s used %s." % (pokemon.name, attack.name))
                node.add_child(child)
            else:
                # If the node has already been visited, visit it again
                child = node.get_child(MonteCarloActionType.ATTACK, i)
                child.visit()
            tree_queue.insert(0, (child, deepcopy(other_player), deepcopy(player)))

        # # Add switch actions
        # for i, switch_pokemon in enumerate(player.party.pokemon_list):
        #     if switch_pokemon.hp == 0 or i == 0:
        #         continue
        #
        #     if not node.has_child(MonteCarloActionType.SWITCH, i):
        #         # Make the bot switch on this child's turn
        #         model = RandomModel
        #         def take_turn(_: Player, __: Player, ___: Callable[[Move], None], ____: Callable[[Item], None], switch_pokemon_at_idx: Callable[[int], None]):
        #             switch_pokemon_at_idx(i)
        #         model.take_turn = take_turn
        #         model.force_switch_pokemon = lambda _: i
        #
        #         # Add the attack node
        #         child = MonteCarloNode(player.id, MonteCarloActionType.ATTACK, i, model, 0, "Switched %s with %s." % (pokemon.name, switch_pokemon.name))
        #         node.add_child(child)
        #     else:
        #         # If the node has already been visited, visit it again
        #         child = node.get_child(MonteCarloActionType.SWITCH, i)
        #         child.visit()
        #     tree_queue.insert(0, (child, deepcopy(other_player), deepcopy(player)))

    def calculate_recursive_outcomes(node: MonteCarloNode):
        cumulative_outcome = 0
        for child in node.children:
            cumulative_outcome += calculate_recursive_outcomes(child)
        cumulative_outcome += node.outcome
        node.outcome = cumulative_outcome
        return cumulative_outcome

    calculate_recursive_outcomes(root)

    return tree


if __name__ == "__main__":
    party1 = get_random_party(1)
    party2 = get_random_party(1)

    player1 = Player("Player 1", party1, None, RandomModel, id=1)
    player2 = Player("Player 2", party2, None, RandomModel, id=2)

    tree = make_tree(player1, player2, 1)
    tree.pre_order_print()

    # print("Next move: %s" % tree.get_next_action().description)
    outcome_probs = tree.get_action_probabilities()
    print("%s vs. %s" % (', '.join([pkmn.name for pkmn in party1.pokemon_list]), ', '.join([pkmn.name for pkmn in party2.pokemon_list])))
    for prob in outcome_probs:
        print("Outcome: %1.4f, Prob: %1.4f, Move: %s" % prob)
