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
            # 1. Inferencia de potencia de gol (Lambdas)
            try:
                def to_prob(o):
                    v = float(str(o).replace('+', ''))
                    return 100/(v+100) if v > 0 else abs(v)/(abs(v)+100)
                l_h, l_v = to_prob(g['home_odd']) * 3.0, to_prob(g['away_odd']) * 3.0
            except: l_h, l_v = 1.4, 1.2

            # 2. Generar matriz Poisson
            m = np.fromfunction(np.vectorize(lambda h, v: self._poisson_pmf(h, l_h) * self._poisson_pmf(v, l_v)), (7, 7))

            # 3. Evaluar Mercados (Agnóstico)
            opciones = []
            
            # Gana o Empate (Doble Oportunidad) - Alta probabilidad
            p_1x = m.sum() - np.tril(m, -1).sum() 
            opciones.append({"pick": f"{g['home']} o Empate", "p": p_1x, "c": 1.25})
            
            # Over 1.5
            p_o15 = 1 - (m[0,0] + m[0,1] + m[1,0])
            opciones.append({"pick": "Over 1.5 Goles", "p": p_o15, "c": 1.35})
            
            # Ambos Anotan
            p_btts = (1 - m[0,:].sum()) * (1 - m[:,0].sum())
            opciones.append({"pick": "Ambos Anotan", "p": p_btts, "c": 1.70})

            # 4. Filtro de Élite 85% + Selección de Mejor Momio
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
            try:
                v = float(str(p['cuota']).replace('+', ''))
                c_tot *= ((v/100 + 1) if v > 0 else (100/abs(v) + 1))
            except: c_tot *= 1.30
        return {"cuota_total": round(c_tot, 2), "pago_total": round(monto * c_tot, 2), "ganancia_neta": round((monto * c_tot) - monto, 2)}

