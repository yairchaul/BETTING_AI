import numpy as np
from scipy.stats import poisson

class EVEngine:
    def __init__(self):
        self.min_edge = 0.02 # 2% de ventaja mínima para considerar "Valor"

    def calcular_poisson_avanzado(self, l_h, l_a):
        max_g = 10
        p_h = [poisson.pmf(i, l_h) for i in range(max_g)]
        p_a = [poisson.pmf(i, l_a) for i in range(max_g)]
        m = np.outer(p_h, p_a)
        
        # Probabilidades Base
        prob_h = np.sum(np.tril(m, -1))
        prob_over_15 = np.sum(m[np.sum(np.indices(m.shape), axis=0) > 1.5])
        prob_over_25 = np.sum(m[np.sum(np.indices(m.shape), axis=0) > 2.5])
        
        # Probabilidades de COMBOS (Gana y Over)
        # Solo sumamos las celdas donde el local gana Y hay más de 1.5/2.5 goles
        mask_h = np.tril(np.ones((max_g, max_g)), -1)
        mask_over15 = np.sum(np.indices(m.shape), axis=0) > 1.5
        mask_over25 = np.sum(np.indices(m.shape), axis=0) > 2.5
        
        prob_h_over15 = np.sum(m * mask_h * mask_over15)
        prob_h_over25 = np.sum(m * mask_h * mask_over25)
        
        return {
            "h": prob_h, "o15": prob_over_15, "o25": prob_over_25,
            "h_o15": prob_h_over15, "h_o25": prob_h_over25
        }

    def get_raw_probabilities(self, game):
        # Limpieza de cuotas
        def to_dec(o):
            n = float(str(o).replace('+', ''))
            return (n/100 + 1) if n > 0 else (100/abs(n) + 1)

        odd_h = to_dec(game['home_odd'])
        # Inferencia de potencia de ataque (λ) basada en cuota
        l_h, l_a = 1.6 / (odd_h/2), 1.2
        
        res = self.calcular_poisson_avanzado(l_h, l_a)
        
        # CASCADA DE VALOR CON COMBOS
        # Cuotas estimadas para combos (multiplicador de seguridad 0.9)
        opciones = [
            {"name": f"Gana {game['home']}", "p": res['h'], "c": odd_h},
            {"name": "Over 2.5 Goles", "p": res['o25'], "c": 1.95},
            {"name": f"{game['home']} y Over 1.5", "p": res['h_o15'], "c": odd_h * 1.4},
            {"name": f"{game['home']} y Over 2.5", "p": res['h_o25'], "c": odd_h * 1.8}
        ]

        for o in opciones: o['ev'] = (o['p'] * o['c']) - 1
        
        # Elegir la mejor opción analítica
        mejor = max(opciones, key=lambda x: x['ev'])
        
        return {
            "home": game['home'], "away": game['away'],
            "pick_final": mejor['name'],
            "prob_final": round(mejor['p'] * 100, 1),
            "ev_final": round(mejor['ev'], 3),
            "cuota_ref": round(mejor['c'], 2),
            "tecnico": f"λH: {round(l_h,2)} | Exp: {round(l_h+l_a,2)} gls"
        }
