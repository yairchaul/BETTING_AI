def obtener_mejor_apuesta(partido):
    home = partido.get("home", "Local")
    away = partido.get("away", "Visitante")
    
    # Ejecutamos las 20,000 simulaciones
    stats = {"home": {"attack": 50, "defense": 50}, "away": {"attack": 50, "defense": 50}}
    probs_ia = run_simulations(stats) # Retorna {'1': p, 'X': p, '2': p, 'Over 2.5': p, etc}

    raw_odds = partido.get("odds") or []
    if len(raw_odds) < 3:
        return None

    # Mapeo de nombres claros para el usuario
    nombres_mercados = {
        "1": f"Gana {home}",
        "X": "Empate",
        "2": f"Gana {away}"
    }

    mejores_opciones = []

    for clave, index in {"1": 0, "X": 1, "2": 2}.items():
        try:
            momio_american = int(str(raw_odds[index]).replace('+', ''))
            
            # Convertir a decimal para calcular EV
            decimal = (momio_american / 100 + 1) if momio_american > 0 else (100 / abs(momio_american) + 1)
            
            prob_ia = probs_ia[clave]
            ev = (prob_ia * decimal) - 1

            # --- FILTROS DE SEGURIDAD ---
            # 1. Probabilidad mínima del 38% (Evita milagros)
            # 2. EV positivo moderado (Evita errores de bulto del OCR)
            # 3. Momio máximo de +400 (Evita apuestas imposibles)
            if prob_ia > 0.38 and ev > 0.05 and momio_american < 400:
                mejores_opciones.append({
                    "mercado_display": nombres_mercados[clave],
                    "prob": prob_ia,
                    "odd": momio_american,
                    "ev": ev
                })
        except:
            continue

    if not mejores_opciones:
        return None

    # Elegimos la opción que mejor balancee Probabilidad y EV
    # Priorizamos probabilidad para "Parlays Seguros"
    mejor = max(mejores_opciones, key=lambda x: x["prob"]) 
    
    return {
        "match": f"{home} vs {away}",
        "selection": mejor["mercado_display"], # Aquí te dirá exactamente qué apostar
        "odd": mejor["odd"],
        "probability": mejor["prob"],
        "ev": mejor["ev"]
    }
