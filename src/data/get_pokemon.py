import csv
import os 
import sys
import random

from typing import *
from os.path import join, dirname

from src.models import Party, Move, MoveBank, Pokemon, Stats, Status

sys.path.append(join(dirname(__file__), '../..'))


def get_pokemon(name_or_id: Union[int, str]) -> Pokemon:
    script_dir = os.path.dirname(__file__)
    rel_path = "pokemon.csv"
    abs_file_path = os.path.join(script_dir, rel_path)
    
    reader = csv.reader(open(abs_file_path, 'r'))
    pokemon = {}
    pokemon_names = []
    for row in reader:
        if len(row) != 0:
            pokemon[row[0]] = row
            pokemon_names.append(row[0])

    info = pokemon[name_or_id.lower()] if isinstance(name_or_id, str) else pokemon[pokemon_names[name_or_id]]

    type_map = {
        "normal": 0,
        "fighting": 1,
        "flying": 2,
        "poison": 3,
        "ground": 4,
        "rock": 5,
        "bug": 6,
        "ghost": 7,
        "steel": 8,
        "fire": 9,
        "water": 10,
        "grass": 11,
        "electric": 12,
        "psychic": 13,
        "ice": 14,
        "dragon": 15,
        "dark": 16,
        "fairy": 17
    }
    status_map = {
        "infatuation": 0,
        "confusion": 1,
        "sleep": 2,
        "poison": 3,
        "bad_poison": 4,
        "paralysis": 5,
        "freeze": 6,
        "burn": 7,
    }

    move_bank = []
    i = 9
    while i < 35:
        if info[i] != '':
            status = Status(status_map[info[i + 5]]) if info[i + 5] != "none" else None
            move_bank.append(Move(info[i], int(info[i + 1]), int(info[i + 2]), type_map[info[i + 3]], info[i + 4] is "special", int(info[i + 6]), status))
        i += 7

    return Pokemon(type_map[info[1]], info[0], int(info[2]), Stats(int(info[4]), int(info[6]), int(info[5]), int(info[7]), int(info[8])), MoveBank(move_bank), int(info[3]))


def get_random_pokemon() -> Pokemon:
    return get_pokemon(random.randint(1, 151))


def get_party(*names) -> Party:
    return Party([ get_pokemon(name) for name in names ])


def get_random_party(n=6) -> Party:
    return Party([ get_random_pokemon() for i in range(n) ])
