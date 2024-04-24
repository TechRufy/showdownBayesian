import os
import warnings

from pgmpy.models import BayesianNetwork
from pgmpy.estimators import BayesianEstimator
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
from pgmpy.inference import VariableElimination
import json

warnings.filterwarnings("ignore")

with open("./data/Weakness.json", 'r+') as weakfile:
    weak = json.load(weakfile)
    weakfile.close()


def percentual_Transform(s):
    l = s.split("\/")
    l = list(map(lambda n: int(n), l))
    p = l[0] / l[1] * 100

    return p


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


def check_stab(df):
    new_col = []
    for i in range(len(df)):
        if df['Pokemon Type'][i].split('\'')[1] == df['Type Move'][i] or (
                len(df['Pokemon Type'][i].split('\'')) > 3 and df['Pokemon Type'][i].split('\'')[3] == df['Type Move'][
            i]):
            new_col.append(True)
        else:
            new_col.append(False)
    df = df.assign(stab=new_col)
    df = df.drop(['Pokemon Type', 'Type Move'], axis=1)
    return df


df = pd.read_csv("./showdown/battle_bots/BayesianBot/parsing Dataset/log/Dataset.csv")

df["UserHP"] = df["UserHP"].map(percentual_Transform)
df["SuffererHP"] = df["SuffererHP"].map(percentual_Transform)

df.rename({"UserHP": "Pokemon HP", "SuffererHP": "Enemy HP", "TypeM": "Type Move",
           "categoryMove": "Category", "TypesS": "Enemy Type", "TypesU": "Pokemon Type",
           "power": "Power"}, axis=1, inplace=True)
df["Multiplicator"] = df[["Enemy Type", "Type Move"]].apply(Generate_Multiplicator, axis=1)
df = df.drop(["Enemy Type"], axis=1)
# df["Choose"] = np.ones(len(df)).astype(int)
df = check_stab(df)
df["Weather"] = df["Weather"].str.rstrip().str.lower()
df["Status enemy"] = df["Status enemy"].str.rstrip().str.lower()
df["Sufferer"] = df["Sufferer"].str.rstrip().str.lower()
df["User"] = df["User"].str.rstrip().str.lower()

df["Boost"] = df["attack_boost"] + df["defense_boost"] + df["special_attack_boost"] + df["special_defense_boost"] + df[
    "speed_boost"] + df["evasion_boost"] + df["accuracy_boost"]

df = df.drop(["accuracy_boost", "speed_boost", "evasion_boost",
              "attack_boost", "defense_boost", "special_attack_boost", "special_defense_boost"], axis=1)

from sklearn.preprocessing import KBinsDiscretizer

encHP = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
encHP.fit(df[["Pokemon HP"]])
df["Pokemon HP"] = encHP.transform(df[["Pokemon HP"]]).astype(int)
encHPE = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
encHPE.fit(df[["Enemy HP"]])
df["Enemy HP"] = encHPE.transform(df[["Enemy HP"]]).astype(int)
encP = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
encP.fit(df[["Power"]])
df["Power"] = encP.transform(df[["Power"]]).astype(int)

encB = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='kmeans')
encB.fit(df[["Boost"]])
df["Boost"] = encB.transform(df[["Boost"]]).astype(int)

custom_model = BayesianNetwork([  #('Pokemon HP', 'Choose'),
    ('Enemy HP', 'Choose'),  #('Status enemy', 'Choose'),
    ('stab', 'Choose'), ('Multiplicator', 'Choose'),  #('Power', 'Choose'),
    #("Weather","Choose"),
    ("Category", "Choose"), ("Boost", "Choose"),
    #('attack_boost',"Choose"), ('defense_boost',"Choose"), ('special_attack_boost',"Choose"
    #('special_defense_boost',"Choose"),
    #('speed_boost',"Choose"), ('accuracy_boost',"Choose"), ('evasion_boost',"Choose")
])
pos = {'Pokemon HP': [0.75, -0.5], 'Enemy HP': [1.25, -0.5],
       "stab": [0.75, -1.], 'Multiplicator': [1.25, -1],
       'Power': [1.25, 0], "Weather": [1.1, 0],
       'Choose': [1, -0.5], "Category": [0.9, 0], "Boost": [1, 0], "Status enemy": [0.6, -0.5],
       # "attack_boost": [0.7, -0.5],
       #'defense_boost': [0.8,-0.6],'special_attack_boost':[0.9,-0.7],'special_defense_boost':[1,-0.8],'speed_boost': [1.1,-0.9],'accuracy_boost':[1.2,-1],'evasion_boost':[1.3,-1.1]
       }
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
nx.draw_networkx(custom_model, pos=pos, ax=ax, node_size=5000)
ax.set_title('Custom model')
fig.savefig('custom_bn')

