import os
import warnings

from pgmpy.models import BayesianNetwork
from pgmpy.estimators import BayesianEstimator
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
from pgmpy.inference import VariableElimination
from pgmpy.estimators import HillClimbSearch, TreeSearch, BDeuScore, MaximumLikelihoodEstimator
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




df_learn = df.drop(["User","name move","Sufferer"],axis=1)
scorer = BDeuScore(data=df_learn)
hc = HillClimbSearch(data=df_learn)
hc_base_model = hc.estimate(scoring_method=scorer, show_progress=False)

fig, ax = plt.subplots(1, 1, figsize=(12, 12))
nx.draw_networkx(hc_base_model, pos=nx.drawing.layout.circular_layout(hc_base_model), ax=ax, node_size=5000)
fig.savefig('hc_base')
ax.set_title('HC base model')
hc_base_model = BayesianNetwork(hc_base_model.edges())

#we estimate the parameter using the Bayesian Estimator
estimator = BayesianEstimator(model=hc_base_model, data=df_learn)

CPDs = []
#for every node we estimate the parameter and add them to the list
for node in hc_base_model.nodes():
    CPDs.append(estimator.estimate_cpd(node=node,
                                       prior_type="BDeu",
                                       equivalent_sample_size=3500))
hc_base_model.add_cpds(*CPDs)

inference = VariableElimination(hc_base_model)


def run_query(target_var, evidence):
    probs = []
    evidence["Enemy HP"] = int(encHPE.transform(np.array(evidence["Enemy HP"]).reshape((1, -1)))[0][0])
    evidence["Boost"] = int(encB.transform(np.array(evidence["Boost"]).reshape((1, -1)))[0][0])

    prob = inference.query([target_var],
                           evidence, )
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

encHP = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
encHP.fit(df_switch[["Pokemon HP"]])
df_switch["Pokemon HP"] = encHP.transform(df_switch[["Pokemon HP"]]).astype(int)
encHPE = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
encHPE.fit(df_switch[["Enemy HP"]])

df_switch["Enemy HP"] = encHPE.transform(df_switch[["Enemy HP"]]).astype(int)

df_learn = df_switch.drop(["Switch In","Switch out","enemy"],axis=1)
scorer = BDeuScore(data=df_learn)
hc = HillClimbSearch(data=df_learn)
hc_base_switch_model = hc.estimate(scoring_method=scorer, show_progress=False)

fig, ax = plt.subplots(1, 1, figsize=(12, 12))
nx.draw_networkx(hc_base_switch_model, pos=nx.drawing.layout.circular_layout(hc_base_switch_model), ax=ax, node_size=5000)
fig.savefig('hc_base')
ax.set_title('HC base model')
hc_base_switch_model = BayesianNetwork(hc_base_switch_model.edges())

#we estimate the parameter using the Bayesian Estimator
estimator = BayesianEstimator(model=hc_base_switch_model, data=df_learn)

CPDs = []
#for every node we estimate the parameter and add them to the list
for node in hc_base_switch_model.nodes():
    CPDs.append(estimator.estimate_cpd(node=node,
                                       prior_type="BDeu",
                                       equivalent_sample_size=3500))
hc_base_switch_model.add_cpds(*CPDs)

inferenceS = VariableElimination(hc_base_switch_model)


def switch_run_query(target_var, evidence):
    probs = []
    evidence["Pokemon HP"] = int(encHP.transform(np.array(evidence["Pokemon HP"]).reshape((1, -1)))[0][0])
    prob = inferenceS.query([target_var],
                            evidence,
                            show_progress=False)
    probs.append(prob.get_value(Switch=1))
    return probs[0]
