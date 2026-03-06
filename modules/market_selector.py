MARKET_STABILITY = {
    "Over 1.5": 1.0,
    "Over 2.5": 0.95,
    "BTTS Sí": 0.92,
    "Home Win": 0.90,
    "Away Win": 0.88,
    "Draw": 0.80
}


def score_market(market):

    prob = market["prob"]
    stability = MARKET_STABILITY.get(market["market"], 0.85)

    score = prob * stability

    market["score"] = score

    return market


def select_best_market(match):

    markets = match["markets"]

    markets = [m for m in markets if m["prob"] > 0.50]

    if not markets:
        return None

    scored = [score_market(m) for m in markets]

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[0]