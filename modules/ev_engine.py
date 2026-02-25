import math
import numpy as np

class EVEngine:
    def poisson_pmf(self, k, lam):
        if lam <= 0: return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)

    def get_advanced_analysis(self, game, context):
        # --- 1. PROBABILIDADES BASE ---
        h_odd = float(str(game['home_odd']).replace('+', '').strip())
        h_dec = (h_odd/100 + 1) if h_odd > 0 else (100/abs(h_odd) + 1)
        prob_implied = 1 / h_dec

        # --- 2. AJUSTE DE GOLES ESPERADOS (LAMBDAS) ---
        l_home = 2.4 * prob_implied
        l_away = 1.3 * (1 - prob_implied)
        if context['bajas']: l_home *= 0.85 

        # --- 3. MATRIZ DE PROBABILIDADES (Poisson 6x6) ---
        matrix = np.zeros((6, 6))
        for h in range(6):
            for a in range(6):
                matrix[h, a] = self.poisson_pmf(h, l_home) * self.poisson_pmf(a, l_away)

        # --- 4. CÁLCULO MULTI-MERCADO (Lo inamovible) ---
        # A. Quien Gana
        p_home = np.sum(np.tril(matrix, -1))
        # B. Ambos Anotan (BTTS)
        p_btts = 1 - (np.sum(matrix[0, :]) + np.sum(matrix[:, 0]) - matrix[0,0])
        # C. Over/Under 2.5
        p_over_2_5 = 1 - sum([matrix[h, a] for h in range(6) for a in range(6) if h+a <= 2.5])
        # D. Over 1.5 Primer Tiempo (Estimación basada en 45% del total esperado)
        l_1t = (l_home + l_away) * 0.45
        p_over_1_5_1t = 1 - (self.poisson_pmf(0, l_1t) + self.poisson_pmf(1, l_1t))

        # --- 5. AUDITORÍA DE VALOR (Selección del mejor Pick) ---
        # Comparamos todos los mercados y elegimos el de mayor probabilidad/valor
        opciones = [
            {"pick": f"Gana {game['home']}", "prob": p_home, "odd": h_dec},
            {"pick": "Ambos Anotan (BTTS)", "prob": p_btts, "odd": 1.90},
            {"pick": "Altas (Over 2.5)", "prob": p_over_2_5, "odd": 1.85},
            {"pick": "Over 1.5 Primer Tiempo", "prob": p_over_1_5_1t, "odd": 2.10}
        ]

        # Si el favorito es pesado, añadimos el mercado combinado que pediste
        if prob_implied > 0.70:
            p_combined = p_home * (1 - (matrix[0,0] + matrix[0,1])) # Gana y Over 1.5 aprox
            opciones.append({"pick": f"{game['home']} & Over 1.5", "prob": p_combined, "odd": 1.65})

        # Elegir la opción con mayor EV (Probabilidad * Cuota)
        best = max(opciones, key=lambda x: x['prob'])

        return {
            "pick": best['pick'],
            "prob": round(best['prob'] * 100, 1),
            "ev": round((best['prob'] * best['odd']) - 1, 2),
            "context_info": "⚠️ Riesgo por bajas" if context['bajas'] else "✅ Sin novedades críticas"
        }
