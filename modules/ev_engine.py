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
            # Inferencia de Lambdas a partir de momios (Agnóstico)
            try:
                def dec_p(o):
                    v = float(str(o).replace('+', ''))
                    return 100/(v+100) if v > 0 else abs(v)/(abs(v)+100)
                l_h, l_v = dec_p(g['home_odd']) * 3.0, dec_p(g['away_odd']) * 3.0
            except: l_h, l_v = 1.4, 1.2

            # Matriz de Probabilidades Poisson
            m = np.fromfunction(np.vectorize(lambda h, v: self._poisson_pmf(h, l_h) * self._poisson_pmf(v, l_v)), (7, 7))

            # --- TODAS LAS CAPAS DE MERCADO ---
            opciones = []
            p_o15 = 1 - (m[0,0] + m[0,1] + m[1,0])
            opciones.append({"pick": "Over 1.5 Goles", "p": p_o15, "c": 1.35})
            
            p_btts = (1 - m[0,:].sum()) * (1 - m[:,0].sum())
            opciones.append({"pick": "Ambos Anotan", "p": p_btts, "c": 1.75})
            
            p_1x = m.sum() - np.tril(m, -1).sum() # Local o Empate
            opciones.append({"pick": f"{g['home']} o Empate", "p": p_1x, "c": 1.30})
            
            p_win_h = np.tril(m, -1).sum()
            opciones.append({"pick": f"Gana {g['home']}", "p": p_win_h, "c": g.get('home_odd', 2.0)})

            # --- EL FILTRO DE HIERRO (85%) + MEJOR CUOTA ---
            validas = [o for o in opciones if o['p'] >= self.threshold]
            
            if validas:
                # De las seguras (>85%), elegimos la que tenga cuota ('c') más alta
                mejor = max(validas, key=lambda x: x['c'])
                resultados_finales.append({
                    "partido": f"{g['home']} vs {g['away']}",
                    "pick": mejor['pick'],
                    "probabilidad": round(mejor['p'] * 100, 1),
                    "cuota": mejor['c']
                })
        
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
