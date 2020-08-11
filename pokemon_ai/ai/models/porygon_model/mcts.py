from typing import *

from pptree import print_tree

from pokenet.battle import Battle
from pokenet.classes import Item, Move, Player, Pokemon
from pokenet.utils import calculations
from .models import MonteCarloActionType
from .predictor import Predictor
from ..damage_model import DamageModel
from ..random_model import RandomModel

class MonteCarloNode:

    def __init__(self, player: Player, other_player: Player, player_id: int = 0, action_type: MonteCarloActionType = -1,
                 action_descriptor: Union[int, str] = 1, model: RandomModel = None, outcome=0, description="", visits=0, depth=0):
        """
        Initializes a MonteCarloNode.
        :param player_id: The ID of the player performing this action.
        :param player: Node player.
        :param other_player: Node other player.
        :param action_type: The type of action taken by this node.
        :param action_descriptor: The index of the action taken by this node.
        :param model: The model to use.
        :param outcome: The total outcome of all children of this node.
        :param description: The description of the action at the node.
        """
        self.player_id = player_id
        self.player = player
        self.other_player = other_player
        self.action_type = action_type
        self.action_descriptor = action_descriptor
        self.model = model
        self.outcome = outcome
        self.parent = None
        self.children: List[MonteCarloNode] = []
        self.childrenMap = {}
        self.description = description
        self.depth = depth
        self.visits = visits
        self.token = ''

    def visit(self):
        """
        Visits this node.
        """
        self.visits += 1

    def get_child(self, pokemon: Pokemon, action_type: MonteCarloActionType, action_descriptor: int):
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

    def has_child(self, pokemon: Pokemon, action_type: MonteCarloActionType, action_descriptor: int):
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
        node.parent = self
        token = self._tokenize_child(pokemon, node.action_type)
        node.token = token
        self.children.append(node)
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
        return "%d-%s" % (pokemon.get_id(), action_type.name)

    def detokenize_child(self) -> int:
        """
        Returns the Pokemon ID of Pokemon associated with the node.
        :return: The ID of the Pokemon.
        """
        return int(self.token.split('-')[0])

    def __str__(self):
        """
        Converts the node to a string.
        :return: The string version of the node.
        """
        return str((self.description, self.outcome, self.visits, self.player.get_party().get_starting().get_name(), self.player.get_party().get_starting().get_hp(), self.other_player.get_party().get_starting().get_name(), self.other_player.get_party().get_starting().get_hp()))


