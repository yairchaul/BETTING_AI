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
        
        # Lambdas basados en cuotas
        lh, lv = round(2.6/(ch**0.7), 2), round(2.6/(cv**0.7), 2)
        
        grid = 8
        m = np.outer(poisson.pmf(np.arange(grid), lh), poisson.pmf(np.arange(grid), lv))
        idx = np.indices(m.shape)
        goles = idx[0] + idx[1]

        # Cascada de opciones
        opciones = [
            {"name": f"Gana {game['home']} & O1.5", "p": np.sum(m * (idx[0]>idx[1]) * (goles>1.5)), "c": ch*1.3},
            {"name": "Ambos Anotan", "p": np.sum(m[1:, 1:]), "c": 1.90},
            {"name": "Over 2.5", "p": np.sum(m[goles>2.5]), "c": 2.00},
            {"name": f"Gana {game['home']}", "p": np.sum(m * (idx[0]>idx[1])), "c": ch}
        ]

        validas = [o for o in opciones if o['p'] >= self.threshold]
        if not validas: return None
        
        mejor = max(validas, key=lambda x: x['c'])
        mejor['lh'], mejor['lv'] = lh, lv
        return mejor
