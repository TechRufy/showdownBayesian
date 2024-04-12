import json
from ..BayesianBot.BayesianNetwork.BayesianPokemon import run_query

with open("./data/Weakness.json", 'r+') as weakfile:
    weak = json.load(weakfile)
    weakfile.close()

with open("./data/moves.json", 'r+') as movefile:
    moves = json.load(movefile)
    weakfile.close()

with open("./data/pokedex.json", 'r+') as pokemonfile:
    pokemon = json.load(pokemonfile)
    weakfile.close()

mapping_table = str.maketrans({' ': '', '-': ''})


def Generate_Multiplicator(move_type, enemy_types):
    EnemyType = enemy_types
    MoveType = move_type
    weakness = 1
    # EnemyType = EnemyType.split(",")
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


def check_stab(active_types, move):
    return active_types.__contains__(move)

#    if active_types.split('\'')[1] == move or (len(active_types.split('\'')) > 3 and active_types[3] == move):
#        return True
#    else:
#        return False


def get_probability(state, move):
    EVIDENCE = {'Weather': state.weather,
                'Power': moves[move.translate(mapping_table).lower()]["basePower"],
                'Multiplicator': Generate_Multiplicator(moves[move.translate(mapping_table).lower()]["type"],
                                                        state.opponent.active.types),
                'stab': check_stab(state.user.active.types, move),
                'Enemy HP': state.opponent.active.hp,
                "Pokemon HP": state.user.active.hp}
    print(EVIDENCE)
    result = run_query(target_var='Choose', evidence=EVIDENCE)
    return result
