import pandas as pd

def ajustar_modelo():

    try:
        df = pd.read_csv("data/history.csv")

        wins = len(df[df["result"] == 1])
        losses = len(df[df["result"] == 0])

        if wins + losses == 0:
            return 1

        accuracy = wins / (wins + losses)

        return 0.8 + accuracy

    except:
        return 1