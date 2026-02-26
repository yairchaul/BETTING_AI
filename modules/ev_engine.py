import math
from typing import Dict, List, Optional
from modules.schemas import PickResult, ParlayResult
from modules.team_profiles import TEAM_PROFILES

# ======================================
# CONFIGURACIÓN FILTROS (Ajustados para encontrar picks)
# ======================================
MIN_EV = 0.02    # Bajamos a 2% para ser menos restrictivos en la búsqueda inicial
MIN_PROB = 0.25  # Probabilidad mínima del 25%

# ======================================
# UTILIDADES MATEMÁTICAS
# ======================================
def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    if not odd or odd <= 0: return -1.0
    return (prob * odd) - 1

# ======================================
# LÓGICA DE PERFILES Y PROBABILIDADES
# ======================================
def get_team_profile(name):
    # Buscamos en TEAM_PROFILES, si no existe usamos valores promedio (50)
    return TEAM_PROFILES.get(name, {"attack": 50, "defense": 50, "form": 50})

def calculate_caliente_probabilities(home_name, away_name):
    h_p = get_team_profile(home_name)
    a_p = get_team_profile(away_name)

    # Convertimos escalas de 0-100 a Lambdas (Goles esperados)
    # Un equipo de 50 vs 50 resultará en aprox 1.25 goles por equipo
    lh = (h_p["attack"] / a_p["defense"]) * 1.25 * (0.9 + (h_p["form"] / 100) * 0.2)
    la = (a_p["attack"] / h_p["defense"]) * 1.10 * (0.9 + (a_p["form"] / 100) * 0.2)
    
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

# ======================================
# ANÁLISIS DE PARTIDO
# ======================================
def analyze_match(match: Dict) -> Optional[Dict]:
    # Normalización de nombres de llaves para compatibilidad total
    h_name = match.get("home") or match.get("home_team")
    a_name = match.get("away") or match.get("away_team")
    
    # Extraer cuotas del diccionario 'odds' o de llaves directas
    raw_odds = match.get("odds", {})
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

        ev = calculate_ev(prob, odd)
        reporte.append(f"{market}: {int(prob*100)}% | EV: {round(ev, 2)}")

        if ev >= MIN_EV and prob >= MIN_PROB:
            candidates.append({
                "market": market,
                "prob": prob,
                "odd": odd,
                "ev": ev
            })

    if not candidates: return None

    # Elegimos el mejor mercado EV+
    best = max(candidates, key=lambda x: x["ev"])
    
    # Construimos el objeto PickResult para el Parlay y el Main
    pick_obj = PickResult(
        match=f"{h_name} vs {a_name}",
        selection=best["market"],
        probability=round(best["prob"], 3),
        odd=best["odd"],
        ev=round(best["ev"], 3)
    )

    return {
        "pick": pick_obj,
        "text": "\n".join(reporte)
    }

def analyze_matches(matches: List[Dict]) -> List[Dict]:
    results = []
    for m in matches:
        res = analyze_match(m)
        if res: results.append(res)
    return results

def build_smart_parlay(picks: List[PickResult], max_picks=3) -> Optional[ParlayResult]:
    if not picks: return None
    # Ordenar por EV y tomar los mejores
    selected = sorted(picks, key=lambda x: x.ev, reverse=True)[:max_picks]
    
    t_odd = 1.0
    t_prob = 1.0
    for p in selected:
        t_odd *= p.odd
        t_prob *= p.probability
        
    return ParlayResult(
        matches=[p.match for p in selected],
        total_odd=round(t_odd, 2),
        combined_prob=round(t_prob, 3),
        total_ev=round(calculate_ev(t_prob, t_odd), 3)
    )
