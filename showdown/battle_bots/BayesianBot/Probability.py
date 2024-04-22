import json
from ..BayesianBot.BayesianNetwork.BayesianPokemon import run_query, switch_run_query

with open("./data/Weakness.json", 'r+') as weakfile:
    weak = json.load(weakfile)
    weakfile.close()

with open("./data/movesB.json", 'r+') as movefile:
    moves = json.load(movefile)
    weakfile.close()

with open("./data/pokedexB.json", 'r+') as pokemonfile:
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


def Generate_Multiplicator_In_switch(EnemyType, InType):
    weakness = 1

    for Itype in InType:
        for Etype in EnemyType:
            if not Etype.isalnum():
                continue
            weakness = weakness * weak[Itype][Etype]
    return weakness


def Generate_Multiplicator_Out_switch(EnemyType, OutType):
    weakness = 1

    for Otype in OutType:
        for Etype in EnemyType:
            if not Etype.isalnum():
                continue
            weakness = weakness * weak[Otype][Etype]
    return weakness


def check_stab(active_types, move):
    return move in active_types


#    if active_types.split('\'')[1] == move or (len(active_types.split('\'')) > 3 and active_types[3] == move):
#        return True
#    else:
#        return False


def get_probability_Move(state, move):
    EVIDENCE = {'Weather': str(state.weather).lower(),
                'Power': moves[move.translate(mapping_table).lower()]["basePower"],
                'Multiplicator': Generate_Multiplicator(moves[move.translate(mapping_table).lower()]["type"],
                                                        state.opponent.active.types),
                'stab': check_stab(state.user.active.types, move),
                'Enemy HP': int((state.opponent.active.hp / state.opponent.active.maxhp) * 100),
                "Pokemon HP": int((state.user.active.hp / state.user.active.maxhp) * 100),
                "Category": moves[move.translate(mapping_table).lower()]["category"],
                "Status enemy": state.opponent.active.status if state.opponent.active.status is not None else "normal"
                }
    print(move)
    result = run_query(target_var='Choose', evidence=EVIDENCE)
    return result


def get_probability_Switch(state, switch):
    maxhpE = state.opponent.active.maxhp
    maxhpP = state.user.active.maxhp
    if maxhpE == 0:
        maxhpE = 1
    if maxhpP == 0:
        maxhpP = 1

    EVIDENCE = {'Weather': str(state.weather).lower(),
                'Multiplicator In': Generate_Multiplicator_In_switch(state.opponent.active.types,
                                                                     pokemon[switch[7:]]["types"]),
                'Multiplicator Out': Generate_Multiplicator_Out_switch(state.opponent.active.types,
                                                                       state.user.active.types),
                'Enemy HP': int((state.opponent.active.hp / maxhpE) * 100),
                "Pokemon HP": int((state.user.active.hp / maxhpP) * 100),
                "Status Pokemon": state.user.active.status if state.user.active.status is not None else "normal"
                }
    print(switch)
    result = switch_run_query(target_var='Switch', evidence=EVIDENCE)
    return result
