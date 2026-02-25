# Dentro de tu clase EVEngine, ajusta esta parte:
def get_probabilities(self, game):
    ch = self._to_dec(game['home_odd'])
    cv = self._to_dec(game['away_odd'])
    
    # Ajuste de Lambdas: La Liga MX tiene un promedio de 2.7 goles por partido
    # Si ch y cv son similares, el modelo debe proyectar goles en ambos lados
    lh = round(2.8 / (ch**0.65), 2)
    lv = round(2.8 / (cv**0.65), 2)
    
    grid = 10
    m = np.outer(poisson.pmf(np.arange(grid), lh), poisson.pmf(np.arange(grid), lv))
    idx = np.indices(m.shape)
    goles = idx[0] + idx[1]

    opciones = [
        # El Over 1.5 suele tener probabilidades de 88-92% en estos partidos
        {"name": "Over 1.5 Goles", "p": np.sum(m[goles > 1.5]), "c": 1.30},
        {"name": "Ambos Anotan", "p": np.sum(m[1:, 1:]), "c": 1.85},
        {"name": f"Gana {game['home']}", "p": np.sum(m * (idx[0] > idx[1])), "c": ch},
        {"name": f"Gana {game['away']}", "p": np.sum(m * (idx[1] > idx[0])), "c": cv}
    ]

    # FILTRO 85%
    validas = [o for o in opciones if o['p'] >= self.threshold]
    
    if not validas:
        # Debug: Si nada pasa, vemos cuál fue la prob más alta
        prob_max = max(o['p'] for o in opciones)
        return {"status": "DESCARTADO", "prob_max": prob_max}
    
    return max(validas, key=lambda x: x['c'])
