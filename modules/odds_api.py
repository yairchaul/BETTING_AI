import random

def get_market_odds(home, away):
    """
    Simulación odds.
    Luego conectamos OddsAPI real.
    """

    return {
        "Home Win": random.uniform(1.6, 3.2),
        "Draw": random.uniform(2.8, 4.5),
        "Away Win": random.uniform(2.0, 4.0),
        "Over 1.5": random.uniform(1.2, 1.6),
        "Over 2.5": random.uniform(1.7, 2.5),
        "BTTS Yes": random.uniform(1.6, 2.2),
        "Under 3.5": random.uniform(1.4, 1.9)
    }
