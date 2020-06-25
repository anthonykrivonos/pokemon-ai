from typing import *
from enum import Enum
from copy import deepcopy
from random import seed, random, shuffle

from src.models import Player, Move, Item, Pokemon
from src.battle import Battle
from src.utils import calculations
from src.ai.models.random_model import RandomModel
from src.data import get_party


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

    def __init__(self, player_id: int = 0, action_type: MonteCarloActionType = -1,
                 action_descriptor: Union[int, str] = 1, model: RandomModel = None, outcome=0, description="", visits=0, depth=0):
        """
        Initializes a MonteCarloNode.
        :param player_id: The ID of the player performing this action.
        :param action_type: The type of action taken by this node.
        :param action_descriptor: The index of the action taken by this node.
        :param model: The model to use.
        :param outcome: The total outcome of all children of this node.
        :param description: The description of the action at the node.
        """
        self.player_id = player_id
        self.action_type = action_type
        self.action_descriptor = action_descriptor
        self.model = model
        self.outcome = outcome
        self.parent = None
        self.children = []
        self.childrenMap = {}
        self.description = description
        self.depth = depth
        self.visits = visits

    def visit(self):
        """
        Visits this node.
        """
        self.visits += 1

    def get_child(self, pokemon: Pokemon, action_type: MonteCarloActionType, action_descriptor: Union[int, str]):
        """
        Is this node a child of the current node?
        :param pokemon: The pokemon the node concerns.
        :param action_type: The type of the action of the child.
        :param action_descriptor: The index of the action of the child.
        :return: Returns the child with the specified action_type and action_descriptor.
        """
        token = self._tokenize_child(pokemon, action_type)
        if self.has_child(pokemon, action_type, action_descriptor):
            node_index = self.childrenMap[token][action_descriptor]
            return self.children[node_index]
        return None

    def has_child(self, pokemon: Pokemon, action_type: MonteCarloActionType, action_descriptor: Union[int, str]):
        """
        Is this node a child of the current node?
        :param pokemon: The pokemon the node concerns.
        :param action_type: The type of the action of the child.
        :param action_descriptor: The index of the action of the child.
        :return: Returns true if the provided node is a child of the current node.
        """
        token = self._tokenize_child(pokemon, action_type)
        return token in self.childrenMap and action_descriptor in self.childrenMap[token]

    def add_child(self, node, pokemon: Pokemon):
        """
        Add a child to the node.
        :param pokemon: The pokemon the node concerns.
        :param node: The node to add.
        """
        node.depth = self.depth + 1
        self.children.append(node)
        node.parent = self
        token = self._tokenize_child(pokemon, node.action_type)
        node_index = len(self.children) - 1
        if token not in self.childrenMap:
            self.childrenMap[token] = {}
        self.childrenMap[token][node.action_descriptor] = node_index

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


