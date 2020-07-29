import sys
from typing import *
from os.path import join, dirname
from math import sqrt, log

from .chance import random_pct, chance
from src.classes import Pokemon, Move, Effectiveness, PokemonType, Player, Criticality

sys.path.append(join(dirname(__file__), '../..'))


##
# Move Calculations
##

def calculate_damage(move: Move, pokemon: Pokemon, on_pokemon: Pokemon) -> (int, Effectiveness, Criticality):
    """
    Calculates a slightly random (due to
    critical hit, etc.) damage from the pokemon to the on_pokemon.
    :param move: The move pokemon attacks on_pokemon with.
    :param pokemon: The attacking Pokemon.
    :param on_pokemon: The defending Pokemon.
    :return: A tuple containing damage dealt, the level of effectiveness of the move, and a critical hit value (2 for critical hit, 1 for regular).
    """
    critical = chance(.0625, lambda: Criticality.CRITICAL, lambda: Criticality.NOT_CRITICAL)
    random = random_pct(85, 100)
    effectiveness = is_effective(move.get_type(), on_pokemon.get_type())
    modifier = critical.value * random * effectiveness.value
    attack = pokemon.get_stats().get_special_attack() if move.is_special() else pokemon.get_stats().get_attack()
    attack *= 1.5 if move.get_type() == pokemon.get_type() else 1  # STAB
    defense = on_pokemon.get_stats().get_special_defense() if move.is_special() else on_pokemon.get_stats().get_defense()
    damage = max(0, int(((((((2 * pokemon.get_level()) / 5) + 2) * move.get_base_damage() * (attack / defense)) / 50) + 2) * modifier))
    damage = damage if damage < on_pokemon.get_hp() else on_pokemon.get_hp()
    return damage, effectiveness, critical

def calculate_damage_deterministic(move: Move, pokemon: Pokemon, on_pokemon: Pokemon) -> (int, Effectiveness, Criticality):
    """
    Calculates deterministic damage from the pokemon to the on_pokemon.
    :param move: The move pokemon attacks on_pokemon with.
    :param pokemon: The attacking Pokemon.
    :param on_pokemon: The defending Pokemon.
    :return: A tuple containing damage dealt, the level of effectiveness of the move, and a critical hit value (2 for critical hit, 1 for regular).
    """
    critical = chance(0, lambda: Criticality.CRITICAL, lambda: Criticality.NOT_CRITICAL)
    random = random_pct(100, 100)
    effectiveness = is_effective(move.get_type(), on_pokemon.get_type())
    modifier = critical.value * random * effectiveness.value
    attack = pokemon.get_stats().get_special_attack() if move.is_special() else pokemon.get_stats().get_attack()
    defense = on_pokemon.get_stats().get_special_defense() if move.is_special() else on_pokemon.get_stats().get_defense()
    damage = max(0, int(((((((2 * pokemon.get_level()) / 5) + 2) * move.get_base_damage() * (attack / defense)) / 50) + 2) * modifier))
    damage = damage if damage < on_pokemon.get_hp() else on_pokemon.get_hp()
    return damage, effectiveness, critical


def upper_confidence_bounds(node_wins, node_visits, parent_visits, c=sqrt(2)) -> float:
    """
    Returns the UCB stat for Monte Carlo Search Tree (MCST) exploration.
    :param node_wins: Number of wins for the current node.
    :param node_visits: Number of visits for the current node.
    :param parent_visits: Number of visits for the parent node.
    :param c: The exploitation parameter.
    """
    return (node_wins / node_visits) + c * sqrt(log(parent_visits) / node_visits)


