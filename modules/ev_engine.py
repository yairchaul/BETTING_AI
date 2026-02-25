import math
import numpy as np

class EVEngine:
    def poisson_pmf(self, k, lam):
        if lam <= 0: return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)

    def get_raw_probabilities(self, game):
        """Calcula probabilidades base para que el Cerebro las procese."""
        try:
            # Limpieza y conversión de momios
            h_odd_str = str(game.get('home_odd', '100')).replace('+', '').strip()
            h_odd = float(h_odd_str) if h_odd_str else 100.0
            
            h_dec = (h_odd/100 + 1) if h_odd > 0 else (100/abs(h_odd) + 1)
            prob_implied = 1 / h_dec

            # Proyección de goles (Lambdas)
            l_home = 2.4 * prob_implied
            l_away = 1.3 * (1 - prob_implied)

            # Matriz de Poisson para mercados inamovibles
            matrix = np.zeros((6, 6))
            for h in range(6):
                for a in range(6):
                    matrix[h, a] = self.poisson_pmf(h, l_home) * self.poisson_pmf(a, l_away)

            p_home = np.sum(np.tril(matrix, -1))
            p_btts = 1 - (np.sum(matrix[0, :]) + np.sum(matrix[:, 0]) - matrix[0,0])
            p_over_2_5 = 1 - sum([matrix[h, a] for h in range(6) for a in range(6) if h+a <= 2.5])

            # Determinación del pick con más valor estadístico
            if p_home > 0.60: pick = f"Gana {game['home']}"; prob = p_home
            elif p_btts > 0.55: pick = "Ambos Anotan"; prob = p_btts
            else: pick = "Over 2.5 Goles"; prob = p_over_2_5

            return {
                "pick": pick,
                "prob": prob,
                "ev": round((prob * h_dec) - 1, 2),
                "cuota_ref": h_dec
            }
        except Exception:
            return {"pick": "Análisis Manual Requerido", "prob": 0.5, "ev": 0, "cuota_ref": 1.80}

    def simulate_parlay_profit(self, picks, monto):
        """Calcula el pago potencial del parlay."""
        cuota_total = 1.0
        for p in picks:
            # Si el pick viene del cerebro, usamos su cuota o una base de 1.80
            cuota_total *= p.get('cuota_ref', 1.80)
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2)
        }
