# modules/ev_engine.py

from modules.schemas import Pick
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context
from modules.odds_api import get_market_odds


# ======================
# UTILIDADES
# ======================

def clamp(v, a=0, b=1):
    return max(a, min(v, b))


def expected_value(prob, odds):
    return prob * odds - 1


# ======================
# MODELADO PARTIDO
# ======================

def goal_rate(home, away):
    return (home["attack"] + away["attack"]) / 2


def corner_projection(home, away):
    avg = home["corners"] + away["corners"]

    if avg > 11:
        return 10.5
    if avg > 10:
        return 9.5
    if avg > 9:
        return 8.5
    return 7.5


# ======================
# PROBABILIDADES
# ======================

def prob_over15_ht(rate):
    return clamp(0.40 + rate * 0.35)


def prob_btts(home, away):
    return clamp(0.35 + (home["attack"] * away["attack"]) * 0.4)


def prob_over25(rate):
    return clamp(0.30 + rate * 0.6)


def prob_home_win(home, away):
    return clamp(0.45 + (home["attack"] - away["attack"]) * 0.4)


def prob_combo(win, over):
    return clamp(win * over * 1.2)


def prob_corners(home, away):
    avg = home["corners"] + away["corners"]
    return clamp(0.55 + (avg - 8) * 0.04)


# ======================
# BOOKMAKER HUNTER CORE
# ======================

def analyze_match(match):

    home = build_team_profile(match["home"])
    away = build_team_profile(match["away"])

    context = get_match_context(match["home"], match["away"])
    market = get_market_odds(match["home"], match["away"])

    rate = goal_rate(home, away)
    corner_line = corner_projection(home, away)

    markets = []

    # PRIORIDAD 1
    p_ht = prob_over15_ht(rate)
    markets.append(("Over 1.5 HT", p_ht, 2.1))

    # PRIORIDAD 2
    p_btts = prob_btts(home, away)
    markets.append(("BTTS Sí", p_btts, 1.9))

    # PRIORIDAD 3
    p_o25 = prob_over25(rate)
    markets.append(("Over 2.5 FT", p_o25, 2.0))

    # PRIORIDAD 4
    p_corner = prob_corners(home, away)
    markets.append((f"Over {corner_line} Corners", p_corner, 1.85))

    # PRIORIDAD 5
    p_home = prob_home_win(home, away)
    markets.append((f"{match['home']} gana", p_home, 2.2))

    # PRIORIDAD ELITE
    p_combo = prob_combo(p_home, p_o25)
    markets.append((f"{match['home']} gana + Over 1.5", p_combo, 3.2))

    # ======================
    # BOOKMAKER FILTER
    # ======================

    valid = []

    for name, prob, odd in markets:

        ev = expected_value(prob, odd)

        if prob < 0.60:
            continue

        if ev <= 0:
            continue

        # castigo por lesiones
        if "injury" in context:
            prob -= 0.05

        valid.append((name, prob, ev))

    if not valid:
        return None

    best = max(valid, key=lambda x: x[2])

    return Pick(
        match=f"{match['home']} vs {match['away']}",
        selection=best[0],
        probability=round(best[1],3),
        ev=round(best[2],3)
    )


# ======================
# ANALISIS GLOBAL
# ======================

def analyze_matches(matches):

    results = []

    for match in matches:

        pick = analyze_match(match)

        if pick:
            results.append(pick)

    return results
