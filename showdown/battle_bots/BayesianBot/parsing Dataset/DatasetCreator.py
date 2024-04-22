from Parser import parser
import pandas as pd
import os

df = pd.DataFrame(columns=["User", "Sufferer", "name move", "TypesU",
                           "TypesS", "TypeM", "power", "UserHP", "SuffererHP"])
df2 = pd.DataFrame(
    columns=["Switch In", "Switch out", "enemy", "TypeIN", "TypeOUT", "TypeEnemy", "HPout", "HPEnemy", "Switch"])

for cartella, sottocartelle, files in os.walk(os.getcwd() + "\\log"):
    if not files.__contains__("Dataset.csv"):
        df.to_csv(".\\log\\Dataset.csv",
                  columns=["User", "Sufferer", "name move", "TypesU",
                           "TypesS", "TypeM", "power", "UserHP", "SuffererHP"], index=False)
    if not files.__contains__("Dataset-Switch.csv"):
        df2.to_csv(".\\log\\Dataset-Switch.csv",
                   columns=["Switch In", "Switch out", "enemy", "TypeIN",
                            "TypeOUT", "TypeEnemy", "HPout", "HPEnemy"], index=False)
    for file in files:
        if file == "Dataset.csv":
            continue
        if file == "Dataset-Switch.csv":
            continue
        with open(os.getcwd() + "\\log\\" + file, 'r+', encoding="utf8") as movefile:
            df = parser(movefile)

        dataset = pd.read_csv(os.getcwd() + "\\log\\" + "Dataset.csv")
        dataset = pd.concat([dataset, df[0]], ignore_index=True)
        dataset.to_csv(".\\log\\Dataset.csv", index=False)

        dataset2 = pd.read_csv(os.getcwd() + "\\log\\" + "Dataset-Switch.csv")
        dataset2 = pd.concat([dataset2, df[1]], ignore_index=True)
        dataset2.to_csv(".\\log\\Dataset-Switch.csv", index=False)
