import math
from typing import Dict, List, Optional
from modules.team_analyzer import build_team_profile
from modules.schemas import PickResult, ParlayResult

def poisson_prob(lambda_: float, k: int) -> float:
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

def calculate_ev(prob: float, odd: float) -> float:
    return (prob * odd) - 1

def analyze_match(match: Dict) -> Optional[Dict]:
    h_name = match.get("home") or match.get("home_team")
    a_name = match.get("away") or match.get("away_team")
    odds = match.get("odds", {}) # Diccionario con todos los mercados del OCR

    # 1. Obtener Data de los últimos 5 partidos
    h_p = build_team_profile(h_name)
    a_p = build_team_profile(a_name)

    # 2. Generar Lambdas (Goles esperados) basados en stats reales
    lh = (h_p["attack"] / a_p["defense"]) * 1.25 * (0.8 + h_p["form_score"] * 0.4)
    la = (a_p["attack"] / h_p["defense"]) * 1.10 * (0.8 + a_p["form_score"] * 0.4)
    
    # 3. Simulación Multimercado (Matriz de Poisson 7x7)
    probs = {
        f"Gana {h_name}": 0.0, f"Gana {a_name}": 0.0, "Empate": 0.0,
        "Ambos Anotan": 0.0, "Over 2.5": 0.0, "Under 2.5": 0.0,
        f"{h_name} y Over 1.5": 0.0, f"{h_name} y Over 2.5": 0.0,
        "Doble Op (L/E)": 0.0, "Doble Op (V/E)": 0.0
    }

    for i in range(7):
        for j in range(7):
            p = poisson_prob(lh, i) * poisson_prob(la, j)
            # Resultado Final
            if i > j: probs[f"Gana {h_name}"] += p
            elif i == j: probs["Empate"] += p
            else: probs[f"Gana {a_name}"] += p
            # Goles
            if i > 0 and j > 0: probs["Ambos Anotan"] += p
            if (i + j) > 2.5: probs["Over 2.5"] += p
            else: probs["Under 2.5"] += p
            # Combinados Caliente
            if i > j and (i + j) > 1.5: probs[f"{h_name} y Over 1.5"] += p
            if i > j and (i + j) > 2.5: probs[f"{h_name} y Over 2.5"] += p
            # Doble Oportunidad
            if i >= j: probs["Doble Op (L/E)"] += p
            if j >= i: probs["Doble Op (V/E)"] += p

    # 4. Encontrar la MEJOR opción entre todos los mercados detectados
    candidates = []
    for market_name, probability in probs.items():
        # Aquí es donde el OCR debe haber mapeado el nombre correctamente
        odd = odds.get(market_name)
        if odd and float(odd) > 1.0:
            ev = calculate_ev(probability, float(odd))
            if ev > 0.05: # Solo si hay ventaja > 5%
                candidates.append(PickResult(
                    match=f"{h_name} vs {a_name}",
                    selection=market_name,
                    probability=round(probability, 3),
                    odd=float(odd),
                    ev=round(ev, 3)
                ))

    # Retornamos la que tenga mayor EV (La decisión más correcta estadísticamente)
    if not candidates: return None
    best_pick = max(candidates, key=lambda x: x.ev)
    
    return {"pick": best_pick, "report": probs}
