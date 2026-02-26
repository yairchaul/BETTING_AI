import math
from typing import Dict, List, Optional
try:
    from modules.team_analyzer import build_team_profile
    from modules.schemas import PickResult, ParlayResult
except ImportError:
    from team_analyzer import build_team_profile
    from schemas import PickResult, ParlayResult

def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    return (prob * odd) - 1

def analyze_match(match: Dict) -> Optional[Dict]:
    h_name = match.get("home") or match.get("home_team")
    a_name = match.get("away") or match.get("away_team")
    odds = match.get("odds", {})

    # Análisis basado en tus últimos 5 partidos (build_team_profile)
    h_p = build_team_profile(h_name)
    a_p = build_team_profile(a_name)

    # Generación de Lambdas de goles
    lh = (h_p["attack"] / a_p["defense"]) * 1.25 * (0.8 + h_p["form_score"] * 0.4)
    la = (a_p["attack"] / h_p["defense"]) * 1.10 * (0.8 + a_p["form_score"] * 0.4)
    
    # 49 escenarios de resultados posibles
    sim = {
        f"Gana {h_name}": 0.0, f"Gana {a_name}": 0.0, "Empate": 0.0,
        "Ambos Anotan": 0.0, "Over 2.5": 0.0, "Under 2.5": 0.0,
        "Over 1.5": 0.0, "Over 3.5": 0.0
    }

    for i in range(7):
        for j in range(7):
            p = poisson_prob(lh, i) * poisson_prob(la, j)
            if i > j: sim[f"Gana {h_name}"] += p
            elif i == j: sim["Empate"] += p
            else: sim[f"Gana {a_name}"] += p
            if i > 0 and j > 0: sim["Ambos Anotan"] += p
            total_goles = i + j
            if total_goles > 1.5: sim["Over 1.5"] += p
            if total_goles > 2.5: sim["Over 2.5"] += p
            if total_goles > 3.5: sim["Over 3.5"] += p
            if total_goles < 2.5: sim["Under 2.5"] += p

    candidates = []
    for market, prob in sim.items():
        odd = odds.get(market)
        if odd:
            ev = calculate_ev(prob, float(odd))
            if ev > 0.02: # Filtro de Valor Esperado positivo
                candidates.append(PickResult(f"{h_name} vs {a_name}", market, prob, float(odd), ev))

    if not candidates: return None
    # Seleccionamos la opción con mejor relación riesgo/beneficio (EV)
    best = max(candidates, key=lambda x: x.ev)
    
    # Creamos un texto simplificado para el desglose
    reporte = "\n".join([f"{k}: {int(v*100)}%" for k, v in sim.items() if v > 0.1])
    return {"pick": best, "text": reporte}

def analyze_matches(matches: List[Dict]) -> List[Dict]:
    results = []
    for m in matches:
        res = analyze_match(m)
        if res: results.append(res)
    return results

def build_smart_parlay(picks: List[PickResult]) -> Optional[ParlayResult]:
    if not picks: return None
    # Tomamos los mejores 5 picks reales
    selected = sorted(picks, key=lambda x: x.ev, reverse=True)[:5]
    
    t_odd, t_prob = 1.0, 1.0
    for p in selected:
        t_odd *= p.odd
        t_prob *= p.probability
        
    return ParlayResult(
        matches=[f"{p.match} ({p.selection})" for p in selected],
        total_odd=round(t_odd, 2),
        combined_prob=round(t_prob, 3),
        total_ev=round(calculate_ev(t_prob, t_odd), 3)
    )

