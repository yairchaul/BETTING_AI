from modules.schemas import Pick
from modules.montecarlo import market_probabilities


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


def infer_lambdas(p_home, p_draw, p_away):

    total_goals = 2.6

    strength_home = p_home + 0.5 * p_draw
    strength_away = p_away + 0.5 * p_draw

    return (
        total_goals * strength_home,
        total_goals * strength_away,
    )


# ======================
# CASCADA UNIVERSAL
# ======================

def cascade_model(match):

    try:

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

            (f"Gana {home}", probs["HOME"], american_to_decimal(match["home_odd"])),

            (f"Gana {away}", probs["AWAY"], american_to_decimal(match["away_odd"])),

            ("Over 1.5 Goles (Tiempo Completo)", probs["OVER15"], 1.40),

            ("Over 2.5 Goles (Tiempo Completo)", probs["OVER25"], 1.85),

            ("Over 3.5 Goles (Tiempo Completo)", probs["OVER35"], 2.40),

            ("Ambos Equipos Anotan", probs["BTTS"], 1.75),

            (f"{home} gana + Over 1.5",
             probs["HOME"] * probs["OVER15"], 2.2),

            (f"{away} gana + Over 1.5",
             probs["AWAY"] * probs["OVER15"], 2.3),
        ]

        thresholds = [0.80, 0.72, 0.65, 0.60]

        for t in thresholds:

            valid = [o for o in options if o[1] >= t]

            if valid:

                best = max(valid, key=lambda x: x[2])

                return Pick(
                    match=f"{home} vs {away}",
                    selection=best[0],
                    probability=round(best[1],3),
                    odd=round(best[2],2),
                )

    except Exception as e:
        print("ERROR CASCADE:", e)

    return None


# ======================
# BUILDER
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
