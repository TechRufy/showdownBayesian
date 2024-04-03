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

    df = pd.DataFrame(columns=["User", "Sufferer", "name move", "TypesU", "TypesS", "TypeM", "power"])

    # Regular expressions for different types of log entries
    player_regex = re.compile(r'\|player\|(\w+)\|(\w+)\|(\d+)\|(\d+)')
    switch_regex = re.compile(r'\|switch\|(\w+): (\w+)\|(\w+), L(\d+)\|(\d+)\/(\d+)')
    move_regex = re.compile(r'\|move\|p\da: [A-Za-z]+\|(.*?)\|p\da: [A-Za-z]+')
    moveP_regex = re.compile(r'\|move\|p\da: [A-Za-z]+\|[A-Za-z]+\|\|\[[A-Za-z]+\]')

    # Function to parse the log data
    for line in log_data:
        if line.startswith('|player|'):
            match = player_regex.match(line)
            if match:
                side, username, pokemon_id, elo = match.groups()
                print(f"Player: {side}, Username: {username}, Pokemon ID: {pokemon_id}, ELO: {elo}")
        elif line.startswith('|switch|'):
            match = switch_regex.match(line)
            if match:
                side, pokemon_name, species, level, hp_current, hp_max = match.groups()
                print(
                    f"Switch: {side}, Pokemon: {pokemon_name}, Species: {species}, Level: {level}, HP: {hp_current}/{hp_max}")
        elif line.startswith('|move|'):
            match2 = None
            match1 = move_regex.match(line)
            if match1 is None:
                match2 = moveP_regex.match(line)
                matches = match2.group().split("|")
            else:
                matches = match1.group().split("|")
            if match1:
                User = None
                Sufferer = None
                for item in matches:
                    if item.startswith("p"):
                        if User is None:
                            User = item[5:]
                        else:
                            Sufferer = item[5:]
                    else:
                        Move = item
                mapping_table = str.maketrans({' ': '', '-': ''})
                df.loc[len(df)] = [User, Sufferer, Move,
                                   pokedex[User.lower()]["types"],
                                   pokedex[Sufferer.lower()]["types"],
                                   moves[Move.translate(mapping_table).lower()]["type"],
                                   moves[Move.translate(mapping_table).lower()]["basePower"]]
            elif match2:
                Move = None
                User = None
                for item in matches[:-2]:
                    if item.startswith("p"):
                        if User is None:
                            User = item[5:]
                    else:
                        Move = item
                mapping_table = str.maketrans({' ': '', '-': ''})
                df.loc[len(df)] = [User, User, Move,
                                   pokedex[User.lower()]["types"],
                                   pokedex[User.lower()]["types"],
                                   moves[Move.translate(mapping_table).lower()]["type"],
                                   moves[Move.translate(mapping_table).lower()]["basePower"]]



    return df
