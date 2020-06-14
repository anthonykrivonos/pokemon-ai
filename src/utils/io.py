import os, sys, console
from typing import *
from enum import Enum
from os.path import join, dirname

sys.path.append(join(dirname(__file__), '../..'))

# Alignment constants
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

# The height of the battle screen when printed
BATTLE_SCREEN_HEIGHT = 9


##
# Alignment
##

class Align(Enum):
    """
    The direction to align text.
    """
    LEFT = 0
    CENTER = 1
    RIGHT = 2


def align(text: str, align: Align = Align.LEFT, width: int = 100):
    """
    Align the text within a certain width LEFT, CENTER, or RIGHT.
    :param text: The text to align.
    :param align: The alignment direction.
    :param width: The total width of the text to align.
    :return: The aligned text string.
    """
    if align is Align.LEFT:
        text = text.ljust(width, ' ')
    elif align is Align.RIGHT:
        text = text.rjust(width, ' ')
    elif align is Align.RIGHT:
        text = text.center(width, ' ')
    return text


def split_align(lhs, rhs, width=100, align_lhs=Align.LEFT, align_rhs=Align.RIGHT):
    """
    Align two different strings within a width.
    :param lhs: The left-hand-side text.
    :param rhs: The right-hand-side text.
    :param width: The total width of the text to align.
    :param align_lhs: The alignment direction of the left-hand-side text.
    :param align_rhs: The alignment direction of the right-hand-side text.
    :return:
    """
    left = align(lhs, align_lhs, int(width / 2))
    right = align(rhs, align_rhs, int(width / 2) + (1 if width % 2 > 0 else 0))
    return left + right


##
# String Manipulation
##


def repeat(val: str, width: int):
    """
    Repeat the value a certain number of times within a width.
    :param val: The value to repeat.
    :param width: The width of the output string.
    :return: The value repeated within a given width.
    """
    return ''.join([val for _ in range(0, int(width / len(val)))])


##
# Terminal Manipulation
##

def clear(n: int = 1):
    """
    Clears the last 1 or n line(s) of text.
    :param n: The number of lines to clear.
    """
    if n == 1:
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        for i in range(n + 1 if n > 1 else 1):
            print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)


def get_terminal_dimensions() -> (int, int):
    """
    Returns the width and the height of the terminal window in characters, as a tuple.
    :return:
    """
    return os.get_terminal_size(0)


##
# Battle Screen
##


def print_battle_screen(player, other_player, screen_width=None):
    """
    Prints a battle screen.
    :param player: The current player who the battle screen is focused on.
    :param other_player: The other player.
    :param screen_width: The width of the terminal.
    """
    screen_width = screen_width if screen_width is not None else get_terminal_dimensions()[0]

    pokemon = player.party.get_starting()
    other_pokemon = other_player.party.get_starting()
    txt_player_name = lambda plyr, aln: align(plyr.name.upper(), aln, screen_width)
    txt_pokemon_top = lambda pkmn: split_align(pkmn.name, 'Lv' + str(pkmn.level), screen_width)
    txt_pokemon_bottom = lambda pkmn: split_align(str(pkmn.hp) + '/' + str(pkmn.base_hp) + ' HP',
                                                  '' if pkmn.status is None else pkmn.status.name,
                                                  screen_width)
    print("\n", end="\r", flush=True)
    print(repeat('=', screen_width))
    print(txt_player_name(other_player, Align.RIGHT))
    print(txt_pokemon_top(other_pokemon))
    print(txt_pokemon_bottom(other_pokemon))

    print(repeat('-', screen_width))

    print(txt_player_name(player, Align.LEFT))
    print(txt_pokemon_top(pokemon))
    print(txt_pokemon_bottom(pokemon))

    print(repeat('=', screen_width))


def clear_battle_screen():
    """
    Clears the last (battle screen height) number of lines.
    """
    clear(BATTLE_SCREEN_HEIGHT)


##
# Input
##


def okay(message: str, print_after=False):
    """
    Prints a message with only a required "OK" response afterward.
    :param message: The message to print.
    :param print_after: Should the message persist?
    """
    input(message + " [Okay]")
    clear(1)
    if print_after:
        print(message)


def prompt(message: str) -> str:
    """
    Prompts the user.
    :param message: The message prompt.
    :return: The response to the input.
    """
    return input(message + "\n > ")


def prompt_multi(message: str, *choices: List[str]) -> (int, str):
    """
    Prompts the user with a message and a list of options.
    :param message: A string message.
    :param choices: String list of choices.
    :return: Returns a tuple containing the index of the choice and its value.
    """
    choice = None
    while choice is None:
        try:
            choice = input(message + "\n" + "\n".join(
                map(lambda x: ("  [" + str(x[0] + 1) + "] " + x[1]), enumerate(choices))) + "\n > ")
            choice_no = int(choice)
            if choice_no is None or choice_no > len(choices) or choice_no < 1:
                choice = None
            else:
                choice = choice_no - 1
        except:
            choice = None
        clear(len(choices) + 1)
    return choice, choices[choice]
