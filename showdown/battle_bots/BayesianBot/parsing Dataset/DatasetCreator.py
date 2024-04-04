from Parser import parser
import pandas as pd
import os

df = pd.DataFrame(columns=["User", "Sufferer", "name move", "TypesU",
                           "TypesS", "TypeM", "power", "UserHP", "SuffererHP"])
for cartella, sottocartelle, files in os.walk(os.getcwd() + "\\log"):
    if not files.__contains__("Dataset.csv"):
        df.to_csv(".\\log\\Dataset.csv",
                  columns=["User", "Sufferer", "name move", "TypesU",
                           "TypesS", "TypeM", "power", "UserHP", "SuffererHP"],index=False)
    for file in files:
        if file == "Dataset.csv":
            continue
        with open(os.getcwd() + "\\log\\" + file, 'r+') as movefile:
            df = parser(movefile)
            print(df)

        dataset = pd.read_csv(os.getcwd() + "\\log\\" + "Dataset.csv")
        print(dataset)
        dataset = pd.concat([dataset, df], ignore_index=True)
        dataset.to_csv(".\\log\\Dataset.csv",index=False)
