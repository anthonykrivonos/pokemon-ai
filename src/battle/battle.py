import sys
from typing import *
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.ai import ModelInterface

from src.models import Status, status_names, Player, Pokemon, PokemonType, Move, Effectiveness, Item
from src.utils import print_battle_screen, clear, clear_battle_screen, prompt_multi, okay, calculate_damage, chance, random_int, get_terminal_dimensions


class Battle:

    _PLAYER_1_ID = 1
    _PLAYER_2_ID = 2

    def __init__(self, player1: Player, player2: Player):
        self.attack_queue = []
        self.player1 = player1
        self.player2 = player2

    def start(self):
        """
        Starts a battle by running it in a loop while there is no winner.
        """
        self._battle_start(self.player1, self.player2)
        while True:
            # Start two turns
            for player, opponent in [[self.player1, self.player2], [self.player2, self.player1]]:
                print_battle_screen(player, opponent)
                self._turn_start(player)
                clear_battle_screen()
            # Perform attacks and get a winner
            did_win, winner = self._turn_perform_attacks(self.player1, self.player2)
            if did_win:
                # Winner!
                self._alert(winner.name + ' won!', self.player1, self.player2)
                return winner
            # End both players' turns and continue
            self._turn_end(self.player1)
            self._turn_end(self.player2)

    ##
    # Alert
    ##

    @staticmethod
    def _alert(message: str, *players: List[Player]):
        """
        Alert a message that non-AI users have to respond "OK" to.
        :param message: The message to write.
        :param players: The list of players to write the message to.
        """
        for player in players:
            if not player.is_ai:
                okay(message)
                break

    ##
    # Battle Functions
    ##

    def _battle_start(self, player1: Player, player2: Player):
        """
        Called when the battle is about to begin.
        :param player1: The first player.
        :param player2: The second player.
        """
        player1.id = self._PLAYER_1_ID
        player2.id = self._PLAYER_2_ID

        # Clear the terminal window
        clear(get_terminal_dimensions()[1])

    ##
    # Turn Functions
    ##

    def _turn_start(self, player: Player):
        """
        Called when the provided player's turn starts.
        :param player: The player whose turn it is.
        """
        turn_complete = False
        while not turn_complete:
            if not player.is_ai:
                pokemon = player.party.get_starting()
                move = prompt_multi('What will ' + player.name + '\'s ' + pokemon.name + ' do?',
                                    "Attack",
                                    "Bag",
                                    "Switch Pokemon",
                                    "End Battle"
                                    )[0]
            else:
                # AI player should make move decision based on provided objects.
                return self._turn_ai(player)
            if move is 0:
                turn_complete = self._turn_attack(player)
            elif move is 1:
                turn_complete = self._turn_bag(player)
            elif move is 2:
                turn_complete = self._turn_switch_pokemon(player)
            else:
                clear_battle_screen()
                self._alert(player.name + ' forfeits...', player)
                exit(0)

    def _turn_end(self, player: Player):
        """
        Called when a turn is about to end to inflict damage from statuses and other things.
        :param player: The player to perform the calculations on.
        :return: True if the player wins, False otherwise.
        """
        # Get the Pokemon that's currently out
        pokemon = player.party.get_starting()

        def self_inflict(base_damage: int):
            # Performs damage calculation for self-inflicted attacks
            damage = pokemon.stats.attack / base_damage
            defense = pokemon.stats.defense / base_damage * 1 / 10
            total_damage = min(max(1, (damage - defense)), pokemon.hp)
            pokemon.hp = pokemon.hp - total_damage
            if pokemon.hp is 0:
                self._alert(pokemon.name + ' fainted!', player)
                return not self._turn_switch_pokemon(player, False)
            return False

        if pokemon.other_status in [Status.POISON, Status.BAD_POISON, Status.BURN]:
            self._alert(pokemon.name + ' is ' + status_names[pokemon.status] + '.', player)

            pokemon.other_status_turns += 1
            if pokemon.other_status is Status.POISON:
                damage = int(pokemon.base_hp / 16)
                self._alert(pokemon.name + ' took ' + damage + ' damage from poison.', player)
                return self_inflict(damage)
            if pokemon.other_status is Status.BAD_POISON:
                damage = int(pokemon.base_hp * pokemon.other_status_turns / 16)
                self._alert(pokemon.name + ' took ' + damage + ' damage from poison.', player)
                return self_inflict(damage)
            elif pokemon.other_status is Status.BURN:
                damage = int(pokemon.base_hp / 8)
                self._alert(pokemon.name + ' took ' + damage + ' damage from its burn.', player)
                return self_inflict(damage)

        return False

    def _turn_ai(self, player: Player):
        """
        Let's the player's AI model perform the turn.
        :param player: The player the AI plays for.
        :return: True, always, as if the model knows what it's doing.
        """
        assert player.model is not None

        # Get the other player
        other_player = self.player2 if player.id == self._PLAYER_1_ID else self.player1

        # Create lambda functions to be used by the model
        attack_func = lambda move: self._turn_attack(player, move)
        use_item_func = lambda item: self._turn_bag(player, item)
        switch_pokemon_at_idx_func = lambda idx: self._turn_switch_pokemon(player, False, idx)

        # Take the turn using the model
        player.model.take_turn(player, other_player, attack_func, use_item_func, switch_pokemon_at_idx_func)

        return True

    def _turn_attack(self, player: Player, ai_move: Move = None):
        """
        Called when the player chooses to attack.
        :param player: The player who is attacking.
        :param ai_move: The move the AI is playing.
        :return: True if the player selected an attack, False if the player chooses to go back.
        """
        pokemon = player.party.get_starting()
        if not player.is_ai:
            move = None
            while move is None or move.pp is 0:
                move_idx = prompt_multi('Select a move.', 'None (Go back)',
                                        *[m.name + ': ' + PokemonType(m.type).name.lower().capitalize() + ', ' + str(
                                            m.pp) + '/' + str(m.base_pp) + ' PP' for m in pokemon.move_bank.moves])[0]
                if move_idx is 0:
                    return False
                move = pokemon.move_bank.get_move(move_idx - 1)
                if move.pp is 0:
                    self._alert("There's no PP left for this move!", player)
        elif ai_move is not None:
            move = ai_move
        else:
            return False

        self._enqueue_attack(player, move)
        return True

    def _turn_bag(self, player: Player, ai_item: Item = None):
        """
        Called when the player chooses to use a bag item.
        :param player: The player who is opening the bag.
        :param ai_item: The item the AI is using.
        :return: True if the player uses a bag item, False if the player chooses to go back.
        """
        pokemon = player.party.get_starting()
        if not player.is_ai:
            item = prompt_multi('Use which item?', 'None (Go back)',
                                *[i.name + " (" + i.description + ")" for i in player.bag.item_list])[0]
        elif ai_item is not None:
            item = ai_item
        else:
            item = 0

        if item is 0:
            return False

        item_idx = item - 1
        item = player.bag.item_list[item_idx]

        # Use the item and remove it from the player's bag
        print("%s used a %s." % (player.name, item.name))
        item.use(player, pokemon)
        player.bag.item_list.remove(item_idx)

        return True

    def _turn_switch_pokemon(self, player: Player, none_option=True, ai_pokemon_idx: int = None):
        """
        Called when the player must switch Pokemon.
        :param player: The player who is switching pokemon.
        :param none_option: Is the player allowed to go back? Aka, is there an option to choose "None"?
        :param ai_pokemon: The Pokemon the AI is switching out.
        :return: True if the player switches Pokemon, false otherwise.
        """
        current_pokemon = player.party.get_starting()
        can_switch_pokemon = len(list(filter(lambda hp: hp > 0, [p.hp for p in player.party.pokemon_list]))) != 0
        if not can_switch_pokemon:
            return False
        while True:
            if not player.is_ai:
                # Write the options out
                options = [p.name + " (" + str(p.hp) + "/" + str(p.base_hp) + " HP)" for p in player.party.pokemon_list]
                if none_option:
                    options.insert(0, 'None (Go back)')
                item = prompt_multi('Which Pokémon would you like to switch in?', *options)[0]

                # The player chooses "None"
                if none_option and item is 0:
                    return False

                # Get the Pokemon to switch in
                idx = item - bool(none_option)
                switched_pokemon = player.party.get_at_index(idx)

                if switched_pokemon.hp is 0:
                    print(switched_pokemon.name + ' has fainted.')
                elif idx is 0:
                    print(switched_pokemon.name + ' is currently in battle.')
                else:
                    print('Switched ' + current_pokemon.name + ' with ' + switched_pokemon.name + '.')
                    player.party.make_starting(idx)
                    return True
            elif ai_pokemon_idx is not None:
                switched_pokemon = player.party.get_at_index(ai_pokemon_idx)
                print('Switched ' + current_pokemon.name + ' with ' + switched_pokemon.name + '.')
                player.party.make_starting(ai_pokemon_idx)
            else:
                return False

    def _turn_perform_attacks(self, player_a: Player, player_b: Player) -> (bool, Player):
        """
        Dequeues and performs the attacks in the attack queue.
        :param player_a: The first player to perform attacks for.
        :param player_b: The second player to perform attacks for.
        :return: Returns a tuple containing whether or not a player won and, if so, which player?
        """
        for player, move in self.attack_queue:
            if player.id is player_a.id:
                if self._perform_attack(move, player_a, player_b):
                    return True, player_a
            elif player.id is player_b.id:
                if self._perform_attack(move, player_b, player_a):
                    return True, player_b
        self.attack_queue = []
        return False, None

    def _perform_attack(self, move: Move, player: Player, on_player: Player):
        """
        Performs a move by the starting Pokemon of player against the starting pokemon of on_player.
        :param move: The move player's Pokemon is performing.
        :param player: The player whose Pokemon is attacking.
        :param on_player: The player whose Pokemon is defending.
        :return: Returns True if player wins, False otherwise.
        """
        pokemon = player.party.get_starting()
        on_pokemon = on_player.party.get_starting()

        def confusion():
            base_damage = 40
            damage = pokemon.stats.attack / base_damage
            defense = pokemon.stats.defense / base_damage * 1 / 10
            total_damage = min(max(1, (damage - defense)), pokemon.hp)
            pokemon.hp = pokemon.hp - total_damage
            self._alert(pokemon.name + ' hurt itself in its confusion.', player, on_player)
            if pokemon.hp is 0:
                self._alert(pokemon.name + ' fainted!', player)
                return not self._turn_switch_pokemon(player, False)
            return False

        def paralysis():
            self._alert(pokemon.name + ' is unable to move.', player, on_player)

        def infatuation():
            self._alert(pokemon.name + ' is infatuated and is unable to move.', player, on_player)

        def freeze():
            self._alert(pokemon.name + ' is frozen solid.', player, on_player)

        def sleep():
            self._alert(pokemon.name + ' is fast asleep.', player, on_player)

        def try_attack():
            move.pp -= 1

            # Checks to see if the attack hit
            change_of_hit = pokemon.stats.accuracy / 100 * on_pokemon.stats.evasion / 100
            did_hit = chance(change_of_hit, True, False)

            if not did_hit:
                self._alert(pokemon.name + '\'s attack missed.', player, on_player)
                return False

            self._alert(pokemon.name + ' used ' + move.name + '!', player, on_player)

            # Calculate damage
            damage, effectiveness, critical = calculate_damage(move, pokemon, on_pokemon)

            # Describe the effectiveness
            if critical is 2 and effectiveness is not Effectiveness.NO_EFFECT:
                self._alert('A critical hit!', player, on_player)
            if effectiveness is Effectiveness.NO_EFFECT:
                self._alert('It has no effect on ' + on_pokemon.name + '.', player, on_player)
            if effectiveness is Effectiveness.SUPER_EFFECTIVE:
                self._alert('It\'s super effective!', player, on_player)
            if effectiveness is Effectiveness.NOT_EFFECTIVE:
                self._alert('It\'s not very effective...', player, on_player)

            self._alert(on_pokemon.name + ' took ' + str(damage) + ' damage.', player, on_player)

            # Lower the opposing Pokemon's HP
            on_pokemon.hp = max(0, on_pokemon.hp - damage)

            # If the move inflicts a status, perform the status effect
            if move.status:
                if move.status in [Status.POISON, Status.BAD_POISON, Status.BURN]:
                    on_pokemon.other_status = move.status
                    on_pokemon.other_status_turns = 0
                else:
                    on_pokemon.status = move.status
                    on_pokemon.status_turns = random_int(1, 7)
                self._alert(pokemon.name + ' was ' + status_names[move.status], player, on_player)

            # Check if the Pokemon fainted
            if on_pokemon.hp == 0:
                self._alert(on_pokemon.name + ' fainted!', player, on_player)
                return not self._turn_switch_pokemon(on_player, False)

            return False

        if pokemon.status not in [None, Status.POISON, Status.BAD_POISON, Status.BURN]:
            # If the Pokemon is inflicted by a status effect that impacts the chance of landing the attack,
            # perform the calculations.
            status = pokemon.status
            pokemon.status_turns = max(0, pokemon.status_turns - 1)
            if pokemon.status_turns is 0:
                pokemon.status = None
            self._alert(pokemon.name + ' is ' + status_names[status] + '.', player, on_player)
            if status is Status.CONFUSION:
                chance(1 / 3, lambda: confusion(), try_attack)
            elif status is Status.PARALYSIS:
                chance(0.25, lambda: paralysis(), try_attack)
            elif status is Status.INFATUATION:
                chance(0.5, lambda: infatuation(), try_attack)
            elif status is Status.FREEZE:
                freeze()
            elif status is Status.SLEEP:
                sleep()
        elif pokemon.status is None:
            # No status effect, attempt to attack
            return try_attack()

        return False

    ##
    # Queue Functions
    ##

    def _enqueue_attack(self, player: Player, move: Move):
        """
        Enqueues an attack to be done by the player, depending on the player's Pokemon's speed.
        :param player: The player whose starter Pokemon will be attacking.
        :param move: The move to attack with.
        """
        attack_tuple = (player, move)
        if len(self.attack_queue) is 0:
            self.attack_queue.append(attack_tuple)
        else:
            op_speed = self.attack_queue[0][0].party.get_starting().stats.speed
            self_speed = player.party.get_starting().stats.speed
            if op_speed > self_speed:
                self.attack_queue.append(attack_tuple)
            elif op_speed < self_speed:
                self.attack_queue.insert(0, attack_tuple)
            else:
                chance(0.5, lambda: self.attack_queue.append(attack_tuple),
                       lambda: self.attack_queue.insert(0, attack_tuple))
