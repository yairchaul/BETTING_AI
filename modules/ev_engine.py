import math
import numpy as np

class EVEngine:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def _poisson_pmf(self, k, lam):
        return (math.exp(-lam) * (lam**k)) / math.factorial(k) if lam > 0 else (1.0 if k==0 else 0.0)

    def build_parlay(self, games):
        resultados_finales = []
        for g in games:
            try:
                def to_prob(o):
                    v = float(str(o).replace('+', ''))
                    return 100/(v+100) if v > 0 else abs(v)/(abs(v)+100)
                # Inferimos lambdas basados en los momios reales
                l_h, l_v = to_prob(g['home_odd']) * 3.0, to_prob(g['away_odd']) * 3.0
            except: l_h, l_v = 1.4, 1.2

            # Matriz de marcadores (Poisson)
            m = np.fromfunction(np.vectorize(lambda h, v: self._poisson_pmf(h, l_h) * self._poisson_pmf(v, l_v)), (7, 7))

            opciones = []
            # Mercados a evaluar
            # 1. Doble Oportunidad (Local o Empate)
            p_1x = m.sum() - np.tril(m, -1).sum() 
            opciones.append({"pick": f"{g['home']} o Empate", "p": p_1x, "c": 1.25})
            
            # 2. Over 1.5 Goles
            p_o15 = 1 - (m[0,0] + m[0,1] + m[1,0])
            opciones.append({"pick": "Over 1.5 Goles", "p": p_o15, "c": 1.38})

            # 3. Gana Local (Simple)
            p_h = np.tril(m, -1).sum()
            opciones.append({"pick": f"Gana {g['home']}", "p": p_h, "c": g['home_odd']})

            # --- FILTRO 85% Y SELECCIÓN DEL MEJOR MOMIO ---
            validas = [o for o in opciones if o['p'] >= self.threshold]
            if validas:
                # De las que pasan el 85%, elegimos la cuota ('c') más alta
                mejor = max(validas, key=lambda x: x['c'])
                resultados_finales.append({
                    "partido": f"{g['home']} vs {g['away']}",
                    "pick": mejor['pick'],
                    "probabilidad": round(mejor['p'] * 100, 1),
                    "cuota": mejor['c']
                })
        
        # El parlay se arma con los 3 mejores de la lista final
        parlay = sorted(resultados_finales, key=lambda x: x['probabilidad'], reverse=True)[:3]
        return resultados_finales, parlay

    def simulate_parlay_profit(self, parlay, monto):
        c_tot = 1.0
        for p in parlay:
            try:
                v = float(str(p['cuota']).replace('+', ''))
                c_tot *= ((v/100 + 1) if v > 0 else (100/abs(v) + 1))
            except: c_tot *= 1.30
        return {"cuota_total": round(c_tot, 2), "pago_total": round(monto * c_tot, 2), "ganancia_neta": round((monto * c_tot) - monto, 2)}

