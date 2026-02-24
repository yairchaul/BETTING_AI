def build_parlay(self, games: list):
    resultados = []
    parlay_picks = []
    
    for g in games:
        # EV para las 3 opciones (usa tus funciones existentes)
        for outcome, odds_key in [("home", "home_odd"), ("draw", "draw_odd"), ("away", "away_odd")]:
            odds = g[odds_key]
            if not odds: continue
            implied_p = american_to_probability(float(odds))  # de ev_scanner
            model_p = 0.38 if outcome == "draw" else 0.45   # placeholder - aquí irá tu modelo real
            ev = calculate_ev(model_p, float(odds))
            
            if ev > 0.05:  # umbral de valor
                pick_name = f"{g['home']} gana" if outcome=="home" else \
                           "Empate" if outcome=="draw" else f"{g['away']} gana"
                resultados.append({
                    "partido": f"{g['home']} vs {g['away']}",
                    "pick": pick_name,
                    "probabilidad": round(model_p*100, 1),
                    "cuota": odds,
                    "ev": round(ev, 3)
                })
                parlay_picks.append({"partido": f"{g['home']} vs {g['away']}", "pick": pick_name})
    
    # Ordenar por EV y armar parlay (máx 4-5 legs)
    resultados.sort(key=lambda x: x["ev"], reverse=True)
    parlay_picks = parlay_picks[:5]
    
    return resultados[:6], parlay_picks   # top 6 análisis + parlay
