import requests
import sys, csv, math
from random import shuffle
from os.path import join, dirname

sys.path.append(join(dirname(__file__), '../..'))

only_attack_moves = True
only_common_status = True

entry_list = []

pokemon_list = requests.get("https://pokeapi.co/api/v2/pokemon?limit=151&offset=0").json()["results"]

for pokemon in pokemon_list:
    name = pokemon["name"].capitalize()

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

    def stat_growth(pokemon_dict: dict):
        """
        Adjust a Pokemon's stats based on their base stats and level
        Formulas based on https://bulbapedia.bulbagarden.net/wiki/Statistic, Gen I & II
        :param pokemon: The pokemon in dictionary entry form
        """
        def round_down(n, decimals=0):
            multiplier = 10 ** decimals
            return math.floor(n * multiplier) / multiplier

        def other_stat_formula(stat: int):
            return round_down((stat * 2 * 100 / 100 ) + 5)

        level = pokemon_dict["Level"]

        pokemon_dict["HP"] = int(round_down((pokemon_dict["HP"] * 2 * level / 100) + level + 10))
        pokemon_dict["Attack"] = int(other_stat_formula(pokemon_dict["Attack"]))
        pokemon_dict["Sp_Attack"] = int(other_stat_formula(pokemon_dict["Sp_Attack"]))
        pokemon_dict["Defense"] = int(other_stat_formula(pokemon_dict["Defense"]))
        pokemon_dict["Sp_Defense"] = int(other_stat_formula(pokemon_dict["Sp_Defense"]))
        pokemon_dict["Speed"] = int(other_stat_formula(pokemon_dict["Speed"]))
    
    stat_growth(entry)

    moves = info["moves"]

    # code regarding move_len specifically for ditto, which has 0 moves
    move_len = 4 if len(moves) >= 4 else len(moves)

    # shuffle available moves before picking
    shuffle(moves)
   
    moveList = []
    i = 0
    for move in moves:
        if i == move_len:
            break

        move_info = requests.get(move["move"]["url"]).json()

        if only_attack_moves:
            if (move_info["power"] is None) or (move_info["power"] is 0):
                continue
        
        if only_common_status:
            common_status = ["none", "poison", "infatuation", "confusion", "sleep", "paralysis", "freeze", "burn"]
            if move_info["meta"]["ailment"]["name"] not in common_status:
                continue

        move_num = i + 1

        entry["Move_%d_Name" % move_num] = move["move"]["name"].capitalize()
        entry["Move_%d_Base_Damage" % move_num] = move_info["power"]
        entry["Move_%d_PP" % move_num] = move_info["pp"]
        entry["Move_%d_Type" % move_num] = move_info["type"]["name"]
        entry["Move_%d_Is_Special" % move_num] = move_info["damage_class"]["name"]
        entry["Move_%d_Status" % move_num] = move_info["meta"]["ailment"]["name"]
        entry["Move_%d_Base_Heal" % move_num] = move_info["meta"]["healing"]

        i += 1

    for i in range(4 - move_len):
        move_num = i + move_len
        entry["Move_%d_Name" % move_num] = ""
        entry["Move_%d_Base_Damage" % move_num] = ""
        entry["Move_%d_PP" % move_num] = ""
        entry["Move_%d_Type" % move_num] = ""
        entry["Move_%d_Is_Special" % move_num] = ""
        entry["Move_%d_Status" % move_num] = ""
        entry["Move_%d_Base_Heal" % move_num] = ""

    entry_list.append(entry)

# creates the csv in cwd (likely pokemon-ai) rather than /src/data, requires manual file moving
# (or goto the data folder to run this script)
try:
    with open('pokemon.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=entry_list[0].keys())
        writer.writeheader()
        for data in entry_list:
            writer.writerow(data)
except IOError:
    print("I/O error")
