try:
    from modules.montecarlo import run_simulations
    from modules.schemas import PickResult
    from modules.stats_fetch import get_team_stats
except ImportError:
    from montecarlo import run_simulations
    from schemas import PickResult
    from stats_fetch import get_team_stats

def asignar_cuota_real(mercado, all_odds):
    try:
        # Limpieza básica de momios
        odds = [float(str(o).replace('+', '')) for o in all_odds]
        if not odds: return None
        
        m_lower = mercado.lower()
        if "local" in m_lower: return odds[0]
        if "empate" in m_lower: return odds[1] if len(odds) > 1 else None
        if "visitante" in m_lower: return odds[2] if len(odds) > 2 else None
        return odds[0]
    except: return None

def obtener_mejor_apuesta(partido_data):
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])

    stats = get_team_stats(home, away)
    
    # AQUÍ SE DEFINE LA VARIABLE: Asegúrate de que run_simulations devuelva un dict
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    
    # Ahora el loop no fallará porque predicciones existe
    for mercado, prob in predicciones.items():
        cuota = asignar_cuota_real(mercado, all_odds)
        
        if cuota:
            # FILTRO ANTI-GETAFE (+1150): Ignoramos momios > +500
            if cuota > 500:
                continue
                
            # Cálculo de Valor Esperado (EV)
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1

            # Solo picks con probabilidad razonable (>30%) y ventaja real
            if ev > 0.05 and prob > 0.30:
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev,
                    log=f"Prob: {int(prob*100)}% | EV: {round(ev,2)}"
                ))
    
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None
