# modules/ev_engine.py
from modules.stats_fetch import get_team_stats # Usando tus módulos existentes

def analyze_matches(ocr_results):
    final_picks = []
    for entry in ocr_results:
        # 1. Obtener data real de la API usando los equipos detectados
        teams = entry["potential_teams"]
        if len(teams) < 2: continue
        
        stats = get_team_stats(teams[0], teams[1]) # Análisis últimos 5 partidos
        
        # 2. EVALUACIÓN DE TODAS LAS POSIBILIDADES (La meta principal)
        # Aquí el motor simula: 1X2, BTTS, O/U 1.5, 2.5, 3.5 basándose en stats
        probabilities = run_montecarlo_sim(stats) # Usando tu montecarlo.py
        
        # 3. Comparación de Probabilidad vs Momio (EV+)
        best_market = None
        max_ev = -1
        
        # Mapeamos los momios detectados por el OCR a los mercados simulados
        for market, prob in probabilities.items():
            # Buscamos si el OCR detectó este mercado
            odd = find_matching_odd(market, entry["detected_odds"], entry["raw_text"])
            if odd:
                ev = (prob * odd) - 1
                if ev > max_ev:
                    max_ev = ev
                    best_market = {"selection": market, "prob": prob, "odd": odd, "ev": ev}
        
        if best_market and best_market["ev"] > 0:
            final_picks.append(best_market)
            
    return final_picks

