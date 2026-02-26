def obtener_mejor_apuesta(partido_data):
    home = partido_data.get('home', 'Local')
    away = partido_data.get('away', 'Visitante')
    all_odds = partido_data.get('all_odds', [])
    stats = get_team_stats(home, away)
    predicciones = run_simulations(stats) 
    
    mejores_opciones = []
    
    # Mapeo dinámico: Si es Doble Op + Over, buscamos un momio compuesto
    for mercado, prob in predicciones.items():
        try:
            # Intentamos obtener el momio base del equipo favorito
            cuota_base = float(str(all_odds[0]).replace('+', '')) if all_odds else 100
            
            # Ajuste de cuota para mercados combinados (estimación si no viene en OCR)
            if "Doble Oportunidad" in mercado:
                cuota = cuota_base * 0.85 # La doble oportunidad baja un poco el riesgo/momio
            else:
                cuota = cuota_base

            if cuota > 500: continue # Filtro anti-getafe +1150
                
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1

            # Bonus de prioridad para la apuesta que pediste
            prioridad = 1.5 if "Doble Oportunidad / Over 1.5" in mercado else 1.0
            
            if ev > 0.02 and prob > 0.40:
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev * prioridad,
                    log=f"Prob: {int(prob*100)}% | EV: {round(ev,2)}"
                ))
        except: continue
    
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None
