from modules.team_profiles import TEAM_PROFILES


# =============================
# Obtener perfil seguro
# =============================
def get_team_profile(name):

    default = {
        "attack": 50,
        "defense": 50,
        "form": 50
    }

    return TEAM_PROFILES.get(name, default)


# =============================
# Probabilidades base
# =============================
def calculate_base_probabilities(home, away):

    attack_diff = home["attack"] - away["defense"]
    defense_diff = away["attack"] - home["defense"]
    form_diff = home["form"] - away["form"]

    home_score = 1 + attack_diff * 0.01 + form_diff * 0.01
    away_score = 1 + defense_diff * 0.01 - form_diff * 0.01
    draw_score = 1.0

    total = home_score + away_score + draw_score

    return {
        "home": home_score / total,
        "draw": draw_score / total,
        "away": away_score / total
    }


# =============================
# EV CALCULATION
# =============================
def expected_value(prob, odd):

    if odd is None:
        return -1

    return (prob * odd) - 1


# =============================
# ANALYZE SINGLE MATCH
# =============================
def analyze_match(match):

    home_profile = get_team_profile(match["home_team"])
    away_profile = get_team_profile(match["away_team"])

    probs = calculate_base_probabilities(
        home_profile,
        away_profile
    )

    options = [
        ("Local", probs["home"], match.get("home_odd")),
        ("Empate", probs["draw"], match.get("draw_odd")),
        ("Visitante", probs["away"], match.get("away_odd")),
    ]

    best_pick = None
    best_ev = -999

    for name, prob, odd in options:

        if odd is None:
            continue

        ev = expected_value(prob, odd)

        if ev > best_ev:
            best_ev = ev
            best_pick = name

    if best_ev <= 0:
        return None

    return {
        "match": f"{match['home_team']} vs {match['away_team']}",
        "pick": best_pick,
        "ev": round(best_ev, 3)
    }


# =============================
# ANALYZE ALL MATCHES
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
def build_smart_parlay(results):

    if not results:
        return []

    results.sort(key=lambda x: x["ev"], reverse=True)

    return results[:3]

