import re
import pandas as pd
import json
import os


def parser(log_data):
    with open("../../../../data/moves.json", 'r+') as movefile:
        moves = json.load(movefile)
        movefile.close()

    with open("../../../../data/pokedex.json", 'r+') as pokedexfile:
        pokedex = json.load(pokedexfile)
        pokedexfile.close()

    df = pd.DataFrame(columns=["User", "Sufferer", "name move", "TypesU",
                               "TypesS", "TypeM", "power", "UserHP", "SuffererHP", "Weather","categoryMove"])

    # Regular expressions for different types of log entries
    switch_regex = re.compile(r'\|switch\|p\da: (.*?)\|(.*?)\|[0-9]+\\/[0-9]+')
    move_regex = re.compile(r'\|move\|p\da: (.*?)\|(.*?)\|p\da: [a-zA-Z0-9\s_.-]+')
    moveP_regex = re.compile(r'\|move\|p\da: (.*?)\|(.*?)\|\|\[[a-zA-Z0-9\s_.-]+\]')


    # Function to parse the log data
    mapping_table = str.maketrans({' ': '', '-': ''})
    pokemon = {"p1a Pokemon": None, "p2a Pokemon": None, "hp p1a": 0, "hp p2a": 0, "weather": "none"}
    for line in log_data:
        if line.startswith('|switch|'):
            match = switch_regex.match(line)
            matches = match.group().split("|")
            for token in matches:
                if token.startswith("p1a"):
                    pokemon["p1a Pokemon"] = token[5:]
                    pokemon["hp p1a"] = matches[-1]
                if token.startswith("p2a"):
                    pokemon["p2a Pokemon"] = token[5:]
                    pokemon["hp p2a"] = matches[-1]
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
                df.loc[len(df)] = [User[5:], Sufferer[5:], Move,
                                   pokedex[User[5:].lower().strip().replace("\n","")]["types"],
                                   pokedex[Sufferer[5:].lower().strip().replace("\n","")]["types"],
                                   moves[Move.translate(mapping_table).lower()]["type"],
                                   moves[Move.translate(mapping_table).lower()]["basePower"],
                                   pokemon["hp " + User[:3]],
                                   pokemon["hp " + Sufferer[:3]],
                                   pokemon["weather"],
                                   moves[Move.translate(mapping_table).lower()]["category"]
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
                df.loc[len(df)] = [User[5:], User[5:], Move,
                                   pokedex[User[5:].lower()]["types"],
                                   pokedex[User[5:].lower()]["types"],
                                   moves[Move.translate(mapping_table).lower()]["type"],
                                   moves[Move.translate(mapping_table).lower()]["basePower"],
                                   pokemon["hp " + User[:3]],
                                   pokemon["hp " + User[:3]],
                                   pokemon["weather"],
                                   moves[Move.translate(mapping_table).lower()]["category"]
                                   ]
        elif line.startswith("|-weather|"):
            matches = line.split("|")
            pokemon["weather"] = matches[2]

    return df
