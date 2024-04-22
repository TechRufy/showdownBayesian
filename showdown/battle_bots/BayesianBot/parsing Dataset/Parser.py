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
                               "Status enemy", "Choose"])

    df2 = pd.DataFrame(
        columns=["Switch In", "Switch out", "enemy", "TypeIN", "TypeOUT", "TypeEnemy", "HPout", "HPEnemy", "StatusP",
                 "Weather","Switch", ])

    # Regular expressions for different types of log entries
    switch_regex = re.compile(r'\|switch\|p\da: (.*?)\|(.*?)\|[0-9]+\\/[0-9]+')
    drag_regex = re.compile(r'\|drag\|p\da: (.*?)\|(.*?)\|[0-9]+\\/[0-9]+')
    move_regex = re.compile(r'\|move\|p\da: (.*?)\|(.*?)\|p\da: [a-zA-Z0-9\s_.-]+')
    moveP_regex = re.compile(r'\|move\|p\da: (.*?)\|(.*?)\|\|\[[a-zA-Z0-9\s_.-]+\]')

    # Function to parse the log data
    team = {"p1a": [], "p2a": []}
    mapping_table = str.maketrans({' ': '', '-': '', '\'': ''})
    pokemon = {"p1a Pokemon": None, "p2a Pokemon": None, "hp p1a": -1, "hp p2a": -1, "weather": "none",
               "p1a mosse": [], "p2a mosse": [], "p1a status": "normal", "p2a status": "normal"}
    for line in log_data:
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
                                             pokedex[token[5:].lower().strip().replace("\n", "").replace("’", "'")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p1a Pokemon"].lower().strip().replace("\n", "").replace("’",
                                                                                                                  "'")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p2a Pokemon"].lower().strip().replace("\n", "").replace("’",
                                                                                                                  "'")][
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
                                                 pokedex[pkmn.lower().strip().replace("\n", "").replace("’", "'")][
                                                     "types"],
                                                 pokedex[
                                                     pokemon["p1a Pokemon"].lower().strip().replace("\n", "").replace(
                                                         "’",
                                                         "'")][
                                                     "types"],
                                                 pokedex[
                                                     pokemon["p2a Pokemon"].lower().strip().replace("\n", "").replace(
                                                         "’",
                                                         "'")][
                                                     "types"],
                                                 pokemon["hp p1a"],
                                                 pokemon["hp p2a"],
                                                 pokemon["p1a status"],
                                                 pokemon["weather"],
                                                 0]
                    pokemon["p1a Pokemon"] = token[5:]
                    pokemon["hp p1a"] = matches[-1]
                    pokemon["p1a mosse"] = []

                if token.startswith("p2a"):
                    if not team["p2a"].__contains__(token[5:]):
                        team["p2a"].append(token[5:])
                    if pokemon["p1a Pokemon"] is not None and pokemon["p2a Pokemon"] is not None:
                        df2.loc[len(df2)] = [token[5:], pokemon["p2a Pokemon"], pokemon["p1a Pokemon"],
                                             pokedex[token[5:].lower().strip().replace("\n", "").replace("’", "'")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p2a Pokemon"].lower().strip().replace("\n", "").replace("’",
                                                                                                                  "'")][
                                                 "types"],
                                             pokedex[
                                                 pokemon["p1a Pokemon"].lower().strip().replace("\n", "").replace("’",
                                                                                                                  "'")][
                                                 "types"],
                                             pokemon["hp p2a"],
                                             pokemon["hp p1a"],
                                             pokemon["p2a status"],
                                             pokemon["weather"],
                                             1]
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
                                                 0]
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
                                   1
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
                                       0
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
                                   1
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
                                       0
                                       ]

        elif line.startswith("|-weather|"):
            matches = line.split("|")
            pokemon["weather"] = matches[2]

    return df, df2
