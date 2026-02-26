from modules.schemas import Pick
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context
from modules.odds_api import get_market_odds


# ======================
# UTILIDADES
# ======================

def clamp(v):
    return max(0, min(v, 1))


def expected_value(prob, odds):
    return (prob * odds) - 1


# ======================
# SHARP MONEY LOGIC
# ======================

def sharp_adjustment(context):

    penalty = 0

    if "injury" in context:
        penalty += 0.05

    if "rotation" in context:
        penalty += 0.04

    return penalty


# ======================
# ANALISIS PARTIDO
# ======================

def analyze_match(match):

    home = match["home"]
    away = match["away"]

    home_profile = build_team_profile(home)
    away_profile = build_team_profile(away)

    context = get_match_context(home, away)
    market = get_market_odds(home, away)

    attack_home = home_profile["attack"]
    attack_away = away_profile["attack"]

    avg_attack = (attack_home + attack_away) / 2
    avg_corners = home_profile["corners"] + away_profile["corners"]

    penalty = sharp_adjustment(context)

    # ======================
    # PROBABILIDADES IA
    # ======================

    p_over15_ht = clamp(0.45 + avg_attack * 0.35 - penalty)
    p_btts = clamp(0.40 + attack_home * attack_away * 0.3 - penalty)
    p_over25 = clamp(0.35 + avg_attack * 0.5 - penalty)
    p_corners = clamp(0.50 + (avg_corners - 9) * 0.05)

    p_home = clamp(0.45 + (attack_home - attack_away) * 0.35)

    # ======================
    # MERCADOS
    # ======================

    options = [

        ("Over 1.5 Goles 1er Tiempo", p_over15_ht, 2.1),

        ("Ambos Equipos Anotan", p_btts, 1.9),

        ("Over 2.5 Goles", p_over25, 2.0),

        (f"Over 9.5 Corners", p_corners, 1.85),

        (f"{home} gana", p_home, 2.2),

        (f"{home} gana + Over 1.5",
         clamp(p_home * p_over25 * 1.1),
         3.2),
    ]

    # ======================
    # SHARP FILTER
    # ======================

    valid = []

    for name, prob, odd in options:

        ev = expected_value(prob, odd)

        if prob < 0.63:
            continue

        if ev <= 0:
            continue

        valid.append((name, prob, ev))

    if not valid:
        return None

    best = max(valid, key=lambda x: x[2])

    return Pick(
        match=f"{home} vs {away}",
        selection=best[0],
        probability=round(best[1],3),
        ev=round(best[2],3),
    )


# ======================
# GLOBAL ANALYSIS
# ======================

def analyze_matches(matches):

    results = []

    for match in matches:

        pick = analyze_match(match)

        if pick:
            results.append(pick)

    return results

