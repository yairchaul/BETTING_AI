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
            # Inferencia de Lambdas (Agnóstico Global)
            try:
                def to_p(o):
                    val = float(str(o).replace('+', ''))
                    return 100/(val+100) if val>0 else abs(val)/(abs(o)+100)
                
                # Base de goles esperados (Ajustable por liga, 2.8 es promedio global)
                l_h = to_p(g['home_odd']) * 3.0
                l_v = to_p(g['away_odd']) * 3.0
            except: l_h, l_v = 1.5, 1.2

            # Generar Matriz de Probabilidades
            m = np.fromfunction(np.vectorize(lambda h, v: self._poisson_pmf(h, l_h) * self._poisson_pmf(v, l_v)), (7, 7))

            # --- CAPAS DE EVALUACIÓN ---
            opciones = []
            
            # 1. Over Puro (1.5, 0.5 2T)
            p_o15 = 1 - (m[0,0] + m[0,1] + m[1,0])
            opciones.append({"pick": "Over 1.5 Goles", "p": p_o15, "c": 1.35})
            
            # 2. BTTS
            p_btts = (1 - m[0,:].sum()) * (1 - m[:,0].sum())
            opciones.append({"pick": "Ambos Anotan", "p": p_btts, "c": 1.80})

            # 3. Doble Oportunidad (1X / X2) - Muy alta prob
            p_1x = m.sum() - np.tril(m, -1).sum() # Gana local o empata
            opciones.append({"pick": f"{g['home']} o Empate", "p": p_1x, "c": 1.40})

            # 4. Gana Local / Gana Visita
            p_h = np.tril(m, -1).sum()
            opciones.append({"pick": f"Gana {g['home']}", "p": p_h, "c": g['home_odd']})

            # --- FILTRO Y SELECCIÓN ---
            # Solo mantenemos lo que supere el 85% de éxito
            validas = [o for o in opciones if o['p'] >= self.threshold]

            if validas:
                # Elegimos la cuota más alta entre las seguras
                mejor = max(validas, key=lambda x: x['c'])
                resultados_finales.append({
                    "partido": f"{g['home']} vs {g['away']}",
                    "pick": mejor['pick'],
                    "probabilidad": round(mejor['p'] * 100, 1),
                    "cuota": mejor['c']
                })

        # Armamos parlay con los 3 mejores picks globales
        parlay = sorted(resultados_finales, key=lambda x: x['probabilidad'], reverse=True)[:3]
        return resultados_finales, parlay

    def simulate_parlay_profit(self, parlay, monto):
        c_tot = 1.0
        for p in parlay:
            try:
                val = float(str(p['cuota']).replace('+', ''))
                c_tot *= ((val/100 + 1) if val > 0 else (100/abs(val) + 1))
            except: c_tot *= 1.35
        pago = monto * c_tot
        return {"cuota_total": round(c_tot, 2), "pago_total": round(pago, 2), "ganancia_neta": round(pago - monto, 2)}
