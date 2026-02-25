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
                # Inferencia de fuerza de gol por momio
                def to_p(o):
                    val = float(str(o).replace('+', ''))
                    return 100/(val+100) if val > 0 else abs(val)/(abs(val)+100)
                l_h, l_v = to_p(g['home_odd']) * 3.0, to_p(g['away_odd']) * 3.0
            except: l_h, l_v = 1.4, 1.2

            # Matriz Poisson (Probabilidades de marcadores 0-6)
            m = np.fromfunction(np.vectorize(lambda h, v: self._poisson_pmf(h, l_h) * self._poisson_pmf(v, l_v)), (7, 7))

            opciones = []
            # 1. Doble Oportunidad (Alta probabilidad)
            p_1x = m.sum() - np.tril(m, -1).sum() 
            opciones.append({"pick": f"{g['home']} o Empate", "p": p_1x, "c": 1.28})
            
            # 2. Over 1.5 Goles
            p_o15 = 1 - (m[0,0] + m[0,1] + m[1,0])
            opciones.append({"pick": "Over 1.5 Goles", "p": p_o15, "c": 1.40})

            # --- FILTRO 85% Y SELECCIÓN DE MEJOR CUOTA ---
            validas = [o for o in opciones if o['p'] >= self.threshold]
            if validas:
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
            v = float(str(p['cuota']).replace('+', ''))
            c_tot *= ((v/100 + 1) if v > 0 else (100/abs(v) + 1))
        return {"cuota_total": round(c_tot, 2), "pago_total": round(monto * c_tot, 2), "ganancia_neta": round((monto * c_tot) - monto, 2)}

