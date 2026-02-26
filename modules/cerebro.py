# modules/cerebro.py
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
    Mapea los momios detectados por el OCR a los 13 mercados de Caliente.
    """
    try:
        # Convertimos momios (+110, -150) a floats
        odds = []
        for o in all_odds:
            clean_o = str(o).replace('+', '')
            odds.append(float(clean_o))
        
        if not odds: return None

        # Lógica de mapeo por palabras clave en el mercado
        m_lower = mercado.lower()
        
        if "resultado final" in m_lower:
            if "local" in m_lower: return odds[0]
            if "empate" in m_lower: return odds[1] if len(odds) > 1 else None
            if "visitante" in m_lower: return odds[2] if len(odds) > 2 else None
        
        if "ambos" in m_lower: return odds[0]
        if "over 2.5" in m_lower: return odds[0]
        if "under 2.5" in m_lower: return odds[1] if len(odds) > 1 else None
        
        # Si no hay coincidencia específica, devolvemos el primer momio como fallback
        return odds[0]
    except:
        return None

def obtener_mejor_apuesta(partido_data):
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])

    # 1. API: Estadísticas reales
    stats = get_team_stats(home, away)
    
    # 2. Motor: Simulación de 13 mercados
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    
    for mercado, prob in predicciones.items():
        cuota_americana = asignar_cuota_real(mercado, all_odds)
        
        if cuota_americana:
            # Conversión a decimal para cálculo de EV
            if cuota_americana > 0:
                decimal_odd = (cuota_americana / 100) + 1
            else:
                decimal_odd = (100 / abs(cuota_americana)) + 1
                
            ev = (prob * decimal_odd) - 1
            
            # Buscamos la mejor probabilidad con valor
            if ev > 0.01: # Valor positivo mínimo
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota_americana,
                    ev=ev
                ))
    
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None
