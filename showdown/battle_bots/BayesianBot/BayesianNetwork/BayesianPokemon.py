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
                len(df['Pokemon Type'][i].split('\'')) > 3 and df['Pokemon Type'][i].split('\'')[3] == df['Type Move'][i]):
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
df

from sklearn.preprocessing import KBinsDiscretizer

encHP = KBinsDiscretizer(n_bins=10, encode='ordinal', strategy='uniform')
encHP.fit(df[["Pokemon HP"]])
df["Pokemon HP"] = encHP.transform(df[["Pokemon HP"]]).astype(int)
encHPE = KBinsDiscretizer(n_bins=10, encode='ordinal', strategy='uniform')
encHPE.fit(df[["Enemy HP"]])
df["Enemy HP"] = encHPE.transform(df[["Enemy HP"]]).astype(int)
encP = KBinsDiscretizer(n_bins=10, encode='ordinal', strategy='uniform')
encP.fit(df[["Power"]])
df["Power"] = encP.transform(df[["Power"]]).astype(int)
df

custom_model = BayesianNetwork([('Pokemon HP', 'Choose'), ('Enemy HP', 'Choose'),
                                ('stab', 'Choose'), ('Multiplicator', 'Choose'), ('Power', 'Choose'),
                                ("Weather", "Choose"), ("Category", "Choose")])
pos = {'Pokemon HP': [0.75, -0.5], 'Enemy HP': [1.25, -0.5],
       "stab": [0.75, -1.], 'Multiplicator': [1.25, -1],
       'Power': [1.25, 0], "Weather": [1.1, 0],
       'Choose': [1, -0.5], "Category": [0.9, 0]}
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
nx.draw_networkx(custom_model, pos=pos, ax=ax, node_size=5000)
ax.set_title('Custom model')
fig.savefig('custom_bn')

estimator = BayesianEstimator(model=custom_model, data=df)

cpds = []
for node in custom_model.nodes():
    cpds.append(estimator.estimate_cpd(node=node,
                                       prior_type="BDeu",
                                       equivalent_sample_size=10))
custom_model.add_cpds(*cpds)

# print('Checking the model...')
# print(f'The model is {custom_model.check_model()}\n\n')

# for cpd in [cpd for cpd in custom_model.get_cpds()]:
# print(f'CPD for {cpd.variable}:')
# print(cpd)

choose = custom_model.get_cpds("Choose")
# print(choose)

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
    evidence["Power"] = int(encP.transform(np.array(evidence["Power"]).reshape((1, -1)))[0][0])
    evidence["Enemy HP"] = int(encHPE.transform(np.array(evidence["Enemy HP"]).reshape((1, -1)))[0][0])
    evidence["Pokemon HP"] = int(encHP.transform(np.array(evidence["Pokemon HP"]).reshape((1, -1)))[0][0])
    print(target_var, evidence)

    prob = inference.query([target_var],
                           evidence,
                           elimination_order='MinFill',
                           show_progress=False)
    probs.append(prob.get_value(Choose=1))
    return probs[0]