def is_effective(type: PokemonType, other_type: PokemonType) -> Effectiveness:
    """
    Returns the effectiveness of one type on the other type.
    :param type: The type to check effectiveness of.
    :param other_type: The type to compare effectiveness against.
    :return: An Effectiveness enum describing the effectiveness of the type.
    """

    # Normal
    if type is PokemonType.NORMAL:
        # Super-Effective:
        if other_type in []:  # Unreachable
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.GHOST:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.ROCK, PokemonType.STEEL]:
            return Effectiveness.NOT_EFFECTIVE
    # Fighting
    elif type is PokemonType.FIGHTING:
        # Super-Effective:
        if other_type in [PokemonType.NORMAL, PokemonType.ROCK, PokemonType.STEEL, PokemonType.ICE, PokemonType.DARK]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.GHOST:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.FLYING, PokemonType.POISON, PokemonType.BUG, PokemonType.PSYCHIC, PokemonType.FAIRY]:
            return Effectiveness.NOT_EFFECTIVE
    # Flying
    elif type is PokemonType.FLYING:
        # Super-Effective:
        if other_type in [PokemonType.FIGHTING, PokemonType.BUG, PokemonType.GRASS]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.ROCK, PokemonType.STEEL, PokemonType.ELECTRIC]:
            return Effectiveness.NOT_EFFECTIVE
    # Poison
    elif type is PokemonType.POISON:
        # Super-Effective:
        if other_type in [PokemonType.GRASS, PokemonType.FAIRY]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.STEEL:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.POISON, PokemonType.GROUND, PokemonType.ROCK, PokemonType.GHOST]:
            return Effectiveness.NOT_EFFECTIVE
    # Ground
    elif type is PokemonType.GROUND:
        # Super-Effective:
        if other_type in [PokemonType.POISON, PokemonType.ROCK, PokemonType.STEEL, PokemonType.FIRE, PokemonType.ELECTRIC]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.FLYING:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.BUG, PokemonType.GRASS]:
            return Effectiveness.NOT_EFFECTIVE
    # Rock
    elif type is PokemonType.ROCK:
        # Super-Effective:
        if other_type in [PokemonType.FLYING, PokemonType.BUG, PokemonType.FIRE, PokemonType.ICE]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.FIGHTING, PokemonType.GROUND, PokemonType.STEEL]:
            return Effectiveness.NOT_EFFECTIVE
    # Bug
    elif type is PokemonType.BUG:
        # Super-Effective:
        if other_type in [PokemonType.GRASS, PokemonType.PSYCHIC, PokemonType.DARK]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.FIGHTING, PokemonType.FLYING, PokemonType.POISON, PokemonType.GHOST, PokemonType.STEEL, PokemonType.FIRE, PokemonType.FAIRY]:
            return Effectiveness.NOT_EFFECTIVE
    # Ghost
    elif type is PokemonType.GHOST:
        # Super-Effective:
        if other_type in [PokemonType.GHOST, PokemonType.PSYCHIC]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.NORMAL:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type is PokemonType.DARK:
            return Effectiveness.NOT_EFFECTIVE
    # Steel
    elif type is PokemonType.STEEL:
        # Super-Effective:
        if other_type in [PokemonType.ROCK, PokemonType.ICE, PokemonType.FAIRY]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.STEEL, PokemonType.FIRE, PokemonType.WATER, PokemonType.ELECTRIC]:
            return Effectiveness.NOT_EFFECTIVE
    # Fire
    elif type is PokemonType.FIRE:
        # Super-Effective:
        if other_type in [PokemonType.BUG, PokemonType.STEEL, PokemonType.GRASS, PokemonType.ICE]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.ROCK, PokemonType.FIRE, PokemonType.WATER, PokemonType.DRAGON]:
            return Effectiveness.NOT_EFFECTIVE
    # Water
    elif type is PokemonType.WATER:
        # Super-Effective:
        if other_type in [PokemonType.GROUND, PokemonType.ROCK, PokemonType.FIRE]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.WATER, PokemonType.GRASS, PokemonType.DRAGON]:
            return Effectiveness.NOT_EFFECTIVE
    # Grass
    elif type is PokemonType.GRASS:
        # Super-Effective:
        if other_type in [PokemonType.GROUND, PokemonType.ROCK, PokemonType.WATER]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.FLYING, PokemonType.POISON, PokemonType.BUG, PokemonType.STEEL, PokemonType.FIRE, PokemonType.GRASS, PokemonType.DRAGON]:
            return Effectiveness.NOT_EFFECTIVE
    # Electric
    elif type is PokemonType.ELECTRIC:
        # Super-Effective:
        if other_type in [PokemonType.FLYING, PokemonType.WATER]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.GROUND:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.GRASS, PokemonType.ELECTRIC, PokemonType.DRAGON]:
            return Effectiveness.NOT_EFFECTIVE
    # Psychic
    elif type is PokemonType.PSYCHIC:
        # Super-Effective:
        if other_type in [PokemonType.FIGHTING, PokemonType.POISON]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.DARK:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.STEEL, PokemonType.PSYCHIC]:
            return Effectiveness.NOT_EFFECTIVE
    # Ice
    elif type is PokemonType.ICE:
        # Super-Effective:
        if other_type in [PokemonType.FLYING, PokemonType.GROUND, PokemonType.GRASS, PokemonType.DRAGON]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.STEEL, PokemonType.FIRE, PokemonType.WATER, PokemonType.ICE]:
            return Effectiveness.NOT_EFFECTIVE
    # Dragon
    elif type is PokemonType.DRAGON:
        # Super-Effective:
        if other_type is PokemonType.DRAGON:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type is PokemonType.FAIRY:
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type is PokemonType.STEEL:
            return Effectiveness.NOT_EFFECTIVE
    # Dark
    elif type is PokemonType.DARK:
        # Super-Effective:
        if other_type in [PokemonType.GHOST, PokemonType.PSYCHIC]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.FIGHTING, PokemonType.DARK, PokemonType.FAIRY]:
            return Effectiveness.NOT_EFFECTIVE
    # Fairy
    elif type is PokemonType.FAIRY:
        # Super-Effective:
        if other_type in [PokemonType.FIGHTING, PokemonType.DRAGON, PokemonType.DARK]:
            return Effectiveness.SUPER_EFFECTIVE
        # No Effect
        if other_type in []:  # Unreachable
            return Effectiveness.NO_EFFECT
        # Not Effective
        elif other_type in [PokemonType.POISON, PokemonType.STEEL, PokemonType.FIRE]:
            return Effectiveness.NOT_EFFECTIVE
    return Effectiveness.NORMAL


