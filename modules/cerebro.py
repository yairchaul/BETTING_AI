import streamlit as st
import os
import sys

# Asegurar que el sistema encuentre los módulos locales
sys.path.append(os.path.dirname(__file__))

try:
    from modules.montecarlo import run_simulations
    from modules.stats_fetch import get_team_stats
    from modules.schemas import PickResult
except ImportError:
    try:
        from montecarlo import run_simulations
        from stats_fetch import get_team_stats
        from schemas import PickResult
    except ImportError:
        st.error("Error crítico: No se pudieron cargar los módulos de lógica.")

def obtener_mejor_apuesta(partido_data):
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])

    # Obtener estadísticas y simulación
    stats = get_team_stats(home, away)
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    
    for mercado, prob in predicciones.items():
        try:
            # Extraemos el momio base (primer elemento detectado)
            cuota_base = float(str(all_odds[0]).replace('+', '')) if all_odds else 100
            
            # Ajuste de cuota para Doble Oportunidad
            cuota = cuota_base if "Doble Oportunidad" not in mercado else cuota_base * 0.9
            
            # Filtro de seguridad cuotas altas
            if cuota > 500: 
                continue 
                
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1

            # PRIORIDAD: Bono para la combinada Gana/Empata + Over 1.5
            prioridad = 1.8 if "Doble Oportunidad / Over 1.5" in mercado else 1.0
            
            if ev > 0.02 and prob > 0.35:
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev * prioridad,
                    log=f"Prob: {int(prob*100)}% | EV: {round(ev,2)}"
                ))
        except: 
            continue
    
    if not mejores_opciones:
        return None
        
    return max(mejores_opciones, key=lambda x: x.ev)
