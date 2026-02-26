import numpy as np

def analyze_last5(team_stats):

    last5 = team_stats[-5:]

    goles_favor = np.mean([m["gf"] for m in last5])
    goles_contra = np.mean([m["ga"] for m in last5])
    corners = np.mean([m.get("corners",0) for m in last5])

    return {
        "attack": goles_favor,
        "defense": goles_contra,
        "corners": corners
    }
