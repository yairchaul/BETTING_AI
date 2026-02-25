import numpy as np
from scipy.stats import poisson

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def get_raw_probabilities(self, game):
        # Limpieza de momios americanos
        def parse_odd(o):
            try:
                val = str(o).replace('+', '').strip()
                n = float(val)
                return (n/100 + 1) if n > 0 else (100/abs(n) + 1)
            except: return 2.0

        ch, cv = parse_odd(game['home_odd']), parse_odd(game['away_odd'])
        
        # Inferencia de potencia goleadora (Lambdas)
        lh = round(2.6 / (ch**0.75), 2)
        lv = round(2.6 / (cv**0.75), 2)
        
        # Matriz de probabilidad Poisson
        grid = 10
        ph = [poisson.pmf(i, lh) for i in range(grid)]
        pa = [poisson.pmf(i, lv) for i in range(grid)]
        m = np.outer(ph, pa)
        idx = np.indices(m.shape)
        goles = idx[0] + idx[1]

        # EVALUACIÓN EN CASCADA
        opciones = [
            # Nivel 1: Combos (Gana + Over) - Prioridad de cuota
            {"name": f"{game['home']} & Over 1.5", "p": np.sum(m * (idx[0]>idx[1]) * (goles>1.5)), "c": round(ch*1.3, 2)},
            {"name": f"{game['home']} & Over 2.5", "p": np.sum(m * (idx[0]>idx[1]) * (goles>2.5)), "c": round(ch*1.8, 2)},
            {"name": f"{game['away']} & Over 1.5", "p": np.sum(m * (idx[1]>idx[0]) * (goles>1.5)), "c": round(cv*1.3, 2)},
            {"name": f"{game['away']} & Over 2.5", "p": np.sum(m * (idx[1]>idx[0]) * (goles>2.5)), "c": round(cv*1.8, 2)},
            # Nivel 2: Mercados fijos
            {"name": "Ambos Anotan", "p": np.sum(m[1:, 1:]), "c": 1.90},
            {"name": "Over 2.5 Goles", "p": np.sum(m[goles>2.5]), "c": 2.05},
            # Nivel 3: Ganador Simple
            {"name": f"Gana {game['home']}", "p": np.sum(m * (idx[0]>idx[1])), "c": ch},
            {"name": f"Gana {game['away']}", "p": np.sum(m * (idx[1]>idx[0])), "c": cv}
        ]

        # FILTRO 85%
        validas = [o for o in opciones if o['p'] >= self.threshold]

        if not validas:
            return {"status": "DESCARTADO", "home": game['home'], "away": game['away']}

        # Selección de la mejor cuota entre las seguras
        mejor = max(validas, key=lambda x: x['c'])

        return {
            "status": "APROBADO", "home": game['home'], "away": game['away'],
            "pick": mejor['name'], "prob": round(mejor['p']*100, 1),
            "cuota": mejor['c'], "ev": round((mejor['p']*mejor['c'])-1, 2),
            "lh": lh, "lv": lv, "exp": round(lh+lv, 2)
        }