def make_tree(player: Player, other_player: Player, num_plays=1, verbose=False):
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
    root.depth = 1
    root.description = 'Battle Start'

    # Play num_plays amount of times
    for current_num_plays in range(num_plays):

        # Keep track of nodes being added into the tree
        tree_queue = []

        def create_node(node_player: Player, action_type: MonteCarloActionType, index: int) -> MonteCarloNode:
            """
            Creates an attack or switch node.
            :param node_player: The current player object for the node.
            :param action_type: Either MonteCarloActionType.ATTACK or MonteCarloActionType.SWITCH.
            :param index: The index of the attack or Pokemon to switch to.
            """
            # The currently battling pokemon
            pokemon = node_player.party.get_starting()

            # Create action descriptor
            if action_type == MonteCarloActionType.ATTACK:
                attack = pokemon.move_bank.get_move(index)
                action_descriptor = index
                description = "%s used %s." % (pokemon.name, attack.name)
            else:
                switch_pokemon = node_player.party.get_at_index(index)
                action_descriptor = switch_pokemon.name
                description = "%s switched out with %s." % (pokemon.name, switch_pokemon.name)

            # Make the bot move on this child's turn
            model = RandomModel

            def take_turn(_: Player, __: Player, do_move: Callable[[Move], None], ___: Callable[[Item], None],
                          switch_pokemon_at_idx: Callable[[int], None]):
                if action_type == MonteCarloActionType.ATTACK:
                    do_move(attack)
                else:
                    switch_pokemon_at_idx(index)

            # Add switch logic
            model.take_turn = take_turn

            # Return the move node
            return MonteCarloNode(node_player.id, action_type, action_descriptor, model, 0, description)

        def insert_node(node: MonteCarloNode, parent: MonteCarloNode, node_player: Player, node_other_player: Player, visit=True) -> MonteCarloNode:
            """
            Adds an attack or switch move node to a tree.
            :param node: The current node.
            :param parent: The parent node.
            :param node_player: The player object at the current node.
            :param node_other_player: The other player object at the current node.
            """
            pokemon = node_player.party.get_starting()
            child_exists = parent.has_child(pokemon, node.action_type, node.action_descriptor)

            if not child_exists:
                child = node
                parent.add_child(child, pokemon)
            else:
                # If the node has already been visited, visit it again
                child = parent.get_child(pokemon, node.action_type, node.action_descriptor)

            # Visit the child
            if visit:
                child.visit()

            # Add them to the queue in switched order
            tree_queue.append((child, node_other_player.copy(), node_player.copy()))
            return child

        ### FIND THE LEAF 
        def traverse(node: MonteCarloNode) -> MonteCarloNode:
            """
            If the node is not fully expanded, pick one of the unvisited children.
            Else, pick the child node with greatest UCT value. If this child node is also
            fully expanded, repeat process. 
            """

            def fully_expanded(node):
                pokemon = player.party.get_starting()

                # Creates all children for node if they do not already exist, and checks visit (0 is unvisited)
                attacks = list(filter(lambda m: m[0].pp > 0, 
                                    [(move, i) for i, move in enumerate(pokemon.move_bank.moves)]))
                for _, attack_idx in attacks:
                    node_player = player.copy()
                    child = create_node(node_player, MonteCarloActionType.ATTACK, attack_idx)
                    insert_node(child, node, node_player, other_player.copy(), visit=False)

                switches = list(filter(lambda p: p[0].hp > 0,
                                        [(pkmn, i) for i, pkmn in enumerate(player.party.pokemon_list)]))[1:]
                for _, switch_idx in switches:
                    node_player = player.copy()
                    child = create_node(node_player, MonteCarloActionType.SWITCH, switch_idx)
                    insert_node(child, node, node_player, other_player.copy(), visit=False)

                return all([child.visits > 0 for child in node.children])

            def best_uct(node):
                uct_values = []
                for child in node.children:
                    uct_values.append(calculations.upper_confidence_bounds(child.outcome, child.visits, node.visits))
                index_of_best_move = uct_values.index(max(uct_values))
                return root.children[index_of_best_move]

            def pick_unvisited(node):
                for child in node.children:
                    if child.visits == 0:
                        return child
                return None

            while fully_expanded(node):
                node = best_uct(node)

            return pick_unvisited(node) or node

        # Traverse and find the leaf to recur from
        leaf = traverse(root)
        tree_queue.append((leaf, player.copy(), other_player.copy()))

        while len(tree_queue) > 0:
            # Store useful variables
            node, node_player, node_other_player = tree_queue[0]
            pokemon = node_player.party.get_starting()

            # Pop the node from the queue
            del tree_queue[0]

            # Battle if on an even layer
            if node != root and node.player_id == player.id:
                # Simulate the battle
                battle = Battle(node_player, node_other_player, 2 if verbose else 0)
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

            seed()
            move_threshold = num_moves / (num_moves + num_switches)
            perform_attack = random() < move_threshold

            if perform_attack:
                # Get a random move
                attacks = list(filter(lambda m: m[0].pp > 0,
                                      [(move, i) for i, move in enumerate(deepcopy(pokemon.move_bank.moves))]))
                shuffle(attacks)
                _, attack_idx = attacks[0]

                # Add attack
                insert_node(create_node(node_player, MonteCarloActionType.ATTACK, attack_idx), node, node_player, node_other_player)
            else:
                # Get a random pokemon
                party = list(filter(lambda p: p[0].hp > 0,
                                    [(pkmn, i) for i, pkmn in enumerate(deepcopy(node_player.party.pokemon_list))]))[1:]
                shuffle(party)
                _, switch_idx = party[0]

                # Add switch
                insert_node(create_node(node_player, MonteCarloActionType.SWITCH, switch_idx), node, node_player, node_other_player)

        def calculate_recursive_outcomes(node: MonteCarloNode) -> int:
            """
            Backpropogates and updates all nodes from the top node using the sums of the leaf nodes.
            :param node: The top/root node.
            :return: A cumulative outcome at a given stage.
            """
            cumulative_outcome = 0
            for child in node.children:
                cumulative_outcome += calculate_recursive_outcomes(child)
            cumulative_outcome += node.outcome
            node.outcome = cumulative_outcome
            return cumulative_outcome

        # On each run, calculate the outcomes via backpropagation
        calculate_recursive_outcomes(root)

    return tree


if __name__ == "__main__":
    party1 = get_party("magmar", "arcanine", "ninetales")
    party2 = get_party("bulbasaur", "butterfree", "ivysaur")
    print("%s vs. %s" % (', '.join([pkmn.name for pkmn in party1.pokemon_list]), ', '.join([pkmn.name for pkmn in party2.pokemon_list])))

    player1 = Player("Player 1", party1, None, RandomModel, id=1)
    player2 = Player("Player 2", party2, None, RandomModel, id=2)

    tree = make_tree(player1, player2, 100)
    # tree.pre_order_print()

    # print("Next move: %s" % tree.get_next_action().description)
    outcome_probs = tree.get_action_probabilities()
    for prob in outcome_probs:
        print("Outcome: %1.4f, Prob: %1.4f, Move: %s" % prob)
