try:
    from modules.stats_fetch import get_team_stats
    from modules.montecarlo import run_simulations
    from modules.schemas import PickResult
except ImportError:
    from stats_fetch import get_team_stats
    from montecarlo import run_simulations
    from schemas import PickResult

def asignar_cuota_real(mercado, all_odds):
    """
    Mapea la posición de los momios detectados por el OCR a los mercados sencillos.
    """
    try:
        odds = []
        for o in all_odds:
            clean_o = str(o).replace('+', '')
            odds.append(float(clean_o))
        
        if not odds: return None

        m_lower = mercado.lower()
        
        # Mapeo estricto a la interfaz de Caliente (Local, Empate, Visitante)
        if "resultado final" in m_lower:
            if "local" in m_lower: return odds[0]
            if "empate" in m_lower: return odds[1] if len(odds) > 1 else None
            if "visitante" in m_lower: return odds[2] if len(odds) > 2 else None
        
        # Mapeo para Over/Under (Sencillos)
        if "over 2.5" in m_lower or "over 1.5" in m_lower: return odds[0]
        if "under 2.5" in m_lower: return odds[1] if len(odds) > 1 else None
        if "ambos" in m_lower: return odds[0]
        
        return odds[0]
    except:
        return None

def obtener_mejor_apuesta(partido_data):
    """
    Analiza individualmente los mercados buscando el máximo EV+.
    """
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])

    # 1. Obtener estadísticas reales (últimos 5 partidos)
    stats = get_team_stats(home, away)
    
    # 2. Motor de Montecarlo (Probabilidades de mercados sencillos)
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    bitacora = []

    for mercado, prob in predicciones.items():
        # Buscamos el momio real en la imagen para este mercado específico
        cuota = asignar_cuota_real(mercado, all_odds)
        
        if cuota:
            # Cálculo de Valor Esperado (EV)
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1

            # Auditoría: Guardamos el análisis de cada uno de los 13 mercados
            bitacora.append(f"Mercado: {mercado} | Prob: {int(prob*100)}% | EV: {round(ev, 2)}")
            
            # Filtro Sharp: Solo picks con ventaja sobre la casa > 5%
            if ev > 0.05:
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev,
                    log="\n".join(bitacora[-5:]) 
                ))
    
    # Retorna la opción que ofrece más dinero a largo plazo (Máximo EV)
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None

