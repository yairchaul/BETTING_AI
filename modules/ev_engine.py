# modules/ev_engine.py

import random

from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context


# ======================================
# SAFE PROFILE NORMALIZER ⭐ NUEVO
# ======================================

def normalize_profile(profile):

    return {
        "attack": profile.get("attack")
                  or profile.get("attack_rating")
                  or random.uniform(0.4, 0.7),

        "defense": profile.get("defense")
                   or profile.get("defense_rating")
                   or random.uniform(0.4, 0.7),

        "tempo": profile.get("tempo")
                 or random.uniform(0.45, 0.75)
    }


# ======================================
# UTILIDADES
# ======================================

def clamp(x):
    return max(0.01, min(0.99, x))


def expected_value(prob, odd):
    return (prob * odd) - 1


# ======================================
# PROBABILITY ENGINE
# ======================================

def calculate_base_probabilities(home, away):

    attack_diff = home["attack"] - away["defense"]
    tempo = (home["tempo"] + away["tempo"]) / 2

    home_prob = clamp(0.40 + attack_diff * 0.25)
    draw_prob = clamp(0.22 + (1 - abs(attack_diff)) * 0.1)
    away_prob = clamp(1 - home_prob - draw_prob)

    return {
        "home": home_prob,
        "draw": draw_prob,
        "away": away_prob,
        "tempo": tempo
    }


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

def generate_markets(archetype, home, away, probs, context):

    markets = []

    goal_rate = (home["attack"] + away["attack"]) / 2
    tempo_boost = probs["tempo"] * 0.1
    hype_boost = context.get("importance", 0.5) * 0.05

    if archetype == "OPEN":

        markets.append(
            ("Over 2.5 Goles",
             clamp(0.45 + goal_rate * 0.35 + tempo_boost),
             2.05)
        )

        markets.append(
            ("BTTS Sí",
             clamp(0.48 + goal_rate * 0.30),
             1.85)
        )

    elif archetype == "BALANCED":

        markets.append(
            ("Empate",
             clamp(probs["draw"] + hype_boost),
             3.3)
        )

        markets.append(("Under 3.5", 0.60, 1.6))

    elif archetype == "HOME_DOMINANT":

        home_win = clamp(probs["home"] + hype_boost)

        markets.append(("Gana Local", home_win, 2.0))
        markets.append(("Local + Over 1.5", clamp(home_win * 0.8), 2.8))

    else:

        markets.append(("Under 2.5", clamp(0.55), 1.9))

    return markets


# ======================================
# ANALISIS PRINCIPAL
# ======================================

def analyze_match(match):

    raw_home = build_team_profile(match["home"])
    raw_away = build_team_profile(match["away"])

    # ⭐ NORMALIZACIÓN ANTI-ERROR
    home_profile = normalize_profile(raw_home)
    away_profile = normalize_profile(raw_away)

    context = get_match_context(match["home"], match["away"])

    probs = calculate_base_probabilities(
        home_profile,
        away_profile
    )

    archetype = detect_archetype(home_profile, away_profile)

    markets = generate_markets(
        archetype,
        home_profile,
        away_profile,
        probs,
        context
    )

    candidates = []

    for name, prob, odd in markets:

        prob += context.get("importance", 0.5) * 0.03
        prob -= context.get("injuries", 0.2) * 0.02

        prob = clamp(prob)

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
# PARLAY BUILDER
# ======================================

def build_smart_parlay(picks):

    if not picks:
        return None

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
