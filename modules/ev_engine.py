from modules.schemas import PickResult, ParlayResult
from modules.team_analyzer import analyze_team_strength
from modules.google_context import get_google_context
from modules.odds_api import get_market_odds 
from typing import List
import math

def calculate_market_probabilities(stats, context):
    """Calcula probabilidades reales evitando el colapso de 0.95."""
    gap = stats.get("home_strength", 0) - stats.get("away_strength", 0)
    
    # Probabilidades dinámicas basadas en stats y contexto de noticias
    prob_home = max(0.20, min(0.45 + (gap * 0.3) + (context * 0.05), 0.82))
    prob_over = max(0.20, min((stats.get("goal_expectancy", 2.5) / 4.5) + (context * 0.02), 0.82))
    
    return {
        "Home Win": prob_home,
        "Away Win": max(0.15, 0.35 - (gap * 0.25)),
        "Draw": max(0.10, 0.30 - (abs(gap) * 0.1)),
        "Over 2.5": prob_over,
        "BTTS Yes": prob_over * 0.9
    }

def analyze_matches(games):
    results = []
    for g in games:
        # Integración de todos los motores de búsqueda y análisis
        stats = analyze_team_strength(g["home"], g["away"])
        context = get_google_context(g["home"], g["away"])
        odds = get_market_odds(g["home"], g["away"]) 
        
        probs = calculate_market_probabilities(stats, context)
        
        best_pick = None
        max_edge = -999
        
        for market, odd in odds.items():
            if market in probs:
                p = probs[market]
                ev = (p * odd) - 1
                if ev > max_edge and ev > 0.02:
                    max_edge = ev
                    best_pick = PickResult(
                        match=f"{g['home']} vs {g['away']}",
                        selection=market,
                        probability=round(p, 2),
                        odd=round(odd, 2),
                        ev=round(ev, 2)
                    )
        if best_pick: results.append(best_pick)
    return results

def build_smart_parlay(picks: List[PickResult]):
    if len(picks) < 2: return None
    top_picks = sorted(picks, key=lambda x: x.ev, reverse=True)[:3]
    
    c_odd = 1.0
    c_prob = 1.0
    for p in top_picks:
        c_odd *= p.odd
        c_prob *= p.probability
        
    return ParlayResult(
        matches=[f"{p.match} ({p.selection})" for p in top_picks],
        total_odd=round(c_odd, 2),
        combined_prob=round(c_prob, 2),
        total_ev=round((c_prob * c_odd) - 1, 2)
    )
