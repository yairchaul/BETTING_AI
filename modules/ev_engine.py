from modules.schemas import PickResult
from modules.team_analyzer import analyze_team_strength
from modules.google_context import get_google_context
from modules.odds_provider import get_market_odds
import math

# --- 1. MODELOS DE PROBABILIDAD POR MERCADO ---

def model_1x2(gap, context):
    """Calcula probabilidades para Local, Empate y Visitante."""
    p_home = 0.38 + (gap * 0.45) + (context * 0.05)
    p_away = 0.32 - (gap * 0.40) + (context * 0.05)
    p_draw = 0.30 - (abs(gap) * 0.20) 
    return {"Home Win": p_home, "Away Win": p_away, "Draw": p_draw}

def model_goals(expectancy, atq_total, def_total, archetype):
    """Calcula Over/Under basado en ritmo y arquetipo del partido."""
    base_over25 = (expectancy / 4.2) + (atq_total * 0.10) - (def_total * 0.05)
    
    if archetype == "PARK_THE_BUS":
        base_over25 -= 0.12
    elif archetype == "SHOOTOUT":
        base_over25 += 0.08
        
    return {
        "Over 1.5": base_over25 + 0.18,
        "Over 2.5": base_over25,
        "Under 3.5": 1.0 - (base_over25 - 0.15)
    }

def model_btts(atq_home, atq_away, def_home, def_away):
    """Calcula la probabilidad de Ambos Anotan."""
    prob = (atq_home * 0.20 + atq_away * 0.20) + (def_home * 0.05 + def_away * 0.05)
    return {"BTTS Yes": prob}

# --- 2. CLASIFICADOR DE ARQUETIPOS ---

def get_match_archetype(stats):
    """Detecta el tipo de partido para ajustar sesgos."""
    gap = abs(stats["home_strength"] - stats["away_strength"])
    exp = stats["goal_expectancy"]
    
    if gap > 0.45: return "DOMINANT_FAVORITE"
    if exp > 3.3: return "SHOOTOUT"
    if exp < 2.0: return "GRIND_MATCH"
    if gap < 0.15 and exp < 2.4: return "BALANCED_STALEMATE"
    return "STANDARD_GAME"

# --- 3. PROCESADOR PRINCIPAL ---

def calculate_market_probabilities(stats, context, archetype):
    """Une modelos y aplica el cap profesional (Regla de Oro)."""
    probs = {}
    gap = stats["home_strength"] - stats["away_strength"]
    atq_total = stats["attack_home"] + stats["attack_away"]
    def_total = stats["defense_home"] + stats["defense_away"]
    
    probs.update(model_1x2(gap, context))
    probs.update(model_goals(stats["goal_expectancy"], atq_total, def_total, archetype))
    probs.update(model_btts(stats["attack_home"], stats["attack_away"], stats["defense_home"], stats["defense_away"]))
    
    # 🔥 REGLA DE ORO: Normalización (Evita el error de 0.95 constante)
    for market in probs:
        probs[market] = max(0.18, min(probs[market], 0.82))
        
    return probs

def analyze_matches(games):
    """Ciclo de análisis completo para generar la lista de resultados."""
    results = []
    for g in games:
        stats = analyze_team_strength(g["home"], g["away"])
        context = get_google_context(g["home"], g["away"])
        odds = get_market_odds(g["home"], g["away"])
        
        archetype = get_match_archetype(stats)
        probabilities = calculate_market_probabilities(stats, context, archetype)
        
        best_pick = None
        max_edge = -999
        
        for market, odd in odds.items():
            if market in probabilities:
                prob = probabilities[market]
                ev = (prob * odd) - 1
                
                # Penalización por mercado de alto volumen (Overs)
                if "Over" in market: 
                    ev -= 0.04
                
                if ev > max_edge and ev > 0.05: # Edge mínimo del 5%
                    max_edge = ev
                    best_pick = PickResult(
                        match=f"{g['home']} vs {g['away']}",
                        selection=market,
                        probability=round(prob, 2),
                        odd=round(odd, 2), # Sincronizado con schemas.py y main.py
                        ev=round(ev, 2)
                    )
        
        if best_pick:
            results.append(best_pick)
            
    return results
