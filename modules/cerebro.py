def obtener_mejor_apuesta(partido_data):
    # ... (mismo inicio anterior)
    
    mejores_opciones = []
    for mercado, prob in predicciones.items():
        cuota = asignar_cuota_real(mercado, all_odds)
        
        if cuota:
            # FILTRO DE CORDURA: Ignorar momios de 'tiro al aire' (> +500)
            if cuota > 500: 
                continue 
                
            decimal_odd = (cuota/100 + 1) if cuota > 0 else (100/abs(cuota) + 1)
            ev = (prob * decimal_odd) - 1

            # Solo picks con ventaja real y probabilidad mínima aceptable (35%)
            if ev > 0.05 and prob > 0.35:
                mejores_opciones.append(PickResult(
                    match=f"{home} vs {away}",
                    selection=mercado,
                    probability=prob,
                    odd=cuota,
                    ev=ev,
                    log=f"Prob: {int(prob*100)}% | EV: {round(ev,2)}"
                ))
    
    return max(mejores_opciones, key=lambda x: x.ev) if mejores_opciones else None

