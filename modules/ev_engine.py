from modules.schemas import Pick
from modules.montecarlo import market_probabilities
from modules.odds_api import get_market_odds
from modules.google_context import get_match_context


# ======================
# CONVERSIONES
# ======================

def american_to_prob(odd):

    odd = int(odd)

    if odd > 0:
        return 100 / (odd + 100)
    else:
        return abs(odd) / (abs(odd) + 100)


def american_to_decimal(odd):

    odd = int(odd)

    if odd > 0:
        return 1 + odd / 100
    else:
        return 1 + 100 / abs(odd)


def normalize_probs(p_home, p_draw, p_away):

    total = p_home + p_draw + p_away

    return (
        p_home / total,
        p_draw / total,
        p_away / total,
    )


# ======================
# LAMBDAS
# ======================

def infer_lambdas(p_home, p_draw, p_away):

    total_goals = 2.6

    lambda_home = total_goals * (p_home + 0.5 * p_draw)
    lambda_away = total_goals * (p_away + 0.5 * p_draw)

    return lambda_home, lambda_away


# ======================
# EDGE CHECK
# ======================

def market_edge(ticket_prob, market_decimal):

    implied_market = 1 / market_decimal

    return ticket_prob - implied_market


# ======================
# MODELO CASCADA IA
# ======================

def cascade_model(match):

    # --- PROBS DESDE TICKET ---
    p_home = american_to_prob(match["home_odd"])
    p_draw = american_to_prob(match["draw_odd"])
    p_away = american_to_prob(match["away_odd"])

    p_home, p_draw, p_away = normalize_probs(
        p_home, p_draw, p_away
    )

    l_home, l_away = infer_lambdas(
        p_home, p_draw, p_away
    )

    probs = market_probabilities(l_home, l_away)

    # --- MERCADO REAL ---
    market_odds = get_market_odds(
        match["home"], match["away"]
    )

    # --- CONTEXTO IA ---
    context = get_match_context(
        match["home"], match["away"]
    )

    injury_penalty = 0.05 if "injury" in context else 0

    # ======================
    # OPCIONES CASCADA
    # ======================

    options = [

        (f"{match['home']} gana + Over 1.5",
         probs["HOME"] * probs["OVER15"] - injury_penalty,
         2.1),

        (f"{match['away']} gana + Over 1.5",
         probs["AWAY"] * probs["OVER15"] - injury_penalty,
         2.2),

        ("BTTS Sí",
         probs["BTTS"],
         1.8),

        ("Over 2.5 Goles (Tiempo Completo)",
         probs["OVER25"],
         2.0),

        ("Over 1.5 Goles (Tiempo Completo)",
         probs["OVER15"],
         1.4),
    ]

    # ======================
    # FILTRO IA
    # ======================

    valid = []

    for name, prob, odd in options:

        if prob < 0.70:
            continue

        edge = 0

        if market_odds:
            for key, val in market_odds.items():
                edge = market_edge(prob, val)

        if edge < -0.02:
            continue

        valid.append((name, prob, odd))

    if not valid:
        return None

    best = max(valid, key=lambda x: x[2])

    return Pick(
        match=f"{match['home']} vs {match['away']}",
        selection=best[0],
        probability=round(best[1], 3),
        odd=round(best[2], 2),
    )


# ======================
# BUILDER FINAL
# ======================

def build_parlay(games):

    results = []
    used = set()

    for g in games:

        pick = cascade_model(g)

        if not pick:
            continue

        if pick.match in used:
            continue

        used.add(pick.match)
        results.append(pick)

    return results

