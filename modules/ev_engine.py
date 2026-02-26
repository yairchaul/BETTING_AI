from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.match_probability import calculate_match_probabilities

# =============================
# UTILIDADES
# =============================

def american_to_decimal(odd):

    odd = int(str(odd).replace("+",""))

    if odd > 0:
        return 1 + odd/100
    else:
        return 1 + 100/abs(odd)


def expected_value(prob, odd):

    decimal = american_to_decimal(odd)

    return prob * decimal - 1


# =============================
# ANALISIS PARTIDO
# =============================

def analyze_match(match):

    home = match["home"]
    away = match["away"]

    home_profile = build_team_profile(home)
    away_profile = build_team_profile(away)

    probs = calculate_match_probabilities(
        home_profile,
        away_profile
    )

    markets = [
        ("Local", probs["home"], match.get("home_odd")),
        ("Empate", probs["draw"], match.get("draw_odd")),
        ("Visita", probs["away"], match.get("away_odd")),
    ]

    candidates = []

    for name, prob, odd in markets:

        if not odd:
            continue

        ev = expected_value(prob, odd)

        if ev <= 0:
            continue

        candidates.append(
            PickResult(
                match=f"{home} vs {away}",
                selection=name,
                probability=round(prob,3),
                odd=american_to_decimal(odd),
                ev=round(ev,3)
            )
        )

    if not candidates:
        return None

    return max(candidates, key=lambda x: x.ev)


# =============================
# ANALISIS GLOBAL
# =============================

def analyze_matches(matches):

    results = []

    for m in matches:

        r = analyze_match(m)

        if r:
            results.append(r)

    return results


# =============================
# SMART PARLAY
# =============================

def build_smart_parlay(picks):

    if not picks:
        return None

    picks = sorted(picks, key=lambda x: x.ev, reverse=True)[:4]

    total_odd = 1
    total_prob = 1

    for p in picks:
        total_odd *= p.odd
        total_prob *= p.probability

    total_ev = total_prob * total_odd - 1

    return ParlayResult(
        matches=[p.match for p in picks],
        total_odd=round(total_odd,2),
        combined_prob=round(total_prob,3),
        total_ev=round(total_ev,3)
    )

