# modules/ev_engine.py

import math
import random


# =============================
# UTILIDADES
# =============================

def clamp(v, min_v=0, max_v=1):
    return max(min_v, min(v, max_v))


def expected_value(prob, odds):
    return (prob * odds) - 1


# =============================
# MODELO ESTADISTICO BASE
# =============================

def estimate_goal_rate(home_attack, away_attack):
    """
    Calcula intensidad ofensiva del partido
    """
    return (home_attack + away_attack) / 2


def estimate_corner_line(home_corners, away_corners):

    avg = (home_corners + away_corners) / 2

    if avg >= 11:
        return 10.5
    elif avg >= 10:
        return 9.5
    elif avg >= 9:
        return 8.5
    else:
        return 7.5


# =============================
# PROBABILIDADES
# =============================

def prob_over15_ht(goal_rate):

    base = 0.45 + goal_rate * 0.35
    variance = random.uniform(-0.05, 0.05)

    return clamp(base + variance)


def prob_btts(home_attack, away_attack):

    strength = (home_attack * away_attack)
    base = 0.40 + strength * 0.5

    return clamp(base)


def prob_over25(goal_rate):

    base = 0.35 + goal_rate * 0.55
    return clamp(base)


def prob_corners(avg_corners):

    base = 0.55 + (avg_corners - 8) * 0.05
    return clamp(base)


def prob_home_win(home_attack, away_attack):

    diff = home_attack - away_attack
    base = 0.45 + diff * 0.4

    return clamp(base)


def prob_win_over(home_win_prob, over_prob):

    combo = home_win_prob * over_prob * 1.15
    return clamp(combo)


# =============================
# ANALISIS PRINCIPAL
# =============================

def analyze_match(match):

    # datos simulados provenientes de motores
    home_attack = match.get("home_attack", random.uniform(0.9, 1.6))
    away_attack = match.get("away_attack", random.uniform(0.9, 1.6))

    home_corners = match.get("home_corners", random.uniform(4,7))
    away_corners = match.get("away_corners", random.uniform(4,7))

    goal_rate = estimate_goal_rate(home_attack, away_attack)

    avg_corners = home_corners + away_corners
    corner_line = estimate_corner_line(home_corners, away_corners)

    # =====================
    # MERCADOS
    # =====================

    markets = []

    # Over 1.5 HT
    p_ht = prob_over15_ht(goal_rate)
    markets.append({
        "market": "Over 1.5 Goles 1er Tiempo",
        "prob": p_ht,
        "odds": 2.1
    })

    # BTTS
    p_btts = prob_btts(home_attack, away_attack)
    markets.append({
        "market": "Ambos Equipos Anotan",
        "prob": p_btts,
        "odds": 1.9
    })

    # Over 2.5 FT
    p_o25 = prob_over25(goal_rate)
    markets.append({
        "market": "Over 2.5 Goles",
        "prob": p_o25,
        "odds": 2.0
    })

    # Corners dinámicos
    p_corner = prob_corners(avg_corners)
    markets.append({
        "market": f"Over {corner_line} Corners",
        "prob": p_corner,
        "odds": 1.85
    })

    # Ganador local
    p_home = prob_home_win(home_attack, away_attack)
    markets.append({
        "market": "Gana Local",
        "prob": p_home,
        "odds": 2.2
    })

    # Combo
    p_combo = prob_win_over(p_home, p_o25)
    markets.append({
        "market": "Local gana + Over 1.5",
        "prob": p_combo,
        "odds": 3.0
    })

    # =====================
    # COMPETENCIA EV
    # =====================

    for m in markets:
        m["ev"] = expected_value(m["prob"], m["odds"])

    # SOLO apuestas positivas
    positive = [m for m in markets if m["ev"] > 0]

    if not positive:
        return None

    best = max(positive, key=lambda x: x["ev"])

    return best


# =============================
# ANALISIS GLOBAL
# =============================

def analyze_matches(matches):

    results = []

    for match in matches:

        analysis = analyze_match(match)

        if analysis:
            results.append({
                "match": f"{match['home']} vs {match['away']}",
                "pick": analysis["market"],
                "prob": round(analysis["prob"],3),
                "ev": round(analysis["ev"],3)
            })

    return results


