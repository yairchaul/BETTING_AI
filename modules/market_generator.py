def generate_markets(match):

    probs = match['probabilities']
    home = match['home_team']
    away = match['away_team']

    markets = []

    markets.append({
        "market": "Home Win",
        "label": f"Gana {home}",
        "prob": probs["home_win"]
    })

    markets.append({
        "market": "Draw",
        "label": "Empate",
        "prob": probs["draw"]
    })

    markets.append({
        "market": "Away Win",
        "label": f"Gana {away}",
        "prob": probs["away_win"]
    })

    markets.append({
        "market": "Over 1.5",
        "label": "Over 1.5",
        "prob": probs["over_1_5"]
    })

    markets.append({
        "market": "Over 2.5",
        "label": "Over 2.5",
        "prob": probs["over_2_5"]
    })

    markets.append({
        "market": "BTTS Sí",
        "label": "BTTS Sí",
        "prob": probs["btts_yes"]
    })

    return markets