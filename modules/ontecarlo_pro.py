import numpy as np


def run_montecarlo(lambda_home, lambda_away, simulations=10000):

    home_goals = np.random.poisson(lambda_home, simulations)
    away_goals = np.random.poisson(lambda_away, simulations)

    home_wins = np.sum(home_goals > away_goals) / simulations
    draws = np.sum(home_goals == away_goals) / simulations
    away_wins = np.sum(home_goals < away_goals) / simulations

    total_goals = home_goals + away_goals

    over15 = np.sum(total_goals >= 2) / simulations
    over25 = np.sum(total_goals >= 3) / simulations
    over35 = np.sum(total_goals >= 4) / simulations

    btts = np.sum((home_goals > 0) & (away_goals > 0)) / simulations

    return {
        "home_win": home_wins,
        "draw": draws,
        "away_win": away_wins,
        "over_1_5": over15,
        "over_2_5": over25,
        "over_3_5": over35,
        "btts_yes": btts
    }