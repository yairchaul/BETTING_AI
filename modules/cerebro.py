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
    Mapea la posición de los momios detectados por el OCR a los 13 mercados.
    """
    try:
        # Convertimos momios (+110, -150) a floats para cálculos de EV
        odds = []
        for o in all_odds:
            clean_o = str(o).replace('+', '')
            odds.append(float(clean_o))
        
        if not odds: return None

        m_lower = mercado.lower()
        
        # Mapeo lógico según la estructura de Caliente detectada en el OCR
        if "resultado final" in m_lower:
            if "local" in m_lower: return odds[0]
            if "empate" in m_lower: return odds[1] if len(odds) > 1 else None
            if "visitante" in m_lower: return odds[2] if len(odds) > 2 else None
        
        # Para mercados de Goles y Ambos Anotan
        if "ambos" in m_lower: return odds[0]
        if "over 2.5" in m_lower: return odds[0]
        if "under 2.5" in m_lower: return odds[1] if len(odds) > 1 else None
        if "over 1.5" in m_lower: return odds[0]
        
        # Fallback: Si no hay coincidencia exacta, tomamos el primer momio disponible
        return odds[0]
    except:
        return None

def obtener_mejor_apuesta(partido_data):
    """
    Analiza cada partido individualmente buscando el máximo EV+ en los 13 mercados.
    """
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])

    # 1. Consulta de estadísticas de los últimos 5 partidos
    stats = get_team_stats(home, away)
    
    # 2. Ejecución de los 13 mercados en el motor de Montecarlo
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    bitacora = []

    for mercado, prob in predicciones.items():
        # DEFINICIÓN AHORA PRESENTE: Llamada a la función de mapeo
        cuota = asignar_cuota_real(mercado, all_odds)
        
        if cuota:
            # Conversión a decimal para cálculo de Valor Esperado (EV)
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1
            
            # Registro para auditoría interna
            bitacora.append(f"{mercado}: Prob {int(prob*100)}% | EV: {round(ev,2)}")
            
    if ev > 0.05:
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev,
                    log="\n".join(bitacora[-5:]) # Ampliamos a los últimos 5 para ver más mercados
                ))
    
    # Retorna la decisión con el EV más alto (el Pick Sharp)
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None 



