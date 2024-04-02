import re
import pandas as pd

log_data = """
|j|☆Eimint64
|j|☆shnen
|t:|1711541006
|gametype|singles
|player|p1|Eimint64|102|1682
|player|p2|shnen|1|1800
|teamsize|p1|6
|teamsize|p2|6
|gen|7
|tier|[Gen 7] Random Battle
|rated|
|rule|Sleep Clause Mod: Limit one foe put to sleep
|rule|HP Percentage Mod: HP is shown in percentages
|rule|Illusion Level Mod: Illusion disguises the Pokémon's true level
|
|t:|1711541006
|start
|switch|p1a: Solrock|Solrock, L89|305\/305
|switch|p2a: Darkrai|Darkrai, L76|231\/231
|turn|1
|inactive|Battle timer is ON: inactive players will automatically lose when time's up. (requested by shnen)
|inactive|Eimint64 also wants the timer to be on.
|
|t:|1711541024
|switch|p1a: Silvally|Silvally-Fighting, L87|307\/307
|move|p2a: Darkrai|Nasty Plot|p2a: Darkrai
|-boost|p2a: Darkrai|spa|2
|
"""
df = pd.DataFrame(columns=["User","Sufferer","name move","TypeU","TypeS","TypeM"],index=["turn"])

# Regular expressions for different types of log entries
player_regex = re.compile(r'\|player\|(\w+)\|(\w+)\|(\d+)\|(\d+)')
switch_regex = re.compile(r'\|switch\|(\w+): (\w+)\|(\w+), L(\d+)\|(\d+)\/(\d+)')
move_regex = re.compile(r'\|move\|p[0-9]+a:\s[A-Za-z]+\|[A-Za-z]+ [A-Za-z]+\|p[0-9]+a:\s[A-Za-z]+')
boost_regex = re.compile(r'\|-boost\|(\w+): (\w+)\|(\w+)\|(\w+)\|(\d+)')


# Function to parse the log data
def parse_log(log_data):
    lines = log_data.strip().split('\n')
    for line in lines:
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
            match = move_regex.match(line)
            matches = match.group().split("|")
            if match:
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

                df.loc[len(df)] = [User,Sufferer,Move,"None","None","None"]

        elif line.startswith('|-boost|'):
            match = boost_regex.match(line)
            if match:
                side, pokemon_name, stat, boost_value = match.groups()
                print(f"Boost: {side}, Pokemon: {pokemon_name}, Stat: {stat}, Boost Value: {boost_value}")


# Parse the log data
parse_log(log_data)
print(df)
