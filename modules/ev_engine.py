from modules.schemas import Pick
from modules.montecarlo import market_probabilities


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
# INFERIR LAMBDAS
# ======================

def infer_lambdas(p_home, p_draw, p_away):

    total_goals = 2.6

    strength_home = p_home + 0.5 * p_draw
    strength_away = p_away + 0.5 * p_draw

    lambda_home = total_goals * strength_home
    lambda_away = total_goals * strength_away

    return lambda_home, lambda_away


# ======================
# CEREBRO CUÁNTICO
# ======================

def cascade_model(match):

    p_home = american_to_prob(match["home_odd"])
    p_draw = american_to_prob(match["draw_odd"])
    p_away = american_to_prob(match["away_odd"])

    p_home, p_draw, p_away = normalize_probs(
        p_home, p_draw, p_away
    )

    lambda_home, lambda_away = infer_lambdas(
        p_home, p_draw, p_away
    )

    probs = market_probabilities(lambda_home, lambda_away)

    home = match["home"]
    away = match["away"]

    options = [

        # GANADOR
        (f"Gana {home}", probs["HOME"], american_to_decimal(match["home_odd"])),
        (f"Gana {away}", probs["AWAY"], american_to_decimal(match["away_odd"])),

        # GOLES
        ("Over 1.5 Goles (Tiempo Completo)", probs["OVER15"], 1.40),
        ("Over 2.5 Goles (Tiempo Completo)", probs["OVER25"], 1.85),
        ("Over 3.5 Goles (Tiempo Completo)", probs["OVER35"], 2.40),

        # BTTS
        ("Ambos Equipos Anotan", probs["BTTS"], 1.75),

        # COMBOS REALES
        (f"{home} gana + Over 1.5", probs["HOME"] * probs["OVER15"], 2.2),
        (f"{away} gana + Over 1.5", probs["AWAY"] * probs["OVER15"], 2.3),

        (f"{home} gana + BTTS", probs["HOME"] * probs["BTTS"], 3.0),
        (f"{away} gana + BTTS", probs["AWAY"] * probs["BTTS"], 3.2),
    ]

    # ======================
    # FILTRO CASCADA REAL
    # ======================

    thresholds = [0.80, 0.72, 0.65, 0.60]

    for threshold in thresholds:

        valid = [o for o in options if o[1] >= threshold]

        if valid:
            best = max(valid, key=lambda x: x[2])

            return Pick(
                match=f"{home} vs {away}",
                selection=best[0],
                probability=round(best[1],3),
                odd=round(best[2],2),
            )

    return None


# ======================
# BUILDER PARLAY
# ======================

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
