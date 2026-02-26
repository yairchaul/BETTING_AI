# modules/ev_engine.py

import random
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile


# ======================================
# UTILIDADES
# ======================================

def clamp(x):
    return max(0.01, min(0.99, x))


def expected_value(prob, odd):
    return (prob * odd) - 1


# ======================================
# MATCH ARCHETYPE
# ======================================

def detect_archetype(home, away):

    tempo = (home["tempo"] + away["tempo"]) / 2
    diff = home["attack"] - away["attack"]

    if abs(diff) < 0.1:
        return "BALANCED"

    if tempo > 0.65:
        return "OPEN"

    if diff > 0.3:
        return "HOME_DOMINANT"

    return "DEFENSIVE"


# ======================================
# MARKET GENERATOR
# ======================================

def generate_markets(archetype, home, away):

    markets = []

    goal_rate = (home["attack"] + away["attack"]) / 2

    if archetype == "OPEN":
        markets.append(("Over 2.5 Goles", clamp(0.45 + goal_rate * 0.4), 2.05))
        markets.append(("BTTS Sí", clamp(0.50 + goal_rate * 0.3), 1.85))

    elif archetype == "BALANCED":
        markets.append(("Empate", clamp(0.30 + random.uniform(0,0.1)), 3.3))
        markets.append(("Under 3.5", clamp(0.60), 1.6))

    elif archetype == "HOME_DOMINANT":
        markets.append(("Gana Local", clamp(0.55), 2.0))
        markets.append(("Local + Over 1.5", clamp(0.45), 2.8))

    else:
        markets.append(("Under 2.5", clamp(0.58), 1.9))

    return markets


# ======================================
# ANALISIS PRINCIPAL
# ======================================

def analyze_match(match):

    home_profile = build_team_profile(match["home"])
    away_profile = build_team_profile(match["away"])

    archetype = detect_archetype(home_profile, away_profile)

    markets = generate_markets(
        archetype,
        home_profile,
        away_profile
    )

    candidates = []

    for name, prob, odd in markets:

        ev = expected_value(prob, odd)

        if ev <= 0:
            continue

        candidates.append(
            PickResult(
                match=f"{match['home']} vs {match['away']}",
                selection=name,
                probability=round(prob,3),
                odd=odd,
                ev=round(ev,3)
            )
        )

    if not candidates:
        return None

    # Sindicato elige mayor EV
    return max(candidates, key=lambda x: x.ev)


# ======================================
# ANALISIS GLOBAL
# ======================================

def analyze_matches(matches):

    results = []

    for match in matches:
        r = analyze_match(match)
        if r:
            results.append(r)

    return results


# ======================================
# PARLAY BUILDER (SYNDICATE)
# ======================================

def build_smart_parlay(picks):

    if not picks:
        return None

    # sindicato evita exceso de picks
    picks = sorted(picks, key=lambda x: x.ev, reverse=True)[:4]

    total_odd = 1
    combined_prob = 1
    matches = []

    for p in picks:
        total_odd *= p.odd
        combined_prob *= p.probability
        matches.append(p.match)

    total_ev = expected_value(combined_prob, total_odd)

    return ParlayResult(
        matches=matches,
        total_odd=round(total_odd,2),
        combined_prob=round(combined_prob,3),
        total_ev=round(total_ev,3)
    )
