class EVEngine:
    def get_best_ev_pick(self, game, context_data=None):
        # 1. Probabilidad del Momio (Cálculo Base)
        h_odd = float(str(game['home_odd']).replace('+', '').strip())
        h_dec = (h_odd/100 + 1) if h_odd > 0 else (100/abs(h_odd) + 1)
        prob_implied = 1 / h_dec

        # 2. Ajuste por Contexto (Aquí entran tus Google APIs)
        # Si context_data dice "Lesión del goleador", bajamos el lambda de goles
        l_home = 2.5 * prob_implied
        l_away = 1.2 * (1 - prob_implied)
        
        if context_data and "baja" in context_data.lower():
            l_home *= 0.8  # Reducción de efectividad por bajas

        # 3. Análisis de Mercados Combinados
        p_over_1_5 = 1 - (poisson_pmf(0, l_home)*poisson_pmf(0, l_away) + 
                         poisson_pmf(1, l_home)*poisson_pmf(0, l_away) +
                         poisson_pmf(0, l_home)*poisson_pmf(1, l_away))
        
        # DECISIÓN DE AUDITORÍA:
        # Caso A: Favorito muy pesado (-400 o más)
        if prob_implied > 0.75:
            if p_over_1_5 > 0.80:
                return {"pick": f"{game['home']} y Over 1.5", "prob": round(prob_implied * p_over_1_5 * 100, 1), "cuota": "-150"}
            else:
                return {"pick": f"{game['home']} gana a cero", "prob": round(prob_implied * 0.6 * 100, 1), "cuota": "+110"}
        
        # Caso B: Partido parejo
        # Aquí es donde el análisis de Poisson decide si es BTTS o Under
        # ... (resto de la lógica)
