from modules.stats_fetch import get_team_stats
from modules.montecarlo import run_simulations
from modules.schemas import PickResult

def obtener_mejor_apuesta(partido_data):
    home, away = partido_data['home'], partido_data['away']
    # 1. API: Análisis de los últimos 5 partidos
    stats = get_team_stats(home, away)
    
    # 2. Motores: Simulación exhaustiva de los 13 mercados
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    
    # 3. Mapeo de Valor (EV) comparando simulación vs momios del OCR
    for mercado, prob in predicciones.items():
        # Función interna para asignar el momio correcto al mercado analizado
        cuota = asignar_cuota_real(mercado, partido_data['all_odds'])
        if cuota:
            ev = (prob * cuota) - 1
            if ev > 0.05: # Filtro de Valor Esperado positivo
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev
                ))
    
    # Retorna la opción con mayor ventaja estadística para este partido
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None