estimator = BayesianEstimator(model=custom_model, data=df)

cpds = []
for node in custom_model.nodes():
    cpds.append(estimator.estimate_cpd(node=node,
                                       prior_type="BDeu",
                                       equivalent_sample_size=3500))
custom_model.add_cpds(*cpds)

# print('Checking the model...')
# print(f'The model is {custom_model.check_model()}\n\n')

# for cpd in [cpd for cpd in custom_model.get_cpds()]:
# print(f'CPD for {cpd.variable}:')
# print(cpd)

choose = custom_model.get_cpds("Choose")

import time

EVIDENCE = {'Power': 0,
            'Multiplicator': 4,
            'stab': True,
            'Enemy HP': 1,
            "Pokemon HP": 9}

ordering_heuristics = ['MinFill', 'MinNeighbors', 'MinWeight', 'WeightedMinFill']
inference = VariableElimination(custom_model)


def run_query(target_var, evidence, print_output=True):
    probs = []
    #evidence["Power"] = int(encP.transform(np.array(evidence["Power"]).reshape((1, -1)))[0][0])
    evidence["Enemy HP"] = int(encHPE.transform(np.array(evidence["Enemy HP"]).reshape((1, -1)))[0][0])
    #evidence["Pokemon HP"] = int(encHP.transform(np.array(evidence["Pokemon HP"]).reshape((1, -1)))[0][0])
    evidence["Boost"] = int(encB.transform(np.array(evidence["Boost"]).reshape((1, -1)))[0][0])

    prob = inference.query([target_var],
                           evidence,
                           elimination_order='MinFill',
                           show_progress=False)
    probs.append(prob.get_value(Choose=1))
    return probs[0]


df_switch = pd.read_csv("./showdown/battle_bots/BayesianBot/parsing Dataset/log/Dataset-Switch.csv")


def Generate_Multiplicator_In_switch(x):
    EnemyType = x["Enemy Type"]
    InType = x["Pokemon In Type"]
    weakness = 1
    EnemyType = EnemyType.split(",")
    InType = InType.split(",")

    for i in range(max(len(EnemyType), len(InType))):
        if i == 0:
            EnemyType[i] = EnemyType[i][2:-1]
            InType[i] = InType[i][2:-1]
        elif i == 1:
            if len(EnemyType) > 1:
                EnemyType[1] = EnemyType[1][2:-2]
            if len(InType) > 1:
                InType[1] = InType[1][2:-2]
    for En_Type in EnemyType:
        if not En_Type.isalnum():
            continue
        for In_Type in InType:
            if not In_Type.isalnum():
                continue
            weakness = weakness * weak[In_Type][En_Type]
    return weakness


def Generate_Multiplicator_Out_switch(x):
    EnemyType = x["Enemy Type"]
    OutType = x["Pokemon Out Type"]
    weakness = 1
    EnemyType = EnemyType.split(",")
    OutType = OutType.split(",")

    for i in range(max(len(EnemyType), len(OutType))):
        if i == 0:
            EnemyType[i] = EnemyType[i][2:-1]
            OutType[i] = OutType[i][2:-1]
        elif i == 1:
            if len(EnemyType) > 1:
                EnemyType[1] = EnemyType[1][2:-2]
            if len(OutType) > 1:
                OutType[1] = OutType[1][2:-2]
    for En_Type in EnemyType:
        if not En_Type.isalnum():
            continue
        for Out_Type in OutType:
            if not Out_Type.isalnum():
                continue
            weakness = weakness * weak[Out_Type][En_Type]
    return weakness


df_switch["HPout"] = df_switch["HPout"].map(percentual_Transform)
df_switch["HPEnemy"] = df_switch["HPEnemy"].map(percentual_Transform)
df_switch["Weather"] = df_switch["Weather"].str.rstrip().str.lower()
df_switch["StatusP"] = df_switch["StatusP"].str.rstrip().str.lower()

