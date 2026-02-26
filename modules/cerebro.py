# modules/cerebro.py - El motor de decisión real
from modules.montecarlo import run_simulation
from modules.stats_fetch import get_last_5_games_stats

def get_best_option_per_match(home, away, detected_odds):
    # 1. Obtener data real de los últimos 5 partidos (API)
    stats = get_last_5_games_stats(home, away)
    
    # 2. Simular TODOS los mercados que enlistaste
    # Resultado Final, BTTS, O/U 1.5/2.5/3.5, etc.
    sim_results = run_simulation(stats) 
    
    best_market = None
    highest_ev = -1.0
    
    # 3. Comparar cada probabilidad simulada contra los momios reales
    for market_name, probability in sim_results.items():
        # Buscamos el momio correspondiente en lo que detectó el OCR
        current_odd = match_odd_to_market(market_name, detected_odds)
        
        if current_odd:
            ev = (probability * current_odd) - 1
            # El sistema elige la "decisión más correcta" por probabilidad y valor
            if ev > highest_ev:
                highest_ev = ev
                best_market = {
                    "match": f"{home} vs {away}",
                    "selection": market_name,
                    "prob": probability,
                    "odd": current_odd,
                    "ev": ev
                }
    return best_market
