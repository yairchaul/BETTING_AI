try:
    from modules.stats_fetch import get_team_stats
    from modules.montecarlo import run_simulations
    from modules.schemas import PickResult
except ImportError:
    from stats_fetch import get_team_stats
    from montecarlo import run_simulations
    from schemas import PickResult

def obtener_mejor_apuesta(partido_data):
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])

    # 1. Análisis de los últimos 5 partidos
    stats = get_team_stats(home, away)
    
    # 2. Simulación de los 13 mercados
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    auditoria = []

    for mercado, prob in predicciones.items():
        # Asignación de momio detectado en la imagen
        cuota = asignar_cuota_real(mercado, all_odds)
        
        if cuota:
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1
            
            # Guardamos para la bitácora
            auditoria.append(f"{mercado}: Prob {int(prob*100)}% | Momio: {cuota} | EV: {round(ev,2)}")
            
            if ev > 0.05: # Solo mercados con ventaja real
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev,
                    log="\n".join(auditoria[-3:]) # Guardamos los últimos análisis
                ))
    
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None
