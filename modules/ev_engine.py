from modules.schemas import PickResult
from modules.team_analyzer import analyze_team_strength
from modules.google_context import get_google_context
from modules.odds_provider import get_market_odds
import math

# --- 1. MODELOS DE PROBABILIDAD INDEPENDIENTES ---

def model_1x2(gap, context):
    """Calcula probabilidades para Local, Empate y Visitante."""
    # El gap representa la diferencia de fuerza estructural entre equipos
    p_home = 0.38 + (gap * 0.45) + (context * 0.05)
    p_away = 0.32 - (gap * 0.40) + (context * 0.05)
    p_draw = 0.30 - (abs(gap) * 0.20) # El empate es más probable si el gap es cercano a 0
    return {"Home Win": p_home, "Away Win": p_away, "Draw": p_draw}

def model_goals(expectancy, atq_total, def_total, archetype):
    """Calcula probabilidades de Over/Under basadas en ritmo y defensas."""
    # Base calculada sobre la expectativa de goles (goal_expectancy)
    base_over25 = (expectancy / 4.2) + (atq_total * 0.10) - (def_total * 0.05)
    
    # Ajustes dinámicos por Arquetipo de partido
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
    """Calcula la probabilidad de que ambos equipos anoten."""
    prob = (atq_home * 0.20 + atq_away * 0.20) + (def_home * 0.05 + def_away * 0.05)
    return {"BTTS Yes": prob}

# --- 2. CLASIFICADOR DE ARQUETIPOS (MAC) ---

def get_match_archetype(stats):
    """Clasifica el partido para aplicar sesgos correctivos profesionales."""
    gap = abs(stats["home_strength"] - stats["away_strength"])
    exp = stats["goal_expectancy"]
    
    if gap > 0.45: return "DOMINANT_FAVORITE"
    if exp > 3.3: return "SHOOTOUT"
    if exp < 2.0: return "GRIND_MATCH"
    if gap < 0.15 and exp < 2.4: return "BALANCED_STALEMATE"
    return "STANDARD_GAME"

# --- 3. PROCESADOR DE MERCADOS ---

def calculate_market_probabilities(stats, context, archetype):
