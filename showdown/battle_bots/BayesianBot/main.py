import json
import os

import constants
from data import all_move_json
from showdown.battle import Battle
from showdown.engine.damage_calculator import calculate_damage
from showdown.engine.find_state_instructions import update_attacking_move
from ..helpers import format_decision
from .Probability import get_probability_Move, get_probability_Switch


class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        state = self.create_state()
        my_options = self.get_all_options()[0]
        choice = None
        moves = []
        switches = []
        for option in my_options:
            if option.startswith(constants.SWITCH_STRING + " "):
                switches.append(option)
            else:
                moves.append(option)
        best_probability = -1
        if self.force_switch or not moves:
            for switch in switches:
                probability = get_probability_Switch(state, switch)
                print(probability)
                if probability > best_probability:
                    choice = switch
                    best_probability = probability

        for move in moves:
            probability = get_probability_Move(state, move)
            print(probability)

            if probability > best_probability:
                choice = move
                best_probability = probability

        for switch in switches:
            probability = get_probability_Switch(state, switch)
            print(probability)
            if probability > best_probability:
                choice = switch
                best_probability = probability

        print(choice)
        return format_decision(self, choice)