##
# Math Functions
##

def to_probs(nums: Union[List[float], List[int]]) -> List[float]:
    min_num = min(nums)
    # Floor to 0
    if min_num < 0:
        nums = [num + abs(min_num) for num in nums]
    # Divide by sum
    sum_num = sum(nums)
    nums = [num / sum_num for num in nums]
    return nums


def outcome_func_v1(player: Player, opponent: Player) -> float:
    """
    Calculates the outcome value on [0, 1] for use in Monte Carlo Tree Search.
    :param player: The current player.
    :param opponent: The opposing player.
    :return: An outcome value between 0 and 1. 1 denotes a strong win, 0 denotes a bad loss.
    """
    # Calculate HP differences and fainted pokemon
    player_total_hp, opp_total_hp = 0, 0
    hp_taken, hp_dealt = 0, 0
    player_fainted_count, opp_fainted_count = 0, 0
    for pokemon in player.get_party().get_as_list():
        player_total_hp += pokemon.get_base_hp()
        hp_taken += pokemon.get_base_hp() - pokemon.get_hp()
        player_fainted_count += int(pokemon.get_hp() == 0)
    for pokemon in opponent.get_party().get_as_list():
        opp_total_hp += pokemon.get_base_hp()
        hp_dealt += pokemon.get_base_hp() - pokemon.get_hp()
        opp_fainted_count += int(pokemon.get_hp() == 0)

    outcome = 0.2 if player_fainted_count == len(player.get_party().get_as_list()) else 0.8

    # Outcome = %hp_dealt - %hp_taken + %pokemon_killed - (%pokemon_fainted)^2
    hp_perc_diff = hp_dealt / opp_total_hp - hp_taken / player_total_hp
    pokemon_fainted_perc_diff = opp_fainted_count / len(opponent.get_party().get_as_list()) - (player_fainted_count / len(player.get_party().get_as_list())) ** 2
    scalar = (hp_perc_diff + pokemon_fainted_perc_diff) / 10

    return outcome + scalar
