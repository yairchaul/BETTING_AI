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
# LAMBDAS DESDE MERCADO
# ======================

def infer_lambdas(p_home, p_draw, p_away):

    total_goals = 2.6

    lambda_home = total_goals * (p_home + 0.5 * p_draw)
    lambda_away = total_goals * (p_away + 0.5 * p_draw)

    return lambda_home, lambda_away


# ======================
# EDGE REAL VS MERCADO
# ======================

def market_edge(model_prob, market_decimal):

    implied_market = 1 / market_decimal
    return model_prob - implied_market


# ======================
# MODELO CASCADA QUANT
# ======================
def cascade_model(match):

    # -------- PROBABILIDADES BASE ----------
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

    # ===============================
    # MERCADOS DERIVADOS IA
    # ===============================

    OVER15_FT = probs["OVER15"]
    OVER25_FT = probs["OVER25"]
    BTTS = probs["BTTS"]
    HOME = probs["HOME"]
    AWAY = probs["AWAY"]

    # ⚡ estimación goles 1T (≈45%)
    OVER15_HT = OVER15_FT * 0.65

    # ⚡ proxy corners (ritmo ofensivo)
    CORNERS_OVER = min(0.85, (l_home + l_away) / 3)

    # ===============================
    # TODAS LAS OPCIONES
    # ===============================

    options = [

        # NIVEL ELITE
        (f"{match['home']} gana + Over 1.5",
         HOME * OVER15_FT, 2.2),

        (f"{match['away']} gana + Over 1.5",
         AWAY * OVER15_FT, 2.3),

        # ATAQUE TEMPRANO
        ("Over 1.5 Goles (1er Tiempo)",
         OVER15_HT, 2.0),

        # GOLES ACTIVOS
        ("Ambos Equipos Anotan",
         BTTS, 1.85),

        ("Over 2.5 Goles (Tiempo Completo)",
         OVER25_FT, 2.0),

        # PRESIÓN
        ("Over Corners",
         CORNERS_OVER, 1.9),

        # BACKUP
        ("Over 1.5 Goles (Tiempo Completo)",
         OVER15_FT, 1.4),

        (f"Gana {match['home']}",
         HOME, american_to_decimal(match["home_odd"])),

        (f"Gana {match['away']}",
         AWAY, american_to_decimal(match["away_odd"])),
    ]

    # ===============================
    # FILTRO CASCADA REAL
    # ===============================

    valid = []

    for name, prob, odd in options:

        if prob < 0.60:
            continue

        EV = (prob * odd) - 1

        if EV <= 0:
            continue

        valid.append((name, prob, odd, EV))

    if not valid:
        return None

    # ⭐ ELEGIR MEJOR VALOR
    best = max(valid, key=lambda x: x[3])

    return Pick(
        match=f"{match['home']} vs {match['away']}",
        selection=best[0],
        probability=round(best[1],3),
        odd=round(best[2],2),
    )

# ======================
# CONSTRUCTOR PARLAY
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

