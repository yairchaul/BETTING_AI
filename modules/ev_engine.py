import math
import numpy as np

class EVEngine:
    def poisson_pmf(self, k, lam):
        if lam <= 0: return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)

    def get_raw_probabilities(self, game):
        """Calcula probabilidades puras para el Cerebro."""
        try:
            # Limpieza de momios
            h_odd = float(str(game['home_odd']).replace('+', '').strip())
            h_dec = (h_odd/100 + 1) if h_odd > 0 else (100/abs(h_odd) + 1)
            prob_implied = 1 / h_dec

            # Lambdas (Goles esperados)
            l_home = 2.4 * prob_implied
            l_away = 1.3 * (1 - prob_implied)

            # Matriz de probabilidad
            matrix = np.zeros((6, 6))
            for h in range(6):
                for a in range(6):
                    matrix[h, a] = self.poisson_pmf(h, l_home) * self.poisson_pmf(a, l_away)

            p_home = np.sum(np.tril(matrix, -1))
            p_btts = 1 - (np.sum(matrix[0, :]) + np.sum(matrix[:, 0]) - matrix[0,0])
            
            # Determinar mercado base
            if p_home > 0.60:
                pick = f"Gana {game['home']}"
                prob = p_home
            elif p_btts > 0.55:
                pick = "Ambos Anotan (BTTS)"
                prob = p_btts
            else:
                pick = "Over 2.5 Goles"
                prob = 0.5 # Valor neutro si no hay claridad

            return {
                "pick": pick,
                "prob": prob,
                "ev": round((prob * h_dec) - 1, 2),
                "h_dec": h_dec
            }
        except Exception as e:
            # Retorno de emergencia si los datos fallan
            return {"pick": "Análisis Pendiente", "prob": 0.5, "ev": 0, "h_dec": 1.0}

    def simulate_parlay_profit(self, picks, monto):
        """Cálculo final del parlay."""
        cuota_total = 1.0
        for p in picks:
            # Usamos un momio estimado de 1.85 si el pick es de valor
            cuota_total *= 1.85
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2)
        }
