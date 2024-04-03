from Parser import parser
import pandas as pd


with open("Gen7RandomBattle-2024-03-27-eimint64-shnen.log", 'r+') as movefile:
    df = parser(movefile)


    df.to_csv("Gen7RandomBattle-2024-03-27-eimint64-shnen.csv")