class MonteCarloTree:

    def __init__(self, player, other_player):
        """
        Initializes a MonteCarloTree.
        """
        self.root = MonteCarloNode(player, other_player)

    def print(self):
        """
        Print the tree using pptree's print_tree.
        """
        print_tree(self.root, "children")

    def get_next_action(self):
        """
        Decides the next action to take from the root.
        :return: Returns the model for the next action to take.
        """
        max_outcome = -1
        max_child = None
        for child in self.root.children:
            if child.outcome > max_outcome:
                max_outcome = child.outcome
                max_child = child
        return max_child.model

    def get_action_probabilities(self):
        """
        Gets the nodes and probabilities as tuples from the root.
        :return: Returns a list of (node, probability, visits, description) tuples from the root.
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
            outcome_probs.append((child.outcome, prob, child.visits, child.description))
        return sorted(outcome_probs, key=lambda o: o[1])


def make_tree(player_real: Player, other_player_real: Player, num_plays=1, predictor: Predictor = None, learning_turns: int = 10, use_damage_model=False, verbose=False):
    """
    Creates a MonteCarloTree of actions for the given battle.
    :param player_real: The player to find actions for.
    :param other_player_real: The opposing player.
    :param num_plays: The number of Monte Carlo simulations to perform.
    :param predictor: An optional neural network to weigh he training.
    :param learning_turns: Number of turns the model will learn before making decisions.
    :param use_damage_model: Use the DamageModel?
    :param verbose: Should the algorithm announce its current actions?
    :return: A MonteCarloTree.
    """

    # Create tree
    tree = MonteCarloTree(player_real.copy(), other_player_real.copy())
    root = tree.root
    root.player.set_model(RandomModel())
    root.other_player.set_model(RandomModel() if not use_damage_model else DamageModel())
    root.depth = 1
    root.description = 'Battle Start'

    # Use workaround to pass this to children
    current_learning_turn = [0]

    # Play num_plays amount of times
    for current_num_plays in range(num_plays):
        def backprop(node: MonteCarloNode, outcome: float) -> None:
            """
            Backpropogates and updates all nodes from the top node using the sums of the leaf nodes.
            Included logic to add wins for respective player
            :param node: The leaf node to start backpropgating from
            :param outcome: The calculated outcome
            """
            if node.depth % 2 == 0 or node.depth == 1:
                node.outcome += outcome
            else:
                node.outcome += (1 - outcome)
            node.visit()
            if node.parent is not None:
                backprop(node.parent, outcome)

        def create_node(node_player: Player, node_other_player: Player, action_type: MonteCarloActionType, index: int) -> MonteCarloNode:
            """
            Creates an attack or switch node.
            :param node_player: The current player object for the node.
            :param action_type: Either MonteCarloActionType.ATTACK or MonteCarloActionType.SWITCH.
            :param index: The index of the attack or Pokemon to switch to.
            """
            # The currently battling pokemon
            pokemon = node_player.get_party().get_starting()

            # Create action descriptor
            if action_type == MonteCarloActionType.ATTACK:
                attack = pokemon.get_move_bank().get_move(index)
                action_descriptor = index
                description = "%s used %s." % (pokemon.get_name(), attack.get_name())
            else:
                switch_pokemon = node_player.get_party().get_at_index(index)
                action_descriptor = switch_pokemon.get_id()
                description = "%s switched out with %s." % (pokemon.get_name(), switch_pokemon.get_name())

            # Create the "turn" to be taken when this node is visited
            if action_type == MonteCarloActionType.ATTACK:
                def take_turn(_: Player, __: Player, do_move: Callable[[Move], None], ___: Callable[[Item], None],
                              ____: Callable[[int], None]):
                    do_move(attack)
            else:
                def take_turn(_: Player, __: Player, ___: Callable[[Move], None], ____: Callable[[Item], None],
                              switch_pokemon_at_idx: Callable[[int], None]):
                    switch_pokemon_at_idx(index)

            model = RandomModel()
            model.take_turn = take_turn

            # Return the move node
            return MonteCarloNode(node_player.copy(), node_other_player.copy(), node_player.get_id(), action_type, action_descriptor, model, 0, description)

        def insert_node(node: MonteCarloNode, parent: MonteCarloNode) -> MonteCarloNode:
            """
            Adds an attack or switch move node to a tree.
            :param node: The current node.
            :param parent: The parent node..
            """
            pokemon = node.player.get_party().get_starting()
            child_exists = parent.has_child(pokemon, node.action_type, node.action_descriptor)

            if not child_exists:
                child = node
                parent.add_child(child, pokemon)
            else:
                child = parent.get_child(pokemon, node.action_type, node.action_descriptor)

            if node.depth % 2 == 1:
                # If on an odd depth, simulate a turn and update the node's state (players).
                node.player.set_model(node.model)
                node.other_player.set_model(parent.model)

                battle = Battle(node.player, node.other_player, 1 if verbose else 0)
                winner = battle.play_turn()

                # Get turn outcome
                if winner is not None and predictor is not None:
                    # Train the predictor
                    predictor.train_model(root, player, other_player)
                    current_learning_turn[0] += 1

            return child

        def traverse(node: MonteCarloNode) -> MonteCarloNode:
            """
            If the node is not fully expanded, pick one of the unvisited children.
            Else, pick the child node with greatest UCT value. If this child node is also
            fully expanded, repeat process.
            """

            def fully_expanded(node: MonteCarloNode):
                if node.depth == 1:
                    c_player = node.player.copy()
                    c_other_player = node.other_player.copy()
                else:
                    c_player = node.other_player.copy()
                    c_other_player = node.player.copy()

                pokemon = c_player.get_party().get_starting()

                # Creates all children for node if they do not already exist, and checks visit (0 is unvisited)
                attacks = list(filter(lambda m: m[0].is_available(),
                                      [(move, i) for i, move in enumerate(pokemon.get_move_bank().get_as_list())]))
                for _, attack_idx in attacks:
                    child = create_node(c_player, c_other_player, MonteCarloActionType.ATTACK, attack_idx)
                    insert_node(child, node)

                switches = list(filter(lambda p: not p[0].is_fainted(),
                                       [(pkmn, i) for i, pkmn in enumerate(node.player.get_party().get_as_list())]))[1:]
                for _, switch_idx in switches:
                    child = create_node(c_player, c_other_player, MonteCarloActionType.SWITCH, switch_idx)
                    insert_node(child, node)

                return all([child.visits > 0 for child in node.children])

            def best_uct_node(node: MonteCarloNode) -> MonteCarloNode:
                uct_values = []
                for child in node.children:
                    uct_values.append(calculations.upper_confidence_bounds(child.outcome, child.visits, node.visits))
                index_of_best_move = uct_values.index(max(uct_values))
                return node.children[index_of_best_move]

            def pick_unvisited(node: MonteCarloNode) -> MonteCarloNode:
                for child in node.children:
                    if child.visits == 0:
                        return child
                return None

            # Adds the opponents moves as child nodes to player's moves (MCT will calculate best move for both sides)
            while fully_expanded(node):
                node = best_uct_node(node)

            return pick_unvisited(node) or node

        # -------------------------
        # START OF ACTUAL ALGORITHM
        # -------------------------
        # Traverse and find the leaf to recur from
        leaf = traverse(root)

        # If the leaf has an even depth, the opponent has yet to chose a move. Thus, set the opp's model to random and
        # take a turn. Then continue to randomly simulate the rest of the battle.
        if leaf.depth % 2 == 0:
            # Even depth also indicates the player is player 1.
            player = leaf.player.copy()
            other_player = leaf.other_player.copy()

            # Adding a move for opponent and taking a turn.
            player.set_model(leaf.model)
            other_player.set_model(RandomModel() if not use_damage_model else DamageModel())

            battle = Battle(player, other_player, 1 if verbose else 0)
            winner = battle.play_turn()

            if winner is None:
                if predictor is not None and current_learning_turn[0] < learning_turns:
                    player.set_model(RandomModel())
                else:
                    model, _, _, _, _ = predictor.predict_move(player, other_player)
                    player.set_model(model)
                battle.play()
        else:
            # Odd depth indicates player is player 2.
            player = leaf.other_player.copy()
            other_player = leaf.player.copy()

            if predictor is not None and current_learning_turn[0] < learning_turns:
                player.set_model(RandomModel())
            else:
                model, _, _, _, _ = predictor.predict_move(player, other_player)
                player.set_model(model)

            other_player.set_model(RandomModel() if not use_damage_model else DamageModel())

            battle = Battle(player, other_player, 1 if verbose else 0)
            battle.play()

        outcome = calculations.outcome_func_v1(player, other_player)

        # On each run, calculate the outcomes via backpropagation
        backprop(leaf, outcome)

    return tree
