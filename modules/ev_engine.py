from modules.schemas import Pick
from modules.montecarlo import market_probabilities


# =========================
# UTILIDADES
# =========================

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


# =========================
# LAMBDAS DESDE CUOTAS
# =========================

def infer_lambdas(p_home, p_draw, p_away):

    # promedio goles global fútbol
    total_goals = 2.6

    strength_home = p_home + 0.5 * p_draw
    strength_away = p_away + 0.5 * p_draw

    lambda_home = total_goals * strength_home
    lambda_away = total_goals * strength_away

    return lambda_home, lambda_away


# =========================
# MODELO CASCADA
# =========================

def cascade_model(match):

    p_home = american_to_prob(match["home_odd"])
    p_draw = american_to_prob(match["draw_odd"])
    p_away = american_to_prob(match["away_odd"])

    p_home, p_draw, p_away = normalize_probs(p_home, p_draw, p_away)

    lambda_home, lambda_away = infer_lambdas(
        p_home, p_draw, p_away
    )

    probs = market_probabilities(lambda_home, lambda_away)

    options = []

    # PRIORIDAD 1 — COMBOS
    options.append(("Home + Over1.5", probs["HOME"] * probs["OVER15"], 2.0))
    options.append(("Away + Over1.5", probs["AWAY"] * probs["OVER15"], 2.2))

    # PRIORIDAD 2 — BTTS
    options.append(("Ambos Anotan", probs["BTTS"], 1.7))

    # PRIORIDAD 3 — OVER
    options.append(("Over 1.5 Goles", probs["OVER15"], 1.4))
    options.append(("Over 2.5 Goles", probs["OVER25"], 1.9))

    # PRIORIDAD 4 — 1X2
    options.append(("Gana Local", probs["HOME"], american_to_decimal(match["home_odd"])))
    options.append(("Empate", probs["DRAW"], american_to_decimal(match["draw_odd"])))
    options.append(("Gana Visitante", probs["AWAY"], american_to_decimal(match["away_odd"])))

    # =========================
    # FILTRO CASCADA
    # =========================

    valid = []

    for name, prob, odd in options:
        if prob >= 0.65:
            valid.append((name, prob, odd))

    if not valid:
        return None

    # elegir mayor cuota entre las válidas
    best = max(valid, key=lambda x: x[2])

    return Pick(
        match=f"{match['home']} vs {match['away']}",
        selection=best[0],
        probability=round(best[1], 3),
        odd=round(best[2], 2),
    )


# =========================
# BUILDER FINAL
# =========================

def build_parlay(games):

    results = []
    used_matches = set()

    for g in games:

        pick = cascade_model(g)

        if not pick:
            continue

        if pick.match in used_matches:
            continue

        used_matches.add(pick.match)
        results.append(pick)

    return results