df_switch.rename({"HPout": "Pokemon HP", "HPEnemy": "Enemy HP", "TypeEnemy": "Enemy Type", "TypeIN": "Pokemon In Type",
                  "TypeOUT": "Pokemon Out Type", "StatusP": "Status Pokemon"}, axis=1, inplace=True)
df_switch["Multiplicator In"] = df_switch[["Enemy Type", "Pokemon In Type"]].apply(Generate_Multiplicator_In_switch,
                                                                                   axis=1)
df_switch["Multiplicator Out"] = df_switch[["Enemy Type", "Pokemon Out Type"]].apply(Generate_Multiplicator_Out_switch,
                                                                                     axis=1)

df_switch = df_switch.drop(["Enemy Type", "Pokemon In Type", "Pokemon Out Type"], axis=1)

from sklearn.preprocessing import KBinsDiscretizer

encHP = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
encHP.fit(df_switch[["Pokemon HP"]])
df_switch["Pokemon HP"] = encHP.transform(df_switch[["Pokemon HP"]]).astype(int)
encHPE = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
encHPE.fit(df_switch[["Enemy HP"]])

df_switch["Enemy HP"] = encHPE.transform(df_switch[["Enemy HP"]]).astype(int)

encIN = KBinsDiscretizer(n_bins=3, encode='ordinal',strategy='kmeans')
encIN.fit(df_switch[["Multiplicator In"]])
df_switch["Multiplicator In"] = encIN.transform(df_switch[["Multiplicator In"]]).astype(int)
encOUT = KBinsDiscretizer(n_bins=3, encode='ordinal',strategy='kmeans')
encOUT.fit(df_switch[["Multiplicator Out"]])
df_switch["Multiplicator Out"] = encOUT.transform(df_switch[["Multiplicator Out"]]).astype(int)


switch_model = BayesianNetwork([  #('Pokemon HP', 'Switch'), #('Enemy HP', 'Switch'),
    ('Status Pokemon', 'Switch'),  #('Weather', 'Switch'),
    ('Multiplicator In', 'Switch'), ('Multiplicator Out', 'Switch')])
pos = {'Pokemon HP': [0.9, 0], 'Enemy HP': [1.1, 0],
       "Multiplicator Out": [0.75, 0], 'Multiplicator In': [1.25, 0],
       'Switch': [1, -0.5], 'Status Pokemon': [0.9, -1], 'Weather': [1.25, -1]}
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
nx.draw_networkx(switch_model, pos=pos, ax=ax, node_size=5000)
ax.set_title('Custom model')
fig.savefig('custom_bn')
estimator = BayesianEstimator(model=switch_model, data=df_switch)

cpds = []
for node in switch_model.nodes():
    cpds.append(estimator.estimate_cpd(node=node,
                                       prior_type="BDeu",
                                       equivalent_sample_size=3500))
switch_model.add_cpds(*cpds)

#print('Checking the model...')
#print(f'The model is {switch_model.check_model()}\n\n')

#for cpd in [cpd for cpd in switch_model.get_cpds()]:
#    print(f'CPD for {cpd.variable}:')
#    print(cpd)

choose = switch_model.get_cpds("Switch")
#print(choose.values)


ordering_heuristics = ['MinFill', 'MinNeighbors', 'MinWeight', 'WeightedMinFill']
inferenceS = VariableElimination(switch_model)


def switch_run_query(target_var, evidence, print_output=True):
    probs = []
    #evidence["Enemy HP"] = int(encHPE.transform(np.array(evidence["Enemy HP"]).reshape((1, -1)))[0][0])
    #evidence["Pokemon HP"] = int(encHP.transform(np.array(evidence["Pokemon HP"]).reshape((1, -1)))[0][0])
    evidence['Multiplicator In'] = int(encIN.transform(np.array(evidence['Multiplicator In']).reshape((1, -1)))[0][0])
    evidence['Multiplicator Out'] = int(encOUT.transform(np.array(evidence['Multiplicator Out']).reshape((1, -1)))[0][0])
    prob = inferenceS.query([target_var],
                            evidence,
                            show_progress=False)
    probs.append(prob.get_value(Switch=1))
    return probs[0]
