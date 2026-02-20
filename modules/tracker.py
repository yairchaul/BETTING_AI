import pandas as pd
from datetime import datetime

def guardar_pick(game, stake, ev):

    data = {
        "date":[datetime.now()],
        "game":[game],
        "stake":[stake],
        "ev":[ev],
        "result":[0],
        "closing_line":[0],
        "model_line":[0]
    }

    df = pd.DataFrame(data)

    df.to_csv(
        "data/history.csv",
        mode="a",
        header=False,
        index=False
    )