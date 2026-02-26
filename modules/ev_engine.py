from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import analyze_team_strength
from modules.google_context import get_google_context
from modules.odds_api import get_market_odds 
from typing import List
import math

def calculate_market_probabilities(stats, context, archetype):
    """
    Combina estadística de equipo y contexto de noticias.
    Aplica el CAP de 0.82 para evitar el error de 0.95 constante.
    """
    # Lógica base usando la fuerza del equipo y el contexto de Google
    # gap positivo = local fuerte | context positivo = noticias a favor
    gap = stats["home_strength"] - stats["away_strength"]
    
    # Probabilidades base dinámicas
    prob_home = 0.45 + (gap * 0.3) + (context * 0.05)
    prob_over = (stats["goal_expectancy"] / 4.5) + (context * 0.02)
    
    # Creamos el diccionario de mercados
    probs = {
        "Home Win": prob_home,
        "Away Win": 0.35 - (gap * 0.25),
        "Draw": 0.30 - (abs(gap) * 0.1),
        "Over 2.5": prob_over,
        "BTTS Yes": (prob_over * 0.9)
    }

    # 🔥 REGLA DE ORO: Normalización profesional
    for market in probs:
        probs[market] = max(0.20, min(probs[market], 0.82))
        
    return probs

def analyze_matches(games):
    results = []
    for g in games:
        stats = analyze_team_strength(g["home"], g["away"])
        context = get_google_context(g["home"], g["away"])
        odds = get_market_odds(g["home"], g["away"]) # Desde tus Secrets
        
        # Obtenemos probabilidades reales
        probabilities = calculate_market_probabilities(stats, context, "STANDARD")
        
        best_pick = None
        max_edge = -999
        
        # Buscamos el mejor EV comparando Probabilidad vs Cuota Real
        for market, odd in odds.items():
            if market in probabilities:
                prob = probabilities[market]
                ev = (prob * odd) - 1
                
                if ev > max_edge and ev > 0.02: # Edge mínimo 2%
                    max_edge = ev
                    best_pick = PickResult(
                        match=f"{g['home']} vs {g['away']}",
                        selection=market,
                        probability=round(prob, 2),
                        odd=round(odd, 2),
                        ev=round(ev, 2)
                    )
        
        if best_pick:
            results.append(best_pick)
            
    return results

def build_smart_parlay(picks: List[PickResult]):
    """Selecciona los mejores 2 o 3 picks para crear una combinada de valor."""
    if len(picks) < 2: return None
    
    # Ordenamos por mayor EV para elegir los mejores 3
    top_picks = sorted(picks, key=lambda x: x.ev, reverse=True)[:3]
    
    combined_odd = 1.0
    combined_prob = 1.0
    for p in top_picks:
        combined_odd *= p.odd
        combined_prob *= p.probability
        
    return ParlayResult(
        matches=[f"{p.match} ({p.selection})" for p in top_picks],
        total_odd=round(combined_odd, 2),
        combined_prob=round(combined_prob, 2),
        total_ev=round((combined_prob * combined_odd) - 1, 2)
    )

