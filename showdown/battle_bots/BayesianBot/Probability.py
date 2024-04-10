import json

with open("./data/Weakness.json", 'r+') as weakfile:
    weak = json.load(weakfile)
    weakfile.close()

with open("./data/Weakness.json", 'r+') as movekfile:
    moves = json.load(weakfile)
    weakfile.close()

with open("./data/Weakness.json", 'r+') as pokemonfile:
    pokemon = json.load(weakfile)
    weakfile.close()

mapping_table = str.maketrans({' ': '', '-': ''})

def Generate_Multiplicator(x):
    EnemyType = x["Enemy Type"]
    MoveType = x["Type Move"]
    weakness = 1
    EnemyType = EnemyType.split(",")
    for i in range(len(EnemyType)):
        if i == 0:
            EnemyType[i] = EnemyType[i][2:-1]
        elif i == 1:
            EnemyType[1] = EnemyType[1][2:-2]
    for Type in EnemyType:
        if not Type.isalnum():
            continue
        weakness = weakness * weak[MoveType][Type]
    return weakness
def percentual_Transform(s):
    l = s.split("\/")
    l = list(map(lambda n: int(n), l))
    p = l[0] / l[1] * 100

    return p


def get_probability(state,move):



    EVIDENCE = {'Weather': state.weather,
                'Power': moves[move.translate(mapping_table).lower()]["basePower"],
                'Multiplicator': 4,
                'stab': True,
                'Enemy HP': 1,
                "Pokemon HP": 9}

