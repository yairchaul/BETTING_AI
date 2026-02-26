try:
    from modules.montecarlo import run_simulations
    from modules.schemas import PickResult
    from modules.stats_fetch import get_team_stats
except ImportError:
    from montecarlo import run_simulations
    from schemas import PickResult
    from stats_fetch import get_team_stats

def obtener_mejor_apuesta(partido_data):
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])

    # 1. Obtener estadísticas reales
    stats = get_team_stats(home, away)
    
    # 2. Ejecutar simulación de Montecarlo para múltiples mercados
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    
    # Mapeo de mercados a sus momios correspondientes
    # Basado en la estructura de Caliente: [Local, Empate, Visitante]
    mapping = {
        "Resultado Final (Local)": 0,
        "Resultado Final (Empate)": 1,
        "Resultado Final (Visitante)": 2,
        "Total Goles Over 1.5": 0, # Usamos el momio local como referencia si no hay market de goles
        "Total Goles Under 2.5": 2
    }

    for mercado, prob in predicciones.items():
        idx = mapping.get(mercado)
        if idx is not None and len(all_odds) > idx:
            try:
                cuota_str = str(all_odds[idx]).replace('+', '')
                cuota = float(cuota_str)
                
                # FILTRO DE SEGURIDAD (Anti-Getafe +1150)
                if cuota > 500 or cuota < -1000: continue
                
                # Cálculo de Valor Esperado (EV)
                decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
                ev = (prob * decimal_odd) - 1

                # PRIORIZACIÓN: Le damos un pequeño bono al mercado "Resultado Final" 
                # para que no elija siempre Over/Under si el EV es similar.
                prioridad = 1.2 if "Resultado Final" in mercado else 1.0
                score_final = ev * prioridad

                if ev > 0.05 and prob > 0.35:
                    mejores_opciones.append(PickResult(
                        match=f"{home} vs {away}",
                        selection=mercado,
                        probability=prob,
                        odd=cuota,
                        ev=ev,
                        log=f"Prob: {int(prob*100)}% | EV: {round(ev,2)}"
                    ))
            except: continue
    
    # Retornar el pick con mejor relación Probabilidad/EV
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None
