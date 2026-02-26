from typing import Dict, List, Optional
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context
from modules.match_probability import calculate_match_probabilities

# ======================================
# CONFIG SHARP
# ======================================

MIN_EV = 0.08
MIN_PROB = 0.35


# ======================================
# EV CALCULATION
# ======================================

def calculate_ev(prob, odds):
    return (prob * odds) - 1


# ======================================
# ANALYZE SINGLE MATCH
# ======================================

def analyze_match(match: Dict) -> Optional[PickResult]:

    home = match.get("home")
    away = match.get("away")

    home_profile = build_team_profile(home)
    away_profile = build_team_profile(away)

    context = get_match_context(home, away)

    probabilities = calculate_match_probabilities(
        home_profile,
        away_profile,
        context
    )

    odds = match.get("odds", {})

    candidates = []

    for market, prob in probabilities.items():

        if market not in odds:
            continue

        ev = calculate_ev(prob, odds[market])

        if ev < MIN_EV:
            continue

        if prob < MIN_PROB:
            continue

        candidates.append(
            PickResult(
                match=f"{home} vs {away}",
                selection=market,
                probability=round(prob, 3),
                odd=odds[market],
                ev=round(ev, 3)
            )
        )

    if not candidates:
        return None

    # 🔥 Sharp choice
    return max(candidates, key=lambda x: x.ev)


# ======================================
# ANALYZE ALL MATCHES  ✅ (LO QUE FALTABA)
# ======================================

def analyze_matches(matches: List[Dict]) -> List[PickResult]:

    results = []

    for match in matches:

        r = analyze_match(match)

        if r:
            results.append(r)

    return results


# ======================================
# SMART PARLAY BUILDER ✅ (LO QUE FALTABA)
# ======================================

def build_smart_parlay(picks: List[PickResult], max_picks=4):

    if not picks:
        return None

    # ordenar por EV
    picks = sorted(picks, key=lambda x: x.ev, reverse=True)

    selected = picks[:max_picks]

    total_odds = 1
    combined_probability = 1

    for p in selected:
        total_odds *= p.odd
        combined_probability *= p.probability

    total_ev = calculate_ev(combined_probability, total_odds)

    return ParlayResult(
        picks=selected,
        total_odds=round(total_odds, 2),
        combined_probability=round(combined_probability, 3),
        total_ev=round(total_ev, 3)
    )
