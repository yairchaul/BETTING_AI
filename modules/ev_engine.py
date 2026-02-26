from modules.schemas import PickResult
from modules.team_analyzer import analyze_team_strength
from modules.google_context import get_google_context
from modules.odds_provider import get_market_odds
import math

# --- 1. MODELOS DE PROBABILIDAD POR MERCADO (Matemática Independiente) ---

def model_1x2(gap, context):
    """Modelo para Local/Empate/Visitante basado en superioridad estructural."""
    # gap positivo = favorito local | gap negativo = favorito visitante
    p_home = 0.38 + (gap * 0.45) + (context * 0.05)
    p_away = 0.35 - (gap * 0.40) + (context * 0.05)
    p_draw = 0.27 - (abs(gap) * 0.15) 
    return {"Home Win": p_home, "Away Win": p_away, "Draw": p_draw}

def model_goals(expectancy, atq_total, def_total, archetype):
    """Modelo para Over/Under basado en ritmo y arquetipo."""
    base_over25 = (expectancy / 4) + (atq_total * 0.08) - (def_total * 0.04)
    
    # Ajuste por arquetipo
    if archetype == "PARK_THE_BUS":
        base_over25 -= 0.15
    elif archetype == "SHOOTOUT":
        base_over25 += 0.10
        
    return {
        "Over 1.5": base_over25 + 0.15,
        "Over 2.5": base_over25,
        "Under 3.5": 1 - (base_over25 - 0.10)
    }

def model_btts(atq_home, atq_away, def_home, def_away):
    """Modelo BTTS: ¿Tienen ambos capacidad de romper la defensa rival?"""
    prob = (atq_home * 0.25 + atq_away * 0.25) - (def_home * 0.1 + def_away * 0.1)
    return {"BTTS Yes": prob}

# --- 2. CLASIFICADOR DE ARQUETIPOS (El Corazón del Sistema) ---

def get_match_archetype(stats):
    gap = abs(stats["home_strength"] - stats["away_strength"])
    exp = stats["goal_expectancy"]
    
    if gap > 0.4: return "DOMINANT_FAVORITE"
    if exp > 3.2: return "SHOOTOUT"
    if exp < 2.1: return "GRIND_MATCH"
    if gap < 0.15 and exp < 2.5: return "BALANCED_STALEMATE"
    return "STANDARD_GAME"

# --- 3. PROCESADOR PRINCIPAL ---

def calculate_market_probabilities(stats, context, archetype):
    """Genera un diccionario con todas las probabilidades reales."""
    probs = {}
    gap = stats["home_strength"] - stats["away_strength"]
    atq_total = stats["attack_home"] + stats["attack_away"]
    def_total = stats["defense_home"] + stats["defense_away"]
    
    # Unificamos modelos
    probs.update(model_1x2(gap, context))
    probs.update(model_goals(stats["goal_expectancy"], atq_total, def_total, archetype))
    probs.update(model_btts(stats["attack_home"], stats["attack_away"], stats["defense_home"], stats["defense_away"]))
    
    # Aplicar Regla #3: Cap profesional (0.40 a 0.82)
    for market in probs:
        probs[market] = max(0.35, min(probs[market], 0.82))
        
    return probs

def analyze_matches(games):
    results = []
    for g in games:
        # Capa 1: Perfiles
        stats = analyze_team_strength(g["home"], g["away"])
        context = get_google_context(g["home"], g["away"])
        odds = get_market_odds(g["home"], g["away"])
        
        # Capa 2: Arquetipo
        archetype = get_match_archetype(stats)
        
        # Capa 3: Probabilidades Específicas
        probabilities = calculate_market_probabilities(stats, context, archetype)
        
        # Capa 4: Selección por EV (Edge Detection)
        best_pick = None
        max_edge = -999
        
        for market, odd in odds.items():
            if market in probabilities:
                prob = probabilities[market]
                ev = (prob * odd) - 1 # Fórmula inamovible
                
                # Sharp Adjustment: Penalizar mercados de alto volumen (Overs)
                if "Over" in market: ev -= 0.03 
                
                if ev > max_edge and ev > 0.05: # Solo picks con edge real > 5%
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

