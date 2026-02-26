def estimate_match_prob(home, away):

    total_attack = home["attack"] + away["attack"]

    prob_over25 = min(0.9, total_attack / 3)
    prob_btts = min(0.85, (home["attack"]*away["attack"]) / 4)

    prob_draw = 0.30 + abs(home["defense"]-away["defense"])*0.05

    return {
        "over25": prob_over25,
        "btts": prob_btts,
        "draw": prob_draw,
        "home_win": 0.40,
        "away_win": 0.30
    }
