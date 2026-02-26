import math
from typing import Dict, List, Optional

# --- IMPORTACIÓN DINÁMICA ---
try:
    from modules.team_analyzer import build_team_profile
    from modules.schemas import PickResult, ParlayResult
except ModuleNotFoundError:
    from .team_analyzer import build_team_profile
    from .schemas import PickResult, ParlayResult

# Configuración Sharp
MIN_EV = 0.02
MIN_PROB = 0.25

def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    if not odd or odd <= 0: return -1.0
    return (prob * odd) - 1

def calculate_caliente_probabilities(home_name: str, away_name: str):
    # Usamos tu analizador de últimos 5 partidos
    h_p = build_team_profile(home_name)
    a_p = build_team_profile(away_name)

    # Convertimos los scores de forma y ataque en Lambdas de goles
    # Usamos form_score que viene de tu analyze_last5
    lh = (h_p["attack"] / a_p["defense"]) * 1.25 * (0.8 + h_p["form_score"] * 0.4)
    la = (a_p["attack"] / h_p["defense"]) * 1.10 * (0.8 + a_p["form_score"] * 0.4)
    
    p_win_h, p_draw, p_win_a = 0.0, 0.0, 0.0
    p_btts, p_o25 = 0.0, 0.0

    for i in range(7):
        for j in range(7):
            prob = poisson_prob(lh, i) * poisson_prob(la, j)
            if i > j: p_win_h += prob
            elif i == j: p_draw += prob
            else: p_win_a += prob
            
            if i > 0 and j > 0: p_btts += prob
            if (i + j) > 2.5: p_o25 += prob

    return {
        "Gana Local": p_win_h,
        "Empate": p_draw,
        "Gana Visitante": p_win_a,
        "Ambos Anotan": p_btts,
        "Over 2.5 Goles": p_o25
    }

def analyze_match(match: Dict) -> Optional[Dict]:
    # Compatibilidad de nombres de equipo
    h_name = match.get("home") or match.get("home_team")
    a_name = match.get("away") or match.get("away_team")
    
    if not h_name or not a_name: return None

    raw_odds = match.get("odds", {})
    # Mapeo flexible de cuotas
    odds_map = {
        "Gana Local": raw_odds.get("Gana Local") or match.get("home_odd"),
        "Empate": raw_odds.get("Empate") or match.get("draw_odd"),
        "Gana Visitante": raw_odds.get("Gana Visitante") or match.get("away_odd"),
        "Ambos Anotan": raw_odds.get("Ambos Anotan"),
        "Over 2.5 Goles": raw_odds.get("Over 2.5 Goles")
    }

    probs = calculate_caliente_probabilities(h_name, a_name)
    candidates = []
    reporte = []

    for market, prob in probs.items():
        odd = odds_map.get(market)
        if not odd: continue
        
        ev = calculate_ev(prob, float(odd))
        reporte.append(f"{market}: {int(prob*100)}% | EV: {round(ev, 2)}")
        
        if ev >= MIN_EV and prob >= MIN_PROB:
            candidates.append({"market": market, "prob": prob, "odd": float(odd), "ev": ev})

    if not

