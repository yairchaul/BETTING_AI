def analizar_probabilidades(partido_dinamico):
    """
    Recibe los datos extraídos y aplica el filtro > 70%.
    No tiene nombres grabados, analiza lo que le entregue el conector.
    """
    analisis_resultados = []

    for mercado in partido_dinamico.get('mercados', []):
        # Convertimos el momio americano a probabilidad decimal
        # Ejemplo: -110 es aproximadamente 52.4% de probabilidad de la casa
        momio = int(mercado['odds'])
        
        if momio < 0:
            prob_casa = (abs(momio) / (abs(momio) + 100)) * 100
        else:
            prob_casa = (100 / (momio + 100)) * 100
            
        # El motor añade un peso estadístico basado en la jerarquía (Triples > Puntos)
        peso = 1.2 if "Triples" in mercado['tipo'] else 1.0
        prob_final = prob_casa * peso

        analisis_resultados.append({
            "partido": partido_dinamico['name'],
            "seleccion": f"{mercado['jugador']} {mercado['linea']} ({mercado['tipo']})",
            "prob": prob_final,
            "momio": momio
        })

    # FILTRO DE ÉLITE: Solo devolvemos el pick si supera el 70% real
    picks_elite = [p for p in analisis_resultados if p['prob'] > 70.0]
    
    return max(picks_elite, key=lambda x: x['prob']) if picks_elite else None
