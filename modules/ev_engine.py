import math
import numpy as np

class EVEngine:
    def poisson_pmf(self, k, lam):
        """Probabilidad de que ocurran exactamente k eventos dado un promedio lam."""
        if lam <= 0: return 1.0 if k == 0 else 0.0
        return (math.exp(-lam) * (lam**k)) / math.factorial(k)

    def get_raw_probabilities(self, game):
        """Calcula una matriz multivariable de probabilidades para auditoría de valor."""
        try:
            # 1. Procesamiento de Momios
            h_odd_str = str(game.get('home_odd', '100')).replace('+', '').strip()
            h_odd = float(h_odd_str) if h_odd_str else 100.0
            
            # Conversión a Decimal (Cuota)
            h_dec = (h_odd/100 + 1) if h_odd > 0 else (100/abs(h_odd) + 1)
            prob_implied = 1 / h_dec

            # 2. Ajuste Dinámico de Lambdas (Goles Esperados)
            # Mejoramos la sensibilidad: Favoritos pesados proyectan más goles y menos recibidos
            l_home = 2.8 * (prob_implied ** 1.2) + 0.2
            l_away = 1.5 * ((1 - prob_implied) ** 1.5) + 0.1

            # 3. Generación de Matriz de Probabilidades (Hasta 6 goles por equipo)
            matrix = np.zeros((7, 7))
            for h in range(7):
                for a in range(7):
                    matrix[h, a] = self.poisson_pmf(h, l_home) * self.poisson_pmf(a, l_away)

            # 4. Cálculo de Mercados Específicos
            p_home = np.sum(np.tril(matrix, -1))
            p_away = np.sum(np.triu(matrix, 1))
            p_draw = np.sum(np.diag(matrix))
            
            p_btts = 1 - (np.sum(matrix[0, :]) + np.sum(matrix[:, 0]) - matrix[0,0])
            p_over_2_5 = 1 - sum([matrix[h, a] for h in range(7) for a in range(7) if h+a <= 2.5])
            p_over_1_5 = 1 - sum([matrix[h, a] for h in range(7) for a in range(7) if h+a <= 1.5])
            
            # Estimación 1er Tiempo (Aprox 45% del total de goles esperado)
            l_total_1t = (l_home + l_away) * 0.45
            p_over_0_5_1t = 1 - self.poisson_pmf(0, l_total_1t)

            # 5. Selección Inteligente del Pick (Auditoría de Valor)
            # Comparamos Prob. Real vs Prob. Implícita para hallar el mayor EDGE
            opciones = [
                {"pick": f"Gana {game.get('home', 'Local')}", "prob": p_home, "edge": p_home - prob_implied},
                {"pick": "Ambos Anotan", "prob": p_btts, "edge": p_btts - 0.52}, # Ref. genérica -110
                {"pick": "Over 2.5 Goles", "prob": p_over_2_5, "edge": p_over_2_5 - 0.50},
                {"pick": "Over 0.5 1T", "prob": p_over_0_5_1t, "edge": p_over_0_5_1t - 0.65}
            ]
            
            # Si el favorito es muy fuerte, añadir mercado combinado
            if prob_implied > 0.65:
                p_gana_over15 = p_home * p_over_1_5
                opciones.append({"pick": f"{game.get('home', 'Local')} & Over 1.5", "prob": p_gana_over15, "edge": p_gana_over15 - 0.55})

            # Elegir el pick con mejor Edge (Ventaja sobre la casa)
            mejor_opcion = max(opciones, key=lambda x: x['edge'])

            return {
                "pick": mejor_opcion['pick'],
                "prob": mejor_opcion['prob'],
                "ev": round((mejor_opcion['prob'] * h_dec) - 1, 2),
                "cuota_ref": h_dec,
                "detalles": {
                    "p_home": p_home, "p_draw": p_draw, "p_away": p_away,
                    "p_btts": p_btts, "p_over_25": p_over_2_5
                }
            }
        except Exception as e:
            return {"pick": "Error de Cálculo", "prob": 0.5, "ev": 0, "cuota_ref": 1.80}

    def simulate_parlay_profit(self, picks, monto):
        """Calcula el pago potencial asegurando consistencia absoluta de nombres de variables."""
        cuota_total = 1.0
        for p in picks:
            # Prioriza cuota_ref, luego cuota, finalmente cuota base
            c = p.get('cuota_ref') or p.get('cuota') or 1.85
            cuota_total *= float(c)
        
        pago = monto * cuota_total
        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago, 2),
            "ganancia_neta": round(pago - monto, 2),
            "monto_invertido": round(monto, 2)
        }
