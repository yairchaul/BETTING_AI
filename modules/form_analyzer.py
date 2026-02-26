import numpy as np

def analyze_last5(matches):

    if not matches:
        return {
            "attack": 1.2,
            "defense": 1.2,
            "form_score": 0.5,
            "corners": 4
        }

    last5 = matches[-5:]

    gf = np.mean([m.get("gf",1) for m in last5])
    ga = np.mean([m.get("ga",1) for m in last5])
    corners = np.mean([m.get("corners",4) for m in last5])

    wins = sum(1 for m in last5 if m.get("gf",0) > m.get("ga",0))
    form_score = wins / len(last5)

    return {
        "attack": max(0.6, gf),
        "defense": max(0.6, ga),
        "corners": corners,
        "form_score": form_score
    }
