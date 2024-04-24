import re
import pandas as pd
import json
import os


def parser(log_data):
    with open("../../../../data/movesB.json", 'r+') as movefile:
        moves = json.load(movefile)
        movefile.close()

    with open("../../../../data/pokedexB.json", 'r+') as pokedexfile:
        pokedex = json.load(pokedexfile)
        pokedexfile.close()

    df = pd.DataFrame(columns=["User", "Sufferer", "name move", "TypesU",
                               "TypesS", "TypeM", "power", "UserHP", "SuffererHP", "Weather", "categoryMove",
                               "Status enemy", "Choose", 'attack_boost', 'defense_boost', 'special_attack_boost',
                               'special_defense_boost', 'speed_boost', 'accuracy_boost', 'evasion_boost'])

    df2 = pd.DataFrame(
        columns=["Switch In", "Switch out", "enemy", "TypeIN", "TypeOUT", "TypeEnemy", "HPout", "HPEnemy", "StatusP",
                 "Weather", "Switch", ])

    # Regular expressions for different types of log entries
    switch_regex = re.compile(r'\|switch\|p\da: (.*?)\|(.*?)\|[0-9]+\\/[0-9]+')
    drag_regex = re.compile(r'\|drag\|p\da: (.*?)\|(.*?)\|[0-9]+\\/[0-9]+')
    move_regex = re.compile(r'\|move\|p\da: (.*?)\|(.*?)\|p\da: [a-zA-Z0-9\s_.-]+')
    moveP_regex = re.compile(r'\|move\|p\da: (.*?)\|(.*?)\|\|\[[a-zA-Z0-9\s_.-]+\]')

    boost_dict = {"spe": "speed_boost", "spd": "special_defense_boost",
                  "atk": "attack_boost", "spa": "special_attack_boost",
                  "def": "defense_boost", "accuracy": "accuracy_boost",
                  "evasion": "evasion_boost"}

    # Function to parse the log data
    team = {"p1a": [], "p2a": []}
    mapping_table = str.maketrans({' ': '', '-': '', '\'': ''})
    pokemon = {"p1a Pokemon": None, "p2a Pokemon": None, "hp p1a": -1, "hp p2a": -1, "weather": "none",
               "p1a mosse": [], "p2a mosse": [], "p1a status": "normal", "p2a status": "normal",
               "p1a boost": {
                   'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                   'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 0, 'evasion_boost': 0},
               "p2a boost": {
                   'attack_boost': 0, 'defense_boost': 0, 'special_attack_boost': 0,
                   'special_defense_boost': 0, 'speed_boost': 0, 'accuracy_boost': 0, 'evasion_boost': 0}}

    pokedex["farfetch’d"] = {
        "num": 83,
        "name": "farfetch\u2019d",
        "types": [
            "normal",
            "flying"
        ],
        "baseStats": {
            "hp": 52,
            "attack": 90,
            "defense": 55,
            "special-attack": 58,
            "special-defense": 62,
            "speed": 60
        },
        "abilities": {
            "0": "Keen Eye",
            "1": "Inner Focus",
            "H": "Defiant"
        },
        "heightm": 0.8,
        "weightkg": 15,
        "color": "Brown",
        "eggGroups": [
            "Flying",
            "Field"
        ],
        "otherFormes": [
            "Farfetch\u2019d-Galar"
        ],
        "formeOrder": [
            "Farfetch\u2019d",
            "Farfetch\u2019d-Galar"
        ]}

    for line in log_data:
        if line.startswith('|-boost|'):
            group = line.split("|")
            pokemon[group[2][:3] + " boost"][boost_dict[group[3]]] = pokemon[group[2][:3] + " boost"][
                                                                         boost_dict[group[3]]] + int(group[4].strip())
            if pokemon[group[2][:3] + " boost"][boost_dict[group[3]]] > 4:
                pokemon[group[2][:3] + " boost"][boost_dict[group[3]]] = 4
        if line.startswith('|-unboost|'):
            group = line.split("|")
            pokemon[group[2][:3] + " boost"][boost_dict[group[3]]] = pokemon[group[2][:3] + " boost"][
                                                                         boost_dict[group[3]]] - int(group[4].strip())
            if pokemon[group[2][:3] + " boost"][boost_dict[group[3]]] < -4:
                pokemon[group[2][:3] + " boost"][boost_dict[group[3]]] = -4
        if line.startswith('|-status|'):
            group = line.split("|")
            if group[2].startswith("p1a"):
                pokemon["p1a status"] = group[3]
            if group[2].startswith("p2a"):
                pokemon["p2a status"] = group[3]
        if line.startswith('|-curestatus|'):
            group = line.split("|")
            if group[2].startswith("p1a"):
                pokemon["p1a status"] = "normal"
            if group[2].startswith("p2a"):
                pokemon["p2a status"] = "normal"
        if line.startswith('|drag|'):
            match = drag_regex.match(line)
            matches = match.group().split("|")
            for token in matches:
                if token.startswith("p1a"):
                    if not team["p1a"].__contains__(token[5:]):
                        team["p1a"].append(token[5:])
                    pokemon["p1a Pokemon"] = token[5:]
                    pokemon["hp p1a"] = matches[-1]
                    pokemon["p1a mosse"] = []

                if token.startswith("p2a"):
                    if not team["p2a"].__contains__(token[5:]):
                        team["p2a"].append(token[5:])
                    pokemon["p2a Pokemon"] = token[5:]
                    pokemon["hp p2a"] = matches[-1]
                    pokemon["p2a mosse"] = []

        if line.startswith('|faint|'):
            pkmn = line.split("|")[-1].strip()
            if pkmn[:3] == "p1a":
                team["p1a"].remove(pkmn[5:])
            if pkmn[:3] == "p2a":
                team["p2a"].remove(pkmn[5:])
        if line.startswith('|switch|'):
            match = switch_regex.match(line)
            matches = match.group().split("|")
            for token in matches:
                if token.startswith("p1a"):
                    if not team["p1a"].__contains__(token[5:]):
                        team["p1a"].append(token[5:])
                    if pokemon["p1a Pokemon"] is not None and pokemon["p2a Pokemon"] is not None:
                        df2.loc[len(df2)] = [token[5:], pokemon["p1a Pokemon"], pokemon["p2a Pokemon"],
                                             pokedex[token[5:].lower().strip().replace("\n", "")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p1a Pokemon"].lower().strip().replace("\n", "")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p2a Pokemon"].lower().strip().replace("\n", "")][
                                                 "types"],
                                             pokemon["hp p1a"],
                                             pokemon["hp p2a"],
                                             pokemon["p1a status"],
                                             pokemon["weather"],
                                             1]
                        for pkmn in team["p1a"]:
                            if pkmn == token[5:] or pkmn == pokemon["p1a Pokemon"]:
                                continue
                            df2.loc[len(df2)] = [pkmn, pokemon["p1a Pokemon"], pokemon["p2a Pokemon"],
                                                 pokedex[pkmn.lower().strip().replace("\n", "")][
                                                     "types"],
                                                 pokedex[
                                                     pokemon["p1a Pokemon"].lower().strip().replace("\n", "")][
                                                     "types"],
                                                 pokedex[
                                                     pokemon["p2a Pokemon"].lower().strip().replace("\n", "")][
                                                     "types"],
                                                 pokemon["hp p1a"],
                                                 pokemon["hp p2a"],
                                                 pokemon["p1a status"],
                                                 pokemon["weather"],
                                                 0
                                                 ]
                    pokemon["p1a Pokemon"] = token[5:]
                    pokemon["hp p1a"] = matches[-1]
                    pokemon["p1a mosse"] = []

                if token.startswith("p2a"):
                    if not team["p2a"].__contains__(token[5:]):
                        team["p2a"].append(token[5:])
                    if pokemon["p1a Pokemon"] is not None and pokemon["p2a Pokemon"] is not None:
                        if token[5:].lower().strip().replace("\n", "") == "type: null":
                            continue
                        df2.loc[len(df2)] = [token[5:], pokemon["p2a Pokemon"], pokemon["p1a Pokemon"],
                                             pokedex[token[5:].lower().strip().replace("\n", "")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p2a Pokemon"].lower().strip().replace("\n", "")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p1a Pokemon"].lower().strip().replace("\n", "")][
                                                 "types"],
                                             pokemon["hp p2a"],
                                             pokemon["hp p1a"],
                                             pokemon["p2a status"],
                                             pokemon["weather"],
                                             1
                                             ]
                        for pkmn in team["p2a"]:
                            if pkmn == token[5:] or pkmn == pokemon["p2a Pokemon"]:
                                continue
                            df2.loc[len(df2)] = [pkmn, pokemon["p2a Pokemon"], pokemon["p1a Pokemon"],
                                                 pokedex[pkmn.lower().strip().replace("\n", "").replace("’", "'")][
                                                     "types"],
                                                 pokedex[
                                                     pokemon["p2a Pokemon"].lower().strip().replace("\n", "").replace(
                                                         "’",
                                                         "'")][
                                                     "types"],
                                                 pokedex[
                                                     pokemon["p1a Pokemon"].lower().strip().replace("\n", "").replace(
                                                         "’",
                                                         "'")][
                                                     "types"],
                                                 pokemon["hp p2a"],
                                                 pokemon["hp p1a"],
                                                 pokemon["p2a status"],
                                                 pokemon["weather"],
                                                 0
                                                 ]
                    pokemon["p2a Pokemon"] = token[5:]
                    pokemon["hp p2a"] = matches[-1]
                    pokemon["p2a mosse"] = []
        elif line.startswith('|move|'):
            match2 = None
            match1 = move_regex.match(line)
            if match1 is None:
                match2 = moveP_regex.match(line)
                if match2 is None:
                    continue
                matches = match2.group().split("|")
            else:
                matches = match1.group().split("|")
            if match1:
                User = None
                Sufferer = None
                for item in matches:
                    if item.startswith("p"):
                        if User is None:
                            User = item
                        else:
                            Sufferer = item
                    else:
                        Move = item
                if not moves.__contains__(Move.translate(mapping_table).lower()):
                    continue
                if not pokemon[User[:3] + " mosse"].__contains__(Move):
                    pokemon[User[:3] + " mosse"].append(Move)
                if User[5:].lower().strip().replace("\n", "") == "type: null" or Sufferer[5:].lower().strip().replace("\n", "") == "type":
                    continue
                df.loc[len(df)] = [User[5:], Sufferer[5:], Move,
                                   pokedex[User[5:].lower().strip().replace("\n", "")]["types"],
                                   pokedex[Sufferer[5:].lower().strip().replace("\n", "")]["types"],
                                   moves[Move.translate(mapping_table).lower()]["type"],
                                   moves[Move.translate(mapping_table).lower()]["basePower"],
                                   pokemon["hp " + User[:3]],
                                   pokemon["hp " + Sufferer[:3]],
                                   pokemon["weather"],
                                   moves[Move.translate(mapping_table).lower()]["category"],
                                   pokemon[Sufferer[:3] + " status"],
                                   1,
                                   pokemon[User[:3] + " boost"]["attack_boost"],
                                   pokemon[User[:3] + " boost"]["defense_boost"],
                                   pokemon[User[:3] + " boost"]["special_attack_boost"],
                                   pokemon[User[:3] + " boost"]["special_defense_boost"],
                                   pokemon[User[:3] + " boost"]["speed_boost"],
                                   pokemon[User[:3] + " boost"]["accuracy_boost"],
                                   pokemon[User[:3] + " boost"]["evasion_boost"]
                                   ]
                for move in pokemon[User[:3] + " mosse"]:
                    if move == Move:
                        continue
                    df.loc[len(df)] = [User[5:], Sufferer[5:], move,
                                       pokedex[User[5:].lower().strip().replace("\n", "")]["types"],
                                       pokedex[User[5:].lower().strip().replace("\n", "")]["types"],
                                       moves[move.translate(mapping_table).lower()]["type"],
                                       moves[move.translate(mapping_table).lower()]["basePower"],
                                       pokemon["hp " + User[:3]],
                                       pokemon["hp " + User[:3]],
                                       pokemon["weather"],
                                       moves[move.translate(mapping_table).lower()]["category"],
                                       pokemon[Sufferer[:3] + " status"],
                                       0,
                                       pokemon[User[:3] + " boost"]["attack_boost"],
                                       pokemon[User[:3] + " boost"]["defense_boost"],
                                       pokemon[User[:3] + " boost"]["special_attack_boost"],
                                       pokemon[User[:3] + " boost"]["special_defense_boost"],
                                       pokemon[User[:3] + " boost"]["speed_boost"],
                                       pokemon[User[:3] + " boost"]["accuracy_boost"],
                                       pokemon[User[:3] + " boost"]["evasion_boost"]
                                       ]

            elif match2:
                Move = None
                User = None
                for item in matches[:-2]:
                    if item.startswith("p"):
                        if User is None:
                            User = item
                    else:
                        Move = item
                if not pokemon[User[:3] + " mosse"].__contains__(Move):
                    pokemon[User[:3] + " mosse"].append(Move)
                if User[5:].lower().strip().replace("\n", "") == "type: null":
                    continue
                df.loc[len(df)] = [User[5:], User[5:], Move,
                                   pokedex[User[5:].lower().strip().replace("\n", "")]["types"],
                                   pokedex[User[5:].lower().strip().replace("\n", "")]["types"],
                                   moves[Move.translate(mapping_table).lower()]["type"],
                                   moves[Move.translate(mapping_table).lower()]["basePower"],
                                   pokemon["hp " + User[:3]],
                                   pokemon["hp " + User[:3]],
                                   pokemon["weather"],
                                   moves[Move.translate(mapping_table).lower()]["category"],
                                   pokemon[User[:3] + " status"],
                                   1,
                                   pokemon[User[:3] + " boost"]["attack_boost"],
                                   pokemon[User[:3] + " boost"]["defense_boost"],
                                   pokemon[User[:3] + " boost"]["special_attack_boost"],
                                   pokemon[User[:3] + " boost"]["special_defense_boost"],
                                   pokemon[User[:3] + " boost"]["speed_boost"],
                                   pokemon[User[:3] + " boost"]["accuracy_boost"],
                                   pokemon[User[:3] + " boost"]["evasion_boost"]
                                   ]
                for move in pokemon[User[:3] + " mosse"]:
                    if move == Move:
                        continue
                    df.loc[len(df)] = [User[5:], User[5:], move,
                                       pokedex[User[5:].lower().strip().replace("\n", "")]["types"],
                                       pokedex[User[5:].lower().strip().replace("\n", "")]["types"],
                                       moves[move.translate(mapping_table).lower()]["type"],
                                       moves[move.translate(mapping_table).lower()]["basePower"],
                                       pokemon["hp " + User[:3]],
                                       pokemon["hp " + User[:3]],
                                       pokemon["weather"],
                                       moves[move.translate(mapping_table).lower()]["category"],
                                       pokemon[User[:3] + " status"],
                                       0,
                                       pokemon[User[:3] + " boost"]["attack_boost"],
                                       pokemon[User[:3] + " boost"]["defense_boost"],
                                       pokemon[User[:3] + " boost"]["special_attack_boost"],
                                       pokemon[User[:3] + " boost"]["special_defense_boost"],
                                       pokemon[User[:3] + " boost"]["speed_boost"],
                                       pokemon[User[:3] + " boost"]["accuracy_boost"],
                                       pokemon[User[:3] + " boost"]["evasion_boost"]
                                       ]

        elif line.startswith("|-weather|"):
            matches = line.split("|")
            pokemon["weather"] = matches[2]

    return df, df2
