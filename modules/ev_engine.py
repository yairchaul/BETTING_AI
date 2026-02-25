# modules/ev_engine.py - Motor de cascada + combos
import numpy as np
from scipy.stats import poisson

class EVEngine:
    def analizar_partido(self, partido):
        # Parseo de cuotas
        try:
            ch = float(partido['home_odd'].replace('+', '')) if '+' in partido['home_odd'] else -float(partido['home_odd'])
            cd = float(partido['draw_odd'].replace('+', '')) if '+' in partido['draw_odd'] else -float(partido['draw_odd'])
            ca = float(partido['away_odd'].replace('+', '')) if '+' in partido['away_odd'] else -float(partido['away_odd'])
        except:
            return None

        # Inferencia de lambdas (potencia ataque/defensa)
        lh = 1.65 / (ch / 1.9) if ch != 0 else 1.4   # Lambda home
        la = 1.35 / (ca / 1.9) if ca != 0 else 1.3

        # Matriz Poisson
        grid = 9
        ph = [poisson.pmf(i, lh) for i in range(grid)]
        pa = [poisson.pmf(i, la) for i in range(grid)]
        m = np.outer(ph, pa)

        prob_home = np.sum(np.tril(m, -1))           # Gana local
        prob_over15 = np.sum(m[np.indices(m.shape).sum(0) > 1.5])
        prob_home_over15 = np.sum(m * np.tril(np.ones((grid,grid)), -1) * (np.indices(m.shape).sum(0) > 1.5))

        # Cascada + combos
        opciones = [
            {"name": f"Gana {partido['home']}", "prob": prob_home, "cuota": 1 + (100 / abs(ch)) if ch < 0 else 1 + ch/100},
            {"name": "Over 1.5", "prob": prob_over15, "cuota": 1.85},
            {"name": f"{partido['home']} + Over 1.5", "prob": prob_home_over15, "cuota": 2.8},
            {"name": f"{partido['home']} + Over 2.5", "prob": prob_home_over15 * 0.65, "cuota": 4.2}
        ]

        for o in opciones:
            o['ev'] = round((o['prob'] * o['cuota']) - 1, 3)

        mejor = max(opciones, key=lambda x: x['ev'])
        
        return {
            "home": partido['home'],
            "away": partido['away'],
            "mejor_pick": mejor['name'],
            "prob": round(mejor['prob'] * 100, 1),
            "ev": mejor['ev'],
            "λ_home": round(lh, 2),
            "λ_away": round(la, 2),
            "edge": round(mejor['ev'] * 100, 2)
        }
