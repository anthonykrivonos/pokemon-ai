import requests
import csv
import json
import os
from random import shuffle

entryList = []

pokemonList = requests.get("https://pokeapi.co/api/v2/pokemon?limit=151&offset=0").json()["results"]

for pokemon in pokemonList:
    name = pokemon["name"]

    info = requests.get(pokemon["url"]).json()

    type = info["types"][0]["type"]["name"]

    stats = [] # hp, attack, defense, sp atk, sp def, speed
    for i in range(6):
        stats.append((info["stats"][i]['base_stat']))

    # switch defense and sp. atk for proper formatting
    # stat order is now: hp, attack, sp atk, defense, sp def, speed
    stats[2], stats[3] = stats[3], stats[2]

    entry = {
        "Name": name.capitalize(),
        "Type": type,
        "Level": 100,
        "HP": stats[0],
        'Attack': stats[1], 
        'Sp_Attack': stats[2], 
        'Defense': stats[3], 
        'Sp_Defense': stats[4], 
        'Speed': stats[5]
    }

    # code regarding move_len specifically for ditto, which has 0 moves
    move_len = 4 if len(info["moves"]) >= 4 else len(info["moves"])

    # shuffle availible moves before picking
    moves = info["moves"]
    shuffle(moves)
    moves = moves[:move_len]
    moveList = []
    for i, move in enumerate(moves):
        move_info = requests.get(move["move"]["url"]).json()

        move_name = move["move"]["name"].capitalize()
        move_base_damage = move_info["power"]
        move_pp = move_info["pp"]
        move_type = move_info["type"]["name"]
        move_damage_class = move_info["damage_class"]["name"]
        move_base_heal = move_info["meta"]["healing"]
        move_status = move_info["meta"]["ailment"]["name"]

        move_num = i + 1

        entry["Move_%d_Name" % move_num] = move_name
        entry["Move_%d_Base_Damage" % move_num] = 0 if move_base_damage is None else move_base_damage
        entry["Move_%d_PP" % move_num] = move_pp
        entry["Move_%d_Type" % move_num] = move_type
        entry["Move_%d_Is_Special" % move_num] = move_damage_class
        entry["Move_%d_Status" % move_num] = move_status
        entry["Move_%d_Base_Heal" % move_num] = move_base_heal

    for i in range(4 - move_len):
        move_num = i + move_len
        entry["Move_%d_Name" % move_num] = ""
        entry["Move_%d_Base_Damage" % move_num] = ""
        entry["Move_%d_PP" % move_num] = ""
        entry["Move_%d_Type" % move_num] = ""
        entry["Move_%d_Is_Special" % move_num] = ""
        entry["Move_%d_Status" % move_num] = ""
        entry["Move_%d_Base_Heal" % move_num] = ""

    entryList.append(entry)

# creates the csv in cwd (likely pokemon-ai) rather than /src/data, requires manual file moving
# (or goto the data folder to run this script)
try:
    with open('pokemon.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=entryList[0].keys())
        writer.writeheader()
        for data in entryList:
            writer.writerow(data)
except IOError:
    print("I/O error")
