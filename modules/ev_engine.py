from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import analyze_team_strength
from modules.google_context import get_google_context
from modules.odds_api import get_market_odds # Usamos tu archivo odds_api.py
import math

def calculate_market_probabilities(stats, context, archetype):
    # Lógica de probabilidad realista (máximo 0.82) para evitar el error 0.95
    # Aquí se integran los datos de team_analyzer y google_context
    pass 

def analyze_matches(games):
    results = []
    for g in games:
        # 1. Análisis estadístico profundo
        stats = analyze_team_strength(g["home"], g["away"])
        # 2. Análisis de noticias/tendencias con Google
        context = get_google_context(g["home"], g["away"])
        # 3. Consulta de cuotas reales desde tu API en Secrets
        odds = get_market_odds(g["home"], g["away"])
        
        # Selección del mejor pick por partido basado en EV
        # ... (lógica de selección) ...
    return results

def build_smart_parlay(picks: List[PickResult]):
    """Calcula el parlay con mayor valor esperado real."""
    if len(picks) < 2: return None
    
    combined_odd = 1.0
    combined_prob = 1.0
    for p in picks:
        combined_odd *= p.odd
        combined_prob *= p.probability
        
    return ParlayResult(
        matches=[p.match for p in picks],
        total_odd=round(combined_odd, 2),
        combined_prob=round(combined_prob, 2),
        total_ev=round((combined_prob * combined_odd) - 1, 2)
    )
