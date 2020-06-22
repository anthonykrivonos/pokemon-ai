import csv
import os 
import sys
import random

from typing import *
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from src.models import Bag, Party, Player, Move, MoveBank, Pokemon, Stats, PokemonType

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

    typeMap = {
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

    for i, field in enumerate(info):
        print(i, field)

    return Pokemon(typeMap[info[1]], info[0], info[2], Stats(info[4], info[6], info[5], info[7], info[8]), 
            MoveBank([Move(info[9], info[10], info[11], typeMap[info[12]], info[13] is "special"),
                        Move(info[16], info[17], info[18], typeMap[info[19]], info[20] is "special"),
                        Move(info[23], info[24], info[25], typeMap[info[26]], info[27] is "special"),
                        Move(info[30], info[31], info[32], typeMap[info[33]], info[34] is "special"),
            ]),
            info[3])

def get_random_pokemon() -> Pokemon:
    return get_pokemon(random.randint(1, 152))

def get_party(*names) -> Party:
    return Party([ get_pokemon(name) for name in names ])

def get_random_party(n=6) -> Party:
    return Party([ get_random_pokemon() for i in range(n) ])
    
