import requests
import csv
import json
import os

entryList = []


csv_columns = ['Name','Type','Level', 'HP', 'Attack', 'Sp_Attack', 'Defense', 'Sp_Defense', 'Speed',
                'Move_1_Name', 'Move_1_Base_Damage', 'Move_1_PP', 'Move_1_Type', 'Move_1_Is_Special', 'Move_1_Base_Heal', 'Move_1_Status',
                'Move_2_Name', 'Move_2_Base_Damage', 'Move_2_PP', 'Move_2_Type', 'Move_2_Is_Special', 'Move_2_Base_Heal', 'Move_2_Status',
                'Move_3_Name', 'Move_3_Base_Damage', 'Move_3_PP', 'Move_3_Type', 'Move_3_Is_Special', 'Move_3_Base_Heal', 'Move_3_Status',
                'Move_4_Name', 'Move_4_Base_Damage', 'Move_4_PP', 'Move_4_Type', 'Move_4_Is_Special', 'Move_4_Base_Heal', 'Move_4_Status']



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
        "Name": name,
        "Type": type,
        "Level": 100,
        "HP": stats[0],
        'Attack': stats[1], 
        'Sp_Attack': stats[2], 
        'Defense': stats[3], 
        'Sp_Defense': stats[4], 
        'Speed': stats[5]
    }

    move_len = 4 if len(info["moves"]) >= 4 else len(info["moves"])

    moves = info["moves"][:move_len]
    moveList = []
    for i, move in enumerate(moves):
        move_info = requests.get(move["move"]["url"]).json()

        move_name = move["move"]["name"]
        move_base_damage = move_info["power"]
        move_pp = move_info["pp"]
        move_type = move_info["type"]["name"]
        move_damage_class = move_info["damage_class"]["name"]
        move_base_heal = move_info["meta"]["healing"]
        move_status = move_info["meta"]["ailment"]["name"]

        move_num = i + 1

        entry["Move_%d_Name" % move_num] = move_name
        entry["Move_%d_Base_Damage" % move_num] = move_base_damage
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

    print(name, "was good")

    entryList.append(entry)


try:
    with open('pokemon.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in entryList:
            print(data["Name"])
            writer.writerow(data)
except IOError:
    print("I/O error")
