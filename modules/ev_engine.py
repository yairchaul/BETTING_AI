# modules/ev_engine.py
import random
from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import build_team_profile
from modules.google_context import get_match_context

# ======================================
# UTILIDADES
# ======================================

def clamp(x):
    return max(0.01, min(0.99, x))

def expected_value(prob, odd):
    return (prob * odd) - 1

# ======================================
# PROBABILITY ENGINE (ACTUALIZADO CON MAPEO)
# ======================================

def calculate_base_probabilities(home, away):
    # Intentar obtener 'attack', si no existe buscar 'home_strength' o 'attack_home' como respaldo
    h_atk = home.get("attack", home.get("home_strength", home.get("attack_home", 0.5)))
    a_def = away.get("defense", away.get("away_strength", away.get("defense_away", 0.5)))
    
    h_tempo = home.get("tempo", 0.5)
    a_tempo = away.get("tempo", 0.5)

    attack_diff = h_atk - a_def
    tempo = (h_tempo + a_tempo) / 2

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
    # Mapeo de seguridad para evitar KeyError
    h_atk = home.get("attack", 0.5)
    a_atk = away.get("attack", 0.5)
    h_tempo = home.get("tempo", 0.5)
    a_tempo = away.get("tempo", 0.5)

    tempo = (h_tempo + a_tempo) / 2
    diff = h_atk - a_atk

    if abs(diff) < 0.1:
        return "BALANCED"
    if tempo > 0.65:
        return "OPEN"
    if diff > 0.3:
        return "HOME_DOMINANT"
    return "DEFENSIVE"

# ======================================
# MARKET GENERATOR (MEJORADO)
# ======================================

def generate_markets(archetype, home, away, probs, context):
    markets = []
    
    # Mapeo de seguridad
    h_atk = home.get("attack", 0.5)
    a_atk = away.get("attack", 0.5)

    goal_rate = (h_atk + a_atk) / 2
    tempo_boost = probs["tempo"] * 0.1
    hype_boost = context["importance"] * 0.05

    # =====================
    # OPEN GAME
    # =====================
    if archetype == "OPEN":
        over_prob = clamp(0.45 + goal_rate * 0.35 + tempo_boost)
        btts_prob = clamp(0.48 + goal_rate * 0.30)
        markets.append(("Over 2.5 Goles", over_prob, 2.05))
        markets.append(("BTTS Sí", btts_prob, 1.85))

    # =====================
    # BALANCED GAME
    # =====================
    elif archetype == "BALANCED":
        draw_prob = clamp(probs["draw"] + hype_boost)
        markets.append(("Empate", draw_prob, 3.3))
        markets.append(("Under 3.5", clamp(0.60), 1.6))

    # =====================
    # HOME DOMINANT
    # =====================
    elif archetype == "HOME_DOMINANT":
        home_win = clamp(probs["home"] + hype_boost)
        markets.append(("Gana Local", home_win, 2.0))
        markets.append(("Local + Over 1.5", clamp(home_win * 0.8), 2.8))

    # =====================
    # DEFENSIVE
    # =====================
    else:
        under_prob = clamp(0.55 + (1 - goal_rate) * 0.3)
        markets.append(("Under 2.5", under_prob, 1.9))

    return markets

# ======================================
# ANALISIS PRINCIPAL (CON FILTRO DE SEGURIDAD)
# ======================================

def analyze_match(match):
    # 1. Obtener perfiles
    home_profile = build_team_profile(match["home"])
    away_profile = build_team_profile(match["away"])
    
    # 2. Obtener contexto
    context = get_match_context(match["home"], match["away"])

    # 3. Probabilidades base
    probs = calculate_base_probabilities(home_profile, away_profile)

    # 4. Arquetipo
    archetype = detect_archetype(home_profile, away_profile)

    # 5. Generar Mercados
    markets = generate_markets(
        archetype,
        home_profile,
        away_profile,
        probs,
        context
    )

    candidates = []
    for name, prob, odd in markets:
        # SHARP MONEY ADJUSTMENT
        prob += context["importance"] * 0.03
        prob -= context["injuries"] * 0.02
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
# PARLAY BUILDER (SYNDICATE)
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
