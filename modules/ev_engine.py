import numpy as np
from scipy.stats import poisson

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def get_raw_probabilities(self, game):
        # 1. Conversión de momios
        def to_dec(o):
            n = float(str(o).replace('+', ''))
            return (n/100 + 1) if n > 0 else (100/abs(n) + 1)

        c_h = to_dec(game['home_odd'])
        c_v = to_dec(game['away_odd'])
        
        # 2. Inferencia Real de Lambdas (λ)
        # Basado en cuotas: cuota baja = λ alto
        l_h = round(2.5 / (c_h**0.8), 2)
        l_v = round(2.5 / (c_v**0.8), 2)
        
        # 3. Matriz de Poisson 10x10
        grid = 10
        ph = [poisson.pmf(i, l_h) for i in range(grid)]
        pa = [poisson.pmf(i, l_v) for i in range(grid)]
        m = np.outer(ph, pa)
        indices = np.indices(m.shape)
        total_goles = indices[0] + indices[1]

        # 4. CAPAS DE EVALUACIÓN (La Cascada)
        # Definimos todas las opciones posibles con sus probabilidades y cuotas estimadas
        opciones = [
            # Combos Local
            {"name": "Local & Over 1.5", "p": np.sum(m * (indices[0] > indices[1]) * (total_goles > 1.5)), "c": round(c_h * 1.3, 2)},
            {"name": "Local & Over 2.5", "p": np.sum(m * (indices[0] > indices[1]) * (total_goles > 2.5)), "c": round(c_h * 1.8, 2)},
            # Combos Visita
            {"name": "Visita & Over 1.5", "p": np.sum(m * (indices[1] > indices[0]) * (total_goles > 1.5)), "c": round(c_v * 1.3, 2)},
            {"name": "Visita & Over 2.5", "p": np.sum(m * (indices[1] > indices[0]) * (total_goles > 2.5)), "c": round(c_v * 1.8, 2)},
            # Mercados Simples
            {"name": "Ambos Anotan", "p": np.sum(m[1:, 1:]), "c": 1.85},
            {"name": "Over 2.5 Goles", "p": np.sum(m[total_goles > 2.5]), "c": 1.90},
            {"name": f"Gana {game['home']}", "p": np.sum(m * (indices[0] > indices[1])), "c": c_h},
            {"name": f"Gana {game['away']}", "p": np.sum(m * (indices[1] > indices[0])), "c": c_v}
        ]

        # 5. FILTRO DE ÉLITE 85%
        validas = [o for o in opciones if o['p'] >= self.threshold]

        if not validas:
            return {"status": "DESCARTADO", "home": game['home'], "away": game['away']}

        # 6. SELECCIÓN DE MEJOR CUOTA entre las válidas
        mejor = max(validas, key=lambda x: x['c'])

        return {
            "status": "APROBADO",
            "home": game['home'], "away": game['away'],
            "pick_final": mejor['name'],
            "prob_final": round(mejor['p'] * 100, 2),
            "cuota_ref": mejor['c'],
            "ev": round((mejor['p'] * mejor['c']) - 1, 2),
            "lh": l_h, "lv": l_v, "exp": round(l_h + l_v, 2)
        }

