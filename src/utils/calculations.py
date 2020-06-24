import sys
import math
from os.path import join, dirname

from .chance import random_pct, chance
from src.models import Pokemon, Move, Effectiveness, PokemonType, Player

sys.path.append(join(dirname(__file__), '../..'))

##
# Move Calculations
##

def calculate_damage(move: Move, pokemon: Pokemon, on_pokemon: Pokemon) -> (int, Effectiveness, int):
    """
    Calculates a slightly random (due to
    critical hit, etc.) damage from the pokemon to the on_pokemon.
    :param move: The move pokemon attacks on_pokemon with.
    :param pokemon: The attacking Pokemon.
    :param on_pokemon: The defending Pokemon.
    :return: A tuple containing damage dealt, the level of effectiveness of the move, and a critical hit value (2 for critical hit, 1 for regular).
    """
    critical = chance(.0625, lambda: 2, lambda: 1)
    random = random_pct(85, 100)
    effectiveness = is_effective(pokemon.type, on_pokemon.type)
    modifier = critical * random * effectiveness.value
    attack = pokemon.stats.special_attack if move.is_special else pokemon.stats.attack
    defense = pokemon.stats.special_defense if move.is_special else pokemon.stats.defense
    damage = max(0, int(((((((2 * pokemon.level) / 5) + 2) * move.base_damage * (attack / defense)) / 50) + 2) * modifier))
    damage = damage if damage < on_pokemon.hp else on_pokemon.hp
    return damage, effectiveness, critical


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
# Math
##

def outcome_func_v1(player: Player, opponent: Player) -> float:
    """
    Calculates the outcome value between (-1 and +1) for use in Monte Carlo Tree Search.
    :param player: The current player.
    :param opponent: The opposing player.
    :return: An outcome value between -1 and +1. +1 denotes a strong win, -1 denotes a bad loss.
    """
    # Calculate HP differences and fainted pokemon
    player_total_hp, opp_total_hp = 0, 0
    hp_taken, hp_dealt = 0, 0
    player_fainted_count, opp_fainted_count = 0, 0
    for pokemon in player.party.pokemon_list:
        player_total_hp += pokemon.base_hp
        hp_taken += pokemon.base_hp - pokemon.hp
        player_fainted_count += int(pokemon.hp == 0)
    for pokemon in opponent.party.pokemon_list:
        opp_total_hp += pokemon.base_hp
        hp_dealt += pokemon.base_hp - pokemon.hp
        opp_fainted_count += int(pokemon.hp == 0)

    # Outcome = %hp_dealt - %hp_taken + %pokemon_killed - (%pokemon_fainted)^2
    hp_perc_diff = hp_dealt / opp_total_hp - hp_taken / player_total_hp
    pokemon_fainted_perc_diff = opp_fainted_count / len(opponent.party.pokemon_list) - (player_fainted_count / len(player.party.pokemon_list))**2
    outcome = hp_perc_diff + pokemon_fainted_perc_diff

    return outcome
