import math

# --------------------------
# Convertir Momio Americano
# --------------------------
def american_to_probability(odds):

    odds = float(odds)

    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


# --------------------------
# QUA NT MODEL (CORE)
# --------------------------
def model_probability(total_line):

    """
    Modelo base estilo sharp book.

    Luego aquí meteremos ML real.
    """

    base = 0.50

    # ligera ventaja simulada
    adjustment = (total_line - 220) * 0.001

    prob = base + adjustment

    return max(min(prob, 0.60), 0.40)


# --------------------------
# Expected Value
# --------------------------
def calculate_ev(model_prob, odds):

    odds = float(odds)

    if odds > 0:
        payout = odds / 100
    else:
        payout = 100 / abs(odds)

    ev = (model_prob * payout) - (1 - model_prob)

    return ev


# --------------------------
# AUTO EV SCANNER
# --------------------------
def scan_ev_opportunities(games):

    picks = []

    for g in games:

        market_prob = american_to_probability(g["odds_over"])

        model_prob = model_probability(g["total_line"])

        ev = calculate_ev(model_prob, g["odds_over"])

        if ev > 0:

            picks.append({
                "game": f"{g['away']} @ {g['home']}",
                "market_prob": round(market_prob,3),
                "model_prob": round(model_prob,3),
                "ev": round(ev,3),
                "odds": g["odds_over"],
                "line": g["total_line"]
            })

    # Ranking Sharp Style
    picks.sort(key=lambda x: x["ev"], reverse=True)

    return picks
