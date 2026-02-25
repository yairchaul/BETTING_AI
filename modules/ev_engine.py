# modules/ev_engine.py actualizado

class EVEngine:
    def __init__(self):
        self.min_ev_threshold = 0.13
        self.high_prob_threshold = 0.88 

    def build_parlay(self, games: list):
        resultados = []
        
        for g in games:
            partido = f"{g.get('home','')} vs {g.get('away','')}"
            # Ajuste de lambdas basado en el favorito de la cuota
            lambda_home = 1.65
            lambda_away = 1.10
            
            try:
                # Si el momio es muy bajo (favorito), subimos su lambda (expectativa de gol)
                h_odd = float(g.get("home_odd", 0))
                a_odd = float(g.get("away_odd", 0))
                if h_odd < 0 or (h_odd > 0 and h_odd < 160): lambda_home += 0.5
                if a_odd < 0 or (a_odd > 0 and a_odd < 160): lambda_away += 0.5
            except: pass

            p_home, p_draw, p_away = get_poisson_probs(lambda_home, lambda_away)
            
            # --- CÁLCULO DE PROBABILIDADES ---
            prob_btts = 0.0
            prob_over_1_5 = 0.0
            prob_over_2_5 = 0.0
            for h in range(7):
                for a in range(7):
                    prob = poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
                    if h > 0 and a > 0: prob_btts += prob
                    if h + a > 1.5: prob_over_1_5 += prob
                    if h + a > 2.5: prob_over_2_5 += prob
            
            prob_over_1t = prob_over_1_5 * 0.45 

            # --- LÓGICA DE CASCADA (EL PRIMERO QUE CUMPLE, GANA) ---
            chosen_pick = None

            if prob_over_1t >= 0.68:
                chosen_pick = {"pick": "Over 1.5 1T", "prob": prob_over_1t, "cuota": 1.85}
            elif prob_btts >= 0.62:
                chosen_pick = {"pick": "Ambos Equipos Anotan", "prob": prob_btts, "cuota": 1.75}
            elif prob_over_2_5 >= 0.58:
                chosen_pick = {"pick": "Over 2.5 Goles", "prob": prob_over_2_5, "cuota": 1.80}
            else:
                # Si no hay mercado especial fuerte, buscar el ganador con mejor probabilidad
                outcomes = [
                    (f"{g['home']} gana", p_home, g.get("home_odd")),
                    ("Empate", p_draw, g.get("draw_odd")),
                    (f"{g['away']} gana", p_away, g.get("away_odd"))
                ]
                # Ordenar por probabilidad de mayor a menor
                outcomes.sort(key=lambda x: x[1], reverse=True)
                best_o, best_p, best_c = outcomes[0]
                chosen_pick = {"pick": best_o, "prob": best_p, "cuota": best_c or "1.90"}

            if chosen_pick:
                prob = chosen_pick["prob"]
                cuota = float(chosen_pick["cuota"])
                resultados.append({
                    "partido": partido,
                    "pick": chosen_pick["pick"],
                    "probabilidad": round(prob * 100, 1),
                    "cuota": cuota,
                    "ev": round(calculate_ev(prob, cuota), 3),
                    "razon": "Prioridad por Cascada de Probabilidad"
                })

        # Para el parlay, ahora priorizamos PROBABILIDAD pura (Seguridad)
        # en lugar de EV (Riesgo/Recompensa)
        best_picks = sorted(resultados, key=lambda x: x["probabilidad"], reverse=True)
        parlay = best_picks[:5]
        
        return resultados, parlay
