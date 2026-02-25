import numpy as np
from scipy.stats import poisson

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def get_raw_probabilities(self, game):
        def to_dec(o):
            try:
                n = float(str(o).replace('+', ''))
                return (n/100 + 1) if n > 0 else (100/abs(n) + 1)
            except: return 2.0

        c_h = to_dec(game['home_odd'])
        c_v = to_dec(game['away_odd'])
        
        # Inferencia conservadora de Lambdas
        l_h = round(2.5 / (c_h**0.8), 2)
        l_v = round(2.5 / (c_v**0.8), 2)
        
        grid = 10
        ph = [poisson.pmf(i, l_h) for i in range(grid)]
        pa = [poisson.pmf(i, l_v) for i in range(grid)]
        m = np.outer(ph, pa)
        idx = np.indices(m.shape)
        goles = idx[0] + idx[1]

        # CAPAS EN ORDEN ESTRICTO
        opciones = [
            # 1. Combos Gana + Over (Prioridad)
            {"name": f"Gana {game['home']} + Over 1.5", "p": np.sum(m * (idx[0]>idx[1]) * (goles>1.5)), "c": round(c_h*1.35, 2)},
            {"name": f"Gana {game['home']} + Over 2.5", "p": np.sum(m * (idx[0]>idx[1]) * (goles>2.5)), "c": round(c_h*1.85, 2)},
            {"name": f"Gana {game['away']} + Over 1.5", "p": np.sum(m * (idx[1]>idx[0]) * (goles>1.5)), "c": round(c_v*1.35, 2)},
            {"name": f"Gana {game['away']} + Over 2.5", "p": np.sum(m * (idx[1]>idx[0]) * (goles>2.5)), "c": round(c_v*1.85, 2)},
            # 2. BTTS
            {"name": "Ambos Anotan (BTTS)", "p": np.sum(m[1:, 1:]), "c": 1.90},
            # 3. Over Puro
            {"name": "Over 2.5 Goles", "p": np.sum(m[goles>2.5]), "c": 2.00},
            {"name": "Over 1.5 Goles", "p": np.sum(m[goles>1.5]), "c": 1.40},
            # 4. Ganador Simple
            {"name": f"Gana {game['home']}", "p": np.sum(m * (idx[0]>idx[1])), "c": c_h},
            {"name": f"Gana {game['away']}", "p": np.sum(m * (idx[1]>idx[0])), "c": c_v}
        ]

        # Filtrar por el 85% inamovible
        validas = [o for o in opciones if o['p'] >= self.threshold]

        if not validas:
            return {"status": "DESCARTADO", "home": game['home'], "away": game['away']}

        # Elegir la de mejor momio (cuota más alta) entre las seguras
        mejor = max(validas, key=lambda x: x['c'])

        return {
            "status": "APROBADO",
            "home": game['home'], "away": game['away'],
            "pick_final": mejor['name'],
            "prob_final": round(mejor['p'] * 100, 2),
            "cuota_ref": mejor['c'],
            "ev": round((mejor['p'] * mejor['c']) - 1, 2),
            "edge": round(((mejor['p'] * mejor['c']) - 1) * 100, 1),
            "lh": l_h, "lv": l_v, "exp": round(l_h + l_v, 2)
        }
