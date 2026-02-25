import numpy as np
from scipy.stats import poisson

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def _to_dec(self, odd):
        try:
            val = float(str(odd).replace('+', ''))
            return (val/100 + 1) if val > 0 else (100/abs(val) + 1)
        except: return 2.0

    def get_probabilities(self, game):
        ch = self._to_dec(game['home_odd'])
        cv = self._to_dec(game['away_odd'])
        
        # Proyección de goles: Liga MX es agresiva (λ 2.8 base)
        lh, lv = round(2.8/(ch**0.65), 2), round(2.8/(cv**0.65), 2)
        
        grid = 10
        m = np.outer(poisson.pmf(np.arange(grid), lh), poisson.pmf(np.arange(grid), lv))
        idx = np.indices(m.shape)
        goles = idx[0] + idx[1]

        opciones = [
            {"name": "Over 1.5 Goles", "p": np.sum(m[goles > 1.5]), "c": 1.30},
            {"name": "Ambos Anotan", "p": np.sum(m[1:, 1:]), "c": 1.85},
            {"name": f"Gana {game['home']}", "p": np.sum(m * (idx[0] > idx[1])), "c": ch},
            {"name": f"Gana {game['away']}", "p": np.sum(m * (idx[1] > idx[0])), "c": cv}
        ]

        # Filtrar por el 85% solicitado
        validas = [o for o in opciones if o['p'] >= self.threshold]
        if not validas: return None
        
        mejor = max(validas, key=lambda x: x['c'])
        return {**mejor, "lh": lh, "lv": lv}
