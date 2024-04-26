import json
from ..BayesianBotReduced.BayesianNetwork.BayesianPokemon import run_query, switch_run_query

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


def get_probability_Move(state, move):
    EVIDENCE = {'Multiplicator': Generate_Multiplicator(moves[move.translate(mapping_table).lower()]["type"],
                                                        state.opponent.active.types),
                'stab': check_stab(state.user.active.types, move),
                'Enemy HP': int((state.opponent.active.hp / state.opponent.active.maxhp) * 100),
                "Category": moves[move.translate(mapping_table).lower()]["category"],
                "Boost": (
                        state.user.active.attack_boost + state.user.active.defense_boost + state.user.active.special_attack_boost + state.user.active.special_defense_boost + state.user.active.speed_boost + state.user.active.accuracy_boost + state.user.active.evasion_boost)
                }
    result = run_query(target_var='Choose', evidence=EVIDENCE)
    return result


def get_probability_Switch(state, switch):
    maxhpP = state.user.active.maxhp
    if maxhpP == 0:
        maxhpP = 1

    EVIDENCE = {'Multiplicator In': Generate_Multiplicator_In_switch(state.opponent.active.types,
                                                                     pokemon[switch[7:]]["types"]),
                'Multiplicator Out': Generate_Multiplicator_Out_switch(state.opponent.active.types,
                                                                       state.user.active.types),
                "Pokemon HP": int((state.user.active.hp / maxhpP) * 100),
                "Status Pokemon": state.user.active.status if state.user.active.status is not None else "normal"
                }
    result = switch_run_query(target_var='Switch', evidence=EVIDENCE)
    return result
