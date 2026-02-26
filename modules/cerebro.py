from modules.stats_fetch import get_team_stats
from modules.montecarlo import run_simulations
from modules.schemas import PickResult

def asignar_cuota_real(mercado, all_odds):
    """
    Mapea la posición de los momios detectados por el OCR a los 13 mercados de Caliente.
    """
    try:
        # Convertimos todos los momios a float
        odds = [float(o.replace('+', '')) for o in all_odds]
        
        # Mapeo por posición estándar en la interfaz de Caliente (OCR row)
        mapping = {
            "Resultado Final (Local)": odds[0] if len(odds) > 0 else None,
            "Resultado Final (Empate)": odds[1] if len(odds) > 1 else None,
            "Resultado Final (Visitante)": odds[2] if len(odds) > 2 else None,
            "Ambos Equipos Anotan": odds[0] if "ambos" in str(all_odds).lower() else None,
            "Over 2.5": odds[0] if any(x in str(all_odds).lower() for x in ["over", "más"]) else None,
            "Under 2.5": odds[1] if any(x in str(all_odds).lower() for x in ["under", "menos"]) else None,
            # Agrega aquí las posiciones según las capturas de mercados mejorados
        }
        
        # Si el OCR solo detectó 3 momios, asumimos 1X2 por defecto
        if len(odds) == 3 and mercado.startswith("Resultado"):
            return mapping.get(mercado)
            
        return mapping.get(mercado)
    except: return None

def obtener_mejor_apuesta(partido_data):
    home, away = partido_data['home'], partido_data['away']
    
    # 1. API: Análisis últimos 5 partidos
    stats = get_team_stats(home, away)
    
    # 2. Motores: Simulación de los 13 mercados
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    
    # 3. Evaluación Exhaustiva
    for mercado, prob in predicciones.items():
        cuota = asignar_cuota_real(mercado, partido_data['all_odds'])
        
        if cuota:
            # Cálculo de EV (Expected Value)
            # odd_decimal = cuota_americana_a_decimal(cuota)
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1
            
            if ev > 0.05: # Umbral de ventaja del 5%
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev
                ))
    
    # Devuelve el pick con mayor EV (la decisión más correcta)
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None
