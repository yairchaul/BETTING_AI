import math
from typing import Dict, List, Optional
try:
    from modules.team_analyzer import build_team_profile
    from modules.schemas import PickResult, ParlayResult
except ImportError:
    from team_analyzer import build_team_profile
    from schemas import PickResult, ParlayResult

# Filtros Sharp para encontrar apuestas reales
MIN_EV = 0.03  # 3% de ventaja mínima
MIN_PROB = 0.20 # Probabilidad mínima (permite cuotas más altas)

def poisson_prob(lambda_: float, k: int) -> float:
    if lambda_ <= 0: return 1.0 if k == 0 else 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    return (prob * odd) - 1

def analyze_match(match: Dict) -> Optional[Dict]:
    h_name = match.get("home") or match.get("home_team")
    a_name = match.get("away") or match.get("away_team")
    odds = match.get("odds", {})

    # Stats de los últimos 5 partidos
    h_p = build_team_profile(h_name)
    a_p = build_team_profile(a_name)

    # Goles esperados (Lambdas)
    lh = (h_p["attack"] / a_p["defense"]) * 1.25 * (0.8 + h_p["form_score"] * 0.4)
    la = (a_p["attack"] / h_p["defense"]) * 1.10 * (0.8 + a_p["form_score"] * 0.4)
    
    # Simulación de mercados reales de Caliente
    probs = {
        f"Gana {h_name}": 0.0, f"Gana {a_name}": 0.0, "Empate": 0.0,
        "Ambos Anotan": 0.0, "Over 2.5": 0.0, "Under 2.5": 0.0,
        "Doble Op (L/E)": 0.0, "Doble Op (V/E)": 0.0
    }

    for i in range(7):
        for j in range(7):
            p = poisson_prob(lh, i) * poisson_prob(la, j)
            if i > j: probs[f"Gana {h_name}"] += p
            elif i == j: probs["Empate"] += p
            else: probs[f"Gana {a_name}"] += p
            if i > 0 and j > 0: probs["Ambos Anotan"] += p
            if (i + j) > 2.5: probs["Over 2.5"] += p
            else: probs["Under 2.5"] += p
            if i >= j: probs["Doble Op (L/E)"] += p
            if j >= i: probs["Doble Op (V/E)"] += p

    candidates = []
    reporte_text = ""
    
    for market, prob in probs.items():
        odd = odds.get(market)
        if odd and float(odd) > 1.0:
            ev = calculate_ev(prob, float(odd))
            reporte_text += f"{market}: {int(prob*100)}% | EV: {round(ev, 2)}\n"
            if ev >= MIN_EV:
                candidates.append(PickResult(
                    match=f"{h_name} vs {a_name}",
                    selection=market,
                    probability=round(prob,

