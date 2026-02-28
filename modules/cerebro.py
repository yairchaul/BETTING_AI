def obtener_mejor_apuesta(partido):
    stats = get_team_stats(partido["home"], partido["away"])
    probs = run_simulations(stats)
    
    # Odds reales (API) o fallback a lista de la imagen
    odds_from_api = fetch_odds(partido["home"], partido["away"])
    
    if odds_from_api and isinstance(odds_from_api, dict):
        odds = odds_from_api
    else:
        # Fallback: la lista all_odds de la imagen → mapear manualmente a mercados
        all_odds = partido.get("all_odds", [])
        if len(all_odds) >= 3:
            odds = {
                "Resultado Final (Local)": float(all_odds[0]),
                "Resultado Final (Empate)": float(all_odds[1]),
                "Resultado Final (Visitante)": float(all_odds[2]),
                # Si hay más odds en la fila (over/under, etc.), mapéalas aquí
                # Por ahora solo 1X2
            }
        else:
            odds = {}  # Nada útil → no picks
    
    mejores = []
    for mercado, prob in probs.items():
        odd = odds.get(mercado, 0)
        if odd == 0:
            continue  # No hay momio para este mercado → salta
        
        # Convertir momio americano a decimal
        if odd > 0:
            decimal = (odd / 100) + 1
        elif odd < 0:
            decimal = (100 / abs(odd)) + 1
        else:
            decimal = 0
        
        if decimal <= 1:
            continue
        
        ev = (prob * decimal) - 1
        if ev > 0.05:
            mejores.append({
                "mercado": mercado,
                "prob": prob,
                "odd": odd,
                "ev": ev,
                "decimal": round(decimal, 2)
            })
    
    if mejores:
        mejor = max(mejores, key=lambda x: x["ev"])
        return PickResult(
            match=f"{partido['home']} vs {partido['away']}",
            selection=mejor["mercado"],
            odd=mejor["odd"],
            probability=mejor["prob"],
            ev=mejor["ev"]
        )
    
    return None